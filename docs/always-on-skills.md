# Always-on skills (every chat)

**Date:** 2026-09-04

These guards run on **every chat** that plans or changes work. They are not optional suggestions.

## Always-on trio

| Guard | Role | Fail rule |
|-------|------|-----------|
| **`@heyeddi-orchestrator`** | Session start + ambiguous tasks: sync `.heyeddi/`, rank skills, route. Do not freestyle the pipeline. | Soft: must load catalog / follow routing before multi-step work |
| **`@engineering-excellence`** | **Plan gate** before coding; **change gate** after edits (`audit_engineering --check`). | **Errors fail**; warns stay advisory |
| **Prose anti-slop** | Any user-facing or `.heyeddi` prose: `verify_prose --check` / `context/PROSE_ANTI_SLOP.md` | Fail on em/en dashes and high-signal filler |

Plus **clarify-before-act** ([clarify-before-act.md](clarify-before-act.md)): ask when product/design/stack intent is missing. Never guess.

## Trigger matrix (not every chat)

| Skill | When |
|-------|------|
| `@heyeddi-intake` | Greenfield / thin `product.md` |
| `@heyeddi-product` | Specs, backlog, usefulness review |
| `@heyeddi-design` | UI / design work (foundations always-on inside design) |
| `@visual-auditor` | After UI changes |
| `@ux-flow-auditor` | Task flows / friction |
| `@pre-merge-gate` | Before merge or ship claim (includes engineering + prose audits) |
| PR / CI skills | Review or respond loops only |

Scaffolders, bridgers, and stack implementers run when the stack/task needs them.

## Agent checklist (every chat)

1. **Orchestrator** — if session start or task is ambiguous: `load_catalog` / `suggest_skills` (or read skills-index); follow `skill-routing.json` when present.
2. **Plan gate** — before implementing: `check_engineering_plan --check` (docs ready + plan smells); read `reuse-catalog.md`.
3. **Work** — follow the routed `@skill`.
4. **Change gate** — after code changes: `audit_engineering --check` (errors only).
5. **Prose** — if copy or `.heyeddi` docs changed: `verify_prose --check`.
6. **Ship** — `@pre-merge-gate` before merge-ready claims.

## Related

- `@engineering-excellence` → `reference/engineering-always-on.md`
- `@heyeddi-orchestrator` → `reference/always-on.md`
- `@pre-merge-gate` runs `audit_engineering --check` and `verify_prose --check` by default
