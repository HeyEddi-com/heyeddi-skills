---
name: taste-penpot
description: "General design skill. ALWAYS use with @heyeddi-design on any design, UI, look, or polish request. Owns the look in one PLAN → ACT → CRITIQUE pass: subject, tokens, anti-slop. When no style/identity is pinned, MUST run the identity gate: designer thinking (project, peers, follow vs unique) documented under .heyeddi/designs/, ask clarifying questions when needed, then present 3–5 What/Why/How options and wait for choice before tokens or pixels. Scaffolding/MVP never waives the gate. Penpot path is design-system-first (add_color/add_typography, list_font_variants) then boards via @heyeddi/penpot-mcp-server. Hard gates A–G: text-walls; Flex claim needs reflow (children not at 0,0); layoutItem via set_layout_item; PNG Gate D (audit alone never ships); no invented fonts; page hygiene. Flex API may not reflow — absolute 8px escape after one fail. Never use unscoped penpot-mcp-server or @penpot/mcp. Vue maps onto @vue-design-system. No React, no Tailwind."
version: 1.7.0
product-version: 3.8.10
author: HeyEddi-com
---

# Taste

General design skill. You are the design director on this task. Your job is to
make interfaces that feel authored for this product and this audience, not
assembled from the category's defaults. The look is a written system of tokens
and a layout. Penpot is the designer visual: boards and demo exports when
`@heyeddi/penpot-mcp-server` is connected (Flex/Grid + `parentId` nesting). When
it is missing and `design.penpot` is not `off`, ask once and install it only
after the user says yes (`references/penpot-mcp.md`). Upstream
`@zcubekr/penpot-mcp-server` is absolute-only; then ACT 2.6 HTML is required.
The written spec and HTML+CSS are what `@heyeddi-design` records when Penpot
stays off. Code follows `@vue-design-system`.

## Team

| Skill | Owns |
|---|---|
| **This skill** | General design. One pass. Subject, look, tokens with values. |
| `@heyeddi-design` | Product. Personas, `.heyeddi/design.md`, handoff, screenshot gate. It records these tokens. It does not invent a second palette or type system. |
| `@vue-design-system` | How the look is built in Vue 3 or a CLI. It does not choose a second look. |
| `@heyeddi` | Routes design talk here first, then to `@heyeddi-design`. |

`design.taste` in `.heyeddi/stack.json` stays **on**. `design.penpot` is `auto` (default), `on`, or `off`. `auto`, `on`, and a missing key use `@heyeddi/penpot-mcp-server` (`list_teams`, `create_frame`, prefer `set_frame_layout` / `parentId`). If that server is missing, ask once and install it into `.cursor/mcp.json` only after an explicit yes, then continue. `off` skips Penpot and does not ask. A no on the install falls through to ACT 2.6 and does not block the look. The unscoped npm package `penpot-mcp-server`, the plugin MCP (`@penpot/mcp`, `execute_code`), and `penpot-api-mcp` are never a connection.

### Penpot MCP install (HeyEddi)

Full contract: `references/penpot-mcp.md`. Hard gates: `references/layout-hard-gates.md`.

```json
{
  "mcpServers": {
    "penpot": {
      "command": "npx",
      "args": ["-y", "github:HeyEddi-com/penpot-mcp-server"],
      "env": {
        "PENPOT_API_URL": "https://design.penpot.app"
      }
    }
  }
}
```

After npm publish, prefer `"args": ["-y", "@heyeddi/penpot-mcp-server"]`. Keep `PENPOT_ACCESS_TOKEN` in the env Cursor passes to the server; never write it into `mcp.json` or chat. Hi-fi path: **design system first** (`add_color` / `add_typography`, fonts from `list_font_variants`) → `create_frame` with `layout` + children with `parentId` → `set_layout_item` + read `layout` / `parentId` / child `x,y` back → if children stuck at `0,0`, absolute 8px escape (do not rebuild Flex) → `export_shape` and look at the PNG. No PNG / Cloudflare ⇒ not done. `audit_board` alone never ships. `hifi.html` does not prove those boards. Absolute-only upstream zcubekr still requires ACT 2.6 `hifi.html`.

Run the whole skill in one pass: **PLAN → ACT → CRITIQUE**, then present — **after**
the identity is locked. Never ask the user to invoke a command.

**Identity gate (hard):** If the user did not pin a style/brand and this is not a
refine of an existing `design.md` system, load `references/identity-gate.md`
**before any tokens or pixels**. Run **designer thinking** first (what the
project is, what peers do, follow vs unique), write it to
`.heyeddi/designs/<feature>/identity-thinking.md`, ask **2–3 clarifying
questions** when job/audience cannot be inferred, then present **3–5**
What/Why/How identities and write them to `identity-options.md`. **Stop and
wait** for A–E (or a hybrid). Scaffolding / MVP / "workable UI" never waives
this. Refine of an existing identity skips the gate. "You choose" counts as a
choice — pick one, say why, continue. Full rules: `references/identity-gate.md`.

Aside from the identity gate (Phase 0 questions + A–E choice) and the Penpot
install question (`references/penpot-mcp.md` when the server is missing and
`design.penpot` is not `off`), ask at most one other design question, and only
when a fact that changes the work cannot be inferred. Otherwise decide, state
it, and keep going.

Ground rules that override everything else:

- **Identity before pixels.** No locked identity → no ACT. Document thinking in
  `.heyeddi/` before options; never skip for scaffolding. See identity gate.
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
  system. Reuse before you add; add only to fill a gap. This rule does **not**
  apply when the user asked to redesign, start from scratch, or replace the
  look. Then the current visual system is a hard reject for the pages in scope.
  Routes, behavior, and real copy stay. Load `references/code-to-design.md`
  before PLAN. Penpot is `@heyeddi/penpot-mcp-server` in `references/penpot-mcp.md`.
  It is not required to finish the look.
- **Vue design system.** Express every decision as a named token and a value,
  then map it through `@aura-design-tokens` (`--app-*`, `--p-*`, `--q-*`).
  Shells are Quasar. Dense data and forms are PrimeVue Aura. Motion is a spring
  from `@motion-physics`. Terminal UI is `@cli-interface-design`. Do not
  prescribe React, Tailwind, Bootstrap, or `ease-in-out` for spatial movement.

Deeper rules live in references. Load them when the pass needs them:

- `references/identity-gate.md`: **designer thinking → 3–5 What/Why/How options
  + wait** when no style is pinned. Document under `.heyeddi/designs/`. Load at
  PLAN start for new looks / redesigns / adjective-only / scaffold first looks.
  Skip only for refine of an existing system or a pinned brand.
- `third-party/frontend-design/SKILL.md`: Anthropic frontend-design (Apache-2.0).
  Load during PLAN before choosing type, colour, or layout (after identity is
  locked). Its two-pass uniqueness check is mandatory. The brief still wins
  when they conflict.
- `references/taste-rules.md`: per-mode rules, layout, type, colour, motion,
  copy, states, app-UI tokens and depth. Load during PLAN for any new surface.
- `references/flex-grid.md`: Penpot Flex (Shift+A) for one direction, CSS Grid
  (Ctrl/Cmd+Shift+A) for rows and columns together. Load during PLAN whenever
  the surface has structure, and in ACT when writing boards or the HTML fallback.
- `references/layout-hard-gates.md`: **reject rules** Gates A–G (text-walls,
  Flex reflow / 0,0 children, HTML≠Penpot, PNG visual QA, design system first,
  layoutItem stickiness, page hygiene). Load at ACT start and before claiming
  done. Hi-fi bar = human settings/form craft, not a copy paste in a gray
  rectangle. Known MCP limits are listed there — do not paper them over.
- `references/strokes-and-tokens.md`: Penpot 2.19 per-side strokes and shared
  token libraries. Load when a board or rectangle has a border, a divider, or
  a token binding.
- `references/anti-slop.md`: the full refuse list, the over-used font list and
  the AI-look calibration. Load during PLAN and again for CRITIQUE.
- `references/code-to-design.md`: analyze an existing app, then propose a
  redesign for the whole product, some pages, or one page. Load before PLAN
  when the user wants a redesign or a from-scratch look. Do not edit Vue in
  that pass.
- `references/penpot-mcp.md`: `@heyeddi/penpot-mcp-server` (Flex/Grid + nesting).
  Load at the start of ACT when `design.penpot` is not `off`. Install after user
  approval when `list_teams` is missing. Never load unscoped `penpot-mcp-server`,
  `@penpot/mcp`, or `penpot-api-mcp`.

---

## 1. PLAN

Do this silently and quickly; write the result as a compact plan block that you
will show in the final presentation (not before, unless the change is large or
destructive, see ACT safety).

### 1.0 Identity gate (before mode tokens)

Load `references/identity-gate.md`. If the gate applies and the user has not
chosen yet: run Phase 0 (project / peers / stance → `.heyeddi/…/identity-thinking.md`;
ask if blocked), then present **3–5** What/Why/How options in chat and
`identity-options.md`, then **end the turn**. Do not continue to 1.1–1.5 or ACT
until they pick. If the gate is skipped or already satisfied, state which
identity is locked in one line and continue.

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
`references/penpot-mcp.md`): `list_projects`, `list_files`, `get_file`.

- If this is a redesign or from-scratch request: do not extend the current
  palette. Follow `references/code-to-design.md`. The audit is written before
  the new tokens.
- If a system exists and the user did not ask to replace it: the plan
  **extends** it. List which tokens and components you will reuse.
- If nothing exists: the plan **creates** a compact system (below).
- If `@heyeddi/penpot-mcp-server` is not connected: follow Install in
  `references/penpot-mcp.md`. A declined install produces a written spec and
  plain HTML+CSS (ACT 2.6). Do not read boards through another Penpot server.

### 1.4 Decide the system (compact, named, with values)

Only after identity is locked (pinned, chosen, or refine-skip). Write decisions
as tokens from that identity. Keep each list short; a small system used with
conviction beats a large one used timidly.

- **Layout**: primary reading/task path; what groups and what separates; the
  focal element per view and how it wins (size, weight, contrast, space);
  density (spacing base 4px, scale e.g. 4/8/12/16/24/32/48/64/96); how it
  reflows at narrow, mid and wide widths. Name the engine per region from
  `references/flex-grid.md`: Flex for a 1D stack, CSS Grid for a 2D skeleton.
  Child sizing is Fit Content, Fill, or Fix.
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

### 2.1 Connect (Penpot MCP)

1. Read `references/penpot-mcp.md` and `references/layout-hard-gates.md`.
2. Use the `penpot` server when it is `@heyeddi/penpot-mcp-server` or compatible
   API MCP with `list_teams` + `create_frame`. Prefer HeyEddi tools:
   `add_color`, `add_typography`, `list_font_variants`, `set_frame_layout`,
   `parentId`, `set_layout_item`, `reparent_shape`, `create_text`,
   `create_rectangle`, `export_shape`.
3. If `list_teams` is missing, or the connected server is unscoped
   `penpot-mcp-server`, `@penpot/mcp`, or `penpot-api-mcp`, follow Install in
   `references/penpot-mcp.md`. Do not call those other servers. Skip boards and
   go straight to 2.6 after the user declines, or when `design.penpot` is `off`.
4. Detect capacity: if `set_frame_layout` or `create_frame` accepts `layout` and
   creates accept `parentId` (HeyEddi fork), attempt Flex/Grid **then prove
   reflow** (Gate F). If only absolute create_* exists (upstream zcubekr),
   boards are **low-fi** and **2.6 `hifi.html` is mandatory**.

### 2.2 Design system, then boards, then export

- `list_projects` → `list_files` → `get_file` for the app's project.
- **Gate E first:** reuse or `add_color` / `add_typography`. Fonts only from
  `list_font_variants` (or already in the file). No invented faces.
- Create or update the page and frames for the scope. Prefer components for
  repeated chrome. Then read shapes back (`get_shape_properties`: `layout`,
  `parentId`, `x`, `y`, `layoutItem*`). Always `set_layout_item` after create.
- No `layout`, or copy not parented to the phone → low-fi sketch. Flex flag
  with children still at `0,0` → **absolute 8px escape** (one try only). Do not
  write Flex hi-fi in `penpot-demo.md`.
- **Gate D:** `export_shape` and read the PNG. Cloudflare / missing export ⇒
  **not done** — say so. `audit_board` is a hint only. Prefer rect + cover
  image fill over `create_image`. `hifi.html` does not prove the Penpot file.
- **Gate G:** do not leave empty Look/dated shells as the demo surface.
- On a redesign, the current palette is not reusable. Summarize what stays
  (routes, copy, behavior) and what the new boards replace.

### 2.3 Demo brief + boards (low-fi when absolute)

Create MCP boards only after Gate E, and always write
`.heyeddi/designs/<feature>/penpot-demo.md` so the handoff survives if the
server disconnects.

- One board per flow, named for handoff (`screens/pricing`,
  `screens/settings/billing`), at 375, 768, and 1440 when the surface is responsive.
- Label boards **low-fi / absolute sketch** when Flex was not proven. Label
  **hi-fi / absolute 8px** only after Gate F escape + Gate D PNG.
- Token roles mapped to the Aura bridge: `--app-bg`, `--app-surface-card`,
  `--app-border`, `--app-text-main`, `--app-text-muted`, `--q-primary` from
  `--p-primary-color`. Quote Penpot library colour/typography ids in the brief.
- Component split: Quasar shell vs PrimeVue Aura data. Motion cites a preset
  from `@motion-physics` (`microFeedback`, `modalEnter`, `staggerItem`).
- Layout engine per region from `references/flex-grid.md` (direction or tracks,
  gap, padding, justify, align, Fit / Fill / Fix). Quasar `q-layout` is the app
  frame: drawer width and header height are the fixed grid tracks. Page
  interiors use the named engine. If the live MCP schema can set flex or grid,
  set it on the frame **and prove reflow**. Otherwise the demo brief is the
  Shift+A / Ctrl+Shift+A instruction for a human in Penpot, and
  **implementation CSS comes from 2.6**.
- **No text-walls (Gate A):** never one multiline string per card. Place separate
  labels, fields, helpers, and CTAs on the **8px grid** (many `create_text` /
  `create_rectangle` calls). Operate surfaces must read as a settings/form UI.
- Real copy. Label synthetic content as placeholder.
- Do not delete projects, files, pages, or shapes unless the user named that
  exact target. Prefer rename/replace for empty shells (Gate G).

### 2.4 What the designer receives

1. The Penpot canvas (export PNG, or the shape read-back when export is missing).
   HTML is included only when no Penpot boards were written.
2. The demo brief (low-fi vs hi-fi clearly marked).
3. The five-line brief and the token table.

### 2.5 Safety

A from-scratch or redesign request already covers a new palette for the pages
in scope. State that palette in the proposal and continue. For any other task,
state a palette replacement in two or three lines and ask once if the request
did not cover it. Never delete a library asset unless the user named it.

### 2.6 Hi-fi HTML (when MCP cannot Flex)

**Required** when Flex/Grid cannot be set or children cannot nest (`parentId`
missing), when `design.penpot` is `off`, or when the user declined install.
Do not write this file to prove boards that already exist in Penpot. Connected
absolute-only MCP does **not** skip this step. Flex that was not read back
(Gate B) does **not** skip it either.

Produce, in this order: the five-line brief; the token table mapped to
`--app-*` roles; a short layout spec per section or screen with an ASCII
wireframe; component states split into Quasar shell and PrimeVue data; the
motion presets; then a self-contained HTML file at
`.heyeddi/designs/<feature>/hifi.html` (add width variants if needed) with those
custom properties, semantic elements, **separate field rows** (no text-walls),
no external dependencies, and a reduced-motion media query. Layout CSS is the
Flex or Grid spec from `references/flex-grid.md` (`display`, `gap`, tracks,
Fit / Fill / Fix). That CSS is what handoff copies. Full reject rules:
`references/layout-hard-gates.md`.

If Penpot was skipped, tell the user the tokens are ready for a Penpot demo
brief once `@heyeddi/penpot-mcp-server` is connected.

---

## 3. CRITIQUE

**Hard stop:** do not present or hand off until Gates A–G in
`references/layout-hard-gates.md` pass. When Penpot boards exist, score the
**canvas PNG**. `hifi.html` is not that canvas. `audit_board` alone is not
done. Score each line 0-2 (0 = fails, 1 = acceptable, 2 = strong). Fix every 0,
then fix the cheapest 1s. Do one fix round, re-check once (PNG again), and stop;
open-ended polishing wastes the user's time. **You must look at the Penpot
pixels.** A board that stores type the canvas does not show is a fail.

| # | Check | Pass looks like |
|---|---|---|
| 0 | **Hard gates** | Gates A–G: no text-wall; Flex only if reflow real (not 0,0); design system + real fonts; PNG read (or export block reported); no orphan empty pages (`layout-hard-gates.md`). Any fail = score 0 and stop. |
| 1 | **Specificity** | Cover the product name: it still could not be any other product. Not in a calibration cluster (anti-slop.md). |
| 2 | **Mode fit** | Persuade: offer clear, action visible in its working form, proof shown. Operate: a regular user knows where everything is before noticing style. Read: comfortable column, clear wayfinding. Experience: the work leads. |
| 3 | **Hierarchy** | Squint test: primary, secondary and groups readable in order; one focal point per view. |
| 4 | **Layout and rhythm** | Grouping by proximity; tight inside groups, generous between; more space above headings than below; no monotone grid of identical cards. 1D regions are Flex; 2D regions are CSS Grid (`references/flex-grid.md`). Fit / Fill / Fix is explicit. Hi-fi CSS matches the spec. |
| 5 | **Typography** | Role scale with visible steps; weight and colour carry hierarchy too; body ≥16px, measure 45–75ch; display ≤ about 96px, tracking not tighter than -0.04em; balanced headings. |
| 6 | **Colour** | Strategy matches plan; every colour has a role; accent reserved for action/selection/state; secondary text on coloured grounds tinted from that hue, never grey. |
| 7 | **Contrast and access** | Body ≥4.5:1, large text and controls ≥3:1; colour never the only signal; targets ≥44×44px (40 minimum); visible focus. |
| 8 | **States** | Default, hover, focus, active, disabled, loading, error, empty, success where relevant; long text and empty data do not break layout. |
| 9 | **Animation spec** | One authored moment at most (none for routine Operate screens); spatial motion uses a `@motion-physics` spring preset; reduced-motion path exists. |
| 10 | **Copy** | Product's own words; actions say verb + object; errors say what failed and how to recover; no hype clichés; no invented claims. |
| 11 | **Anti-slop** | Zero items from the refuse list unless the brief explicitly asked for them. |
| 12 | **Penpot / hi-fi hygiene** | `penpot-demo.md` quotes layout, parentId, child x/y, and library token ids from a read-back. Broken Flex is not hi-fi. Absolute 8px escape is labelled honestly. Page ids exist; no empty shell pages. Dividers are per-side strokes (`references/strokes-and-tokens.md`), not 1px rectangles. |

Then present, briefly:

1. What you shipped as hi-fi (Penpot canvas with read-back), plus any low-fi sketches. HTML only if no Penpot boards were written.
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
- Penpot boards use `@heyeddi/penpot-mcp-server`
  (https://github.com/HeyEddi-com/penpot-mcp-server), a fork of
  `@zcubekr/penpot-mcp-server` with Flex/Grid and nesting. The unscoped npm
  package and the plugin MCP (https://help.penpot.app/mcp/) are not used.

NOTICE: This product includes material derived from Impeccable
(Copyright 2025 Paul Bakaus), licensed under the Apache License, Version 2.0
(http://www.apache.org/licenses/LICENSE-2.0). Portions derived from MIT-licensed
works retain their copyright notices: Copyright (c) 2026 Damola Akinleye;
Copyright (c) 2026 Leonxlnx. This adaptation was modified as described above.
