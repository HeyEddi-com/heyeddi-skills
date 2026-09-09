# Always-on skills (every chat)

**Date:** 2026-09-08

These guards run on **every chat** that plans or changes work. They are not optional suggestions.

## Always-on guards

| Guard | Role | Fail rule |
|-------|------|-----------|
| **`@heyeddi-orchestrator`** | Session start + ambiguous tasks: sync `.heyeddi/`, rank skills, route. Do not freestyle the pipeline. | Soft: must load catalog / follow routing before multi-step work |
| **`@heyeddi-setup`** | **Prefs gate** before git/CI/commit/push or agent autonomy assumptions (`verify_setup --check`). | **Incomplete prefs fail** those actions; run setup until check passes |
| **`@engineering-excellence`** | **Plan gate** before coding; **change gate** after edits (`audit_engineering --check`). | **Errors fail**; warns stay advisory |
| **Prose anti-slop** | Any user-facing or `.heyeddi` prose: `verify_prose --check` / `context/PROSE_ANTI_SLOP.md` | Fail on em/en dashes and high-signal filler |

Plus **clarify-before-act** ([clarify-before-act.md](clarify-before-act.md)): ask when product/design/stack intent is missing. Never guess.

Plus **host surfaces** (`@heyeddi-orchestrator` → `reference/host-surfaces.md`): prefer this session's native plan / data / visual tools when listed; never require IDE-only surfaces on CLI or Cloud Run.

Non-git work may continue when prefs are incomplete. Never invent branch names, PR bases, or auto-commit/push until `verify_setup --check` passes.

## Trigger matrix (not every chat)

| Skill | When |
|-------|------|
| `@heyeddi-setup` | Incomplete `stack.json` prefs (hard for git/agent), or user asks for setup / preferences |
| `@heyeddi-intake` | Greenfield / thin `product.md` |
| `@heyeddi-product` | Specs, backlog, usefulness review |
| `@heyeddi-design` | UI / design work (foundations always-on inside design) |
| `@visual-auditor` | After UI changes |
| `@ux-flow-auditor` | Task flows / friction |
| `@pre-merge-gate` | Before merge or ship claim (includes setup + engineering + prose audits) |
| PR / CI skills | Review or respond loops only |

Scaffolders, bridgers, and stack implementers run when the stack/task needs them.

## Agent checklist (every chat)

1. **Orchestrator** — if session start or task is ambiguous: `load_catalog` / `suggest_skills` (or read skills-index); follow `skill-routing.json` when present.
2. **Setup (hard)** — before git/CI/agent assumptions: `verify_setup --check`. On fail: `@heyeddi-setup` until pass. Honor existing keys when complete.
3. **Plan gate** — before implementing: `check_engineering_plan --check` (docs ready + plan smells); read `reuse-catalog.md`.
4. **Work** — follow the routed `@skill`.
5. **Change gate** — after code changes: `audit_engineering --check` (errors only).
6. **Prose** — if copy or `.heyeddi` docs changed: `verify_prose --check`.
7. **Ship** — `@pre-merge-gate` before merge-ready claims.

## Related

- `@heyeddi-setup` → `reference/setup-always-on.md`
- `@engineering-excellence` → `reference/engineering-always-on.md`
- `@heyeddi-orchestrator` → `reference/always-on.md` · `reference/host-surfaces.md`
- `@pre-merge-gate` runs `verify_setup --check`, `audit_engineering --check`, and `verify_prose --check` by default
