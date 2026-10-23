
# Vocabulary: PrimeVue + project tokens

Compatibility skill. Component and color decisions live in `@vue-design-system`.

- **Token source:** `src/assets/design-tokens.css` via `@aura-design-tokens` (`--app-*`, `--p-*`, `--q-*`).
- **Semantic vars:** `var(--app-bg)`, `var(--app-surface-card)`, `var(--app-border)`, `var(--app-text-main)`, `var(--app-text-muted)`.
- **OpenProps (when present):** prefer aliases in `:root` over raw OpenProps names in components.
- PrimeVue components in use: Button, DataTable, Dialog, InputText, Card, Panel, Toast.
- **Card slots:** `#title`, `#subtitle`, `#content` (required for body), `#footer`: never rely on default slot.
- Vue 3 `<script setup lang="ts">` with typed props and `defineEmits`.
- Import shared wrappers from `@/components/ui/` before creating new primitives.
- Wire PrimeVue Aura `primary` to project `--brand` / `design.md` `{colors.primary}`: never leave default green on shipped UI.
- **PrimeVue v4:** map brand with `definePreset(Aura, { semantic: { primary: { 500: "{indigo.500}", … } } })` in `main.ts`: `--p-primary-color` in CSS alone does not change Aura buttons.
- Spacing: project token scale (`var(--size-*)`): OpenProps fluid sizes when project uses OpenProps; else follow `design.md` spacing table.
