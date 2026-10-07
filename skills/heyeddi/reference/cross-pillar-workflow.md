# Cross-pillar workflow (product · UX · design)

**Date:** 2026-07-07

One feature route is owned by **three pillars**. They stay connected through `.heyeddi/docs/workflow/`: not siloed skill runs.

## Pillars

| Pillar | Skill | Maintains |
|--------|-------|-----------|
| Product | `@heyeddi-product` | `docs/product/`, stories, AC, backlog |
| UX | `@ux-flow-auditor` | `docs/ux-flows/`, click budgets, friction |
| Design | `@heyeddi-design` | `design.md`, `designs/`, briefs, Decision log |

`@heyeddi-intake` seeds product.md upstream; `@visual-auditor` supports design legibility: not a fourth pillar, but design runs it.

## Mandatory session bookends (every pillar)

```
@heyeddi  init_workflow_sync          (once per project)
@heyeddi  load_workflow_context --route /path
… pillar work + update primary docs …
@heyeddi  append_pillar_opinion --pillar <product|ux|design> …
→ siblings MUST respond before route is "done"
```

## When pillar X runs, siblings must opine

| You run | You maintain | UX must | Design must | Product must |
|---------|--------------|---------|-------------|--------------|
| **heyeddi-product** | feature specs, backlog | `trace_flow` or friction opinion | `critique` or persona opinion |: |
| **ux-flow-auditor** | flow reports |: | layout/IA note if friction is visual | AC update if flow fails |
| **heyeddi-design** | design.md, briefs | flow note if IA blocks tasks |: | scope/persona note if drift |

**Opinion** = short conclusion for this route, not full re-run. **Full sibling run** when opinion flags P0 or first time on route.

## Artifacts

```
.heyeddi/docs/workflow/
├── README.md
├── active-context.json      # last route + pending pillars
├── sync-log.md
└── opinions/
    ├── product.md
    ├── ux.md
    └── design.md
```

## Anti-patterns

- Running `@heyeddi-design craft` without reading `opinions/product.md` for the route
- Closing UX trace without product AC check when clicks exceed budget
- Product review without design + UX opinions in the same sync cycle
