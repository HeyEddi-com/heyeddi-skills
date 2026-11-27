#!/usr/bin/env python3
"""Drive the backlog loop: `next` names the item to build, `done` and `block` close it.

Reads the table in `.heyeddi/docs/product/backlog.md`. A build run repeats
`next` until it returns no item.
"""
from __future__ import annotations

import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Next doable backlog item, or close one")
    parser.add_argument("--project-root", default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("next", help="Highest-priority item that is not done or blocked")
    done = commands.add_parser("done", help="Mark an item done")
    done.add_argument("feature")
    done.add_argument("--note", default=None, help="PR or commit link")
    block = commands.add_parser("block", help="Mark an item blocked (autonomy.md: The only pauses)")
    block.add_argument("feature")
    block.add_argument("--reason", required=True, help="Exact error or missing access")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    path = product_docs_dir(root) / "backlog.md"
    if not path.is_file():
        if args.command == "next":
            emit({"status": "no_backlog", "item": None, "path": str(path.relative_to(root))})
            return
        fail(f"missing {path.relative_to(root)}: run init_product_docs.py")

    if args.command == "next":
        emit(next_item(parse_backlog(path.read_text(encoding="utf-8"))))
    elif args.command == "done":
        emit(set_status(path, args.feature, "done", args.note))
    else:
        emit(set_status(path, args.feature, BLOCKED, args.reason))


if __name__ == "__main__":
    main()
