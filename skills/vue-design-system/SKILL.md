---
name: vue-design-system
description: "Routes Vue 3 UI and CLI work to Quasar shells, PrimeVue Aura, spring motion, CSS tokens, visual verification, or terminal UI. No React, no Tailwind, no Bootstrap. GUI work ends in a Playwright MCP screenshot of the Vite server. CLI work ends by running the script and reading stdout."
version: 1.0.0
product-version: 3.6.0
author: HeyEddi-com
---

# Vue Design System

**Target stack:** Vue 3 (Composition API, `<script setup>`) · no React · no Tailwind · no Bootstrap · web, desktop, mobile, and CLI.

This skill is the Vue and CLI build router. It does not invent a second look. `@taste-penpot` is the general design skill and owns aesthetic direction. `@heyeddi-design` records it in `.heyeddi/design.md`. This skill decides which package builds the surface, then you load that skill and follow it.

## When to use

Load this skill before writing interface code when the prompt is a screen, shell, dashboard, form, menu, theme, motion, or terminal UI.

| Surface | Primary skill | Supporting skill |
|---------|---------------|------------------|
| App framing, drawers, tabs, mobile or desktop shell | `@quasar-foundation` | `@aura-design-tokens` |
| Tables, trees, pickers, SaaS forms, overlays | `@primevue-aura` | `@motion-physics` |
| Micro-interactions and transitions | `@motion-physics` | `@aura-design-tokens` |
| Terminal, CLI, dev tools | `@cli-interface-design` | Terminal execution (run the script, read ANSI stdout) |
| Theming and color | `@aura-design-tokens` | `@quasar-foundation` |
| Visual QA of the live page | `@visual-verification` | Playwright MCP |
| Designer boards, demo exports | `@taste-penpot` | `@aura-design-tokens` |

After either GUI branch, load `@motion-physics`, then `@visual-verification`.

## Routing

```
Agent prompt
    │
    ├─ Visual UI (GUI)
    │     ├─ App shell / native layout  → @quasar-foundation
    │     │     navigation, drawers, tabs, mobile/desktop shell
    │     └─ Data-dense / form UI       → @primevue-aura
    │           tables, trees, pickers, SaaS dashboards
    │     then @motion-physics
    │     then @visual-verification
    │           Vite HMR, Playwright MCP screenshot, fix what you see
    │
    └─ Terminal / CLI                   → @cli-interface-design
          @clack/prompts, consola, picocolors
          then run the script and read ANSI stdout
```

Packages:

| Scope | Primary | Supporting | Packages |
|-------|---------|------------|----------|
| App framing and native packaging | `quasar-foundation` | `aura-design-tokens` | `quasar`, `@quasar/extras` |
| Complex tables, forms, overlays | `primevue-aura` | `motion-physics` | `primevue`, `@primevue/themes` |
| Micro-interactions | `motion-physics` | `aura-design-tokens` | `@vueuse/motion` |
| Visual QA and screenshot inspection | `visual-verification` | Playwright MCP | `@playwright/mcp` |
| Terminal / CLI | `cli-interface-design` | Terminal execution | `@clack/prompts`, `consola`, `picocolors` |
| Theming | `aura-design-tokens` | `quasar-foundation` | CSS custom properties |

## Instructions

1. Classify the prompt: visual UI or terminal. A GUI screen that also has a CLI is two skills, in that order.
2. Read the primary skill's `SKILL.md` and its component table before choosing a component.
3. Read the supporting skill. GUI work also reads `@motion-physics`, `@aura-design-tokens`, and then `@visual-verification`.
4. App bootstrap (Vite plugin order, `main.js` load order) lives in `@primevue-aura`. Quasar CSS loads first. PrimeVue Aura loads second. Motion loads third.
5. Map colors through `@aura-design-tokens`. Do not write raw hex in components.
6. Designer visuals and Penpot demos: `@taste-penpot` using the **Penpot API MCP** (`penpot-api`). Do not use the plugin MCP (`@penpot/mcp`, `execute_code`, a connected browser plugin).

## Agent directives

### Core architecture

- Framework: Vue 3 (Composition API with `<script setup>`).
- Prohibited libraries: do not introduce or suggest React, Tailwind CSS, or Bootstrap.
- Layout vs data:
  - Quasar (`<q-layout>`, `<q-drawer>`, `<q-header>`) for application framing and cross-platform native builds.
  - PrimeVue (Aura preset) for data tables, form fields, badges, and contextual menus.
  - `@vueuse/motion` for animations.

### Visual self-correction (GUI)

When generating or heavily refactoring a visual component:

1. Verify the local dev server is running (`http://localhost:5173`).
2. Use the Playwright MCP (`browser_navigate`, `browser_resize`, `browser_take_screenshot`) to capture the route.
3. Inspect the image for visual overlap, broken flex wrap, misaligned padding, or unstyled raw fonts.
4. Correct those defects before declaring the task complete.

Desktop is 1440×900. Mobile is 390×844. Details are in `@visual-verification`.

### Terminal and CLI

- When asked to build CLI utilities or terminal views, do not write browser HTML/CSS.
- Use `@clack/prompts` for interactive question trees and inputs.
- Use `consola` for badges, status reports, and structured log displays.
- Keep output formatting within 16-color ANSI palettes using `picocolors`.
- Run the script in the terminal and inspect stdout to verify alignment. Do not screenshot a CLI.

### Styling and tokens

- Do not output raw hex colors (`#1a2b3c`) or inline styling coordinates in components.
- Reference CSS custom properties:
  - Surface layers: `var(--app-bg)`, `var(--app-surface-card)`
  - Borders: `1px solid var(--app-border)`
  - Text tones: `var(--app-text-main)`, `var(--app-text-muted)`

### Motion

- All animations must use spring physics:
  - Interactive elements: `{ type: 'spring', stiffness: 350, damping: 25 }`
  - Dialogs and overlays: `{ type: 'spring', stiffness: 280, damping: 22 }`
- Avoid linear transitions, unmotivated continuous bounces, and stagger delays over 40ms.
- Prefer the named presets in `@motion-physics` when they match the moment.

## MCP servers

PrimeVue and Quasar run offline over stdio. Penpot designer access uses the API MCP (HTTP), not `@penpot/mcp`.

```json
{
  "mcpServers": {
    "primevue": {
      "command": "npx",
      "args": ["-y", "@primevue/mcp"]
    },
    "quasar": {
      "command": "npx",
      "args": ["-y", "--fetch-retries=0", "@quasar/mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "penpot-api": {
      "type": "http",
      "url": "http://127.0.0.1:3051/mcp"
    }
  }
}
```

Start Penpot API MCP only when a designer visual or demo export is in scope. See `@taste-penpot` → `references/penpot-mcp.md`. Never print `PENPOT_ACCESS_TOKEN`.

`@primevue-openprops-architect` is a compatibility name. If it loads, follow this skill. Do not add OpenProps unless the project already depends on `open-props`.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill vue-design-system --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
