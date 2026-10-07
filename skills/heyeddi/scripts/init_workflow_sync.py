#!/usr/bin/env python3
"""Scaffold `.heyeddi/docs/workflow/` for product + UX + design cross-pillar sync."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from _skill_cli import emit, resolve_project_root
from _workflow_paths import (
    PILLARS,
    active_context_path,
    opinions_dir,
    opinion_path,
    readme_path,
    sync_log_path,
    workflow_dir,
)

README = """# Workflow sync: product · UX · design

**Date:** {today}

Three pillars share one route/feature. **Whenever one pillar runs, all three maintain opinions and docs.**

| Pillar | Skill | Primary docs |
|--------|-------|----------------|
| **Product** | `@heyeddi-product` | `.heyeddi/docs/product/`, `product.md` |
| **UX** | `@ux-flow-auditor` | `.heyeddi/docs/ux-flows/` |
| **Design** | `@heyeddi-design` | `.heyeddi/design.md`, `.heyeddi/designs/` |

## Tools (`@heyeddi`)

```
init_workflow_sync
load_workflow_context --route /path
append_pillar_opinion --pillar product|ux|design --route /path --opinion "…"
```

## Rules

1. **Start** any pillar workflow with `load_workflow_context`.
2. **End** with `append_pillar_opinion`: cite docs you updated.
3. **Siblings** must respond: product run → UX + design opinions; UX run → product AC + design layout; design run → product scope + UX flow notes.
4. Read `opinions/*.md` before changing a route another pillar touched recently.

See hub `docs/cross-pillar-workflow.md` and `reference/cross-pillar-workflow.md` in `@heyeddi`.
"""

OPINION_HEADER = """# {pillar} opinions

Append-only log. Each entry: route, opinion, docs updated, sibling requests.

"""


def scaffold_workflow(root: Path, *, force: bool = False) -> dict:
    """Create the cross-pillar workflow docs under `.heyeddi/docs/workflow/`.

    Importable so callers (e.g. `sync.py`) run it in-process: no child
    process is spawned.
    """
    out = workflow_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    opinions_dir(root).mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    today = date.today().isoformat()

    readme = readme_path(root)
    if not readme.is_file() or force:
        readme.write_text(README.format(today=today), encoding="utf-8")
        created.append(str(readme.relative_to(root)))

    for pillar in PILLARS:
        path = opinion_path(root, pillar)
        if not path.is_file() or force:
            path.write_text(OPINION_HEADER.format(pillar=pillar.title()), encoding="utf-8")
            created.append(str(path.relative_to(root)))

    log = sync_log_path(root)
    if not log.is_file() or force:
        log.write_text(f"# Workflow sync log\n\n**Started:** {today}\n\n", encoding="utf-8")
        created.append(str(log.relative_to(root)))

    ctx = active_context_path(root)
    if not ctx.is_file() or force:
        ctx.write_text(
            json.dumps({"route": None, "feature": None, "last_pillar": None, "updated": today}, indent=2) + "\n",
            encoding="utf-8",
        )
        created.append(str(ctx.relative_to(root)))

    return {"status": "ok", "created": created, "workflow_dir": str(out.relative_to(root))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Init cross-pillar workflow docs")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    emit(scaffold_workflow(root, force=args.force))


if __name__ == "__main__":
    main()
