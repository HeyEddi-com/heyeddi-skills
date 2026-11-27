---
version: alpha
name: Project-name-design-system
description: >-
  One paragraph in designer voice: mood, density, register (product app vs marketing),
  how token surfaces and PrimeVue components should feel together. Name the north star
  and the one thing agents must not get wrong.

colors:
  primary: "var(--brand)"
  on-primary: "var(--surface-1)"
  ink: "var(--text-1)"
  ink-mute: "var(--text-2)"
  ink-faint: "var(--text-3)"
  canvas: "var(--surface-1)"
  canvas-soft: "var(--surface-2)"
  hairline: "var(--border-1)"
  danger: "var(--red-6)"
  success: "var(--green-6)"

typography:
  display-lg:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  heading-md:
    fontFamily: "system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  body-md:
    fontFamily: "system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  body-strong:
    fontFamily: "system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.5
    letterSpacing: "0"
  button-md:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0"
  caption:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0"

rounded:
  xs: "var(--radius-1)"
  sm: "var(--radius-2)"
  md: "var(--radius-3)"
  lg: "var(--radius-4)"
  full: "9999px"

spacing:
  xs: "var(--size-2)"
  sm: "var(--size-3)"
  md: "var(--size-4)"
  lg: "var(--size-5)"
  xl: "var(--size-6)"
  xxl: "var(--size-7)"

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "var(--size-3) var(--size-5)"
  button-primary-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "var(--size-3) var(--size-5)"
  button-secondary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "var(--size-3) var(--size-5)"
  text-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "var(--size-3) var(--size-4)"
  card-section:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "var(--size-5)"
---

## Overview

_(Open with how the app should **feel**: density, register, primary surfaces. Reference tokens inline like `{colors.canvas}` and `{typography.display-lg}`.)_

**Key Characteristics:**

- …
- …
- …

## Foundations (always on)

_Non-negotiable HeyEddi defaults: see `heyeddi-design/reference/foundations.md`. Summarize here; do not delete this section._

### Responsive

Mobile-first; audit at **375 / 768 / 1024 / 1440**. Touch targets ≥ 44px. Stack forms and primary CTAs below 768px.

### Color scheme

**System default:** `prefers-color-scheme` via `light-dark()` in `tokens.css` and `{colors.canvas}` / dark equivalents. User setting: `system` | `light` | `dark` (default **system**). WCAG 2.2 AA in both schemes.

### Internationalization

| Code | Language | Status |
|------|----------|--------|
| `en` | English | shipped (fallback) |
| `es` | Spanish | shipped |

Detect `navigator.language` on first visit; user picker overrides. `vue-i18n`; `html lang` synced. Expandable: add rows when scoping new locales.

### Accessibility

Keyboard + `:focus-visible`; skip link; semantic landmarks; form labels; `prefers-reduced-motion`; no color-only state. PrimeVue a11y preserved.

### Reading modes

| Mode | Trigger | Typography |
|------|---------|------------|
| Default |: | `{typography.body-md}` |
| Dyslexia-friendly | Settings toggle → `data-reading-mode="dyslexia"` | Atkinson Hyperlegible or OpenDyslexic; line-height 1.75; wider letter/word spacing; max-width 65ch |

### UI states

Loading, empty, error, and success patterns required on data views and forms.

## Colors

> **Source:** scan from code, seed interview, or design interview: **not** mockup PNG colors (handoff mockups are layout-only).

### Token source

Document once per project: **Aura bridge** (HeyEddi scaffold: `tokens.css`) | **custom** (`:root` vars only) | **other** (document waiver). See `heyeddi-design/reference/token-strategy.md`.

### Brand & Accent

- **Primary** (`{colors.primary}`): …
- **On primary** (`{colors.on-primary}`): …

### Surface

- **Canvas** (`{colors.canvas}`): default page background.
- **Canvas soft** (`{colors.canvas-soft}`): cards, raised panels.
- **Hairline** (`{colors.hairline}`): 1px borders, dividers.

### Text

- **Ink** (`{colors.ink}`): default body and headings.
- **Ink mute** (`{colors.ink-mute}`): secondary labels, hints.
- **Ink faint** (`{colors.ink-faint}`): placeholders, disabled.

## Typography

### Font Family

_(System stack or project fonts. Note substitutes if brand fonts are unavailable.)_

### Hierarchy

| Token | Size | Weight | Line height | Use |
|-------|------|--------|-------------|-----|
| `{typography.display-lg}` | … | … | … | Page title |
| `{typography.heading-md}` | … | … | … | Section title |
| `{typography.body-md}` | … | … | … | Default UI body |
| `{typography.button-md}` | … | … | … | Button labels |
| `{typography.caption}` | … | … | … | Helper text |

### Principles

- …

## Layout

### Spacing system

- **Base unit:** 8px via `{spacing.*}`.
- **Section padding:** …
- **Form field gap:** …

### Grid & container

- App shell: _(sidebar / top nav / hybrid)_.
- Content max-width: …
- Breakpoints: mobile-first; stack below 768px unless noted.

### Whitespace philosophy

_(One short paragraph: comfortable enterprise vs dense dashboard.)_

## Elevation & Depth

| Level | Treatment | Use |
|-------|-----------|-----|
| 0 | Flat `{colors.canvas}` | Default surface |
| 1 | `var(--shadow-2)` or 1px `{colors.hairline}` | Cards |
| 2 | `var(--shadow-4)` | Modals, popovers |

## Shapes

| Token | Value | Use |
|-------|-------|-----|
| `{rounded.sm}` | … | Inputs, buttons |
| `{rounded.md}` | … | Cards |
| `{rounded.lg}` | … | Modals |

## Components

Map **frontmatter component tokens** to **PrimeVue** primitives. Name variants (`button-primary`, `button-primary-hover`) like the [Superhuman example](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/superhuman/DESIGN.md).

### Buttons

**`button-primary`**: …

- PrimeVue: `Button` severity `primary`, size `normal`.
- Background `{colors.primary}`, type `{typography.button-md}`, rounded `{rounded.sm}`.

**`button-secondary`**: …

### Inputs & forms

**`text-input`**: …

- PrimeVue: `InputText`, `Password`, `InputMask` as needed.
- Never native unstyled `<input>` on production routes.

### Cards & sections

**`card-section`**: …

- PrimeVue: `Card` with title slot + content.

### Navigation

_(App shell, tabs, breadcrumbs: PrimeVue component names.)_

## Do's and Don'ts

### Do

- Use semantic `var(--*)` from project `tokens.css` in Vue/CSS; reference tokens from frontmatter in prose. Existing `open-props` projects keep their aliases.
- One primary action per view band when possible.
- Append per-feature rationale to **Decision log** after craft, polish, or handoff.

### Don't

- Raw hex in components unless listed here as an exception.
- Duplicate PrimeVue wrappers without updating this file.
- Dump code in Decision log: write designer talk.

## Responsive Behavior

### Breakpoints

| Name | Width | Key changes |
|------|-------|-------------|
| Mobile | < 768px | Stack forms; full-width CTAs |
| Tablet | 768-1023px | … |
| Desktop | ≥ 1024px | … |

### Touch targets

- Interactive controls ≥ 44×44px on mobile.

## Decision log

_Append-only: episodic "we chose / we rejected" and handoff mockup → UI mapping. Keep the living system in sections above; do not let the log replace them._

### YYYY-MM-DD: feature or route (@heyeddi-design | @heyeddi-handoff)

**Context:** …

**We chose:** …

**We rejected:** …

**Mockup → UI:** _(handoff)_ …

**Open questions:** none
