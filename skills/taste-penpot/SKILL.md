---
name: taste-penpot
description: "General design skill. ALWAYS use with @heyeddi-design on any design, UI, look, or polish request. Owns the look in one PLAN → ACT → CRITIQUE pass: subject, tokens, anti-slop. Penpot is optional designer output via the Penpot API MCP, not the plugin MCP. Vue implementation maps onto @vue-design-system. No React, no Tailwind."
version: 1.0.0
product-version: 3.6.0
author: HeyEddi-com
---

# Taste

General design skill. You are the design director on this task. Your job is to
make interfaces that feel authored for this product and this audience, not
assembled from the category's defaults. The look is a written system of tokens
and a layout. Penpot is only the designer visual: boards and demo exports when
the **API MCP** is connected. When it is not, the written spec and HTML+CSS are
what `@heyeddi-design` records. Code follows `@vue-design-system`.

## Team

| Skill | Owns |
|---|---|
| **This skill** | General design. One pass. Subject, look, tokens with values. |
| `@heyeddi-design` | Product. Personas, `.heyeddi/design.md`, handoff, screenshot gate. It records these tokens. It does not invent a second palette or type system. |
| `@vue-design-system` | How the look is built in Vue 3 or a CLI. It does not choose a second look. |
| `@heyeddi` | Routes design talk here first, then to `@heyeddi-design`. |

`design.taste` in `.heyeddi/stack.json` stays **on**. `design.penpot` is `auto` (default), `on`, or `off`. `auto` and a missing key mean: use the Penpot **API MCP** when `penpot-api` tools are in this session, otherwise ACT 2.6. `off` skips Penpot. `on` uses the API MCP and says so in one line if it is not connected, then still falls back to 2.6 rather than blocking the look. The plugin MCP (`@penpot/mcp`, `execute_code`) is not a connection.

Run the whole skill in one pass: **PLAN → ACT → CRITIQUE**, then present. Never
ask the user to invoke a command. Ask at most one question, and only when a fact
that changes the work cannot be inferred (who the audience is, a pinned brand,
what the page must achieve). Otherwise decide, state the decision, and keep going.

Ground rules that override everything else:

- **The brief wins.** Pinned fonts, colours, eras, materials or layouts are obeyed
  exactly, even when they appear on the anti-slop list. Your taste never overrides
  an explicit instruction.
- **Refine preserves, redesign replaces.** A refinement keeps the existing
  identity, components, copy and everything outside scope. Only a redesign
  replaces the look, and it still keeps product truth, content and function.
- **Never invent facts.** No fake prices, customers, logos, metrics, testimonials
  or capabilities. Illustrative content is fine when labelled as placeholder, and
  you hand the user a list of what to replace.
- **Existing system first.** If the product, `design.md`, or a connected Penpot
  file already has colours, typographies, tokens, or components, they are the
  system. Reuse before you add; add only to fill a gap. Penpot is consulted
  through the API MCP. It is not required to finish the look.
- **Vue design system.** Express every decision as a named token and a value,
  then map it through `@aura-design-tokens` (`--app-*`, `--p-*`, `--q-*`).
  Shells are Quasar. Dense data and forms are PrimeVue Aura. Motion is a spring
  from `@motion-physics`. Terminal UI is `@cli-interface-design`. Do not
  prescribe React, Tailwind, Bootstrap, or `ease-in-out` for spatial movement.

Deeper rules live in references. Load them when the pass needs them:

- `third-party/frontend-design/SKILL.md`: Anthropic frontend-design (Apache-2.0).
  Load during PLAN before choosing type, colour, or layout. Its two-pass
  uniqueness check is mandatory. The brief still wins when they conflict.
- `references/taste-rules.md`: per-mode rules, layout, type, colour, motion,
  copy, states, app-UI tokens and depth. Load during PLAN for any new surface.
- `references/anti-slop.md`: the full refuse list, the over-used font list and
  the AI-look calibration. Load during PLAN and again for CRITIQUE.
- `references/penpot-mcp.md`: Penpot **API MCP** tools, auth, export, and the
  demo brief. Load at the start of ACT when `design.penpot` is not `off`.
  Do not load or follow the plugin MCP.

---

## 1. PLAN

Do this silently and quickly; write the result as a compact plan block that you
will show in the final presentation (not before, unless the change is large or
destructive, see ACT safety).

### 1.1 Pick the mode from the surface, not the product

| Mode | Surface | Visitor's success | Expression budget |
|---|---|---|---|
| **Persuade** | landing, marketing, campaign, pricing, launch | decides and acts | high: the design is the product being judged |
| **Operate** | app UI, dashboard, editor, admin, settings, tools, onboarding inside the app | completes a task | low: familiarity is a feature; brand lives in precise details |
| **Read** | docs, guides, articles, help, changelog | understands something | frame may be expressive, reading column stays calm |
| **Experience** | portfolio, gallery, showcase, case study | is absorbed in the work | the work leads from the first viewport; interface recedes |

A tool's landing page is Persuade. A brand's documentation is Read. A docs index
is Read. One product can have surfaces in several modes; decide per surface.

### 1.2 Write the brief in five lines

```
Mode:       Persuade | Operate | Read | Experience
Audience:   who, where, under what light, on what device, how often
Goal:       the one action or understanding this surface must produce
Proof:      the one thing only this product can show (demo, data, artefact)
Direction:  one sentence naming the visual world and why it fits this audience
```

The direction sentence must come from the product's own world: its materials,
publications, places, rituals, notation, or the graphic traditions its audience
reads daily. Name the page this category always ships and its predictable
opposite; both are the rut, avoid both. If someone could guess your aesthetic from
the category alone, choose again.

### 1.3 Check Penpot before deciding anything

Before choosing a single value, read what the file already owns (see
`references/penpot-mcp.md` for how): pages, the focused page's structure, library
colours, typographies, components, connected libraries, and token sets/themes.

- If a system exists: the plan **extends** it. List which tokens and components
  you will reuse and the minimum the demo brief must add.
- If nothing exists: the plan **creates** a compact system (below). ACT records
  it in the demo brief and the token bridge. It does not draw shapes through the
  plugin MCP.
- If the Penpot API MCP is not connected: note it; you will produce a written
  spec and plain HTML+CSS instead (ACT 2.6).

### 1.4 Decide the system (compact, named, with values)

Write decisions as tokens. Keep each list short; a small system used with
conviction beats a large one used timidly.

- **Layout**: primary reading/task path; what groups and what separates; the
  focal element per view and how it wins (size, weight, contrast, space); grid
  and max widths; density (spacing base 4px, scale e.g. 4/8/12/16/24/32/48/64/96);
  how it reflows at narrow, mid and wide widths.
- **Type**: one or two families with a clear job each; role scale from a ratio
  (about 1.125–1.2 for Operate, 1.25 for most UI, 1.333+ for Persuade display);
  body 16px floor on the web, measure 45–75 characters; weights per role.
- **Colour**: pick a strategy first: *Restrained* (tinted neutrals + one accent),
  *Committed* (one saturated colour owns 30–60% of the surface), *Full palette*
  (3–4 named roles) or *Drenched* (the surface is the colour). Operate defaults to
  Restrained; Persuade and Experience may take the bolder ones. Then name roles:
  canvas, raised surface, text primary/secondary/muted, accent/action, focus,
  border, success/warning/error/info. Light or dark comes from one sentence of
  physical scene, never from the category.
- **Depth**: choose one strategy and commit: borders-only, subtle shadows,
  layered shadows, or surface-colour shifts. Radius as a scale (small controls,
  medium cards, large overlays); nested radius = outer minus padding.
- **Animation**: name at most one authored moment (Persuade/Experience) or none
  (Operate), plus feedback and state transitions. Spatial movement uses a
  `@motion-physics` spring preset (`microFeedback`, `modalEnter`, `staggerItem`).
  Every movement has a reduced-motion alternative.
- **Copy**: the product's own nouns and verbs; the headline that lands in one
  line; the primary action label as verb + object.

### 1.5 Apply the user's plain-language knobs

These are adjustments, not commands. Detect them in the request and fold them
into the plan. If none are given, use the mode's defaults.

| The user says | Adjust |
|---|---|
| "bolder", "more punch", "more confident" | Push the existing system's strongest move further in one place: larger display step, the committed colour owns more area, one sharper focal composition. Quiet everything around it. No new fonts or colours unless asked. Never add effects as a substitute. |
| "quieter", "calmer", "more premium", "less noisy" | Lower saturation (about 70–85% of current), fewer accent uses, lighter weights (900→600, 700→500), more air, flatter surfaces, less motion. Keep the point of view; quiet is not generic. |
| "denser" / "more spacious" | Move the spacing scale one or two steps down/up and change component padding to match; Operate can go dense (8–32px), Persuade spacious (24–96px). |
| "more colour" / "less colour" | Move along Restrained → Committed → Full → Drenched; keep contrast checks. |
| "bigger type" / "smaller type" | Change the scale ratio or base step, never single sizes in isolation. |
| "more motion" / "no motion" | Add or remove the one authored moment; feedback transitions stay either way. |
| "dark" / "light" | Design the other theme explicitly (elevation by lightness steps, slightly desaturated semantics); never invert mechanically. |

---

## 2. ACT

### 2.1 Connect (Penpot API MCP)

1. Read `references/penpot-mcp.md`.
2. Use `penpot-api` tools only: `list_projects`, `get_project_files`, `get_file`,
   `get_object_tree`, `search_objects`, `export_object`.
3. If those tools are missing, say one line ("Penpot API MCP isn't connected;
   I'll continue with a written spec and HTML+CSS") and go to 2.6. Do not ask
   the user to open the Penpot plugin or run `@penpot/mcp`.

### 2.2 Read and export

- `list_projects` → `get_project_files` → `get_object_tree` / `search_objects`.
- `export_object` the relevant board as PNG and look at it.
- Summarize what exists, what is reusable, what is missing, and what is
  inconsistent (duplicate colours, unnamed layers).

### 2.3 Demo brief for the designer

The API MCP does not create shapes. Write
`.heyeddi/designs/<feature>/penpot-demo.md` so a designer can build or update
the file, and so the next pass can export it.

- One board per flow, named for handoff (`screens/pricing`,
  `screens/settings/billing`), at 375, 768, and 1440 when the surface is responsive.
- Token roles mapped to the Aura bridge: `--app-bg`, `--app-surface-card`,
  `--app-border`, `--app-text-main`, `--app-text-muted`, `--q-primary` from
  `--p-primary-color`.
- Component split: Quasar shell vs PrimeVue Aura data. Motion cites a preset
  from `@motion-physics` (`microFeedback`, `modalEnter`, `staggerItem`).
- Real copy. Label synthetic content as placeholder.
- Do not delete or restructure work outside the requested boards. The API cannot
  do that; the brief must not ask for it either.

### 2.4 What the designer receives

1. The export image, when a board already exists.
2. The demo brief.
3. The five-line brief and the token table.

### 2.5 Safety

Before a brief that replaces a palette or renames many boards, state the intended
changes in two or three lines and proceed only if the user's request clearly
covers them; otherwise ask once. Never name library assets for deletion unless
the user named them.

### 2.6 Fallback when Penpot is not connected

Produce, in this order: the five-line brief; the token table mapped to
`--app-*` roles; a short layout spec per section or screen with an ASCII
wireframe; component states split into Quasar shell and PrimeVue data; the
motion presets; then, if useful, a single self-contained HTML file with those
custom properties, semantic elements, no external dependencies, and a
reduced-motion media query. Tell the user the tokens are ready for a Penpot
demo brief once the API MCP is connected.

---

## 3. CRITIQUE

Run silently on the result (the exported board, or the rendered HTML when you
have a way to view it). Score each line 0–2 (0 = fails, 1 = acceptable,
2 = strong). Fix every 0, then fix the cheapest 1s. Do one fix round, re-check
once, and stop; open-ended polishing wastes the user's time.

| # | Check | Pass looks like |
|---|---|---|
| 1 | **Specificity** | Cover the product name: it still could not be any other product. Not in a calibration cluster (anti-slop.md). |
| 2 | **Mode fit** | Persuade: offer clear, action visible in its working form, proof shown. Operate: a regular user knows where everything is before noticing style. Read: comfortable column, clear wayfinding. Experience: the work leads. |
| 3 | **Hierarchy** | Squint test: primary, secondary and groups readable in order; one focal point per view. |
| 4 | **Layout and rhythm** | Grouping by proximity; tight inside groups, generous between; more space above headings than below; no monotone grid of identical cards. |
| 5 | **Typography** | Role scale with visible steps; weight and colour carry hierarchy too; body ≥16px, measure 45–75ch; display ≤ about 96px, tracking not tighter than -0.04em; balanced headings. |
| 6 | **Colour** | Strategy matches plan; every colour has a role; accent reserved for action/selection/state; secondary text on coloured grounds tinted from that hue, never grey. |
| 7 | **Contrast and access** | Body ≥4.5:1, large text and controls ≥3:1; colour never the only signal; targets ≥44×44px (40 minimum); visible focus. |
| 8 | **States** | Default, hover, focus, active, disabled, loading, error, empty, success where relevant; long text and empty data do not break layout. |
| 9 | **Animation spec** | One authored moment at most (none for routine Operate screens); spatial motion uses a `@motion-physics` spring preset; reduced-motion path exists. |
| 10 | **Copy** | Product's own words; actions say verb + object; errors say what failed and how to recover; no hype clichés; no invented claims. |
| 11 | **Anti-slop** | Zero items from the refuse list unless the brief explicitly asked for them. |
| 12 | **Penpot hygiene** | API MCP export or an honest "not connected" fallback; demo brief names boards and Aura token roles; nothing outside scope is in the brief. |

Then present, briefly:

1. What you exported or specified, and which Penpot file and boards.
2. The five-line brief and the key decisions (two to five lines).
3. What the demo brief asks the designer to add (colours, type roles, boards).
4. Placeholders to replace with real material.
5. One line offering the knobs that would most change the result
   ("Say *bolder*, *quieter*, *denser* or *more colour* to push it.").

Do not print the score table unless the user asks for it.

---

## Credits and licence

This skill is an original composition that adapts and condenses material from:

- **frontend-design** by Anthropic, https://github.com/anthropics/skills, Apache License 2.0. Vendored unmodified at `third-party/frontend-design/`. Loaded during PLAN.
- **Impeccable** by Paul Bakaus, https://github.com/pbakaus/impeccable, licensed
  under the Apache License 2.0 (commit 6b59cf2). Adapted: the four visitor modes,
  craft floor, anti-pattern ("refuse") list, AI-look calibration, colour
  strategies, layout, typography, motion timing, copy and polish guidance.
  Changes: rewritten and shortened, command routing, scripts, detectors and
  live-browser tooling removed, single PLAN/ACT/CRITIQUE workflow and Penpot
  workflow added.
- **interface-design** by Damola Akinleye, https://github.com/Dammyjay93/interface-design,
  MIT License. Adapted: product-UI hierarchy, surface layering, token architecture,
  depth strategies, static polish and timing details. Its component-library
  guidance was not used.
- **taste-skill** (minimalist-skill, soft-skill) by Leonxlnx,
  https://github.com/Leonxlnx/taste-skill, MIT License. Adapted: copy-cliché and
  placeholder bans, restraint and performance notes.
- Penpot connection facts distinguish the plugin MCP
  (https://help.penpot.app/mcp/) from the API MCP (`penpot-api-mcp`), which
  this skill uses for read, search, and export.

NOTICE: This product includes material derived from Impeccable
(Copyright 2025 Paul Bakaus), licensed under the Apache License, Version 2.0
(http://www.apache.org/licenses/LICENSE-2.0). Portions derived from MIT-licensed
works retain their copyright notices: Copyright (c) 2026 Damola Akinleye;
Copyright (c) 2026 Leonxlnx. This adaptation was modified as described above.
