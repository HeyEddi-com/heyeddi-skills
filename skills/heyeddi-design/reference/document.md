# DESIGN.md authoring (HeyEddi)

Write **`.heyeddi/design.md`** in the [DESIGN.md ecosystem](https://getdesign.md/what-is-design-md) format.

**Gold-standard example:** [Superhuman DESIGN.md](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/superhuman/DESIGN.md): study its density, voice, and structure.

## Two layers (non-negotiable)

1. **YAML frontmatter**: normative tokens: `colors`, `typography`, `rounded`, `spacing`, `components` with `{token.ref}` syntax and variant siblings (`button-primary`, `button-primary-hover`).
2. **Markdown body**: designer rationale. **Reference tokens inline** in prose: `{colors.ink}`, `{typography.body-md}`, `{spacing.lg}`.

The `description` field in frontmatter is a **full brand paragraph**: not a one-liner.

## Section order

Follow [awesome-design-md extended sections](https://github.com/VoltAgent/awesome-design-md) (adapted for HeyEddi + PrimeVue):

**Include `## Foundations (always on)`** after Overview: copy from scaffold or `reference/foundations.md` (responsive, system theme, en+es i18n, a11y, dyslexia reading mode). Only omit items waived in `product.md`.

| # | Section | What to write |
|---|---------|---------------|
| 1 | **Overview** | Mood, register, how surfaces read; **Key Characteristics** bullet list |
| 2 | **Foundations (always on)** | Responsive, theme, i18n, a11y, reading modes: see `foundations.md` |
| 3 | **Colors** | Grouped (Brand, Surface, Text); **Token source** row (OpenProps / custom); each swatch = role + token |
| 4 | **Typography** | Font family, hierarchy **table**, principles |
| 5 | **Layout** | Spacing scale, shell, whitespace. Per region: Flex or CSS Grid (`../taste-penpot/references/flex-grid.md`), tracks or direction, gap, Fit / Fill / Fix. Quasar owns the app frame. |
| 6 | **Elevation & Depth** | Level table (flat → shadow) |
| 7 | **Shapes** | Border-radius token table |
| 8 | **Components** | Named tokens → PrimeVue mapping; states; signature patterns |
| 9 | **Do's and Don'ts** | Prescriptive guardrails |
| 10 | **Responsive Behavior** | Breakpoint table, touch targets, collapse rules |
| 11 | **Decision log** | HeyEddi extension: append per feature (see `design-talk.md`) |

## Voice (like Superhuman)

- Write as a designer briefing the team, not as a linter report.
- Name rules: "**The single-CTA rule.** One primary button per band."
- Explain *why*: warm grey ink vs pure black, tight display leading, etc.
- For handoff: map mockup regions to component token names and PrimeVue primitives.

## HeyEddi stack mapping

| DESIGN.md | HeyEddi implementation |
|-----------|------------------------|
| `colors.*` | Semantic `var(--*)` in `tokens.css`: OpenProps-backed or custom per `token-strategy.md` |
| `components.*` | PrimeVue `Button`, `InputText`, `Card`, `ToggleSwitch`, … |
| Hex in frontmatter | OK for Stitch lint; prefer semantic `var()` in implementation |
| PrimeVue severity/size | Document in Components prose when it matters |

## Mode detection

| Condition | Mode |
|-----------|------|
| CSS tokens, Vue components exist | **Scan**: extract into frontmatter + sections |
| Empty / pre-implementation | **Seed**: interview, then fill scaffold template |

Seed interview (2-3 questions per round): color strategy, light/dark, density, PrimeVue catalog, motion.

## After writing

- Do not delete **Decision log** history on refresh.
- Confirm before overwriting a mature `design.md`.
- Optional: `npx @google/design.md lint .heyeddi/design.md` if the CLI is installed.

See `design-talk.md` for Decision log entries. Template: `skills/project-engineering/scaffold/heyeddi/design.md`.
