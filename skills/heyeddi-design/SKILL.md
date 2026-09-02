---
name: heyeddi-design
description: "Stack-agnostic UI design: discovery, briefs, critique, design system docs. Uses GenerateImage + Canvas to show direction during explore/shape. Implementation via @heyeddi-handoff or @design-handoff-flutter. Auto-fix on critique. Screenshots → @heyeddi-handoff."
version: 2.5.0
product-version: 3.4.7
author: HeyEddi-com
---

# HeyEddi Design

**Stack-agnostic UI design** for HeyEddi apps: discovery, briefs, critique, and design-system documentation. **Implementation** (Vue, Flutter, CSS in components) belongs to stack skills — see `reference/implement-routing.md`.

**Calm wow:** when users ask for modern / wow / living UI, read `reference/modern-reference.md` and `reference/aesthetic-direction.md` (**Calm wow for B2B**) before shaping.

**You do not need design vocabulary from the user.** Plain intent ("enterprise view for our app") is enough: ask questions until direction is clear.

## Design vs implement (mandatory split)

| Layer | Skill | Delivers |
|-------|-------|----------|
| Design (this skill) | `@heyeddi-design` | Briefs, wireframes, critique, `design.md`, IA, aesthetic direction |
| Implement (stack) | `@heyeddi-handoff`, `@design-handoff-flutter` | Production UI code in Vue / Flutter |
| Enforce (stack) | `@primevue-openprops-architect` | Vue tokens + PrimeVue guardrails |
| Verify (agnostic) | `@visual-auditor`, `@ux-flow-auditor` | Screenshots, contrast, flows, **fixes** |

Read **`reference/implement-routing.md`** every session that ends in shipped UI.

## Default behavior (no confirmation)

- **Critique + fix:** "looks bad", "fix this page", "improve UI" → critique report **then** stack implementer fixes code **then** `@visual-auditor` — do not ask
- **Craft:** confirmed brief → hand off to stack implementer in the same workflow
- **Ambition bar:** impressive craft is default on flagship routes — do not wait for user to ask

## Subagents (default)

**Delegate by sub-command**: see `reference/subagents.md`. Main chat confirms briefs and merges results.

| Always delegate | Subagent |
|-----------------|----------|
| `@visual-auditor` / Playwright | `shell` |
| `validate_vue`, npm test, build | `shell` |
| `critique`, `craft`, `polish` (route work) | `generalPurpose` |
| `research`, wireframe `explore` | `generalPurpose` |
| Codebase scan for `document` | `explore` |

Do not run visual capture inline during handoff turns.

## Cross-pillar sync (mandatory)

Read **`reference/cross-pillar-handoff.md`**. Bookend **craft**, **critique**, **polish**, **shape** (confirmed brief):

```
@heyeddi-orchestrator  load_workflow_context --route /path
… design work + Decision log in design.md …
@heyeddi-orchestrator  append_pillar_opinion --pillar design …
→ @heyeddi-product scope check; @ux-flow-auditor flow note if IA affects tasks
```

## Setup (every session)

1. Run `python scripts/load_context.py --project-root <root>` once per session (skip if output is already in the conversation).
2. If `product_exists` is false and the task needs strategic context, run **`init`** before shape/craft.
3. Read the sub-command reference file for the invoked mode (required: do not skip).
3a. Read `reference/implement-routing.md` when shaping, crafting, critiquing, or polishing any route.
3b. Read `reference/surface-completeness.md` once per session when shaping, crafting, or critiquing any route.
3c. Read `reference/foundations.md` once per session: responsive, theme, i18n, a11y, reading modes are **always on** unless `product.md` waives them.
3d. Read `reference/modern-reference.md` when shaping **marketing, dashboard, or settings** routes.
3e. Read `reference/audience-design.md` when shaping, crafting, or polishing **any user-facing route**.
3f. Read `reference/design-ambition.md` on **flagship routes**.
3g. Read `reference/aesthetic-direction.md` on **any user-facing route**.
3h. Read `context/PROSE_ANTI_SLOP.md` when writing **UI copy** in briefs or `design.md`.
3i. Read `reference/visual-tools.md` during **`explore`**, **`shape`**, and **`critique`** on flagship routes: use **GenerateImage** for direction probes and **Canvas** for compare/brief/critique summaries when the IDE provides them.
4. After **shape** (brief confirmed), **critique**, or **polish**, append to **Decision log** in `.heyeddi/design.md`.
5. After stack implementer finishes, ensure `@visual-auditor` ran at 375/768/1440 before calling design work done.

## Commands

| Command | Purpose |
|---------|---------|
| *(no sub-command)* | Vague design request → start **`discover`** |
| `init` | Create or refresh `PRODUCT.md`; offer `document` for `DESIGN.md` |
| `discover` | Discovery interview only: no code, no final brief yet |
| `research` | Web trend / reference research for current design direction |
| `explore` | Concept images (GenerateImage) + Canvas compare + wireframes |
| `shape` | Full planning flow: discover → research → explore → confirmed brief |
| `document` | Generate or refresh `DESIGN.md` from code or seed questions |
| `craft` | Brief ready → **hand off to stack implementer** (see implement-routing) |
| `critique` | UX review of existing UI → report → **auto-chain implement + visual-auditor** |
| `polish` | Design-spec refinement + stack implementer for code (after critique) |

## Routing rules

1. **Existing UI: critique or improve** ("critique", "looks bad", "fix this page"): load `reference/critique.md` → implement + `@visual-auditor` in the same workflow. Do **not** ask.
2. **No sub-command, vague greenfield**: load `reference/discover.md`.
3. **Sub-command matches table**: load `reference/<command>.md`.
4. **`craft` without confirmed brief**: run **`shape`** first.
4b. **Flagship routes** without personas: `@heyeddi-intake` or `discover` first.
5. **`polish` without critique this session**: run **critique** first.
6. **Screenshots / approved mockups**: `@heyeddi-handoff` (implement), not design `craft` code.
7. **Never invoke impeccable**: this skill replaces it.

## Artifacts

| Artifact | Location |
|----------|----------|
| Design brief (confirmed) | `.heyeddi/designs/<feature>/brief.md` |
| Wireframes | `.heyeddi/designs/<feature>/wireframes/` |
| Research notes | `.heyeddi/designs/<feature>/research.md` |
| Design system | `.heyeddi/design.md` |
| Product context | `.heyeddi/product.md` |
| Critiques, audits | `.heyeddi/docs/` |

Use kebab-case for `<feature>`.

## Foundations (design spec — implementer enforces in code)

Responsive, light/dark, `en`+`es` i18n, WCAG 2.2 AA, semantic tokens: see `reference/foundations.md`, `reference/token-strategy.md`.

See `context/VOCABULARY.md`, `context/ANTI_PATTERNS.md`, `context/PROSE_ANTI_SLOP.md`, `context/EXAMPLES.md`.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py \
  --current-skill heyeddi-design --project-root .
```

Add `--route /path` and `--mode <sub-command>` when known.
