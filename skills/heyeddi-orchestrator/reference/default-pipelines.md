# Default pipelines (top-tier bar)

**Date:** 2026-09-01

Agents should run these chains **automatically** — do not ask the user for confirmation at each step.

## UI: greenfield route

```
@heyeddi-intake          → product.md + skill-routing
@heyeddi-design shape    → confirmed brief.md
<stack implementer>      → @heyeddi-handoff (vue) or @design-handoff-flutter
@primevue-openprops-architect   (vue)
@visual-auditor          → fix, not report-only
@ux-flow-auditor         → flagship routes
@pre-merge-gate
```

## UI: improve existing screen

```
@heyeddi-design critique → report + auto-chain
<stack implementer>      → P0/P1 from critique
@visual-auditor
```

## PR: address review

```
@heyeddi-ci-fails        → always first
@heyeddi-pr-respond      → fix, commit, push, every thread
@pre-merge-gate
```

## Design vs implement

| Question | Skill |
|----------|-------|
| What should it look/feel like? | `@heyeddi-design` |
| Write Vue/Flutter code? | `@heyeddi-handoff` / `@design-handoff-flutter` |
| Screenshot mockup? | `@heyeddi-handoff` |
| Pixels wrong? | `@visual-auditor` (fixes code) |

See `@heyeddi-design` → `reference/implement-routing.md`.

## Never ask (user preference)

- Fix PR review comments?
- Post threaded replies?
- Check CI failures?
- Fix visual issues found in audit?
- Implement after confirmed brief?

Default answer to all: **yes, do it now**.

Only **merge** needs **authorize merge** in the current turn.
