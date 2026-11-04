
# Anti-patterns: HeyEddi design

- NEVER skip discovery for vague briefs: ask before building.
- NEVER craft on adjective-only briefs ("professional", "clean", "modern") without `@taste-penpot` **identity gate** (≥3 options + user choice) and **subject/metaphor + hard rejects** — read `reference/brief-language.md` and taste `references/identity-gate.md`.
- NEVER invent a look or tokens while waiting for the user to pick an identity option.
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
- NEVER ship marketing/flagship UI that reads as **generic AI chrome** (template KPI hero, Inter-only type, fake 01/02/03, purple gradient SaaS, cream+terracotta default, scattered motion, boxed/inset heroes, opaque slabs over washes): follow `reference/aesthetic-direction.md` + `brief-language.md` and take **one justified aesthetic risk**.
- NEVER call flagship/marketing **done** without `@visual-auditor --preset done` (6 widths) and fixing what you see; logo-off brand test must pass.
- NEVER hand off or craft when `@taste-penpot` layout hard gates fail: text-wall cards, absolute MCP boards sold as Flex, missing `hifi.html` while MCP cannot Flex/nest, or no pixel review (`taste-penpot/references/layout-hard-gates.md`).
- NEVER accept a Suite/settings/form design that is one multiline string in a gray rectangle: require separate fields on an 8px grid (human hi-fi bar).
- NEVER put edge/link accent colors where they disappear on washed paper — edges must read on the plane.
- NEVER treat "make it artistic / top notch / better design / redesign" as spacing-only polish: run critique ambition gate; escalate to `shape` when template-like or signature missing (`design-ambition.md`, `critique.md`).
- NEVER answer redesign intent with hierarchy-unchanged token tweaks when the name-swap or scaffold test fails.
- NEVER hand off to `@heyeddi-handoff` without a confirmed brief and Design signature: run `shape` first.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
