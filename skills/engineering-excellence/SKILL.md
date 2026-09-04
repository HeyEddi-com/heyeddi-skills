---
name: engineering-excellence
description: "ALWAYS-ON: audits plans and code for KISS, YAGNI, DRY, SOLID, and testability; maintains .heyeddi/docs/engineering/. Use on every chat that plans or changes code, before merge, refactor, ADRs, or reuse-catalog work. Not for visual UX (ux-flow-auditor) or full CI (pre-merge-gate includes this audit)."
version: 1.1.0
product-version: 3.4.7
author: HeyEddi-com
---

# Engineering Excellence

Simple solutions that scale: documented so the next agent does not over-build or repeat work.

**Always on** for every chat that plans or changes code. See `reference/engineering-always-on.md` and hub `docs/always-on-skills.md`.

**All artifacts go under `.heyeddi/docs/`**: never repo root.

## When to use

- **Every chat** that proposes an implementation plan or edits code
- After a feature ships: capture how it works
- Before adding abstractions: check reuse catalog
- Refactor / architecture review: KISS, YAGNI, SOLID
- User asks: "don't over-engineer", "document the system", "engineering notes"

## Subagents (default)

See `reference/subagents.md`. Delegate `audit_engineering.py`, `check_engineering_plan.py`, and doc init to **Task `shell`**. Main chat interprets findings and updates living docs.

## Pipeline

```
check_engineering_plan  → plan gate (docs + optional plan smells)
init_engineering_docs   → .heyeddi/docs/engineering/{architecture,reuse-catalog,decisions}.md
implement / refactor
audit_engineering       → .heyeddi/docs/engineering-audit-<date>.md (--check = errors fail)
append_decision         → ADR when trade-off is non-obvious
```

## Instructions

1. **Plan gate (every chat before coding):** `python scripts/check_engineering_plan.py --project-root <root> --check` (add `--plan-file` when a written plan exists).
2. **First time in project:** `python scripts/init_engineering_docs.py --project-root <root>`
3. **While coding:** read `reuse-catalog.md` before new components/composables/services
4. **After meaningful change:** update `architecture.md` module map and add reuse rows
5. **Non-obvious trade-off:** `append_decision.py --title … --context … --decision …`
6. **Change gate (every chat after edits):** `audit_engineering.py --check` (errors fail; warns advisory). Use `--strict` only when the user asks for warn-blocking.

## Principles (how we enforce)

| Principle | Skill behavior |
|-----------|----------------|
| **KISS** | Warn on oversized files; **error** when extreme; prefer flat modules |
| **YAGNI** | Flag abstraction names without clear reuse; plan gate errors on new Factory/Manager without reuse cite |
| **DRY** | Maintain `reuse-catalog.md`; chain `@no-duplicate-ui` for UI |
| **SOLID** | Warn on fat routers; views thin, services fat |
| **Testable** | Note views missing smoke specs |

## `.heyeddi/` outputs

| Path | Purpose |
|------|---------|
| `.heyeddi/docs/engineering/architecture.md` | System map, data flow, boundaries |
| `.heyeddi/docs/engineering/reuse-catalog.md` | What exists: do not rebuild |
| `.heyeddi/docs/engineering/decisions.md` | Engineering ADRs (not design log) |
| `.heyeddi/docs/engineering-audit-<date>.md` | Point-in-time audit report |

Design decisions stay in `.heyeddi/design.md` Decision log: do not mix.

## Chain

- `@heyeddi-orchestrator`: always-on router before this skill when the task is ambiguous
- `@project-engineering`: scaffold first
- `@composable-patterns` / `@backend-type-bridger`: after architecture notes exist
- `@pre-merge-gate`: final CI; includes `audit_engineering --check`

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill (not after every tool call or subagent phase), suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py --current-skill engineering-excellence --project-root .
   ```

   Add `--route /path` if you worked a specific route.

2. Include the script's **`### Next step`** block in your **final** reply. The user copies the **Prompt** line into chat (e.g. `@visual-auditor review and fix /settings`).

Pass `--mode audit` when the change-gate audit just finished.

See `@heyeddi-orchestrator` → `reference/next-skill-handoff.md`.
