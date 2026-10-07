---
name: heyeddi-design
description: "Product design partner for @taste-penpot. Use on design, UI, look, polish, or handoff requests AFTER taste-penpot has chosen the look. Records personas, route job, and tokens into .heyeddi/design.md, then hands off to @heyeddi-handoff or @design-handoff-flutter. Does not invent a second palette, type system, or multi-step aesthetic. Screenshot gate still applies before done."
version: 2.7.0
product-version: 3.5.0
author: HeyEddi-com
---

# HeyEddi Design

**Stack-agnostic UI design** for HeyEddi apps: discovery, briefs, critique, and design-system documentation. **Implementation** (Vue, Flutter, CSS in components) belongs to stack skills — see `reference/implement-routing.md`.

**Team:** `@taste-penpot` owns the look in one pass (Anthropic frontend-design + tokens). This skill owns product fit and implementation handoff. Read `reference/design-team.md` before any design turn. Do not author a second palette or restart discover → research → explore to find a look.

**Auto-pickup:** Design talk still loads this skill, and it immediately loads `@taste-penpot` if that pass has not already produced tokens. Then record those tokens. `reference/brief-language.md` is product language for the brief, not a second art direction.

## Design vs implement (mandatory split)

| Layer | Skill | Delivers |
|-------|-------|----------|
| Design (this skill) | `@heyeddi-design` | Briefs, wireframes, critique, `design.md`, IA, aesthetic direction |
| Implement (stack) | `@heyeddi-handoff`, `@design-handoff-flutter` | Production UI code in Vue / Flutter |
| Enforce (stack) | `@primevue-openprops-architect` | Vue tokens + PrimeVue guardrails |
| Verify (agnostic) | `@visual-auditor`, `@ux-flow-auditor` | Screenshots, contrast, flows, **fixes** |

Read **`reference/implement-routing.md`** every session that ends in shipped UI.

## Default behavior (no confirmation)

- **Design talk of any kind:** load `brief-language.md` first; pin taste + subject + hard rejects before chrome
- **Better design / redesign:** "better design", "make it better", "redesign", "new look", "overhaul", "wow", "top notch" → **do not polish-only**. Run critique ambition gate (`reference/critique.md`); if template-like or ambition fails → **`shape` → craft → implement**. Spacing/token tweaks alone are wrong for these phrases.
- **Critique + fix (local):** "looks bad", "fix this page", "polish", "tweak spacing" → critique **then** stack implementer + `@visual-auditor` — **unless** the ambition gate says escalate to `shape` (then shape first; do not ask).
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
@heyeddi  load_workflow_context --route /path
… design work + Decision log in design.md …
@heyeddi  append_pillar_opinion --pillar design …
→ @heyeddi-product scope check; @ux-flow-auditor flow note if IA affects tasks
```

## Setup (every session)

1. Run `python scripts/load_context.py --project-root <root>` once per session (skip if output is already in the conversation).
2. If `product_exists` is false and the task needs strategic context, run **`init`** before shape/craft.
3. Read the sub-command reference file for the invoked mode (required: do not skip).
3a. Read **`reference/brief-language.md` first** on any design/look/feel talk (discover, shape, craft, critique, polish, or informal "make it look…"): subject/metaphor, hard rejects, hero/type/accent/responsive/SSOT, first-viewport checklist, done gate.
3b. Read `reference/implement-routing.md` when shaping, crafting, critiquing, or polishing any route.
3c. Read `reference/surface-completeness.md` once per session when shaping, crafting, or critiquing any route.
3d. Read `reference/foundations.md` once per session: responsive, theme, i18n, a11y, reading modes are **always on** unless `product.md` waives them.
3e. Read `reference/modern-reference.md` when shaping **marketing, dashboard, or settings** routes.
3f. Read `reference/audience-design.md` when shaping, crafting, or polishing **any user-facing route**.
3g. Read `reference/design-ambition.md` on **flagship routes**.
3h. Read `reference/aesthetic-direction.md` on **any user-facing route**.
3i. Read `context/PROSE_ANTI_SLOP.md` when writing **UI copy** in briefs or `design.md`.
3j. Read `reference/visual-tools.md` during **`explore`**, **`shape`**, and **`critique`** on flagship routes: use **GenerateImage** for direction probes and **Canvas** for compare/brief/critique summaries when the IDE provides them.
4. After **shape** (brief confirmed), **critique**, or **polish**, append to **Decision log** in `.heyeddi/design.md`.
5. After stack implementer finishes: `@visual-auditor` **fast** widths `375,768,1440` while iterating. **Before calling done** on flagship/marketing: **done** widths `375,430,768,1024,1440,1920` (`--preset done`) and fix what you see. Logo-off test: if it could be another startup after removing the brand, it is not done.

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

1. **Better design / redesign intent** ("better design", "make it better", "redesign", "new look", "overhaul", "major improvement", "wow", "top notch" on an existing route): load `reference/critique.md` **ambition gate** → if escalate → `reference/shape.md` then `craft` (not polish-only). See `reference/design-ambition.md` § Improve vs redesign.
2. **Existing UI: local fix** ("critique", "looks bad", "fix this page", "polish"): load `reference/critique.md` → run ambition gate → polish-path implement + `@visual-auditor` **only if** gate says stay local. Do **not** ask.
3. **No sub-command, vague greenfield**: load `reference/discover.md` + `brief-language.md`.
4. **Sub-command matches table**: load `reference/<command>.md` (+ `brief-language.md` for shape/craft/critique/polish).
5. **`craft` without confirmed brief**: run **`shape`** first (brief must include subject + hard rejects).
5b. **Flagship routes** without personas: `@heyeddi-intake` or `discover` first.
6. **`polish` without critique this session**: run **critique** first (including ambition gate).
7. **Screenshots / approved mockups**: `@heyeddi-handoff` (implement), not design `craft` code.
8. **Never invoke impeccable**: this skill replaces it.

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

Responsive, light/dark, `en`+`es` i18n, WCAG 2.2 AA, semantic tokens: see `reference/foundations.md`, `reference/token-strategy.md`, `reference/brief-language.md`.

See `context/VOCABULARY.md`, `context/ANTI_PATTERNS.md`, `context/PROSE_ANTI_SLOP.md`, `context/EXAMPLES.md`, `reference/brief-language.md`.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py \
  --current-skill heyeddi-design --project-root .
```

Add `--route /path` and `--mode <sub-command>` when known.
