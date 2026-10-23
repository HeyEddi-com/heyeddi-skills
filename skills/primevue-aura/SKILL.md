---
name: primevue-aura
description: "PrimeVue with the Aura preset for dense Vue 3 data grids, filters, complex form controls, and overlays. No Tailwind. Use for DataTable, TreeSelect, menus, badges, and the Quasar plus PrimeVue bootstrap order."
version: 1.0.0
product-version: 3.6.0
author: HeyEddi-com
---

# PrimeVue Aura

High-density data, advanced filtering, complex form controls, and contextual menus styled with PrimeVue's Aura preset. No Tailwind.

Application frames, drawers, and native shells belong to `@quasar-foundation`. Token names belong to `@aura-design-tokens`. Motion belongs to `@motion-physics`.

## When the agent activates this skill

- Building data grids, sorting, row expansion, virtual scrolling, and column filters.
- Multi-tiered menus, tree-select dropdowns, cascade selects, and date or time range pickers.
- In-app modals, floating tooltips, and popovers that require refined styling.
- Scaffolding `vite.config.js` and `src/main.js` for a Quasar plus PrimeVue app.

## Installation

```bash
npm install primevue @primevue/themes primeicons
```

## Hybrid harmony setup

Quasar's CSS resets load first. PrimeVue Aura loads second so its components keep their styling.

```js
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { quasar, transformAssetUrls } from '@quasar/vite-plugin';

export default defineConfig({
  plugins: [
    vue({ template: { transformAssetUrls } }),
    quasar({ sassVariables: 'src/quasar-variables.sass' })
  ]
});
```

```js
// src/main.js
import { createApp } from 'vue';
import App from "@/App.vue";

// 1. Quasar core base & icon assets (Loads FIRST to apply foundational resets)
import { Quasar, Dialog, Notify } from 'quasar';
import '@quasar/extras/material-icons/material-icons.css';
import 'quasar/src/css/index.sass';

// 2. PrimeVue & Aura Preset (Loads SECOND to take precedence on components)
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import 'primeicons/primeicons.css';

// 3. Motion Engine
import { MotionPlugin } from '@vueuse/motion';

const app = createApp(App);

app.use(Quasar, { plugins: { Dialog, Notify } });

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark-mode',
      cssLayer: false
    }
  }
});

app.use(MotionPlugin);
app.mount('#app');
```

`cssLayer: false` is required so Aura wins over Quasar resets on PrimeVue components. Dark mode uses the `.dark-mode` class from `@aura-design-tokens`.

## Component responsibility

Use PrimeVue for these primitives:

| Component category | PrimeVue primitive | Rationale |
|--------------------|--------------------|-----------|
| Data presentation | `<DataTable>`, `<Column>`, `<TreeTable>` | High-density layout, virtual scroll, multi-sort, Excel-like filtering. |
| Complex pickers | `<MultiSelect>`, `<TreeSelect>`, `<CascadeSelect>` | Chip badges, grouped hierarchies, inline search filtering. |
| Context controls | `<TieredMenu>`, `<ContextMenu>`, `<Breadcrumb>` | Precision desktop menus with sub-menu flyouts. |
| Status and metric badges | `<Tag>`, `<Badge>`, `<ProgressBar>` | Consistent typography and semantic tone indicators. |

Also use PrimeVue for form fields inside data-dense screens (`InputText`, `Select`, `DatePicker`, `Password`) when the control is not a Quasar shell primitive. Do not restyle them with Tailwind. Do not wrap them in Quasar `q-input` when PrimeVue already owns the field.

Card body content goes in `<template #content>`.

## Instructions

1. Confirm the surface is data, a complex control, or an overlay. Shell chrome stays Quasar.
2. Import components from `primevue/<name>` (PascalCase path, unstyled entry is not used; Aura is the preset).
3. When the PrimeVue MCP server is connected, confirm props there before inventing them.
4. After the view exists, load `@motion-physics` for row and dialog entry. Do not add PrimeVue's default CSS transitions for spatial movement.
5. Surfaces and text use `var(--app-*)` from `@aura-design-tokens`, which read `--p-*`.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill primevue-aura --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
