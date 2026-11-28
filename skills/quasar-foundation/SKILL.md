---
name: quasar-foundation
description: "Quasar application frames, drawers, mobile gestures, and Capacitor or Tauri shells for Vue 3. Use for headers, footers, navigation, pull-to-refresh, bottom sheets, and Capacitor or Tauri packaging. Not for data tables or CLI."
version: 1.0.1
product-version: 3.9.0
author: HeyEddi-com
---

# Quasar Foundation

Responsive application framing, mobile touch gestures, drawer interactions, and platform wrappers for Capacitor (mobile) and Tauri or Electron (desktop).

Load `@vue-design-system` first if this skill was opened alone. Data grids, complex pickers, and menus belong to `@primevue-aura`. Colors belong to `@aura-design-tokens`. Motion belongs to `@motion-physics`.

## When the agent activates this skill

- Defining application scaffolding: headers, footers, responsive side drawers, and page containers.
- Touch-first mobile layouts requiring pull-to-refresh, swipeable tabs, or bottom sheets.
- Packaging for mobile (Capacitor) or desktop (Tauri). See Native targets below.

## Installation

```bash
npm install quasar @quasar/extras
npm install -D @quasar/vite-plugin sass-embedded
```

Vite and `main.ts` load order is the hybrid setup in `@primevue-aura`. Quasar core CSS loads **first**. Do not let Quasar components replace PrimeVue data components.

## Native targets

This setup uses the Quasar Vite plugin, not the Quasar CLI, so build with Vite and package with the platform's own CLI. Install what the target needs:

```bash
# Mobile: set webDir to "dist" in capacitor.config
npm install @capacitor/core && npm install -D @capacitor/cli
npx cap init && npm run build && npx cap sync
# Desktop
npm install -D @tauri-apps/cli
npx tauri init && npx tauri build
```

## Component responsibility

Use Quasar only for these primitives:

| Component category | Quasar primitive | Rationale |
|--------------------|------------------|-----------|
| Layout framing | `<q-layout>`, `<q-page-container>`, `<q-page>` | Handles viewport calculation and native safe areas automatically. |
| Side navigation | `<q-drawer>` | Built-in touch swipe, responsive breakpoints, mini-mode toggles. |
| Application bars | `<q-header>`, `<q-footer>`, `<q-toolbar>` | Sticky positioning and elevation handling without manual CSS. |
| Mobile actions | `BottomSheet` plugin (`$q.bottomSheet()`), `<q-fab>`, `<q-pull-to-refresh>` | Hardware-optimized touch listeners. |

## Instructions

1. Confirm the surface is a shell, drawer, bar, or mobile gesture. If it is a table, tree, select, or menu, stop and load `@primevue-aura`.
2. Use `<script setup>` and the primitives above. Do not recreate the shell with raw `div` sticky positioning.
3. Brand color comes from `--q-primary`, which `@aura-design-tokens` bridges to PrimeVue. Do not set a second Quasar palette in hex.
4. After the shell exists, load `@motion-physics` for entry and press feedback.
5. When the Quasar MCP server is connected, confirm component props there before inventing them. Config is in `@vue-design-system`.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill quasar-foundation --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
