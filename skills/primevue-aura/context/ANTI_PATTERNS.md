# Anti-patterns

- Tailwind, unstyled PrimeVue without Aura, or `cssLayer: true` (Quasar resets then win).
- PrimeVue `Menubar` or custom divs as the application frame. The frame is Quasar.
- Quasar `q-table` for an enterprise grid this skill already covers.
- Importing `primevue/resources/themes/*` (legacy themes). Aura is the preset.
- Card body content placed outside `<template #content>`.
