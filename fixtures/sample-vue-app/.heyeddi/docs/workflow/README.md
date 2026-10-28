# Workflow sync — product · UX · design

**Date:** 2026-07-07

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
2. **End** with `append_pillar_opinion` — cite docs you updated.
3. **Siblings** must respond: product run → UX + design opinions; UX run → product AC + design layout; design run → product scope + UX flow notes.
4. Read `opinions/*.md` before changing a route another pillar touched recently.

See hub `docs/cross-pillar-workflow.md` and `reference/cross-pillar-workflow.md` in `@heyeddi`.
