# HeyEddi

**HeyEddi** is a **collaborative workspace for agents and humans**. Product context, design artifacts, and skill-generated reports live in `.heyeddi/` so AI agents and your team share one source of truth while building SaaS applications: Vue or Flutter frontends, FastAPI or Firebase backends, OpenProps + PrimeVue on web.

This folder is that workspace **inside your repository**. Skills read and write here; humans review, decide, and merge like any other contributor.

## Skills (free to use)

Our [Cursor Agent Skills](https://github.com/HeyEddi-com/heyeddi-skills) are **free and open**. Install the full set into any project:

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --all
```

Invoke with `@skill-name` in Cursor (e.g. `@heyeddi-intake`, `@heyeddi-handoff`) or wire the same skills into a Cloud Run agent. They automate intake, design, engineering scaffold, handoff, API types, QA gates, and PR workflows.

**You own your code.** Skills suggest and generate; you review and merge.

## Need humans?

Agents handle repeatable workflow; some work still needs people. **[heyeddi.com/humans](https://heyeddi.com/humans)**: hire vetted designers, engineers, and product folks to complement your agents.

## How we use this folder

| Path | Purpose |
|------|---------|
| `stack.json` | Declared stacks: Vue, FastAPI, Firebase |
| `product.md` | Product brief: users, routes, acceptance criteria |
| `design.md` | DESIGN.md format: tokens, rationale, Decision log |
| `designs/<feature>/` | Per-feature artifacts: handoff PNGs, briefs, wireframes, research |
| `docs/` | Skill-generated reports (ship checklist, PR tracking, drift audits, gate output) |
| `docs/engineering/` | Architecture, reuse catalog, engineering ADRs (`@engineering-excellence`) |
| `docs/ux-flows/` | Task flow traces: click depth, friction (`@ux-flow-auditor`) |
| `audits/` | Visual audit summaries, pre-merge snapshots, UX flow screenshots (optional) |

**Convention:** When a skill creates documentation, save it under `.heyeddi/docs/` or the relevant subfolder above: not scattered at repo root. Root `PRODUCT.md` / `DESIGN.md` / `designs/` are legacy fallbacks; prefer this folder for new work.

## Typical flow

1. `@project-engineering`: audit scaffold, install deps, declare `stack.json`
2. `@heyeddi-design` or `@heyeddi-handoff`: product + design docs, then UI
3. `@backend-type-bridger` + `@composable-patterns`: API types and composables
4. `@verify-build` + `@visual-auditor` + `@pre-merge-gate`: ship checklist
5. `@engineering-excellence`: architecture notes under `docs/engineering/`
6. `@ux-flow-auditor`: task flows under `docs/ux-flows/`

See [HeyEddi skills hub](https://github.com/HeyEddi-com/heyeddi-skills) for the full cheat sheet.

---
*Last updated: 2026-07-04: maintained by project-engineering scaffold*
