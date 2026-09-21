# Design excellence — HeyEddi layers

**Date:** 2026-09-20

How HeyEddi skills produce **world-class, audience-driven** UI — not generic “modern SaaS.”

## The stack (bottom → top)

| Layer | Artifact / skill | What it does |
|-------|------------------|--------------|
| **1. Intake** | `@heyeddi-intake` → `product.md` | Personas, per-route intent, competitors, voice |
| **2. Routing** | `skill-routing.json`, `@heyeddi-orchestrator` | Which skill runs per route; skills index cache |
| **3. Discovery** | `@heyeddi-design discover` + **`brief-language.md`** | Pin subject/metaphor + hard rejects (not adjectives); purpose, audience, scene |
| **4. Research** | `designs/<feature>/research.md` | Category + competitor + audience-specific trends |
| **5. Direction** | `audience-design.md` + `modern-reference.md` + `aesthetic-direction.md` | Map persona → aesthetic; technique execution |
| **6. Explore** | Wireframes + concept direction | User picks a direction before code |
| **7. Brief** | `designs/<feature>/brief.md` | Confirmed contract — Design signature (taste, rejects, hero, type, accent, responsive, SSOT) |
| **8. Craft / handoff** | `@heyeddi-design craft`, `@heyeddi-handoff` | Build from brief + DESIGN.md |
| **9. Audience-fit critique** | `audience-fit.md` | “Would Alex trust this?” gate |
| **10. Polish + visual proof** | `@visual-auditor` (`--preset done` on flagship), `@primevue-openprops-architect` | 6-width proof, logo-off brand test, token compliance |

Skip a layer → cap quality at that layer.

**Auto-pickup:** `@heyeddi-design` description matches design/look/feel talk without requiring `@` — agents must load `brief-language.md` in the same turn.

## `product.md` contract (required for flagship routes)

Sections every greenfield product should have:

- **Personas** — name, role, job, anxiety, design implication
- **Per-route intent** — register, mindset, success feeling, primary persona
- **Competitors & anti-audience** — what users compare you to; who this is NOT for
- **Voice & tone** — microcopy direction

See `skills/heyeddi-intake/reference/audience-intake.md`.

## Flagship route rule

For `/`, `/login`, `/dashboard`, `/settings`:

1. `product.md` audience sections present
2. `shape` completed OR brief exists with persona + **subject/metaphor + hard rejects** cited
3. `research.md` ties recommendations to a persona
4. Decision log cites **persona + pattern borrowed + memorable detail**
5. Visual done gate: `@visual-auditor --preset done` + logo-off brand test

## Related

- [heyeddi-folder.md](./heyeddi-folder.md)
- [clarify-before-act.md](./clarify-before-act.md)
- [always-on-skills.md](./always-on-skills.md)
- `skills/heyeddi-design/reference/brief-language.md`
- `skills/heyeddi-design/reference/audience-design.md`
- `skills/heyeddi-design/reference/audience-fit.md`
