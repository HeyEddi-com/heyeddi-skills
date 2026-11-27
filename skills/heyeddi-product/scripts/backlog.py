#!/usr/bin/env python3
"""Keep the backlog: `next` names the item to build; `add`, `done`, `block` maintain it.

`.heyeddi/stack.json` says where it lives (`backlog.provider`):

  local  the table in `.heyeddi/docs/product/backlog.md` (default)
  mcp    a task or project manager reached through an MCP server. This script
         cannot call MCP, so it prints the operation for the agent to run.

`done` needs `--docs` (the documents updated with the item) or `--docs-none`.
`docs.provider` says where documents live: `repo` (default), `mcp`, or `external`.
See reference/backlog.md.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _heyeddi_paths import product_docs_dir
from _skill_cli import emit, fail, resolve_project_root

CLOSED = {"done", "shipped", "complete", "completed", "merged"}
BLOCKED = "blocked"
COLUMNS = ("priority", "feature", "story", "status", "notes")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in CELL_SPLIT.split(line.strip().strip("|"))]


def parse_backlog(text: str) -> list[dict]:
    rows: list[dict] = []
    header: list[str] | None = None
    for number, line in enumerate(text.splitlines()):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if header is None:
            names = [cell.lower().split(" ")[0] for cell in cells]
            if "status" in names and "feature" in names:
                header = ["story" if name == "user" else name for name in names]
            continue
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        row = {name: "" for name in COLUMNS}
        row.update({name: cell.replace("\\|", "|") for name, cell in zip(header, cells)})
        row["line"] = number
        row["header"] = header
        rows.append(row)
    return rows


def _is_stub(row: dict) -> bool:
    return not row["feature"] or "(agent fills)" in row["feature"]


def _public(row: dict) -> dict:
    return {name: row[name] for name in COLUMNS}


def _priority(row: dict) -> tuple[int, int]:
    match = re.search(r"\d+", row["priority"])
    return (int(match.group()) if match else 99, row["line"])


def next_item(rows: list[dict]) -> dict:
    real = [row for row in rows if not _is_stub(row)]
    if not real:
        return {
            "status": "unfilled",
            "item": None,
            "action": "Fill backlog.md from product.md and the feature specs, then run next again.",
        }
    blocked = [row for row in real if row["status"].lower() == BLOCKED]
    todo = sorted(
        (row for row in real if row["status"].lower() not in CLOSED | {BLOCKED}),
        key=_priority,
    )
    result = {
        "status": "item" if todo else "none",
        "item": _public(todo[0]) if todo else None,
        "remaining": len(todo),
        "blocked": [_public(row) for row in blocked],
    }
    if todo:
        result["action"] = (
            "Build this item on its own branch, open the PR, pass @pre-merge-gate --signoff, "
            "merge below production, run `backlog.py done`, then run `backlog.py next` again."
        )
    return result


def set_status(path: Path, feature: str, status: str, note: str | None) -> dict:
    text = path.read_text(encoding="utf-8")
    rows = parse_backlog(text)
    wanted = feature.strip().strip("`")
    matches = [row for row in rows if row["feature"].strip("`") == wanted]
    if not matches:
        known = ", ".join(row["feature"] for row in rows if not _is_stub(row)) or "none"
        fail(f"no backlog item {feature!r}. Items: {known}")
    open_rows = [row for row in matches if row["status"].lower() not in CLOSED]
    row = (open_rows or matches)[0]
    row["status"] = status
    if note:
        row["notes"] = note
    lines = text.splitlines(keepends=True)
    cells = [row.get(name, "").replace("|", "\\|") for name in row["header"]]
    ending = "\n" if lines[row["line"]].endswith("\n") else ""
    lines[row["line"]] = "| " + " | ".join(cells) + " |" + ending
    path.write_text("".join(lines), encoding="utf-8")
    return {"status": "ok", "item": _public(row)}


def _main_checkout(root: Path) -> Path | None:
    """The main checkout of a linked worktree. Ignored files live only there."""
    marker = root / ".git"
    if not marker.is_file():
        return None
    gitdir = (root / marker.read_text(encoding="utf-8").removeprefix("gitdir:").strip()).resolve()
    return gitdir.parents[2] if gitdir.parent.name == "worktrees" else None


def _find(root: Path, relative: Path) -> Path:
    here = root / relative
    main = _main_checkout(root)
    if here.exists() or main is None or not (main / relative).exists():
        return here
    return main / relative


def _choices(root: Path, key: str, default: str) -> dict:
    """The `key` block of stack.json, with its provider filled in."""
    path = _find(root, Path(".heyeddi") / "stack.json")
    try:
        block = json.loads(path.read_text(encoding="utf-8")).get(key)
    except (OSError, json.JSONDecodeError, AttributeError):
        block = None
    block = block if isinstance(block, dict) else {}
    return {**block, "provider": block.get("provider") or default}


def add_item(path: Path, feature: str, priority: str, story: str) -> dict:
    text = path.read_text(encoding="utf-8")
    rows = parse_backlog(text)
    if any(row["feature"].strip("`") == feature.strip("`") and row["status"].lower() not in CLOSED for row in rows):
        fail(f"{feature!r} is already open in the backlog")
    lines = text.splitlines(keepends=True)
    if rows:
        after, header = rows[-1]["line"], rows[-1]["header"]
    else:
        header = list(COLUMNS)
        after = next((i for i, line in enumerate(lines) if set(line.strip()) <= set("|-: ") and "-" in line), None)
        if after is None:
            fail("backlog.md has no table: run init_product_docs.py")
    row = {"priority": priority, "feature": feature, "story": story, "status": "planned", "notes": ""}
    cells = [row.get(name, "").replace("|", "\\|") for name in header]
    if not lines[after].endswith("\n"):
        lines[after] += "\n"
    lines.insert(after + 1, "| " + " | ".join(cells) + " |\n")
    path.write_text("".join(lines), encoding="utf-8")
    return {"status": "ok", "item": row}


def _doc_note(root: Path, docs: list[str] | None, none_reason: str | None) -> str:
    if none_reason:
        return f"docs unchanged: {none_reason}"
    if not docs:
        fail("done needs --docs <files updated> or --docs-none <reason>: documents are part of the item")
    # Documents kept outside the repo, and links, cannot be checked from here.
    in_repo = _choices(root, "docs", "repo")["provider"] == "repo"
    missing = [
        doc for doc in docs
        if in_repo and "://" not in doc and not (root / doc).exists() and not _find(root, Path(doc)).exists()
    ]
    if missing:
        fail(f"no such document: {', '.join(missing)}")
    return "docs: " + ", ".join(docs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Next doable backlog item, or maintain one")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--local", action="store_true", help="Use backlog.md when the MCP server is unavailable")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("next", help="Highest-priority item that is not done or blocked")
    done = commands.add_parser("done", help="Mark an item done")
    done.add_argument("feature")
    done.add_argument("--note", default=None, help="PR or commit link")
    done.add_argument("--docs", nargs="+", default=None, help="Documents updated with this item")
    done.add_argument("--docs-none", default=None, help="Why no document changed")
    add = commands.add_parser("add", help="Record new work")
    add.add_argument("feature")
    add.add_argument("--priority", default="P2")
    add.add_argument("--story", default="")
    block = commands.add_parser("block", help="Mark an item blocked (autonomy.md: The only pauses)")
    block.add_argument("feature")
    block.add_argument("--reason", required=True, help="Exact error or missing access")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    note = None
    if args.command == "done":
        docs = _doc_note(root, args.docs, args.docs_none)
        note = f"{args.note}; {docs}" if args.note else docs

    config = _choices(root, "backlog", "local")
    if config["provider"] == "mcp" and not args.local:
        mcp = config.get("mcp") or {}
        fields = {k: v for k, v in vars(args).items() if k in {"feature", "priority", "story", "reason"}}
        if note:
            fields["notes"] = note
        emit(
            {
                "status": "external",
                "operation": args.command,
                "server": mcp.get("server", ""),
                "project": mcp.get("project", ""),
                "fields": fields,
                "action": "Run this operation with the MCP server's tools (reference/backlog.md). "
                "If the server is unavailable, rerun with --local and sync it later.",
            }
        )
        return

    path = _find(root, product_docs_dir(root).relative_to(root) / "backlog.md")
    if not path.is_file():
        if args.command == "next":
            emit({"status": "no_backlog", "item": None, "path": str(path)})
            return
        fail(f"missing {path}: run init_product_docs.py")

    if args.command == "next":
        emit(next_item(parse_backlog(path.read_text(encoding="utf-8"))))
    elif args.command == "add":
        emit(add_item(path, args.feature, args.priority, args.story))
    elif args.command == "done":
        emit(set_status(path, args.feature, "done", note))
    else:
        emit(set_status(path, args.feature, BLOCKED, args.reason))


if __name__ == "__main__":
    main()
