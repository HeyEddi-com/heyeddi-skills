#!/usr/bin/env python3
"""Append a typed entry (decision, trade-off, gotcha, how-it-works) to `.heyeddi/docs/engineering/decisions.md`."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from _heyeddi_paths import engineering_docs_dir
from _skill_cli import emit, fail, resolve_project_root

INIT_ENGINEERING = "Run init_engineering_docs.py first."
BODY_LABEL = {"decision": "Decision", "trade-off": "Trade-off", "gotcha": "What bites", "how-it-works": "How it works"}
CONTEXT_INDEX = Path(__file__).resolve().parents[2] / "heyeddi" / "scripts" / "context_index.py"


def _secret_kinds(text: str) -> list[str] | None:
    """Kinds of credential in `text`, or None when @heyeddi (which holds the patterns) is not installed."""
    if not CONTEXT_INDEX.is_file():
        return None
    sys.path.append(str(CONTEXT_INDEX.parent))
    from context_index import find_secrets  # noqa: PLC0415

    return sorted({kind for _, kind in find_secrets(text)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Append engineering decision")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--type", default="decision", choices=sorted(BODY_LABEL))
    parser.add_argument("--title", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--consequences", default="")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    decisions = engineering_docs_dir(root) / "decisions.md"
    if not decisions.is_file():
        fail(INIT_ENGINEERING)

    today = date.today().isoformat()
    block = f"""
### {today}: {" ".join(args.title.split())}

**Type:** {args.type}

**Context:** {args.context}

**{BODY_LABEL[args.type]}:** {args.decision}

**Consequences:** {args.consequences or "Document follow-ups in next audit."}
"""
    kinds = _secret_kinds(block)
    if kinds:
        fail(f"Entry holds a {', '.join(kinds)}. These docs are committed: name the secret, never its value.")
    text = decisions.read_text(encoding="utf-8")
    decisions.write_text(text.rstrip() + "\n" + block + "\n", encoding="utf-8")
    emit(
        {
            "ok": True,
            "path": str(decisions.relative_to(root)),
            "title": args.title,
            "type": args.type,
            "secret_check": "passed" if kinds is not None else "skipped: @heyeddi not installed",
        }
    )


if __name__ == "__main__":
    main()
