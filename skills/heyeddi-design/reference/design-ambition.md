# Design ambition: project-specific, top-tier craft

**Date:** 2026-07-06

**Audience** (`audience-design.md`) = *who* and *why*.  
**Modern reference** (`modern-reference.md`) = *how* (tokens, surfaces, type).  
**This file** = *how impressive*: the bar for **individual**, memorable design per project.

Default stance: **strive for impressive craft** unless the user explicitly asks for minimal/admin/wireframe fidelity. Do not wait for the user to say "make it artistic": that is the baseline for flagship routes.

## What "impressive" means here

Not decoration for its own sake. A persona on a **flagship route** (`/`, `/login`, `/dashboard`, `/settings`) should feel within 5 seconds:

1. **This product has a point of view**: not a PrimeVue demo with the logo swapped
2. **Hierarchy is intentional**: type scale, spacing rhythm, one clear primary action
3. **At least one memorable detail**: hero rhythm, nav character, table/data treatment, or settings IA: **chosen for this product**, not copied from the last HeyEddi project
4. **Differentiation vs competitors** (from `product.md`) is **visible** in layout or copy: not only in `product.md` text

| Shipped | Not shipped |
|---------|-------------|
| Stripe/Linear-level **restraint + precision** for B2B | Random gradients and glass everywhere |
| Warm Notion-like **approachability** when persona needs it | Stock "SaaS purple gradient hero" template |
| Bold editorial **brand** when brief asks for personality | Same sidebar + profile cards on every app |
| Sketch/wireframe fidelity when brief scopes it | Polished template pretending to be custom |

## Project signature (required per product)

Before `craft` on any flagship route, define in `designs/<feature>/brief.md`:

```markdown
## Design signature (this project only)

- **Aesthetic energy:** (e.g. calm precision | warm human | bold editorial | dense utilitarian)
- **Subject / page job:** one concrete subject + what this page must do
- **Signature moment:** one screen/region that should feel unmistakably *this* product
- **Aesthetic risk:** one bold, justified choice (type, hero, layout, motion) — not random ornament
- **Borrow:** 2 named references: what specifically (not "like Linear")
- **Avoid:** 2 tells that would make this look like our last scaffold, a competitor clone, or generic AI UI
- **Memorable detail:** one concrete choice (type pairing, hero grid, stat treatment, settings card rhythm, nav pill style, …)
```

Re-read this section at **craft** and **polish**. If implementation could belong to another product with a name swap, **revise before calling done**. Also read `reference/aesthetic-direction.md` (hero as thesis, type personality, anti–generic-AI clusters).
## Discovery: ask when ambition is unclear

Add to `discover` (2-3 questions per round):

- What should a user **remember** about this UI vs `{competitor}`?
- **Aesthetic energy**: restrained precision, warm, bold, or utilitarian? Any reference that nails the feeling?
- On the flagship route: what is the **one moment** we should nail (hero, first table load, settings save, sign-in trust)?
- What must this **NOT** look like? (generic admin, template marketplace, previous project?)

If the user says "top notch / artistic / impressive": treat that as **confirmation** of the default bar, not a license to skip `shape` or audience work.

## Shape & explore

- **`research`:** find 2-3 references **in the product's category**, not only generic "SaaS dashboard 2026"
- **`explore`:** **2-4 lanes** that differ in hierarchy, density, nav, or typographic voice: not palette-only variants
- **Brief:** Design signature section is **mandatory** for flagship routes; optional for internal tools only when brief says minimal/admin

## Craft: ambition checklist (before done)

After `modern-reference` + `aesthetic-direction` checks and before audience-fit:

- [ ] **Signature moment** from brief is implemented and visible at 1440 and 375
- [ ] **Aesthetic risk** from brief is visible and justified (Decision log)
- [ ] **Three PrimeVue tells removed** (default card padding mush, undifferentiated table, system-font sameness, flat gray shell: pick what applied)
- [ ] **Competitor differentiation**: one layout or copy choice a clone would not make
- [ ] **Decision log** cites persona + **specific** borrowed pattern + **this project's** memorable detail + aesthetic risk
- [ ] Screenshot test: would a designer say "template" or "crafted for {product_name}"?

If any fail → `@heyeddi-design polish` or revise in craft; do not hand off to `@heyeddi-handoff` with generic chrome.

## Polish & critique

When user asks to "make it more artistic" or "top of the line":

1. Re-read **Design signature**: sharpen memorable detail, do not add random ornament
2. Upgrade **typography + surfaces + spacing** before adding new components
3. Run `audience-fit` + ambition checklist; report which dimension was weak

## Handoff boundary

- **`@heyeddi-intake` wireframes** = layout intent only (ASCII, diagrams)
- **`@heyeddi-design` shape/craft** = where ambition and visual signature live
- **`@heyeddi-handoff`** = implement approved mockups/briefs: not a substitute for skipping ambition in design phase

## Related

- `audience-design.md`, `modern-reference.md`, `aesthetic-direction.md`, `explore.md`, `audience-fit.md`
- `context/ANTI_PATTERNS.md`: template swap called out
