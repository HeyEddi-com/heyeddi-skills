#!/usr/bin/env python3
"""Post replies on unresolved pull-request review threads only.

Never use bare ``gh pr comment`` for individual replies (top-level spam).
Never quote-reply issue comments.

Resolution (mandatory — never guess):
- Review thread → REST ``/pulls/{pr}/comments/{ROOT_id}/replies``
  (walk ``in_reply_to_id`` to the top-level comment; GitHub rejects reply-to-reply)
- On REST failure → GraphQL ``addPullRequestReviewThreadReply``
- Issue comments, tests-hold notes, review summaries, and comments written by
  the responding account are skipped. There is no quote.

Outgoing bodies that still contain ``<<<UNTRUSTED_`` are refused.

If this script still errors for a review-thread id, the agent MUST use GitHub
MCP ``add_reply_to_pull_request_comment`` with the root id — never report
"thread not found" as done, and never ``add_issue_comment`` to quote a parent.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from _comment_resolve import (
    ReplyTarget,
    build_comment_index,
    find_review_thread_id,
    resolve_reply_target,
)


def _load_sibling(module_name: str):
    path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(
        f"heyeddi_pr_respond.{module_name}",
        path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


is_already_wrapped = _load_sibling("_untrusted_doc").is_already_wrapped
from _replies_parse import (
    infer_reply_kind,
    parse_reply_sections,
    summary_is_last,
)
from _skill_cli import emit, resolve_project_root, run_command
from _temp_store import comments_cache_path
from assert_fixes_pushed import evaluate as evaluate_fixes_pushed

# Status values that satisfy verify_response checks
OK_STATUSES = frozenset(
    {
        "posted",
        "dry-run",
        "skipped_review_body",
        "skipped_issue_comment",
        "skipped_own",
        "skipped_answered",
        "already-replied",
    }
)

_SKIP_STATUS = {
    "skip_review": "skipped_review_body",
    "skip_issue_comment": "skipped_issue_comment",
    "skip_own": "skipped_own",
    "skip_answered": "skipped_answered",
}

_UNTRUSTED_REFUSAL = (
    "refusing to post a body that still contains <<<UNTRUSTED_. "
    "Use the plain reply text. The wrapper stays in the comment cache the model reads."
)

BANNED_BODY = re.compile(
    r"acknowledged review attachment|inline threads carry the detailed",
    re.IGNORECASE,
)


def _load_replies_text(args: argparse.Namespace) -> str:
    if args.replies_text:
        return args.replies_text
    if args.replies_file:
        path = Path(args.replies_file)
        if not path.is_file():
            emit(json.dumps({"error": "replies file not found", "path": str(path)}, indent=2))
            sys.exit(1)
        return path.read_text(encoding="utf-8")
    emit(
        json.dumps(
            {
                "error": "missing replies draft",
                "hint": (
                    "Pass --replies-text or --replies-file. "
                    "Do not write pr-*-replies.md under .heyeddi/docs/."
                ),
            },
            indent=2,
        )
    )
    sys.exit(1)


def _resolve_repo(root: Path, cache_path: Path) -> str | None:
    if cache_path.is_file():
        try:
            repo = json.loads(cache_path.read_text(encoding="utf-8")).get("repo")
            if isinstance(repo, str) and repo.strip():
                return repo.strip()
        except (json.JSONDecodeError, OSError):
            pass
    if not shutil.which("gh"):
        return None
    out = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        root,
    )
    if out.startswith("[exit") or out.startswith("[error]"):
        return None
    return out.strip() or None


def _load_cache(cache_path: Path) -> dict[str, Any]:
    if not cache_path.is_file():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _gh_api_json(
    root: Path,
    endpoint: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    cmd = ["gh", "api", endpoint, "-X", method, "-H", "Accept: application/vnd.github+json"]
    stdin = None
    if payload is not None:
        cmd.extend(["--input", "-"])
        stdin = json.dumps(payload)
    raw = run_command(cmd, root, stdin_text=stdin)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return None, raw[:500]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "non-JSON response"
    return data, None


def _post_review_reply_rest(
    root: Path, repo: str, pr: int, root_comment_id: str, body: str
) -> tuple[str, str | None]:
    data, err = _gh_api_json(
        root,
        f"repos/{repo}/pulls/{pr}/comments/{root_comment_id}/replies",
        method="POST",
        payload={"body": body},
    )
    if err or not isinstance(data, dict):
        return "error", err or "empty response"
    reply_id = data.get("id")
    return "posted", str(reply_id) if reply_id is not None else None


def _post_review_reply_graphql(
    root: Path, repo: str, pr: int, root_comment_id: str, body: str
) -> tuple[str, str | None]:
    thread_id = find_review_thread_id(root, repo, pr, root_comment_id)
    if not thread_id:
        return (
            "error",
            f"GraphQL fallback: no review thread contains comment {root_comment_id}",
        )
    mutation = (
        "mutation($threadId:ID!,$body:String!){"
        "addPullRequestReviewThreadReply(input:{"
        "pullRequestReviewThreadId:$threadId,body:$body"
        "}){comment{databaseId id}}}"
    )
    # body=@- keeps multiline / special characters intact (never -f body=...)
    raw = run_command(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={mutation}",
            "-f",
            f"threadId={thread_id}",
            "-f",
            "body=@-",
        ],
        root,
        stdin_text=body,
    )
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    try:
        data = json.loads(raw)
        errors = data.get("errors")
        if errors:
            return "error", json.dumps(errors)[:300]
        comment = (
            ((data.get("data") or {}).get("addPullRequestReviewThreadReply") or {}).get(
                "comment"
            )
            or {}
        )
        rid = comment.get("databaseId") or comment.get("id")
        return "posted", str(rid) if rid is not None else thread_id
    except json.JSONDecodeError:
        return "error", "graphql non-JSON"


def _already_replied_inline(
    root: Path, repo: str, pr: int, root_comment_id: str
) -> bool:
    """True when this root thread already has at least one reply (any author)."""
    data, err = _gh_api_json(
        root, f"repos/{repo}/pulls/{pr}/comments?per_page=100", method="GET"
    )
    # Prefer paginated dedicated fetch when list endpoint used without paginate —
    # fall back to single-comment children check via full paginate.
    if err or not isinstance(data, list):
        raw = run_command(
            ["gh", "api", f"repos/{repo}/pulls/{pr}/comments", "--paginate"],
            root,
        )
        if raw.startswith("[exit") or raw.startswith("[error]"):
            return False
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return False
    if not isinstance(data, list):
        return False
    for item in data:
        if not isinstance(item, dict):
            continue
        if str(item.get("in_reply_to_id") or "") == str(root_comment_id):
            return True
    return False


def _post_one(
    *,
    root: Path,
    repo: str,
    pr: int,
    target: ReplyTarget,
    body: str,
) -> tuple[str, str | None, list[str]]:
    """Post using resolved target. Returns (status, ref, attempts)."""
    attempts: list[str] = []
    if BANNED_BODY.search(body):
        return (
            "error",
            "banned body: do not post 'Acknowledged review attachment' top-level spam",
            attempts,
        )

    skipped = _SKIP_STATUS.get(target.post_method)
    if skipped:
        return skipped, target.detail or skipped, attempts

    if is_already_wrapped(body):
        return "error", _UNTRUSTED_REFUSAL, attempts

    if target.post_method == "unresolved" or not target.reply_to_id:
        hint = target.mcp_hint or "Use GitHub MCP pull_request_read get_review_comments"
        return (
            "error",
            (target.detail or f"Cannot resolve {target.input_id}") + f" | fallback: {hint}",
            attempts,
        )

    if target.post_method != "review_reply":
        return (
            "error",
            f"unsupported post_method {target.post_method} for {target.input_id}",
            attempts,
        )

    # inline review_reply — body is posted as-is, never quoted from the parent
    root_id = target.reply_to_id
    attempts.append(f"REST pulls/{pr}/comments/{root_id}/replies")
    status, ref = _post_review_reply_rest(root, repo, pr, root_id, body)
    if status == "posted":
        return status, ref, attempts

    attempts.append(f"REST failed: {ref}")
    # Common: already replied by us / race — treat as success only if a child exists
    if ref and ("422" in ref or "already" in ref.lower() or "replies to replies" in ref.lower()):
        if _already_replied_inline(root, repo, pr, root_id):
            # If 422 was "replies to replies", we should have walked to root already.
            # If still failing but thread has replies from a previous run, ok.
            if "replies to replies" not in (ref or "").lower():
                return "already-replied", root_id, attempts

    attempts.append("GraphQL addPullRequestReviewThreadReply")
    status, ref = _post_review_reply_graphql(root, repo, pr, root_id, body)
    if status == "posted":
        return status, ref, attempts
    attempts.append(f"GraphQL failed: {ref}")

    mcp = target.mcp_hint or (
        f"MCP add_reply_to_pull_request_comment commentId={root_id} pullNumber={pr}"
    )
    return (
        "error",
        f"All gh strategies failed for {target.input_id} (root={root_id}). "
        f"Last: {ref} | MUST fallback: {mcp}",
        attempts,
    )


def _gh_login(root: Path) -> str | None:
    if not shutil.which("gh"):
        return None
    out = run_command(["gh", "api", "user", "-q", ".login"], root)
    if out.startswith("[exit") or out.startswith("[error]"):
        return None
    login = out.strip()
    return login or None


def _post_summary_once(root: Path, pr: int, body: str) -> tuple[str, str | None]:
    """Only allowed use of top-level PR comment: a single final summary."""
    if is_already_wrapped(body):
        return "error", _UNTRUSTED_REFUSAL
    if BANNED_BODY.search(body):
        return "error", "banned summary body"
    raw = run_command(["gh", "pr", "comment", str(pr), "--body", body], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    url = raw.strip().splitlines()[-1] if raw.strip() else None
    return "posted", url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post drafted replies in-thread (never top-level per-comment spam)"
    )
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--replies-text",
        default=None,
        help="Draft replies markdown (## Comment <id> sections + ## Summary last)",
    )
    parser.add_argument(
        "--replies-file",
        default=None,
        help="Path to replies markdown (prefer --replies-text; never .heyeddi/docs/pr-*-ci-*)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate posts without calling gh (evals / offline); results on stdout only",
    )
    parser.add_argument(
        "--post-summary",
        action="store_true",
        help="Post ## Summary once via gh pr comment AFTER all threads succeed (optional)",
    )
    parser.add_argument(
        "--allow-unpushed",
        action="store_true",
        help=(
            "Skip commit+push gate (decline-only / no code changes). "
            "Never use after applying fixes — debate only sees remote HEAD."
        ),
    )
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    cache_path = comments_cache_path(args.pr)

    # Live posts require remote HEAD to already contain any code fixes.
    dry_run = args.dry_run or not shutil.which("gh")
    if not dry_run and not args.allow_unpushed:
        gate = evaluate_fixes_pushed(root)
        if not gate.get("ok"):
            emit(
                json.dumps(
                    {
                        "error": "commit_push_required_before_replies",
                        "issues": gate.get("issues"),
                        "dirty_paths": gate.get("dirty_paths"),
                        "unpushed_commits": gate.get("unpushed_commits"),
                        "rule": gate.get("rule"),
                        "hint": (
                            "Commit + push fixes to the PR branch, then re-run "
                            "post_thread_replies. Do not claim Fixed while changes "
                            "are local-only."
                        ),
                    },
                    indent=2,
                )
            )
            sys.exit(1)

    replies_text = _load_replies_text(args)
    sections, summary_body = parse_reply_sections(replies_text)
    if not sections:
        emit(json.dumps({"error": "no ## Comment <id> sections in replies draft"}, indent=2))
        sys.exit(1)
    if summary_body is None or not summary_body.strip():
        emit(json.dumps({"error": "replies draft missing ## Summary body"}, indent=2))
        sys.exit(1)
    if not summary_is_last(replies_text):
        emit(json.dumps({"error": "## Summary must be last (after all individual replies)"}, indent=2))
        sys.exit(1)

    cache = _load_cache(cache_path)
    index = build_comment_index(cache)
    responder = cache.get("responder_login")
    responder_login = responder.strip() if isinstance(responder, str) and responder.strip() else None
    if responder_login is None and not dry_run:
        responder_login = _gh_login(root)
    repo = None if dry_run else _resolve_repo(root, cache_path)
    if not dry_run and not repo:
        emit(json.dumps({"error": "could not resolve repo for gh posts"}, indent=2))
        sys.exit(1)

    posted: list[dict] = []
    errors: list[str] = []
    succeeded_ids: set[str] = set()

    for section in sections:
        if not section.body.strip():
            errors.append(f"empty body for {section.comment_id}")
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": infer_reply_kind(section.comment_id, None, section.kind),
                    "status": "error",
                    "detail": "empty body",
                }
            )
            continue

        if BANNED_BODY.search(section.body):
            errors.append(f"{section.comment_id}: banned acknowledgement spam body")
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": infer_reply_kind(section.comment_id, None, section.kind),
                    "status": "error",
                    "detail": "banned acknowledgement body",
                }
            )
            continue

        kind_hint = infer_reply_kind(section.comment_id, None, section.kind)
        target = resolve_reply_target(
            root=root,
            repo=repo,
            pr=args.pr,
            comment_id=section.comment_id,
            kind_hint=kind_hint if kind_hint != "unknown" else section.kind,
            index=index,
            live=not dry_run,
            responder_login=responder_login,
        )

        if dry_run:
            status = _SKIP_STATUS.get(target.post_method, "dry-run")
            if target.post_method == "review_reply" and is_already_wrapped(section.body):
                status = "error"
                errors.append(f"{section.comment_id}: {_UNTRUSTED_REFUSAL}")
            if target.post_method == "unresolved":
                status = "error"
                errors.append(f"{section.comment_id}: {target.detail}")
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": target.kind,
                    "status": status,
                    "reply_ref": target.reply_to_id,
                    "post_method": target.post_method,
                    "resolve_detail": target.detail,
                    "mcp_fallback": target.mcp_hint,
                    "note": (
                        target.detail
                        if target.post_method in _SKIP_STATUS
                        else (
                            f"Would {target.post_method} → {target.reply_to_id}"
                            if target.reply_to_id
                            else target.detail
                        )
                    ),
                }
            )
            if status in OK_STATUSES:
                succeeded_ids.add(section.comment_id)
            continue

        assert repo is not None
        status, ref, attempts = _post_one(
            root=root,
            repo=repo,
            pr=args.pr,
            target=target,
            body=section.body,
        )

        entry: dict = {
            "comment_id": section.comment_id,
            "type": target.kind,
            "status": status,
            "reply_ref": ref if status in OK_STATUSES else None,
            "post_method": target.post_method,
            "resolved_root_id": target.reply_to_id,
            "resolve_detail": target.detail,
            "attempts": attempts,
            "mcp_fallback": target.mcp_hint,
        }
        if status in OK_STATUSES:
            succeeded_ids.add(section.comment_id)
            if status == "skipped_review_body":
                entry["detail"] = ref
        else:
            entry["detail"] = ref
            errors.append(f"{section.comment_id}: {ref}")
        posted.append(entry)

    summary_status = None
    if args.post_summary and not errors:
        if dry_run:
            summary_status = {"status": "dry-run", "reply_ref": None}
        else:
            status, ref = _post_summary_once(root, args.pr, summary_body)
            summary_status = {
                "status": status,
                "reply_ref": ref if status == "posted" else None,
            }
            if status != "posted":
                errors.append(f"summary: {ref}")

    payload = {
        "pr": args.pr,
        "dry_run": dry_run,
        "posted": posted,
        "posted_count": sum(1 for p in posted if p["status"] in OK_STATUSES),
        "error_count": len(errors),
        "errors": errors,
        "summary": summary_status,
        "rule": (
            "Reply only on unresolved review threads at the root comment id, "
            "with no quote. Never quote-reply issue comments. Never post a body "
            "that contains <<<UNTRUSTED_. On a review-thread error, use GitHub "
            "MCP add_reply_to_pull_request_comment with the root id."
        ),
        "hint": "Run verify_response.py --pr <N> --live --check after posting.",
    }

    emit(json.dumps(payload, indent=2))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
