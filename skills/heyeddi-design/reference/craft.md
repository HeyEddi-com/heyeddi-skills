# Craft: build screen in Vue

**Scope:** Production implementation from a confirmed brief and `DESIGN.md`.

## Prerequisites (hard gates)

1. **Confirmed design brief** at `designs/<feature>/brief.md` OR explicit user confirmation of brief in chat from a completed `shape` run.
2. **`DESIGN.md` exists**: if not, run `document` first (or init → document).
3. Run `load_context.py`: read PRODUCT.md + DESIGN.md. If `audience_blocker` is set, **stop**.
4. Brief **Audience** section filled: primary persona cited.

If user invokes craft with only a vague prompt and no brief, **stop and run `shape` first**.

## Implementation steps

0. Read `reference/audience-design.md`: confirm direction for primary persona on this route.
0a. Read `reference/design-ambition.md`: implement **Design signature** from brief; run ambition checklist before done.
0a2. Read `reference/aesthetic-direction.md`: implement thesis/hero, type personality, intentional motion; avoid generic AI look clusters; log the aesthetic risk.
0b. Read `reference/surface-completeness.md`: implement full brief regions, affordances, and states; stub unwired actions; document **Deferred wiring**.
0c. Read `reference/modern-reference.md`: apply typography, surfaces, and layout character (not default PrimeVue admin).
1. Map brief regions → PrimeVue components per component map in brief.
2. Use project semantic tokens: detect OpenProps vs custom per `token-strategy.md`; no raw hex unless DESIGN.md documents exceptions.
3. Implement Vue SFCs following project structure (`src/views/`, `src/components/`).
4. Cover key states from brief: default, empty, loading, error where in scope.
5. Run `@primevue-openprops-architect` validation (`validate_vue` if available).
6. Run full **`@visual-auditor`** loop on the route: `load_visual_context --write-review` → capture → contrast → **fix issues** → `append_fix_log` → `finalize_visual_review --check`.
7. Compare against wireframes in `designs/<feature>/wireframes/` if present.
8. **Append** to **Decision log** in `.heyeddi/design.md`: persona + pattern borrowed (`reference/design-talk.md`).
9. Run `reference/audience-fit.md` rubric: append to critique doc or chat summary.
10. Run **ambition checklist** in `reference/design-ambition.md`: revise or `polish` if any item fails.
11. Run `python scripts/verify_prose.py --check` (or `.agents/skills/heyeddi-design/scripts/verify_prose.py`): fix em/en dashes and banned filler in Vue/locale copy before calling done.

## Quality

- Production-ready: not prototype stubs unless brief scoped sketch fidelity.
- No lorem ipsum on production paths: use realistic microcopy from brief.
- Mobile-first responsive behavior per wireframes and DESIGN.md layout rules.

## After craft

Summarize what was built, route path, and any brief open questions deferred to follow-up.

Recommend `@heyeddi-design polish` if visual-auditor shows hierarchy or spacing issues.
