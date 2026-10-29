# Handoff to code: designer then implementer

One agent often plays both roles, but **do not blend them in one pass**. The brief failed when it was designer prose without measurable layout: the implementer guessed spacing and shipped a weak sidebar.

## Two roles

| Role | Output | Does **not** |
|------|--------|----------------|
| **Designer** (interpret) | `mockup-brief.md` with region map + **Implementation spec** | Write Vue/CSS |
| **Implementer** (build) | `AppShell`, route views, tokens | Reinterpret mockups from scratch |

Switch hats explicitly in chat: *"Designer pass complete: implementation spec below. Starting implementer pass."*

## Pipeline (mandatory order)

```
load_handoff
  → INTERPRET (designer)     mockup-brief.md + Implementation spec
  → describe_handoff --sync-design
  → BUILD SHELL (implementer) AppShell, AppSidebar, AppTopBar: tokens updated
  → verify_handoff --phase shell
  → BUILD ROUTE (implementer) SettingsView / route content
  → verify_handoff --phase full
  → Decision log
```

**Do not** start `AppShell.vue` until `mockup-brief.md` includes **## Implementation spec**.

## Designer pass: what to measure from PNGs

Designer-eye prose is not enough. From mockups, extract **numbers and CSS intent**:

| Measure from mockup | Write in Implementation spec |
|---------------------|------------------------------|
| Sidebar width | `--sidebar-width: 15.5rem` (248px) |
| Top bar height | `--topbar-height: 4rem` (64px) |
| Content column max-width | `--content-max-width: 45rem` (~720px) |
| Card internal padding | PrimeVue override: `padding: var(--size-6)` on `.p-card-body` |
| Gap between cards | `gap: var(--size-6)` on stack |
| Nav row height | `min-height: 2.75rem` (44px); pill horizontal inset `padding-inline: var(--size-3)` |
| Sidebar structure | `flex` column; `nav { flex: 1 }`; `user { margin-top: auto }` |
| Active nav | `background: var(--brand-subtle)`; `color: var(--brand)`: **not** gray `--surface-2` |
| User chip | bordered card, avatar circle, pinned bottom |

Compare **reference PNG** side-by-side while writing spec: if you cannot cite a token for a gap, you have not finished the designer pass.

When `penpot-demo.md` or the Penpot Inspect panel names an engine, the Implementation spec uses that CSS (`display: flex` or `display: grid`, `gap`, `grid-template-columns`, `flex-grow`). Rules: `../taste-penpot/references/flex-grid.md`. Map Fit Content to `max-content`, Fill to `flex-grow: 1` or `1fr`, and Fix to a tokenized px size. The app frame stays Quasar: `q-drawer` width is the sidebar track, `q-header` height is the header track. Nested page regions use the named engine. A 375 layout collapses the sidebar track into the drawer.

## Implementation spec (required section in brief)

Add after **Spacing & alignment**:

```markdown
## Implementation spec

Measurable layout for the frontend dev: implement exactly; adjust tokens.css first.

| Component / region | Token or CSS rule | File(s) |
|--------------------|-------------------|---------|
| Sidebar width | `--sidebar-width: 15.5rem` | `tokens.css`, `AppSidebar.vue` |
| Sidebar column | `display:flex; flex-direction:column; min-height:100%` | `AppSidebar.vue` |
| Nav scroll area | `flex: 1` on nav wrapper | `AppSidebar.vue` |
| User chip pin | `margin-top: auto` on user block | `AppSidebar.vue` |
| Nav active pill | `background: var(--brand-subtle); border-radius: var(--radius-2); padding: var(--size-2) var(--size-3)` | `AppSidebar.vue` |
| Top bar | `height: var(--topbar-height)` (4rem) | `tokens.css`, `AppTopBar.vue` |
| Content padding | `padding: var(--size-6) var(--size-5)` on route root | `SettingsView.vue` |
| Card stack gap | `gap: var(--size-6)` | `SettingsView.vue` |
| Card body | `:deep(.p-card-body) { padding: var(--size-6) }` | `SettingsView.vue` |
| Save CTA | below cards; desktop `justify-content: flex-end`; `margin-top: var(--size-6)` | `SettingsView.vue` |
```

## Implementer pass: rules

1. **Tokens first**: add/update `tokens.css` from Implementation spec before layout components.
2. **Shell before route**: `AppShell` → `AppSidebar` → `AppTopBar`; run `verify_handoff.py --phase shell`.
3. **Match spec, not memory**: open `mockup-brief.md` Implementation spec table while coding.
4. **PrimeVue Card slots**: all body UI inside `<template #content>`; see `primevue-card-slots.md`.
5. **PrimeVue gaps**: default Card/Input padding is often too tight; override in scoped CSS when spec says so.
6. **Run verify**: `verify_handoff.py --route <route> --phase full` before calling done.

## Common failures (08-33-59Z eval)

| Symptom | Cause | Spec fix |
|---------|-------|----------|
| Flat, full-width nav highlight | Gray or full-bleed active state | Pill with horizontal inset + `brand-subtle` |
| User chip floats mid-sidebar | Missing `margin-top: auto` | Implementation spec row |
| Cramped cards | PrimeVue defaults | `:deep(.p-card-body)` padding in spec |
| Empty cards (title only, no fields) | Body outside `#content` slot | Wrap fields in `<template #content>`: `primevue-card-slots.md` |
| Sidebar feels narrow/wrong | `15rem` vs 248px | `--sidebar-width: 15.5rem` in tokens |
| Designer brief ignored | No spec table; implementer rushed | Stop between passes; run `verify_handoff` |
| `[Vue Router warn]: No match for "/"` in unit tests | `createWebHistory()` + single route | `createMemoryHistory(initialPath)` + stub `/`, `/dashboard`, `/settings` |

## Verification

```bash
python scripts/verify_handoff.py --route /settings --project-root .
python scripts/verify_handoff.py --route /settings --phase shell   # after shell only
python scripts/verify_handoff.py --route /settings --check         # exit 1 if gaps
```

`verify_handoff` reads **Implementation spec** from the brief and checks tokens + Vue sources for required patterns.
