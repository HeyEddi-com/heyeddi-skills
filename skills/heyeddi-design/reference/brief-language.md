# Brief language: taste + subject + hard rejects (always on)

**Date:** 2026-09-20

**Auto-load:** Read this file whenever the user talks about design, UI look/feel, marketing, heroes, dashboards, polish, critique, or "make it professional/clean/modern." Do **not** wait for them to say "brief" or "shape."

Vague adjectives are not a brief. **Naming taste + subject + hard rejects up front** prevents the first ship from being "random framework + dark mode."

## Hard gate (before pixels or craft)

Pin all of these in chat or `brief.md` **before** inventing a look. If the user only said "professional" / "clean" / "modern," translate or ask — never ship on adjectives alone.

| Must name | Working language (adapt to product) |
|-----------|-------------------------------------|
| **Subject / metaphor** | One concrete world: "Treat this like a cartographer's desk / instrument panel / lab notebook — not a SaaS dashboard." |
| **Hard rejects** | Say what you refuse: "No Inter/Outfit-only admin kit. No dark slate + blue-400. No boxed hero card. No opaque panel over the wash." |
| **Hero composition** | "Full-bleed atmosphere with a soft paper→ink degrade; brand as the loudest signal; one headline, one lede, two CTAs; graph lives in the dark side." |
| **Typography roles** | "Sans for logo + H1/H2 only; body stays quieter. No italic serif wordmark." |
| **Accent system** | Brand/UI accent vs edge/data accent: "Sea teal for brand/UI; coral-red only for graph edges so links read on the plane." |
| **Responsive contract** | Explicit stack order: "Desktop: side degrade. Mobile: title block first, graph band below — never graph above the title." |
| **Token SSOT** | "One token file; change brand/edge once, all surfaces update." |

Also required on flagship routes (see `design-ambition.md`): audience, single page job, **one aesthetic risk**, explicit **do not look like X**.

## What else to ask (sharper pass)

Ask 2–3 per round in `discover`; fill gaps before confirming the brief.

| Ask | Why it helps |
|-----|--------------|
| **3 references + what to steal** | "Stripe marketing rhythm, Linear density, atlas map — borrow X not Y." |
| **Intensity dial** | "Marketing can have atmosphere; app shell quieter same language." |
| **Motion budget** | "2–3 intentional motions; respect reduced-motion." |
| **First viewport checklist** | Brand, one headline, one sentence, one CTA group, one visual — nothing else. |
| **Contrast / edge rule** | "Edges must read on the plane; never put link color on the washed paper." |
| **Screenshot gate** | Don't call done until **done widths** (see below) and fix what you see. |
| **What 'done' means** | "If it could be another startup after removing the logo, it's wrong." |

## First viewport checklist (marketing / brand register)

The first viewport usually contains **only**:

1. Brand (loudest signal)
2. One headline
3. One short supporting sentence (lede)
4. One CTA group (typically ≤2)
5. One dominant visual / atmosphere plane

Nothing else in the first viewport: no stats strips, schedule snippets, address blocks, promo chips, or secondary marketing content.

**Full-bleed default** for marketing heroes: atmosphere edge-to-edge. No inset hero cards, no opaque white slab under copy over a wash, no boxed hero floating on the page unless the brief explicitly demands it.

## Screenshot / done gate

| Mode | Widths | When |
|------|--------|------|
| **Fast** | `375, 768, 1440` | Iteration during craft/polish |
| **Done** | `375, 430, 768, 1024, 1440, 1920` | Before calling flagship/marketing done; `@visual-auditor` finalize |

Pass done widths to capture/contrast: `--widths 375,430,768,1024,1440,1920` (or auditor `--preset done`).

## Short prompt template (pasteable)

Adapt product names; keep the structure:

```text
Design {Product} marketing + app shell as {subject metaphor} for {core job}.
{Palette in 1 line}. {Type roles in 1 line}.
Full-bleed hero with {composition}; reject opaque slabs / inset hero cards.
{Primary visual} placement + mobile stack order.
Tokens in one CSS SSOT. Reject: {3 hard rejects}. Ambition: {calm wow / craft bar} — impressive craft, not template.
```

Example:

```text
Design Proven3 marketing + app shell as an atlas desk for a core graph engine. Cool paper + deep ink + sea teal brand. Outfit for logo/H1/H2 only. Full-bleed hero with smooth paper→dark degrade (no opaque white slab under copy). Graph on the dark side with bright coral-red edges. Mobile: copy first, graph below. Tokens in one CSS SSOT. Reject: dark Tailwind admin, Inter-default SaaS, inset hero cards, purple/cream AI looks. Ambition: calm wow B2B — impressive craft, not template.
```

## Map to Design signature

When writing `brief.md`, fold this language into **Design signature** (`design-ambition.md`):

- Subject / metaphor → **Subject / page job**
- Hard rejects → **Avoid** (concrete tells)
- References + steal → **Borrow**
- Hero / type / accent / responsive → **Signature moment** + layout strategy
- Intensity + motion → Decision log / interaction model
- Aesthetic risk → **Aesthetic risk** (one justified bold choice)

## Related

- `discover.md` — interview; refuse adjective-only briefs
- `design-ambition.md` — Design signature schema
- `aesthetic-direction.md` — craft pillars + anti–generic-AI clusters
- `foundations.md` — responsive + reduced motion
- `@visual-auditor` — fast vs done width presets
