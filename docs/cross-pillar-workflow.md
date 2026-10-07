# Cross-pillar workflow (hub)

**Date:** 2026-07-07

Canonical spec: `skills/heyeddi/reference/cross-pillar-workflow.md`

Product (`@heyeddi-product`), UX (`@ux-flow-auditor`), and design (`@heyeddi-design`) share `.heyeddi/docs/workflow/`. Whenever one pillar runs on a route, siblings **opine and maintain their docs** before the route is done.

Tools live on `@heyeddi`: `init_workflow_sync`, `load_workflow_context`, `append_pillar_opinion`.
