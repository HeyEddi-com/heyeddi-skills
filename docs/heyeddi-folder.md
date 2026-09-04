# The `.heyeddi/` folder

**Date:** 2026-07-14

Every HeyEddi client or internal app uses a **`.heyeddi/`** directory at the project root. It is the single place for product context, design artifacts, and documents that skills generate — so nothing important gets lost at repo root.

## What is HeyEddi?

**HeyEddi** is a **collaborative workspace for agents and humans**. The `.heyeddi/` folder in your repo is where product context, design artifacts, and skill-generated docs live so AI agents and your team share one source of truth while building SaaS apps (Vue or **Flutter** + FastAPI or Firebase, OpenProps + PrimeVue for web).

We publish **free, open [Cursor Agent Skills](https://github.com/HeyEddi-com/heyeddi-skills)** — install the full bundle with `npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'` or `./scripts/install-skills.sh --all`. Invoke with `@skill-name` in Cursor.

**Need people, not just agents?** [heyeddi.com/humans](https://heyeddi.com/humans) — hire vetted designers, engineers, and product folks to complement your agent workflows.

## Folder layout

```
.heyeddi/
├── README.md          # HeyEddi intro (agents + humans workspace), free skills, folder guide
├── stack.json         # { "frontend": "vue"|"flutter", "backends": ["fastapi"], "api_port": 8090, "web_port": 8085 }
├── product.md         # Users, routes, acceptance criteria
├── skills-index.json  # Cached skill catalog (@heyeddi-orchestrator)
├── skills-index.md    # Human-readable catalog table
├── design.md          # DESIGN.md format — tokens + rationale + Decision log
├── designs/
│   └── <feature>/     # Handoff PNGs, briefs, wireframes, research
├── docs/              # Skill-generated reports (ship, PR, drift, gates)
│   ├── intake/        # @heyeddi-intake — translation-*.md, skill-routing.json
│   ├── product/       # @heyeddi-product — backlog, features/, review plans
│   ├── workflow/      # @heyeddi-orchestrator — cross-pillar opinions (product·UX·design)
│   │   └── opinions/
│   ├── ux-flows.md    # Index of traced user tasks (@ux-flow-auditor)
│   ├── engineering/   # architecture, reuse-catalog, decisions (@engineering-excellence)
│   └── ux-flows/      # Per-task .flow.json + reports (@ux-flow-auditor)
└── audits/            # Visual / merge / ux-flow snapshots
    ├── visual/        # @visual-auditor — screenshots/, reviews/, fix-log, contrast
    │   ├── screenshots/
    │   ├── reviews/
    │   └── fix-log.md
    └── eval-process/  # Multi-turn eval proof (integration): manifest.json + per-step PNGs
```

## Conventions

1. **`scaffold_stack`** (via `@project-engineering` for Vue or `@flutter-engineering` for Flutter) creates `.heyeddi/` if missing, including `README.md`.
2. **`@heyeddi-intake`** (greenfield) writes `product.md`, optional mockups/briefs, and `docs/intake/skill-routing.json` before other skills.
3. **`@heyeddi-product`** reviews intake, writes feature specs (stories + AC), delegates UX/design/engineering research, and synthesizes review plans under `docs/product/`.
4. **Cross-pillar sync** — `@heyeddi-orchestrator` `init_workflow_sync` + `opinions/`; product, UX, and design pillars opine on each route (see `docs/cross-pillar-workflow.md`).
5. **Design skills** write to `.heyeddi/design.md` and `.heyeddi/designs/` (product.md often from `@heyeddi-intake` first).
6. **Always-on** — `@heyeddi-orchestrator` (router), `@engineering-excellence` (plan + change gates), prose anti-slop. See [always-on-skills.md](always-on-skills.md).
7. **QA / PR skills** write reports to `.heyeddi/docs/` (e.g. `ship-report.md`, `pr-42-tracking.md`).
8. **Engineering excellence** maintains `.heyeddi/docs/engineering/` and audit reports (`engineering-audit-<date>.md`).
9. **UX flow auditor** maintains `.heyeddi/docs/ux-flows/` and index `ux-flows.md`.
10. **Visual auditor** writes contrast reports and screenshots to `.heyeddi/audits/visual/` (not repo-root `.visual-audit/`).
11. **Skill orchestrator** — `.heyeddi/` stays current **automatically** when any HeyEddi skill tool runs (refreshes `skills-index.*` when missing). Optional explicit full sync: `@heyeddi-orchestrator` `sync`.
12. **Audience-driven design** — `product.md` Personas + Per-route intent drive `@heyeddi-design`; see `docs/design-excellence.md`.
13. **Legacy paths** at repo root (`PRODUCT.md`, `DESIGN.md`, `designs/`, `.visual-audit/`) still readable — skills write to `.heyeddi/` first.

## Path resolution

Shared helper: `skills/project-engineering/scripts/_heyeddi_paths.py` (copied into design skills). Scripts resolve canonical paths before falling back to legacy locations.

## Related

- [design-excellence.md](./design-excellence.md) — audience-driven design layers
- [clarify-before-act.md](./clarify-before-act.md) — when skills ask vs read `.heyeddi/`
- [team-cheat-sheet.md](./team-cheat-sheet.md)
- [eval-philosophy.md](./eval-philosophy.md)
- `skills/project-engineering/scaffold/heyeddi/README.md` — template copied into new projects
