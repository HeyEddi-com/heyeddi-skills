# Theme coherence: light / dark / PrimeVue

**Problem:** Custom shell uses `tokens.css` grays while PrimeVue Aura follows `prefers-color-scheme` independently → dark Cards on a light page, unreadable labels, black search inputs.

## Rule

**One scheme per layer.** Shell, main content, and PrimeVue primitives must read the **same semantic tokens** (`--surface-*`, `--text-*`) in both light and dark.

## Implementation checklist

1. **`tokens.css`**: use `light-dark()` (or `@media (prefers-color-scheme: dark)`) for `--surface-0`…`--text-2`, `--brand`, `--brand-subtle`. Set `color-scheme: light dark` on `:root`.
2. **`main.ts`**: Aura preset with `primary` wired to `{brand}`; `darkModeSelector: 'system'` (default) **only after** tokens flip together.
3. **PrimeVue overrides**: Card, InputText, Button surfaces in views or `src/styles/primevue-surfaces.css`:
   ```css
   .settings__card :deep(.p-card) {
     background: var(--surface-2);
     color: var(--text-1);
   }
   .settings__card :deep(.p-inputtext) {
     background: var(--surface-0);
     color: var(--text-1);
     border-color: var(--surface-3);
   }
   ```
4. **Labels**: never hardcode `#333` / `#666`; use `var(--text-2)` on the same surface as the control.
5. **Verify**: `verify_theme.py --check` before handoff done; visual pass at **light and dark** (toggle OS or `prefers-color-scheme` in Playwright).

## mockup-brief.md

Add **Theme notes** subsection:

- Surfaces: which token for page bg, card bg, input bg
- Confirm PrimeVue `:deep` overrides listed in Implementation spec

## Anti-patterns

- Light sidebar + dark PrimeVue cards (unmapped Aura dark palette)
- Subtitle/label text `--text-2` on a dark card without checking contrast in dark mode
- Search input defaulting to Aura filled surface while top bar is `--surface-0`
