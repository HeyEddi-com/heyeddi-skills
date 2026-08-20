# Aesthetic direction: distinctive craft (not template AI UI)

**Date:** 2026-08-13

Work as a design lead hired for a point of view the client could not get from a template. Make deliberate, product-specific choices about palette, type, layout, and motion — and take **one justified aesthetic risk**.

Read during **`shape`**, **`craft`**, **`critique`**, and **`polish`**. Stay inside HeyEddi constraints: PrimeVue + `design.md` tokens (`token-strategy.md`), `.heyeddi/` briefs, and `PROSE_ANTI_SLOP.md` for copy.

## Ground it in the subject

Before pixels: name **one concrete subject**, **primary audience**, and the page's **single job**. State the choice in the brief.

Distinctive choices come from the product's world — materials, instruments, artifacts, vernacular — not from a reusable “nice SaaS” kit. Prefer real content from `product.md` / brief over placeholder marketing mush.

If the brief is vague, pin subject + job yourself (and say so) before inventing a look.

## Design pillars

### Hero is a thesis

Open with the most characteristic thing in the product's world: headline, image, animation, live demo, or interactive moment. Be deliberate.

A big number + small label + supporting stats + gradient accent is the **template** answer — use it only if it is truly the best option for this brief.

On app shells (dashboard/settings), the “hero” may be hierarchy: title treatment, first actionable region, or data density — still a thesis, not chrome.

### Typography carries personality

Pair display and body deliberately. Set a clear type scale with intentional weights and spacing. Type treatment should be memorable, not a neutral delivery vehicle.

Avoid default stacks that erase identity (Inter / Roboto / Arial / system-ui as the whole brand). Prefer project faces from `design.md` / tokens; if none exist, choose and document them in the Decision log.

### Structure is information

Numbering, eyebrows, dividers, and labels must encode something true about the content. Fake sequences (`01 / 02 / 03`) are only appropriate when order is real (process, timeline). If it is decoration, cut it.

### Motion with intent

Use motion where it serves the subject: load sequence, scroll reveal, hover micro-interaction, ambient atmosphere. Prefer **one orchestrated moment** over scattered effects. Extra animation often reads as AI-generated.

Always respect `prefers-reduced-motion` (`foundations.md`).

### Calm wow for B2B (studio craft → product calm)

When the brief asks for “wow,” “modern,” or “alive” (or when borrowing **Volta / motion-studio** from `modern-reference.md`), translate — do not costume-change:

| Studio signal | HeyEddi translation |
|---------------|---------------------|
| Particle void + dual neon | Brand-token mesh drift; **one** accent glow (blue/cyan family). No magenta+cyan cyberpunk |
| Giant kinetic wordmark | Marketing: display hero thesis. App: strong page title + first actionable region |
| Scroll chapters | One job per section; real structure only (Planning spine order OK; fake `01/02/03` not OK) |
| LIVE / LOOP chips | Sharp brutalist/enterprise chips with quiet pulse; copy names product truth (“Ready now”, “Vault live”) |
| GLSL / metaball grids | Marketing atmosphere only if budgeted; **never** inside dashboard task density |

**Intensity dial:** marketing = higher atmosphere; app shell = lower (focus first). Same language both places so the product feels one brand.

**Aesthetic risk default for flagship:** living atmosphere + status craft, not a new palette.

### Match complexity to the vision

Maximalist directions need elaborate execution. Minimal directions need precision in spacing, type, and detail. Elegance is executing the chosen vision well — not adding more chrome.

## Looks that cluster as generic AI UI

These can be legitimate for a brief that asks for them. When the brief leaves an axis free, **do not** spend that freedom on:

1. Warm cream background (~`#F4F1EA`) + high-contrast serif display + terracotta accent  
2. Near-black background + single acid-green or vermilion accent “glow”  
3. Near-black + **dual neon** (cyan + magenta) “studio void” when the product is calm B2B — borrow atmosphere, not the costume  
4. Broadsheet: hairline rules, zero radius, dense newspaper columns  
5. Purple-on-white / purple-to-indigo gradient SaaS hero  
6. Card grid everywhere (especially in heroes) when a single composition would read clearer  

Where the brief pins a look, follow the brief. Where it does not, choose something grounded in **this** product.

## Two-pass plan (before code)

**Pass 1 — compact design plan** (brief / chat):

| Axis | Capture |
|------|---------|
| **Color** | 4–6 named roles → token/hex from `design.md` (or propose + log) |
| **Type** | Display + body (+ utility for data/captions if needed) |
| **Layout** | One-sentence concept + ASCII wire if exploring |
| **Signature** | The single unique element this page will be remembered by |
| **Aesthetic risk** | One bold choice you can justify in one sentence |

**Pass 2 — uniqueness check:** if any axis reads like the default you would produce for *any* similar page, revise it and say what changed. Only then implement — derive color and type from the plan, not ad-hoc hex in Vue.

When writing CSS, watch selector fights (utility classes canceling each other on padding/margin). Prefer scoped tokens and clear hierarchy.

## Restraint

Spend boldness in **one** place (the signature). Keep surroundings quiet. Cut decoration that does not serve the brief.

Not taking a risk can itself be a failure mode for flagship routes — but the risk must be **justified**, not random ornament.

Quality floor (always on unless waived): responsive to mobile, visible focus, reduced motion (`foundations.md`).

Self-critique while building: before done, remove one accessory that does not earn its place.

## UI writing (design material)

Words are design, not decoration. Same intentionality as spacing and color.

- Name things users control (“Notifications”), not system guts (“webhook config”)  
- Active voice; same verb through the flow (“Publish” → “Published”)  
- Failure/empty: direction and fix, not apology or vagueness  
- One job per element: label labels; example demonstrates  

Full copy rules: `context/PROSE_ANTI_SLOP.md` + `verify_prose.py`.

## Checklist (shape / craft / polish)

- [ ] Subject, audience, and single page job stated  
- [ ] Aesthetic energy + **one justified aesthetic risk** in Design signature  
- [ ] Hero/thesis is not a default KPI/gradient template (unless brief demands it)  
- [ ] Type pairing is deliberate and documented in tokens/`design.md`  
- [ ] Structural chrome encodes real information  
- [ ] Motion is intentional (or intentionally absent)  
- [ ] If wow/alive was requested: calm-wow translation applied (not neon studio clone)  
- [ ] Avoided generic AI look clusters unless brief asked for them  
- [ ] Signature element is the one memorable thing; surroundings restrained  
- [ ] Copy passes prose anti-slop  

## Related

- `design-ambition.md` — project signature and craft bar  
- `modern-reference.md` — PrimeVue techniques and anti-admin-template  
- `audience-design.md` — persona-tied direction  
- `foundations.md` — a11y, responsive, reduced motion  
