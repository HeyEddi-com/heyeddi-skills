#!/usr/bin/env python3
"""Scaffold and check operating documents under `.heyeddi/docs/ops/`."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from _skill_cli import emit, fail, resolve_project_root

SECTIONS = ("Setup", "Verify", "Failure", "Rotation", "Rollback", "Teardown")
LESSON_FIELDS = ("Symptom", "Cause", "Fix", "Lesson")
THREAT = """# Threat model

## Assets

TODO

## Threats and controls

TODO

## Accepted risks

| Risk | Reason |
| --- | --- |
"""
LESSONS = "# Incident lessons\n\n## TODO date and title\n\n" + "".join(f"**{f}:** TODO\n\n" for f in LESSON_FIELDS)


def _ops_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs" / "ops"


def init(root: Path, service: str) -> list[Path]:
    """Create the documents that are missing; return them."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", service):
        raise ValueError(f"service must be a plain name, got {service!r}")
    ops = _ops_dir(root)
    runbook = f"# Runbook: {service}\n\n" + "".join(f"## {s}\n\nTODO\n\n" for s in SECTIONS)
    created = []
    for path, text in (
        (ops / "threat-model.md", THREAT),
        (ops / "runbooks" / f"{service}.md", runbook),
        (ops / "lessons.md", LESSONS),
    ):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            created.append(path)
    return created


def _sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.MULTILINE)
    return {name: body.strip() for name, body in zip(parts[1::2], parts[2::2])}


def check(root: Path) -> list[str]:
    """Return one line per missing or empty required part."""
    ops = _ops_dir(root)
    documents = sorted(ops.rglob("*.md"))
    if not documents:
        return ["No operating documents: run --init --service <name>"]
    problems = []
    for path in documents:
        text = path.read_text(encoding="utf-8", errors="replace")
        name = path.relative_to(ops).as_posix()
        if "TODO" in text:
            problems.append(f"{name}: unfilled TODO")
        if path.parent.name == "runbooks":
            sections = _sections(text)
            problems += [f"{name}: section {s} is missing or empty" for s in SECTIONS if not sections.get(s)]
        elif name == "threat-model.md":
            for line in _sections(text).get("Accepted risks", "").splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if line.startswith("|") and cells[0] not in ("Risk", "---") and not (len(cells) > 1 and cells[1]):
                    problems.append(f"{name}: accepted risk without a reason: {cells[0]}")
        elif name == "lessons.md":
            for title, body in _sections(text).items():
                problems += [f"{name}: {title}: no {f}" for f in LESSON_FIELDS if f"**{f}:**" not in body]
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="HeyEddi operating documents")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--init", action="store_true", help="Create missing documents")
    parser.add_argument("--service", default="app", help="Runbook name for --init")
    parser.add_argument("--check", action="store_true", help="Exit 1 while a required part is empty")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    created = []
    if args.init:
        try:
            created = [str(p.relative_to(root)) for p in init(root, args.service)]
        except ValueError as error:
            fail(str(error))
    problems = check(root)
    emit({"ok": not problems, "created": created, "problems": problems})
    if args.check and problems:
        fail(f"{len(problems)} operating document problem(s)")


if __name__ == "__main__":
    main()
