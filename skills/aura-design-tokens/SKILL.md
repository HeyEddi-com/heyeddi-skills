---
name: aura-design-tokens
description: "Synchronizes PrimeVue Aura, Quasar, and custom CSS through CSS custom properties. Use for themes, color, surfaces, radii, and dark mode. No Tailwind utility classes and no raw hex in components."
version: 1.0.1
product-version: 3.11.0
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

Add this to the primary stylesheet (`src/styles/tokens.css`) and import it after the PrimeVue setup in `src/main.ts`. The `@project-engineering` Vue scaffold already ships it, plus `--surface-*`, `--text-*`, and `--size-*` aliases.

```css
/* Aura design tokens: PrimeVue (--p-*) bridged to app roles (--app-*) and Quasar (--q-*) */
:root {
  color-scheme: light;

  /* Surface hierarchy. light-dark() follows color-scheme, which .dark-mode flips. */
  --app-bg: light-dark(var(--p-surface-50, #f8fafc), var(--p-surface-950, #090d16));
  --app-surface-card: light-dark(var(--p-surface-0, #ffffff), var(--p-surface-900, #111827));
  --app-border: light-dark(var(--p-surface-200, #e2e8f0), var(--p-surface-800, #1f2937));
  --app-text-main: light-dark(var(--p-surface-900, #0f172a), var(--p-surface-50, #f9fafb));
  --app-text-muted: light-dark(var(--p-surface-500, #64748b), var(--p-surface-400, #9ca3af));
  --app-spotlight: color-mix(in srgb, var(--p-primary-color, #0ea5e9) 14%, transparent);
  --app-glass: color-mix(in srgb, var(--app-surface-card) 72%, transparent);
  --app-glass-border: color-mix(in srgb, var(--app-text-main) 12%, transparent);
  --app-glass-rim: light-dark(
    color-mix(in srgb, white 70%, transparent),
    color-mix(in srgb, white 28%, transparent)
  );

  /* Brand bridge (synchronizes Quasar and PrimeVue) */
  --brand: var(--p-primary-color, #0ea5e9);
  --brand-subtle: color-mix(in srgb, var(--brand) 14%, var(--app-surface-card));
  --q-primary: var(--brand);
  --q-secondary: var(--p-surface-700, #334155);
}

.dark-mode {
  color-scheme: dark;

  --q-dark: var(--app-bg);
  --q-dark-page: var(--app-bg);
}

body {
  margin: 0;
  background-color: var(--app-bg);
  color: var(--app-text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
  -webkit-font-smoothing: antialiased;
}
```

Fallbacks exist only inside this file, so a missing Aura variable still paints. Components reference `var(--app-bg)`, `var(--app-surface-card)`, `var(--app-border)`, `var(--app-text-main)`, `var(--app-text-muted)`, and, for depth, `var(--app-spotlight)`, `var(--app-glass)`, `var(--app-glass-border)`, and `var(--app-glass-rim)`.

## Instructions

1. Import `tokens.css` after Quasar and PrimeVue so `--p-*` exists before the bridge reads it.
2. Toggle dark mode by adding or removing `.dark-mode` on an ancestor. That matches PrimeVue `darkModeSelector: '.dark-mode'`.
3. Do not introduce Tailwind, OpenProps, or a parallel hex scale. If `open-props` is already a dependency, leave it; new surfaces still use `--app-*`.
4. Radius and shadow for custom CSS should reference Aura when present (`var(--p-border-radius-md)`, `var(--p-content-border-radius)`) rather than a new numeric scale in each component.
5. A taste-penpot display face may set `--app-font-display` when the brief names one. Body text stays on the stack above unless the brief pins a different UI family.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill aura-design-tokens --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
