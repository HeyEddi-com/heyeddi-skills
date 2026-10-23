# Anti-patterns

- Hex literals in `.vue` or in CSS outside `design-tokens.css` fallbacks.
- Tailwind `@apply` or utility classes for color, spacing, or radius.
- A second dark class such as `.dark` or `body--dark` that PrimeVue is not configured to read.
- Redefining `--app-bg: var(--app-bg)`.
- OpenProps `--surface-1` on new work when this bridge exists.
