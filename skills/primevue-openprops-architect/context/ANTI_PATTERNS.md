
# Anti-patterns: PrimeVue + OpenProps

- NEVER use inline `style=""` attributes or hardcoded hex colors (`#fff`, `#333`).
- NEVER invent PrimeVue props: check component API before use.
- NEVER put body content as direct children of PrimeVue `Card`: use `<template #content>` or the card body is empty in the browser.
- NEVER duplicate Button/Input wrappers when a shared component exists.
- NEVER use Tailwind utility classes. NEVER add React or Bootstrap.
- NEVER add `open-props` on new work. Existing `open-props` stays; new surfaces use `--app-*`.
- NEVER add raw `<style>` blocks with magic numbers: use design tokens.
- NEVER import PrimeVue components globally when the project uses on-demand registration.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
