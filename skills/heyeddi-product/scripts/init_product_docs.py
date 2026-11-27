#!/usr/bin/env python3
"""Scaffold `.heyeddi/docs/product/`: backlog, feature specs, review index."""
from __future__ import annotations

import argparse
from datetime import date

from _heyeddi_paths import features_dir, product_docs_dir
from _skill_cli import emit, resolve_project_root

TODAY = date.today().isoformat()

BACKLOG = """# Product backlog

**Last updated:** {today}

Prioritized by user value. PM owns order: engineering estimates inform but do not override user pain.
Status is `planned`, `done`, or `blocked`. A build run repeats `backlog.py next` until no item is left.

| Priority | Feature / route | User story (summary) | Status | Notes |
|----------|-----------------|--------------------|--------|-------|
| P0 | *(agent fills)* | | planned | |

## Out of scope (v1)

- *(what we are explicitly not building yet)*
"""

FEATURES_README = """# Feature specs

Per-route **user stories** and **acceptance criteria**: testable Definition of Done.

Create with `write_feature_spec.py` or author `features/<slug>.md` manually.

Template sections:
- Problem / user job
- User stories (`As a… I want… so that…`)
- Acceptance criteria (measurable)
- Success metric
- Open questions
"""

REVIEWS_INDEX = """# Product reviews

**Last updated:** {today}

Holistic PM reviews: usefulness, gaps, delegated findings, recommended changes.

| Date | Type | Report |
|------|------|--------|
| | | |
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Init product docs under .heyeddi/docs/product/")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    out = product_docs_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    features_dir(root).mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    for name, body in (
        ("backlog.md", BACKLOG.format(today=TODAY)),
        ("features/README.md", FEATURES_README),
        ("reviews.md", REVIEWS_INDEX.format(today=TODAY)),
    ):
        path = out / name if name != "features/README.md" else features_dir(root) / "README.md"
        if path.is_file() and not args.force:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        created.append(str(path.relative_to(root)))

    emit({"status": "ok", "created": created, "product_docs": str(out.relative_to(root))})


if __name__ == "__main__":
    main()
