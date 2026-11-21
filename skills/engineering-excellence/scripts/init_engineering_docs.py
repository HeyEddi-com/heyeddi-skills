#!/usr/bin/env python3
"""Scaffold `.heyeddi/docs/engineering/` living architecture notes."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from _heyeddi_paths import engineering_docs_dir, heyeddi_dir
from _skill_cli import emit, fail, resolve_project_root

TODAY = date.today().isoformat()

ARCHITECTURE = """# Architecture

**Last updated:** {today}

How this system works: modules, data flow, and boundaries. Update when structure changes.

## Stack

Read `.heyeddi/stack.json` and summarize here after `@project-engineering` scaffold.

## Module map

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Views / pages | `src/views/` | Route UI only: no business rules |
| Components | `src/components/` | Reusable UI; layout vs feature |
| Composables | `src/composables/` | Client state + API calls |
| Services / API | `src/services/` or `backend/` | Business logic, persistence |
| Router | `src/router/` | Paths only: thin |

## Data flow

1. User action in view
2. Composable or service call
3. API / store
4. Reactive UI update

## Boundaries (SOLID)

- **Single responsibility:** one reason to change per file
- **Open/closed:** extend via composables/wrappers, not forks
- **Dependency direction:** views → composables → services: not the reverse

## What not to build

See `reuse-catalog.md` before adding new abstractions.
"""

REUSE_CATALOG = """# Reuse catalog

**Last updated:** {today}

**DRY rule:** search this file before creating a new component, composable, or helper.

| Name | Path | Use when |
|------|------|----------|
| *(empty: agent fills after audit)* | | |

## Patterns to prefer

- Shared UI: `src/components/ui/` before new PrimeVue wrappers
- API access: one composable per domain (`useUsers`, `useTasks`)
- Layout: `AppShell`, `AppSidebar`, `AppTopBar`: do not duplicate shell markup per route

## Anti-patterns

- Copy-pasting a Card+form block across views → extract wrapper
- Second `api.ts` fetch helper → extend existing composable
"""

DECISIONS = """# Engineering decisions

**Last updated:** {today}

Engineering ADRs: separate from the **Design Decision log** in `.heyeddi/design.md`.

## Template

```markdown
### YYYY-MM-DD: Title

**Context:** …
**Decision:** …
**Consequences:** …
```
"""

BUDGET = """{
  "currency": "USD",
  "change_warn_monthly": 25,
  "change_error_monthly": 200,
  "monthly_limit": null,
  "current_monthly": null,
  "firestore_reads_per_day_limit": 1000000,
  "assumptions": {
    "llm_calls_per_month": 10000,
    "llm_input_tokens": 2000,
    "llm_output_tokens": 500,
    "ci_runs_per_month": 200,
    "ci_minutes_per_run": 5,
    "concurrent_clients": 50,
    "firestore_sessions_per_day": 200,
    "firestore_docs_per_query": 1000,
    "firestore_doc_changes_per_day": 5000,
    "firestore_loop_iterations": 20,
    "firestore_reads_per_day_warn": 100000
  },
  "rates": {}
}
"""

README = """# Engineering docs

Living notes for **KISS, YAGNI, DRY, SOLID**: maintained by `@engineering-excellence`.

| File | Purpose |
|------|---------|
| `architecture.md` | How the system works: modules and data flow |
| `reuse-catalog.md` | What already exists: do not rebuild |
| `decisions.md` | Engineering ADRs |
| `budget.json` | Cost gate limits and usage assumptions (`estimate_change_cost.py`) |

Run `audit_engineering.py --check` before merge on non-trivial changes.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Init .heyeddi/docs/engineering/")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true", help="Overwrite templates if empty")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    heyeddi_dir(root).mkdir(parents=True, exist_ok=True)
    eng = engineering_docs_dir(root)
    eng.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    specs = {
        "README.md": README,
        "architecture.md": ARCHITECTURE.format(today=TODAY),
        "reuse-catalog.md": REUSE_CATALOG.format(today=TODAY),
        "decisions.md": DECISIONS.format(today=TODAY),
    }
    for name, body in specs.items():
        path = eng / name
        if path.is_file() and path.stat().st_size > 200 and not args.force:
            continue
        path.write_text(body, encoding="utf-8")
        created.append(str(path.relative_to(root)))

    budget = eng / "budget.json"
    if not budget.is_file():
        budget.write_text(BUDGET, encoding="utf-8")
        created.append(str(budget.relative_to(root)))

    emit({"ok": True, "created_or_updated": created, "engineering_dir": str(eng.relative_to(root))})


if __name__ == "__main__":
    main()
