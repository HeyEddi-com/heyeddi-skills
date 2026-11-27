# Craft: hand off to stack implementer

**Scope:** Brief is confirmed — route **implementation** to the project's frontend stack. This skill does **not** write Vue/Flutter/CSS in component files.

Read **`reference/implement-routing.md`** first.

## Prerequisites (hard gates)

1. **Design brief** at `designs/<feature>/brief.md`. A design request needs it confirmed in `shape`; in a build request the written brief counts.
2. **`design.md` exists** — run `document` if missing.
3. Run `load_context.py`: read `product.md` + `design.md`. On `audience_blocker`: in a build request, fill personas and per-route intent from the repo, record them as assumptions, and continue; in a design request, run `discover`.
4. Brief **Audience** + **Design signature** sections filled.
5. **Taste layout hard gates A–G** (`@taste-penpot` `references/layout-hard-gates.md`):
   - No text-wall mockups (multiline paste in a gray card ≠ settings/form UI)
   - Penpot design system first (colours/typographies; fonts from Penpot library)
   - Flex claim only when reflow is real (children not stuck at `0,0`); else absolute 8px escape or `hifi.html`
   - `.heyeddi/designs/<feature>/hifi.html` when MCP cannot nest, **or** boards proven on canvas
   - `penpot-demo.md` (if present) labels honestly (Flex / absolute 8px / low-fi)
   - Taste CRITIQUE read the **export PNG** (audit alone does not ship; a blocked export follows the Gate D fallback)
   - Implementation spec CSS comes from `hifi.html` or real Inspect CSS, not from absolute geometry guesses or broken Flex flags

If no brief, run `shape` first. If gate 5 fails, run `@taste-penpot` ACT / CRITIQUE again, fix it, and continue. Do not hand off a text-wall or empty phones. When only the Penpot export is blocked in a build request, use the Gate D fallback and continue to code.

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
- Runs `@vue-design-system` (Vue: Quasar, PrimeVue Aura, motion, tokens)
- Runs full `@visual-auditor` fix loop
- Runs `reference/audience-fit.md` on flagship routes

## After handoff

Summarize: route, feature slug, which implementer was chained, and open questions deferred.

Run `@ux-flow-auditor` on flagship routes after visual-auditor passes, and fix what fails.
