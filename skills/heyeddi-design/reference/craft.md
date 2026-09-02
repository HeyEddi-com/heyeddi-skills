# Craft: hand off to stack implementer

**Scope:** Brief is confirmed — route **implementation** to the project's frontend stack. This skill does **not** write Vue/Flutter/CSS in component files.

Read **`reference/implement-routing.md`** first.

## Prerequisites (hard gates)

1. **Confirmed design brief** at `designs/<feature>/brief.md` OR explicit brief confirmation from `shape`.
2. **`design.md` exists** — run `document` if missing.
3. Run `load_context.py`: read `product.md` + `design.md`. Stop on `audience_blocker`.
4. Brief **Audience** + **Design signature** sections filled.

If no brief, **stop and run `shape`**.

## Steps (design skill)

0. Read `reference/audience-design.md`, `design-ambition.md`, `aesthetic-direction.md`, `surface-completeness.md`, `modern-reference.md`.
1. Ensure brief maps regions → component **intent** (not PrimeVue prop lists — implementer maps to catalog).
2. Append **Decision log** in `design.md`: persona + pattern borrowed + memorable detail.
3. **Hand off** to stack implementer per `implement-routing.md`:

| Stack | Invoke |
|-------|--------|
| Vue | `@heyeddi-handoff implement <route> from .heyeddi/designs/<feature>/` |
| Flutter | `@design-handoff-flutter implement <route> from .heyeddi/designs/<feature>/` |
| No scaffold | `@project-engineering` or `@flutter-engineering` scaffold → then handoff |

4. **Do not** write `*View.vue` or `.dart` files in this turn.

## Implementer completes (not design)

The stack skill:

- Builds shell + route from brief/mockups
- Runs `@primevue-openprops-architect` (Vue)
- Runs full `@visual-auditor` fix loop
- Runs `reference/audience-fit.md` on flagship routes

## After handoff

Summarize: route, feature slug, which implementer was chained, and open questions deferred.

Recommend `@ux-flow-auditor` on flagship routes after visual-auditor passes.
