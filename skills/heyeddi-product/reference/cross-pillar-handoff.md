# Cross-pillar workflow

**Date:** 2026-07-07

Product, UX, and design are **one loop**. See:

- Hub: `docs/cross-pillar-workflow.md`
- Skill: `@heyeddi` → `reference/cross-pillar-workflow.md`

## Every session

1. `init_workflow_sync` (once)
2. `load_workflow_context --route <route>`
3. Do pillar work: **update your primary docs** (not opinions alone)
4. `append_pillar_opinion --pillar <you> --route <route> --opinion "…" --docs-updated "…"`
5. **Invoke siblings**: each appends their opinion or runs their tool (trace, critique)

Do not mark a route complete until `opinions/product.md`, `opinions/ux.md`, and `opinions/design.md` have entries for that route in the current cycle (or documented N/A with reason in product opinion).
