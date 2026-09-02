
# Anti-patterns: HeyEddi design

- NEVER skip discovery for vague briefs: ask before building.
- NEVER write Vue, Flutter, or component CSS in this skill — `@heyeddi-handoff` / `@design-handoff-flutter` implement; see `reference/implement-routing.md`.
- NEVER stop after critique and ask whether to fix — chain implement + `@visual-auditor` automatically.
- NEVER add OpenProps to a brownfield project that does not use it: follow `token-strategy.md`.
- NEVER design outside the project's token system + PrimeVue without documenting exception in `DESIGN.md`.
- NEVER use impeccable: this skill replaces it for the HeyEddi stack.
- NEVER skip web research in `shape` unless the user explicitly opts out.
- NEVER skip GenerateImage / Canvas during `explore` when the IDE provides them — show direction, don't only describe it (`visual-tools.md`).
- NEVER treat generated concept images as final accessibility or copy spec.
- NEVER ship **default PrimeVue admin** look on marketing or flagship app routes: read `reference/modern-reference.md` and add typography, surfaces, and hierarchy.
- NEVER craft flagship routes without **Personas + Per-route intent** in `product.md`: run `@heyeddi-intake` or `discover` first.
- NEVER skip **audience-fit** critique on marketing, dashboard, or settings: see `reference/audience-fit.md`.
- NEVER ship flagship routes that look like **the last project with a name swap**: define and implement **Design signature** per `reference/design-ambition.md`.
- NEVER ship marketing/flagship UI that reads as **generic AI chrome** (template KPI hero, Inter-only type, fake 01/02/03, purple gradient SaaS, cream+terracotta default, scattered motion): follow `reference/aesthetic-direction.md` and take **one justified aesthetic risk**.
- NEVER treat "make it artistic / top notch" as optional polish: that is the **default ambition bar** unless brief scopes minimal/wireframe.
- NEVER hand off to `@heyeddi-handoff` without a confirmed brief and Design signature: run `shape` first.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
