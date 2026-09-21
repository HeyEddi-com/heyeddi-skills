# Foundations: always on (HeyEddi)

Every HeyEddi app ships these **by default**. They are not optional upsells: document them in `.heyeddi/design.md` under **## Foundations (always on)** and implement in craft/handoff unless `product.md` explicitly defers one (with reason in Decision log).

Read this file before `craft`, `polish`, `document`, or `@heyeddi-handoff` implementation.

---

## 1. Responsive (mobile-first)

- **Mobile-first CSS**: base styles for narrow; enhance at breakpoints.
- **Audit widths (fast):** 375, 768, 1440 — iteration during craft/polish.
- **Audit widths (done):** 375, 430, 768, 1024, 1440, 1920 — flagship/marketing before calling done (`@visual-auditor --preset done`). See `brief-language.md`.
- **Fluid layouts**: no fixed desktop-only widths; forms and CTAs stack on small screens.
- **Touch targets** ≥ 44×44px on coarse pointers.
- **No horizontal scroll** on primary content at 375px unless intentional (data tables → scroll container with caption).
- **Responsive contract** in the brief: state desktop vs mobile stack order (e.g. copy before visual on mobile).

## 2. Color scheme: system default

- **Default:** follow `prefers-color-scheme` (light / dark / no-preference).
- **Implementation:** semantic CSS variables from project `tokens.css` / `design.md` (`var(--surface-*)`, `var(--text-*)`). **OpenProps** is the HeyEddi scaffold default: use it when the project already imports `open-props`; otherwise custom `:root` vars are fine. See `heyeddi-design/reference/token-strategy.md`.
- **Light/dark:** `prefers-color-scheme` via project tokens; set `color-scheme: light dark` on `:root` when supporting both schemes.
- **User override (optional in Settings):** `system` | `light` | `dark`; persist in `localStorage`; default **`system`**.
- **Contrast:** WCAG **2.2 AA** minimum in both schemes: document exceptions in Decision log.

## 3. Internationalization (i18n)

- **Default locales:** `en` (fallback) + `es`; **expandable** via locale files.
- **Detection:** `navigator.language` / `navigator.languages` on first visit; map `es-*` → `es`, `en-*` → `en`; unknown → `en`.
- **User override:** language picker in Settings or header; persist preference; beats browser on next visit.
- **Implementation:** `vue-i18n` (or project standard); no hard-coded user-facing strings in Vue templates.
- **HTML:** `lang` on `<html>` matches active locale; update on switch.
- **RTL-ready:** when adding `ar`, `he`, etc., set `dir="rtl"` and mirror layout: plan in `product.md` locales table.
- **Copy:** dates/numbers/currency via `Intl` APIs: not hand-formatted.

### Locale table (in `product.md` + `design.md`)

| Code | Language | Status | Notes |
|------|----------|--------|-------|
| `en` | English | shipped | fallback |
| `es` | Spanish | shipped | default pair |
| … | … | planned | add row when scoped |

## 4. Accessibility (baseline)

Target **WCAG 2.2 AA** for product UI.

| Area | Rule |
|------|------|
| **Keyboard** | Full keyboard path; visible `:focus-visible`; logical tab order |
| **Skip link** | “Skip to main content” as first focusable element |
| **Semantics** | Landmarks (`header`, `nav`, `main`, `footer`); headings in order |
| **Forms** | `<label>` or `aria-label`; errors linked with `aria-describedby` |
| **Color** | Never color-only meaning; icons/text reinforce state |
| **Motion** | Respect `prefers-reduced-motion`: disable non-essential animation |
| **Contrast** | `prefers-contrast: more`: avoid ultra-light grey on white |
| **Modals** | Focus trap, `aria-modal`, restore focus on close |
| **Live regions** | Toasts/async status use `aria-live` appropriately |
| **PrimeVue** | Use built-in a11y props; don’t strip `aria-*` from wrappers |

## 5. Reading modes (incl. dyslexia-friendly)

**Default reading mode** uses project `{typography.body-md}`.

**Optional dyslexia-friendly mode**: user toggle in Settings (and optionally quick toggle in reading-heavy views):

| Setting | Default | Dyslexia-friendly |
|---------|---------|-------------------|
| Font | system / project body | **Atkinson Hyperlegible** or **OpenDyslexic** (document choice in Typography) |
| Line height | 1.5 | **1.7-1.8** |
| Letter spacing | normal | **+0.05em** |
| Word spacing | normal | **+0.1em** |
| Paragraph width | ≤ 75ch | **≤ 65ch** |

- Apply via `data-reading-mode="dyslexia"` on `<html>` (or `class`) + CSS variables.
- Persist user choice; **does not** replace locale or theme.
- Long-form pages (help, legal, articles) must respect active reading mode.

## 6. Universal UI states

Every route with async data or user input documents:

- **Loading**: skeleton or spinner; no layout jump
- **Empty**: helpful copy + primary action
- **Error**: plain language + retry; no raw stack traces
- **Success**: confirm destructive/save actions

## 7. Performance & media defaults

- `font-display: swap` for webfonts
- Lazy-load below-fold images; meaningful `alt` text
- No autoplay video/audio with sound
- Respect `prefers-reduced-data` where practical (fewer hero assets)

## 8. Handoff mockups (layout only)

When `@heyeddi-handoff` receives designer PNGs:

- Mockups define **where** things go: shell topology, cards, field order, CTA placement, responsive structure.
- Mockups do **not** define brand colors: use this file's **Colors** / **Components** and project semantic tokens (OpenProps-backed or custom: see `token-strategy.md`).
- Always implement **layout components** + PrimeVue primitives; never flat unstyled forms on a bare page background.
- See `heyeddi-handoff/reference/mockup-contract.md`.

## 9. Privacy & safety (UI layer)

- Don’t put secrets in URLs or UI copy
- Confirm destructive actions
- Session timeout messaging where auth exists (product scope)

---

## What to customize per project

Only **brand** sections (Colors, Typography voice, Components, marketing register) vary. Foundations stay unless `product.md` lists an **explicit waiver** with business reason.

## Checklist before ship

- [ ] 375 / 768 / 1440 visual pass (fast); flagship done = 375 / 430 / 768 / 1024 / 1440 / 1920
- [ ] Light + dark (system) checked
- [ ] `en` + `es` strings present for new copy
- [ ] Keyboard + focus on new interactive UI
- [ ] Reading mode toggle works if page is reading-heavy
- [ ] Loading / empty / error for new data views
