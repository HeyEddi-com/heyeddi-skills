# Modern reference: beyond default PrimeVue

**Date:** 2026-07-03

HeyEddi scaffolds use PrimeVue + semantic tokens. That stack is **fast to ship** but defaults to an **admin-template** look unless the designer deliberately adds depth, typography, and layout character.

Read this during **`research`**, **`shape`**, **`craft`**, and **`polish`**. Tie choices to `product.md`: do not paste trends unrelated to the product.

**Audience first:** read `reference/audience-design.md` + `product.md` **Personas** before picking references from the table below.

**Ambition:** read `reference/design-ambition.md`: impressive craft is the default for flagship routes; borrow techniques below into a **project-specific signature**, not a reusable template.

## The problem we are fixing

| Plain (avoid) | Modern (target) |
|---------------|-----------------|
| Flat white cards on gray background | Layered surfaces, subtle borders, intentional elevation |
| System font, one heading size | Distinct display + body scale, weight contrast |
| Full-width tables with no rhythm | Max-width content, bento sections, clear hierarchy |
| Generic blue primary everywhere | Brand seed + semantic roles (success/warn/muted) |
| Every page looks like `/admin` | Marketing pages feel editorial; app pages feel focused |

## Named references (what to borrow: never clone)

Use these in `research.md` and briefs as **direction anchors**. Describe *what* to borrow in one line each.

| Product | Borrow |
|---------|--------|
| **Linear** | Tight typography, dark-friendly surfaces, crisp borders, minimal chrome |
| **Vercel** | Marketing hero rhythm, gradient accents, high-contrast CTAs, generous whitespace |
| **Stripe Dashboard** | Data density without clutter, table + filter bar hierarchy, calm neutrals |
| **Raycast** | Soft radius, pill nav, subtle glass/blur on shell (web-safe fallbacks) |
| **Notion (marketing)** | Large headlines, feature grids, muted illustration placeholders |
| **Superhuman** | Confident single-column settings, strong section labels, one primary action |
| **Arc / Dia (marketing)** | Bold color blocks, personality in hero: sparingly for B2B |

During **`research`**, web-search 2-3 of the above plus your product category (e.g. "B2B team dashboard UI 2026").

## Concrete techniques (PrimeVue + CSS tokens)

### Typography

```css
/* tokens.css: example semantic scale */
--font-display: var(--font-sans, system-ui);
--text-display: clamp(1.75rem, 2vw + 1rem, 2.25rem);
--text-body: 1rem;
--text-muted: var(--text-2);
```

- Page title: `--text-display`, weight 700, tight letter-spacing
- Section labels: uppercase optional, `--text-muted`, size-1
- Avoid identical `font-size` on h1 and body

### Surfaces (light + dark)

```css
.app-shell {
  background: var(--surface-1);
}
.card-elevated {
  background: var(--surface-2);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-3, 12px);
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.04);
}
```

- Prefer **border + subtle shadow** over heavy PrimeVue default elevation
- Override `.p-card .p-card-body` padding in scoped CSS when brief specifies rhythm

### Marketing / home pages

- Hero: headline + subcopy + **one** primary CTA + optional secondary link
- Feature row: 3 columns with icon or simple SVG, not lorem blocks
- Background: subtle gradient mesh or noise via CSS (`radial-gradient` at low opacity): not full-bleed stock photo unless brief asks

### App dashboard (TaskFlow-style)

- Header row: title + subtitle + **one** secondary action (Refresh)
- Optional **1-2** stat cards, not mandatory 3-tile KPI grid
- Table in elevated card; striped rows OK; column headers with muted color
- Banner for offline/demo state: not silent failure

### Settings

- Card stack with 16-24px gap; Save **outside** cards, right-aligned
- Inputs filled + rounded per theme; toggle in its own card section

### Motion (light touch)

- `transition: background 150ms, border-color 150ms` on nav items
- No gratuitous page transitions in eval turns

## Anti-slop checklist (craft / polish)

Before calling a screen done:

- [ ] Would a user confuse this with an unstyled PrimeVue demo? If yes, add hierarchy + surfaces.
- [ ] Is there one clear primary action per viewport?
- [ ] Do cards have padding ≥ 16px and visible separation from background?
- [ ] Does dark mode look intentional (not inverted gray mush)?
- [ ] Decision log entry cites which reference pattern you borrowed **and this project's memorable detail** (`design-ambition.md`)
- [ ] UI **copy** follows `context/PROSE_ANTI_SLOP.md` (no em dashes, no AI filler)
- [ ] `verify_prose.py --check` passes on Vue/locale files
- [ ] Smell test: would this copy survive Slack without an eye-roll?
- [ ] Smell test: would this copy survive Slack without an eye-roll?

## When plain is OK

- Internal tools with explicit "minimal/admin" in brief
- Wireframe fidelity evals (structure over polish)
- User opts out of research in `shape`

## Related

- `reference/research.md`: synthesize trends into `research.md`
- `reference/surface-completeness.md`: full states and affordances
- `context/ANTI_PATTERNS.md`: plain admin template called out
- `context/PROSE_ANTI_SLOP.md`: writing / copy anti-slop (em dashes, filler phrases)
