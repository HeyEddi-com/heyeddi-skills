"""Classify a shell command as allow, plan, or deny.

Allow: local edits, reads, and terraform fmt/validate/init.
Plan: terraform plan, tofu plan, pulumi preview, ansible-playbook --check.
      The agent must warn the user what would change. Nothing is applied.
Deny: live mutations (apply, destroy, gcloud writes, Firebase deploy, and
      the same class of command hidden in bash -c, substitutions, or scripts).
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import shlex
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

ACTION_ALLOW = "allow"
ACTION_PLAN = "plan"
ACTION_DENY = "deny"

_MAX_SCRIPT_BYTES = 200_000
_SHELLS = {"bash", "sh", "zsh", "dash", "ash"}
_RUNNERS = {"npx", "npm", "pnpm", "yarn", "bunx", "bun"}
_WRAPPERS = {"sudo", "command", "nohup", "time", "nice", "stdbuf"}
_SUDO_ARG_FLAGS = {"-u", "-g", "--user", "--group"}
_TF_BINS = {"terraform", "tofu"}
_TF_DENY = {
    "apply",
    "destroy",
    "import",
    "taint",
    "untaint",
    "refresh",
    "force-unlock",
}
_TF_STATE_DENY = {"push", "rm", "mv", "replace-provider"}
_TF_WORKSPACE_DENY = {"delete", "new"}
_GCLOUD_LOCAL = {"config", "auth", "components", "topic", "help", "info", "version", "cheat-sheet"}
_GCLOUD_SKIP = {"alpha", "beta", "preview"}
_MUTATE = {
    "add",
    "add-iam-policy-binding",
    "apply",
    "bind",
    "cancel",
    "create",
    "delete",
    "deploy",
    "destroy",
    "disable",
    "enable",
    "execute",
    "import",
    "insert",
    "invoke",
    "kill",
    "move",
    "patch",
    "publish",
    "remove",
    "remove-iam-policy-binding",
    "rename",
    "replace",
    "reset",
    "resume",
    "send",
    "set",
    "set-iam-policy",
    "ssh",
    "start",
    "stop",
    "submit",
    "suspend",
    "unbind",
    "undelete",
    "update",
    "upload",
}
_GSUTIL_READ = {"ls", "cat", "stat", "du", "hash", "help", "version"}
_BQ_READ = {"ls", "show", "head", "version", "help"}
_KUBECTL_READ = {
    "get",
    "describe",
    "logs",
    "top",
    "explain",
    "api-resources",
    "api-versions",
    "cluster-info",
    "diff",
    "auth",
    "config",
    "version",
    "options",
    "port-forward",
}
_HELM_READ = {
    "list",
    "ls",
    "get",
    "status",
    "history",
    "show",
    "search",
    "version",
    "template",
    "lint",
    "diff",
    "repo",
    "env",
    "plugin",
    "pull",
}
_AWS_READ_PREFIXES = (
    "describe",
    "list",
    "get",
    "head",
    "lookup",
    "search",
    "filter",
    "preview",
    "estimate",
    "simulate",
    "test",
    "wait",
    "ls",
)
_AWS_LOCAL = {"configure", "help", "version"}
_GAM_READ = {"info", "show", "print", "version", "help"}
_LIVE_EMBEDDED = re.compile(
    r"\b(?:terraform|tofu)\b[\s\S]{0,80}?\b(?:apply|destroy|import|taint|refresh)\b"
    r"|\bgcloud\b[\s\S]{0,160}\b(?:delete|deploy|create|update|set-iam-policy|add-iam-policy-binding)\b"
    r"|\bfirebase(?:-tools)?\b[\s\S]{0,40}\bdeploy\b",
    re.IGNORECASE,
)
_GOOGLE_HOST = re.compile(
    r"https?://[^\s'\"`]*(?:googleapis\.com|google\.com|cloud\.google\.com|firebaseio\.com|run\.app)",
    re.IGNORECASE,
)
_HTTP_WRITE = re.compile(
    r"(?:-X|--request)\s*(?:POST|PUT|PATCH|DELETE)\b|--data(?:-binary|-raw)?\b|--json\b|(?:^|\s)-d(?:\s|$)",
    re.IGNORECASE,
)
_ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    tool: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"action": self.action, "reason": self.reason, "tool": self.tool}


def _embedded_deny(text: str) -> Decision | None:
    if _LIVE_EMBEDDED.search(text):
        return _deny("script", "script or -c payload contains a live infrastructure command")
    return None


def _allow() -> Decision:
    return Decision(ACTION_ALLOW, "read or local command")


def _plan(tool: str, reason: str) -> Decision:
    return Decision(ACTION_PLAN, reason, tool)


def _deny(tool: str, reason: str) -> Decision:
    return Decision(ACTION_DENY, reason, tool)


def _basename(token: str) -> str:
    name = token.replace("\\", "/").rsplit("/", 1)[-1]
    if name.endswith(".exe"):
        name = name[:-4]
    return name.lower()


# Commands whose message arguments and stdin are text, never something the shell runs.
_DATA_COMMAND = re.compile(
    r"^\s*(?:git(?:\s+-C\s+[^\s'\"]+)?\s+(?:commit|tag|notes)\b"
    r"|gh\s+(?:pr|issue|release)\s+(?:create|comment|edit|review|close|merge)\b)"
)
_MESSAGE_FLAG = re.compile(r"(?:^|\s)(?:-[a-zA-Z]*m|--message|-b|--body|-t|--title|-n|--notes)(?:\s+|=)?$")
_STDIN_FLAG = re.compile(r"(?:^|\s)(?:-F|--file|--body-file|--notes-file)(?:\s+|=)-\s*$")
_HEREDOC = re.compile(r"<<(-?)[ \t]*(['\"])([A-Za-z_]\w*)\2[ \t]*(?=\n)")


def strip_inert_text(command: str) -> str:
    """Drop text the shell never runs: comments, and git / gh messages quoted so nothing expands.

    That means single-quoted message arguments and quoted heredocs fed to a git
    or gh message. Anything this scanner does not fully understand is returned
    unchanged, so it is judged as before.
    """
    blank: list[tuple[int, int]] = []
    stack: list[list] = [["code", 0]]  # [kind, start of the current command]
    i, n = 0, len(command)
    while i < n:
        kind, start = stack[-1]
        char = command[i]
        if char == "\\":
            i += 2
            continue
        if char == "`":
            end = command.find("`", i + 1)
            if end < 0:
                return command
            i = end + 1
            continue
        if command.startswith("${", i):
            end = command.find("}", i)
            if end < 0 or any(c in command[i + 2 : end] for c in " \t\n#'\"`("):
                return command
            i = end + 1
            continue
        if command.startswith("$(", i):
            stack.append(["subst", i + 2])
            i += 2
            continue
        if kind == "dquote":
            if char == '"':
                stack.pop()
            i += 1
            continue
        if char == "#" and (i == 0 or command[i - 1] in " \t\n;&|("):
            end = command.find("\n", i)
            end = n if end < 0 else end
            blank.append((i, end))
            i = end
            continue
        if char == "'":
            if i and command[i - 1] == "$":
                return command
            end = command.find("'", i + 1)
            if end < 0:
                return command
            before = command[start:i]
            if _DATA_COMMAND.match(before) and _MESSAGE_FLAG.search(before):
                blank.append((i + 1, end))
            i = end + 1
            continue
        if command.startswith("<<<", i):
            i += 3
            continue
        if command.startswith("<<", i):
            doc = _HEREDOC.match(command, i)
            if not doc:
                return command
            before = command[start:i]
            from_stdin = len(stack) == 1 and _DATA_COMMAND.match(before) and _STDIN_FLAG.search(before)
            # Only `git ... "$(cat <<'EOF'`: deeper nesting could hand the text to a shell.
            through_cat = (
                kind == "subst"
                and before.strip() == "cat"
                and [frame[0] for frame in stack[:-1]] in (["code"], ["code", "dquote"])
                and _DATA_COMMAND.match(command[stack[0][1] : i])
            )
            if not (from_stdin or through_cat):
                return command
            indent = r"\t*" if doc.group(1) else ""
            close = re.compile(rf"^{indent}{doc.group(3)}$", re.M).search(command, doc.end() + 1)
            if not close:
                return command
            blank.append((doc.end() + 1, close.start()))
            i = close.end()
            continue
        if char == '"':
            stack.append(["dquote", i + 1])
        elif char == "(":
            stack.append(["paren", i + 1])
        elif char == ")" and len(stack) > 1:
            stack.pop()
        elif char in ";\n&|":
            stack[-1][1] = i + 1
        i += 1
    if len(stack) != 1:
        return command
    for begin, end in reversed(blank):
        command = command[:begin] + command[end:]
    return command


def split_segments(command: str) -> list[str]:
    """Split on unquoted &&, ||, ;, |, and newlines."""
    segments: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    i = 0
    n = len(command)
    while i < n:
        c = command[i]
        if quote:
            buf.append(c)
            if c == quote and command[i - 1] != "\\":
                quote = None
            i += 1
            continue
        if c in {"'", '"'}:
            quote = c
            buf.append(c)
            i += 1
            continue
        if c in {"\n", ";"}:
            segments.append("".join(buf))
            buf = []
            i += 1
            continue
        if command.startswith("&&", i) or command.startswith("||", i):
            segments.append("".join(buf))
            buf = []
            i += 2
            continue
        if c == "|":
            segments.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    segments.append("".join(buf))
    return [part.strip() for part in segments if part.strip()]


def _substitutions(command: str) -> list[str]:
    found: list[str] = []
    i = 0
    while i < len(command):
        if command.startswith("$(", i):
            depth = 1
            j = i + 2
            while j < len(command) and depth:
                if command.startswith("$(", j):
                    depth += 1
                    j += 2
                    continue
                if command[j] == ")":
                    depth -= 1
                j += 1
            found.append(command[i + 2 : j - 1])
            i = j
            continue
        if command[i] == "`":
            j = command.find("`", i + 1)
            if j == -1:
                break
            found.append(command[i + 1 : j])
            i = j + 1
            continue
        i += 1
    return found


def _tokenize(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _unwrap(tokens: list[str]) -> list[str]:
    tokens = list(tokens)
    while tokens and _ENV_ASSIGN.match(tokens[0]):
        tokens.pop(0)
    while tokens and _basename(tokens[0]) in _WRAPPERS:
        tokens.pop(0)
        while tokens and tokens[0].startswith("-"):
            flag = tokens.pop(0)
            if flag in _SUDO_ARG_FLAGS and tokens:
                tokens.pop(0)
    if tokens and _basename(tokens[0]) in _RUNNERS:
        tokens.pop(0)
        if tokens and tokens[0] in {"exec", "dlx", "x"}:
            tokens.pop(0)
        while tokens and tokens[0].startswith("-"):
            tokens.pop(0)
    return tokens


def _skip_flags(tokens: list[str], arg_flags: set[str] | None = None) -> list[str]:
    arg_flags = arg_flags or set()
    i = 0
    while i < len(tokens) and tokens[i].startswith("-"):
        token = tokens[i]
        name = token.split("=", 1)[0]
        i += 1
        if "=" not in token and name in arg_flags and i < len(tokens):
            i += 1
    return tokens[i:]


def _first_unflagged(tokens: list[str], arg_flags: set[str] | None = None) -> str:
    rest = _skip_flags(tokens, arg_flags)
    return rest[0] if rest else ""


def _classify_terraform(tokens: list[str], binary: str) -> Decision:
    rest = _skip_flags(tokens[1:], {"-chdir"})
    if not rest:
        return _allow()
    sub = rest[0]
    nxt = rest[1] if len(rest) > 1 else ""
    if sub == "state" and nxt in _TF_STATE_DENY:
        return _deny(binary, f"{binary} state {nxt} changes remote state")
    if sub == "workspace" and nxt in _TF_WORKSPACE_DENY:
        return _deny(binary, f"{binary} workspace {nxt} changes remote workspaces")
    if sub in _TF_DENY:
        return _deny(binary, f"{binary} {sub} changes live infrastructure")
    if sub == "plan":
        return _plan(binary, f"{binary} plan shows what would change and does not apply it")
    return _allow()


def _service_tokens(tokens: list[str]) -> list[str]:
    rest = _skip_flags(tokens[1:], {"--project", "--billing-project", "--account", "--configuration", "--impersonate-service-account"})
    while rest and rest[0] in _GCLOUD_SKIP:
        rest = rest[1:]
    return rest


def _has_mutate(tokens: list[str]) -> str:
    for token in tokens:
        if token.lower() in _MUTATE:
            return token.lower()
    return ""


def _classify_gcloud(tokens: list[str]) -> Decision:
    rest = _service_tokens(tokens)
    if not rest:
        return _allow()
    if rest[0] in _GCLOUD_LOCAL:
        return _allow()
    verb = _has_mutate(rest)
    if verb:
        return _deny("gcloud", f"gcloud {verb} changes live Google Cloud resources")
    return _allow()


def _classify_firebase(tokens: list[str]) -> Decision:
    rest = [token for token in tokens[1:] if not token.startswith("-")]
    if any(token == "emulators" or token.startswith("emulators:") for token in rest):
        return _allow()
    if any(token in {"login", "logout", "help", "use", "projects:list"} for token in rest):
        if not any(token == "deploy" or "delete" in token or "disable" in token for token in rest):
            return _allow()
    blob = " ".join(rest).lower()
    if any(word in blob for word in ("deploy", "delete", "disable", "create", "update", ":set")):
        return _deny("firebase", "firebase command changes live Firebase or Google resources")
    return _allow()


def _classify_gsutil(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:])
    sub = rest[0] if rest else ""
    if sub in _GSUTIL_READ:
        return _allow()
    return _deny("gsutil", f"gsutil {sub or 'command'} can write or delete live objects")


def _classify_bq(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:])
    sub = rest[0] if rest else ""
    if sub in _BQ_READ:
        return _allow()
    if sub == "query" and any(token == "--dry_run" or token.startswith("--dry_run") for token in tokens):
        return _plan("bq", "bq query --dry_run does not run the query")
    return _deny("bq", f"bq {sub or 'command'} can change BigQuery data")


def _classify_kubectl(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:], {"-n", "--namespace", "--context", "--kubeconfig", "-f", "--filename"})
    sub = rest[0] if rest else ""
    if sub in _KUBECTL_READ:
        return _allow()
    return _deny("kubectl", f"kubectl {sub or 'command'} changes a live cluster")


def _classify_helm(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:], {"-n", "--namespace", "--kube-context", "--kubeconfig"})
    sub = rest[0] if rest else ""
    if sub in _HELM_READ:
        return _allow()
    return _deny("helm", f"helm {sub or 'command'} changes a live cluster")


def _aws_is_read(token: str) -> bool:
    lower = token.lower()
    return lower.startswith(_AWS_READ_PREFIXES) or lower in {"help", "version"}


def _classify_aws(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:], {"--profile", "--region", "--endpoint-url"})
    if not rest:
        return _allow()
    if rest[0] in _AWS_LOCAL:
        return _allow()
    if rest[0] == "sts" and len(rest) > 1 and rest[1] == "get-caller-identity":
        return _allow()
    if rest[0] == "s3" and len(rest) > 1 and rest[1] in {"cp", "mv", "rm", "mb", "rb", "sync"}:
        return _deny("aws", f"aws s3 {rest[1]} changes live objects")
    for token in rest:
        lower = token.lower()
        if _aws_is_read(lower):
            continue
        if lower in {"update-kubeconfig", "get-caller-identity"}:
            continue
        if lower in _MUTATE or lower.startswith(("put-", "delete-", "create-", "update-", "terminate-", "modify-", "remove-", "attach-", "detach-", "run-")):
            return _deny("aws", f"aws {lower} changes live resources")
    return _allow()


def _classify_pulumi(tokens: list[str]) -> Decision:
    rest = _skip_flags(tokens[1:], {"--stack", "-s", "--cwd"})
    sub = rest[0] if rest else ""
    if sub in {"preview", "diff"}:
        return _plan("pulumi", "pulumi preview shows what would change and does not apply it")
    if sub in {"up", "destroy", "refresh", "cancel", "import"}:
        return _deny("pulumi", f"pulumi {sub} changes live infrastructure")
    if sub == "state" and len(rest) > 1 and rest[1] in {"delete", "unprotect"}:
        return _deny("pulumi", f"pulumi state {rest[1]} changes state")
    if sub == "stack" and len(rest) > 1 and rest[1] in {"rm", "init"}:
        return _deny("pulumi", f"pulumi stack {rest[1]} changes stacks")
    return _allow()


def _classify_ansible(tokens: list[str]) -> Decision:
    if any(token in {"--check", "-C"} for token in tokens[1:]):
        return _plan("ansible-playbook", "ansible-playbook --check is a dry run")
    return _deny("ansible-playbook", "ansible-playbook applies changes to live hosts")


def _classify_gam(tokens: list[str]) -> Decision:
    rest = [token for token in tokens[1:] if not token.startswith("-")]
    sub = rest[0].lower() if rest else ""
    if sub in _GAM_READ:
        return _allow()
    return _deny("gam", "GAM commands can change Google Workspace, including calendar accounts")


def _classify_http(segment: str, binary: str) -> Decision | None:
    if _GOOGLE_HOST.search(segment) and _HTTP_WRITE.search(segment):
        return _deny(binary, f"{binary} write to a Google API changes live data")
    return None


def _script_text(token: str, cwd: Path | None) -> str | None:
    if token.startswith("-"):
        return None
    path = Path(token)
    if not path.is_absolute() and cwd is not None:
        path = cwd / path
    if path.suffix.lower() not in {".sh", ".bash", ".py"}:
        return None
    try:
        if not path.is_file() or path.stat().st_size > _MAX_SCRIPT_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# The gate's own files hold command strings as data. Only an identical copy is trusted.
_OWN_FILES = {"classify_command.py", "permission_policy.py", "check_permission.py",
              "hook_before_shell.py", "hook_before_mcp.py"}
_PROCESS_CALLS = {"run", "call", "check_call", "check_output", "Popen", "getoutput", "getstatusoutput"}
_PASS_THROUGH = {"bash", "sh", "zsh", "dash", "ash", "env", "sudo", "nohup", "xargs", "ssh", "npx"}


def _is_own_file(token: str, cwd: Path | None) -> bool:
    path = Path(token)
    if not path.is_absolute() and cwd is not None:
        path = cwd / path
    if path.name not in _OWN_FILES:
        return False
    try:
        return path.read_bytes() == (Path(__file__).resolve().parent / path.name).read_bytes()
    except OSError:
        return False


def _executable_python(text: str) -> str:
    """Python source without what never runs a command: comments, docstrings, imports."""
    try:
        tree = ast.parse(text)
        lines = [line.encode() for line in text.split("\n")]
        for node in ast.walk(tree):
            bare_string = (
                isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            )
            if not (bare_string or isinstance(node, (ast.Import, ast.ImportFrom))):
                continue
            first, last = node.lineno - 1, node.end_lineno - 1
            for row in range(first, last + 1):
                begin = node.col_offset if row == first else 0
                end = node.end_col_offset if row == last else len(lines[row])
                lines[row] = lines[row][:begin] + b" " * (end - begin) + lines[row][end:]
        source = b"\n".join(lines).decode()
        rows = source.split("\n")
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                row, column = token.start
                rows[row - 1] = rows[row - 1][:column]
        return "\n".join(rows)
    except (SyntaxError, ValueError, tokenize.TokenError):
        return text


def _words_of(node: ast.AST, names: dict[str, list[ast.AST]], seen: set[str]) -> tuple[list[str], bool]:
    """Literal words an expression can hold, and whether part of it is unknown."""
    if isinstance(node, ast.Constant):
        return ([node.value] if isinstance(node.value, str) else []), False
    if isinstance(node, ast.Attribute) and ast.unparse(node) == "sys.executable":
        return ["python3"], False
    if isinstance(node, ast.Starred):
        return _words_of(node.value, names, seen)
    if isinstance(node, ast.Name) and node.id in names and node.id not in seen:
        parts = [_words_of(value, names, seen | {node.id}) for value in names[node.id]]
        return [w for words, _ in parts for w in words], any(unknown for _, unknown in parts)
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        parts = [_words_of(item, names, seen) for item in node.elts]
        words = [w for found, _ in parts for w in found]
        head = {_basename(w) for w in parts[0][0]}
        # An unknown argument matters only when the program runs its arguments.
        python_code = "-c" in words and any(h.startswith("python") for h in head)
        runs_arguments = bool(head & _PASS_THROUGH) or python_code
        return words, parts[0][1] or (runs_arguments and any(unknown for _, unknown in parts))
    constants = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    return constants, True


def _starts_process(module: str, name: str) -> bool:
    if module == "subprocess":
        return name in _PROCESS_CALLS
    if module == "os":
        return name in {"system", "popen"} or name.startswith(("exec", "spawn"))
    return module == "asyncio" and name.startswith("create_subprocess_")


def _test_file_runs_live(text: str, depth: int) -> Decision | None:
    """For `python -m pytest <file>`: judge the commands its process calls run.

    Test files quote live commands as data. When a call's program cannot be
    read from the source, any live command in the file counts.
    """
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return _embedded_deny(text)
    names: dict[str, list[ast.AST]] = {}
    imported: set[str] = set()
    modules = {"subprocess": "subprocess", "os": "os", "asyncio": "asyncio"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.setdefault(target.id, []).append(node.value)
        elif isinstance(node, ast.Import):
            modules.update({a.asname: a.name for a in node.names if a.asname and a.name in modules})
        elif isinstance(node, ast.ImportFrom) and node.module in modules:
            imported.update(a.asname or a.name for a in node.names if _starts_process(node.module, a.name))
    unknown_call = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = ast.unparse(node.func)
        module, _, attr = func.rpartition(".")
        module = modules.get(module, module)
        if not (func in imported or _starts_process(module, attr)):
            continue
        arguments = list(node.args) or [k.value for k in node.keywords if k.arg in {"args", "cmd"}]
        if module == "os" and attr.startswith(("exec", "spawn")):
            arguments = [ast.List(elts=arguments)]
        if not arguments:
            unknown_call = True
            continue
        words, unknown = _words_of(arguments[0], names, set())
        unknown_call = unknown_call or unknown
        line = " ".join(words)
        found = _embedded_deny(line) or classify(line, depth=depth + 1)
        if found.action == ACTION_DENY:
            return _deny("script", "test file runs a live infrastructure command")
    return _embedded_deny(_executable_python(text)) if unknown_call else None


def _classify_tokens(tokens: list[str], segment: str, cwd: Path | None, depth: int) -> Decision:
    if not tokens:
        return _allow()
    binary = _basename(tokens[0])
    if binary in _SHELLS:
        flags = tokens[1:]
        if "-c" in flags or "--command" in flags:
            try:
                idx = flags.index("-c")
            except ValueError:
                idx = flags.index("--command")
            if idx + 1 < len(flags):
                return classify(flags[idx + 1], cwd=cwd, depth=depth + 1)
        for token in flags:
            text = _script_text(token, cwd) if depth < 2 else None
            if text:
                embedded = _embedded_deny(text)
                if embedded is not None:
                    return embedded
                nested = classify(text, cwd=cwd, depth=depth + 1)
                if nested.action != ACTION_ALLOW:
                    return nested
        return _allow()
    if binary in {"python", "python3", "python3.12", "python3.14"}:
        if "-c" in tokens:
            idx = tokens.index("-c")
            if idx + 1 < len(tokens):
                payload = tokens[idx + 1]
                embedded = _embedded_deny(payload)
                if embedded is not None:
                    return embedded
                return classify(payload, cwd=cwd, depth=depth + 1)
        pytest_run = any(a == "-m" and b == "pytest" for a, b in zip(tokens, tokens[1:]))
        for token in tokens[1:]:
            text = _script_text(token, cwd) if depth < 2 else None
            if not text or _is_own_file(token, cwd):
                continue
            if pytest_run:
                live = _test_file_runs_live(text, depth)
                if live is not None:
                    return live
                continue
            if token.endswith(".py"):
                text = _executable_python(text)
            embedded = _embedded_deny(text)
            if embedded is not None:
                return embedded
            nested = classify(text, cwd=cwd, depth=depth + 1)
            if nested.action != ACTION_ALLOW:
                return nested
        return _allow()
    if binary in _TF_BINS:
        return _classify_terraform(tokens, binary)
    if binary == "gcloud":
        return _classify_gcloud(tokens)
    if binary in {"firebase", "firebase-tools"}:
        return _classify_firebase(tokens)
    if binary == "gsutil":
        return _classify_gsutil(tokens)
    if binary == "bq":
        return _classify_bq(tokens)
    if binary == "kubectl":
        return _classify_kubectl(tokens)
    if binary == "helm":
        return _classify_helm(tokens)
    if binary == "aws":
        return _classify_aws(tokens)
    if binary == "pulumi":
        return _classify_pulumi(tokens)
    if binary == "ansible-playbook":
        return _classify_ansible(tokens)
    if binary in {"gam", "gam7", "gamadv"}:
        return _classify_gam(tokens)
    if binary in {"curl", "wget", "http", "https"}:
        http = _classify_http(segment, binary)
        if http is not None:
            return http
    text = _script_text(tokens[0], cwd) if depth < 2 else None
    if text and not _is_own_file(tokens[0], cwd):
        if tokens[0].endswith(".py"):
            text = _executable_python(text)
        embedded = _embedded_deny(text)
        if embedded is not None:
            return embedded
        return classify(text, cwd=cwd, depth=depth + 1)
    return _allow()


def _rank(decision: Decision) -> int:
    return {ACTION_ALLOW: 0, ACTION_PLAN: 1, ACTION_DENY: 2}[decision.action]


def classify(command: str, cwd: Path | None = None, depth: int = 0) -> Decision:
    if depth > 3 or not command or not command.strip():
        return _allow()
    command = strip_inert_text(command)
    pieces = [command, *_substitutions(command)]
    decision = _allow()
    for piece in pieces:
        for segment in split_segments(piece):
            tokens = _unwrap(_tokenize(segment))
            current = _classify_tokens(tokens, segment, cwd, depth)
            if _rank(current) > _rank(decision):
                decision = current
            if decision.action == ACTION_DENY:
                return decision
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify a shell command for the local-first gate")
    parser.add_argument("--command", required=True)
    parser.add_argument("--cwd", default="")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the command is a live mutation. Plan and allow exit 0.",
    )
    args = parser.parse_args(argv)
    cwd = Path(args.cwd).resolve() if args.cwd else None
    decision = classify(args.command, cwd=cwd)
    payload = decision.as_dict()
    if decision.action == ACTION_PLAN:
        payload["warning"] = (
            "Tell the user what would be created, changed, or destroyed. Do not apply."
        )
    if decision.action == ACTION_DENY:
        payload["blocked"] = True
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if args.check and decision.action == ACTION_DENY:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
