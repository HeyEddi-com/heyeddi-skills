---
name: aura-design-tokens
description: "Synchronizes PrimeVue Aura, Quasar, and custom CSS through CSS custom properties. Use for themes, color, surfaces, radii, and dark mode. No Tailwind utility classes and no raw hex in components."
version: 1.0.0
product-version: 3.8.0
author: HeyEddi-com
---

# Aura Design Tokens

Synchronizes color palettes, surface depths, and border radii across PrimeVue components, Quasar shells, and custom CSS. No Tailwind utility classes.

`@taste-penpot` may name a brand direction. Record the resulting roles here. Do not invent a second palette in a component.

## When the agent activates this skill

- Adding or changing color, surface, border, radius, or dark mode.
- Bridging PrimeVue Aura tokens (`--p-*`) to Quasar (`--q-*`) and app roles (`--app-*`).
- Replacing raw hex or inline color in Vue or CSS.

## Token bridge

Add this to the primary stylesheet (`src/assets/design-tokens.css`) and import it after the PrimeVue setup in `src/main.js`.

```css
:root {
  /* Surface hierarchy (Light mode default) */
  --app-bg: var(--p-surface-50, #f8fafc);
  --app-surface-card: var(--p-surface-0, #ffffff);
  --app-border: var(--p-content-border-color, #e2e8f0);
  --app-text-main: var(--p-text-color, #0f172a);
  --app-text-muted: var(--p-text-muted-color, #64748b);
  --app-spotlight: color-mix(in srgb, var(--p-primary-color, #0ea5e9) 14%, transparent);
  --app-glass: color-mix(in srgb, var(--app-surface-card) 72%, transparent);
  --app-glass-border: color-mix(in srgb, var(--app-text-main) 12%, transparent);
  --app-glass-rim: color-mix(in srgb, white 70%, transparent);

  /* Primary brand bridge (Synchronizes Quasar & PrimeVue) */
  --q-primary: var(--p-primary-color, #0ea5e9);
  --q-secondary: var(--p-surface-700, #334155);
}

.dark-mode {
  /* Surface hierarchy (Dark mode) */
  --app-bg: var(--p-surface-950, #090d16);
  --app-surface-card: var(--p-surface-900, #111827);
  --app-border: var(--p-surface-800, #1f2937);
  --app-text-main: var(--p-surface-50, #f9fafb);
  --app-text-muted: var(--p-surface-400, #9ca3af);
  --app-spotlight: color-mix(in srgb, var(--p-primary-color, #38bdf8) 18%, transparent);
  --app-glass: color-mix(in srgb, var(--app-surface-card) 55%, transparent);
  --app-glass-border: color-mix(in srgb, white 16%, transparent);
  --app-glass-rim: color-mix(in srgb, white 28%, transparent);

  /* Quasar dark surface sync */
  --q-dark: var(--app-bg);
  --q-dark-page: var(--app-bg);
}

/* Base resets relying on variables */
body {
  background-color: var(--app-bg);
  color: var(--app-text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
  margin: 0;
  -webkit-font-smoothing: antialiased;
}
```

Fallbacks exist only inside this file, so a missing Aura variable still paints. Components reference `var(--app-bg)`, `var(--app-surface-card)`, `var(--app-border)`, `var(--app-text-main)`, `var(--app-text-muted)`, and, for depth, `var(--app-spotlight)`, `var(--app-glass)`, `var(--app-glass-border)`, and `var(--app-glass-rim)`.

## Instructions

1. Import `design-tokens.css` after Quasar and PrimeVue so `--p-*` exists before the bridge reads it.
2. Toggle dark mode by adding or removing `.dark-mode` on an ancestor. That matches PrimeVue `darkModeSelector: '.dark-mode'`.
3. Do not introduce Tailwind, OpenProps, or a parallel hex scale. If `open-props` is already a dependency, leave it; new surfaces still use `--app-*`.
4. Radius and shadow for custom CSS should reference Aura when present (`var(--p-border-radius-md)`, `var(--p-content-border-radius)`) rather than a new numeric scale in each component.
5. A taste-penpot display face may set `--app-font-display` when the brief names one. Body text stays on the stack above unless the brief pins a different UI family.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill aura-design-tokens --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
