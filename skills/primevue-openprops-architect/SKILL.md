---
name: primevue-openprops-architect
description: "Compatibility name for Vue UI checks. Follow @vue-design-system (Quasar, PrimeVue Aura, spring motion, CSS tokens). Do not add OpenProps, Tailwind, or React. Runs vue-tsc and stylelint when available."
version: 1.0.0
product-version: 3.8.3
author: HeyEddi-com
paths:
  - "**/*.vue"
  - "**/*.css"
  - "**/*.scss"
---

# PrimeVue + project tokens (compatibility)

This name remains so older routes still resolve. The design system is `@vue-design-system`.

- Shell, drawers, and native targets: `@quasar-foundation`
- Tables, forms, menus, badges: `@primevue-aura`
- Motion: `@motion-physics`
- Color: `@aura-design-tokens`
- Terminal: `@cli-interface-design`

Do not add OpenProps, Tailwind, React, or Bootstrap. If the project already depends on `open-props`, leave that dependency and still use `--app-*` for new surfaces.

When chained from parent skills, **`validate_vue.py` runs in a `shell` subagent** by default. See `reference/subagents.md`.

## When to use

- An older prompt names `@primevue-openprops-architect`
- Editing `.vue` or CSS after `@vue-design-system` has chosen the primitives

## Instructions

1. Read `@vue-design-system` and the child skill for the surface. This file does not choose components.
2. Read `context/VOCABULARY.md` and `context/ANTI_PATTERNS.md` before writing UI code.
3. After edits, run `python scripts/validate_vue.py --project-root <root>`.
4. Fix all reported issues before finishing.

## Scripts

- `validate_vue.py`: runs `vue-tsc --noEmit` and stylelint if installed
