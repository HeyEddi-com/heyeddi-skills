# Taste rules (deep reference)

Load during PLAN for any new surface, and during CRITIQUE when a check fails.
Everything here is a default for when the brief leaves the axis free; the brief's
own words always win.

---

## 1. Modes in depth

### Persuade (landing, marketing, campaign, pricing)

- The first viewport must make the offer intelligible and desirable, show a clear
  action, and demonstrate something only this product can prove.
- The action is the one visitors came to take, in its working form where possible:
  a booking search, open appointment slots, a pricing toggle with real numbers,
  "add to cart". A decorative link pointing elsewhere does not count.
- A hook that lands in one line, a visible primary action, a legible reading order.
- The visual world may carry the page (its material is the ground and the major
  surfaces, its type sets the headlines), but the page must still work as a page:
  navigation reads as links, copy reads as text, the action is plainly clickable,
  sections keep a steady vertical rhythm.
- A world reduced to an accent on a neutral template is the category default with
  a sticker on it. A full-viewport picture of the world with no working parts is a
  poster, not a website. Avoid both ends.
- Template skeletons stay templates whatever colours paint them: split hero (copy
  left, product right, badge row below) or centred headline over a row of equal
  cards. Choose a composition from the content instead.
- When the world is an object (a book, a ticket, a facade), show it once, at one
  scale, keeping its real form; more content goes on its own surfaces or the next
  section, not on extra copies.

### Operate (apps, dashboards, settings, tools)

- Someone who uses tools like this should know where everything is before they
  notice the style. The tool should disappear into the task.
- The visual world lends exactly four things: **type, palette, density, one
  signature move**. It never supplies the layout, navigation model or controls.
- Controls are the standard ones people already know: buttons, tabs, inputs,
  selects, filters, sortable tables, navigation that reads as navigation. Never a
  costume of an instrument (terminal prompts, bezels, ledger paper as a table).
- Failure mode is strangeness without purpose: over-decorated buttons, mismatched
  form controls, gratuitous motion, display faces in labels, invented affordances.
- A grey screen with one accent is not restraint; it is the default without the
  polish. Colour does real jobs: shell (a coloured rail or tinted ground), states,
  data series, selection, the signature move.
- Name the signature move concretely (service health drawn as a transit map, a
  schedule set in a timetable's column rhythm).
- Finish bar: the best product in the category. Aligned grid, consistent spacing,
  real type scale, clear hierarchy. The signature move adds to a clean screen; it
  never replaces cleanliness.
- Permissions: system or workhorse UI faces, standard navigation (top bar + side
  nav, breadcrumbs, tabs, command palette), real density, consistency over
  surprise. Delight is for moments, not pages.
- Constraints: decorative motion that conveys no state; inconsistent component
  vocabulary between screens; display faces in labels, buttons or data; reinvented
  standard affordances; full-saturation accents on inactive states; a modal as the
  first idea (exhaust inline and progressive options first).

### Read (docs, guides, articles, changelogs)

- The reader's question leads; comprehension and wayfinding stay intact.
- The world owns the frame (masthead, navigation rail, ground, title and section
  openers, how code, tables and callouts are set). The reading column stays calm:
  a reading face, real contrast, 60–75 characters at about 16px body.
- Monospace is for code, parameters and small data labels, never running text or
  headings by default.
- Self-check: can a reader tell where they are and where to go next?

### Experience (portfolios, galleries, showcases)

- The work leads from the first viewport; the interface recedes.
- Composition may be asymmetric or fluid when the work earns it; navigation still
  reads as navigation.

---

## 2. Layout

- **Squint test**: blur the screen. Primary element, secondary element and major
  groups must still read in order.
- **Group by meaning**: proximity before containers. Containers compensating for
  weak spacing are a smell; nested cards are always wrong.
- **Rhythm**: deliberate contrast between tight and generous intervals. One
  spacing value repeated everywhere flattens everything to equal weight.
- **Spacing scale**: base 4px gives useful middle steps (4, 8, 12, 16, 24, 32,
  48, 64, 96). Use only scale values. Padding symmetrical unless content demands
  otherwise.
- **Spacing contexts**: micro (icon gaps), component (inside controls/cards),
  section (between groups), major (between areas).
- **Proportions speak**: a 280px sidebar beside full-width content says
  "navigation serves content"; 360px says "these are peers". Choose widths that
  state a relationship.
- **Structure follows content**: repeated cards or columns only when the items are
  genuinely equivalent.
- **Density is a decision**: workbench-tight panels at 12–16px padding versus
  brochure-airy at 24px+. Pick once, hold it.
- **Responsive is structural**: reorder, collapse, reflow or reveal by priority;
  check narrow, intermediate, wide, zoomed, and long-language states. Visual order
  and focus order agree.
- **Extremes**: long names, empty states, overlays, sticky elements, safe areas,
  small targets. Design for them, do not discover them later.
- Depth only when it clarifies state or hierarchy. Optical corrections only after
  looking at the rendered result.

---

## 3. Typography

| Role (example, 16px base, ratio 1.25) | Size | Weight | Line height |
|---|---|---|---|
| Display (Persuade only) | 48–96px | 500–800 | 1.0–1.1 |
| Heading L | 39px | 600 | 1.15 |
| Heading M | 31px | 600 | 1.2 |
| Heading S | 25px | 600 | 1.25 |
| Body | 16px | 400 | 1.5–1.6 |
| Body small / meta | 13–14px | 400–500 | 1.45 |
| Label | 12–13px | 500 | 1.3 |
| Data | match body or label, tabular figures | 500–600 | 1.3 |

- Choose a ratio and step it: about 1.125–1.2 for dense Operate, 1.25 for most UI,
  1.333 or more for expressive Persuade. Round to whole pixels.
- **Weight and colour do hierarchy work, not only size.** A single 14px size can
  hold three tiers: value 600 primary, label 500 secondary, meta 400 muted.
- One family is often right for Operate. For Persuade/Experience choose faces like
  objects from the subject's world; a second family needs a job only it can do.
- Body: 16px floor on the web; measure 45–75ch; wider measure needs more leading.
- Large type: tighten tracking as size grows (headings slightly negative, never
  tighter than -0.04em); display no larger than about 96px.
- Light text on dark grounds: a touch more line height, tracking and weight.
- Balanced heading wraps; no orphans in short body copy; run the real copy at
  every width and fix overflow.
- Paragraph rhythm: spacing **or** first-line indent, not both.
- Tabular figures for prices, counters, timers and table columns.
- Load only the weights used; respect user zoom and text scaling.

---

## 4. Colour

- Pick the strategy before picking colours: Restrained, Committed, Full palette,
  Drenched (see SKILL.md 1.4). Colour commits at page scale: fields that own whole
  regions, not tiny accents scattered over grey.
- Build roles, not a bag of swatches: canvas, raised surfaces, text primary /
  secondary / tertiary / muted, action, focus, selection, borders, success,
  warning, error, info, data categories.
- Hue comes from product meaning and the visual world, never from a category
  association ("fintech = blue").
- About 60/30/10 for Restrained surfaces: dominant neutral, secondary tone, ~10%
  accent. One accent used with intent beats five used without thought.
- Neutrals may be tinted from the brand hue when it creates cohesion; neutral grey
  is fine when it serves the world.
- On coloured grounds, derive secondary text from the ground or foreground hue,
  never washed-out grey.
- Prefer OKLCH when deriving new ramps: vary lightness, reduce chroma near white
  and black. Prefer explicit colours over stacks of translucent overlays.
- Dark themes are designed, not inverted: elevation by small lightness steps
  (for example base, +7%, +9%, +12%), borders over shadows, semantics slightly
  desaturated, one hue across surfaces.

| Content | Minimum contrast (WCAG AA) |
|---|---|
| Body and placeholder text | 4.5:1 |
| Large text (≥24px, or ≥18.7px bold) | 3:1 |
| Controls, icons, focus indicators | 3:1 |

Colour is never the only signal; pair it with text, shape, icon or position.

---

## 5. Depth, surfaces and app-UI tokens

- **Choose one depth strategy and commit**: borders-only (technical, dense),
  subtle shadows (approachable), layered shadows (premium), surface-colour shifts
  (tints, no shadows). Do not mix.
- **Surface elevation**: numbered levels, each a few percent of lightness apart;
  you feel them stacked rather than see one step. Dropdowns one level above their
  parent. Sidebars share the canvas colour with a quiet border. Inputs slightly
  darker than surroundings (inset).
- **Borders** disappear until you look for them: low-opacity edges
  (dark mode about 6–12% white; light mode a little stronger). A progression:
  standard, soft separator, emphasis, focus ring.
- **Shadows** carry an offset and a soft blur. Light-mode lift example: a 1px ring
  at 6% black plus two soft depths (0 1px 2px at 6%, 0 2px 4px at 4%). On dark,
  a single 1px ring at about 8% white.
- **Radius scale**: small for controls, medium for cards, large for overlays.
  Nested radius: outer = inner + padding. No large radius on small elements.
- **Text hierarchy tokens**: four levels (primary, secondary, tertiary, muted).
- **Control tokens**: inputs, selects and checkboxes get their own background,
  border and focus tokens so they can be tuned separately from surfaces.
- **Token architecture**: every colour traces to primitives (foreground,
  background, border, brand, semantic). No stray hex values.

Before building each component, be able to state: intent (who, what, how it
should feel), the focal element and how it wins, palette and why, depth and why,
surfaces, typography levers, spacing base and density. If you cannot say why,
you are defaulting.

---

## 6. Animation and timing

| Duration | Use |
|---|---|
| 0ms | actions repeated many times a day (shortcuts, command palette) |
| 100–150ms | immediate feedback (press, toggle, hover) |
| 150–250ms | routine state change, tooltips, dropdowns |
| 300–500ms | layout change, overlay, drawer, view transition |
| 500–800ms | one deliberately authored focal entrance (Persuade/Experience only) |

| Easing token | Curve | Use |
|---|---|---|
| `ease.out` | cubic-bezier(0.16, 1, 0.3, 1) | confident arrivals, entering elements |
| `ease.out.snappy` | cubic-bezier(0.23, 1, 0.32, 1) | interactive feedback |
| `ease.inout` | cubic-bezier(0.77, 0, 0.175, 1) | elements moving across the screen |

- Movement explains state, relationship or hierarchy, or it is one authored moment
  the surface has earned. Decoration without purpose is debt.
- One rehearsed focal sequence beats repeated section reveals. Never the same
  fade-and-rise on every section; never a hover lift on every card.
- Exit faster than entrance. No reflexive bounce or elastic curves. No ease-in for
  entrances (it delays the first frame the user watches).
- Nothing appears from nothing: start at about 95% scale with zero opacity, not 0%.
  Press feedback about 97% scale, never below 95%.
- Popovers grow from their trigger; modals stay centred.
- Stagger only real lists, 30–80ms between items, with a capped total.
- Properties: prefer transform and opacity; blur, clip, mask and shadow are
  allowed when bounded to small regions. Do not animate width, height, top, left
  or margins. Name exact properties, never "all".
- Default state is visible: if an animation fails, content is still there.
- Reduced motion: remove or shrink spatial movement, keep opacity, colour and
  state changes that carry meaning.
- Operate: 150–250ms on most transitions, no orchestrated page-load sequences.

---

## 7. States and polish

- Every interactive element: default, hover, focus, active, disabled, plus
  loading, error and success where relevant. Data views: loading (skeletons, not
  a spinner in the middle of content), empty, error, partial.
- Empty states teach the interface and offer the next action; distinguish first
  use, no results, filtered out, no permission and failure.
- Hit areas 44×44px (40 minimum), even when the visible mark is smaller; never
  overlapping.
- Optical alignment: fix what looks off even when the maths is right (icon-side
  padding slightly smaller than text-side; play triangles nudged right).
- Icons from one consistent family or authored set, one stroke and weight; never
  emoji or text glyphs standing in for an icon system.
- Images: correct aspect ratio, no layout shift, useful alt text; a faint 1px
  inner outline (about 10% black on light, 10% white on dark) keeps edges clean.
- Browser-drawn parts still carry the design in code handoffs: text selection
  colour, caret, scrollbars, focus rings, link underline offset, numerals.
- Backdrop blur and grain only on fixed layers (navigation, overlays), never on
  large scrolling regions. Layering (z-order) reserved for systemic levels: sticky
  nav, overlays, modals, tooltips.

---

## 8. Copy

- Use the product's own language and the user's vocabulary, not system internals
  ("manage notifications", not "webhook config").
- Actions: specific verb + object ("Save changes", "Start free trial", "Export
  CSV"). The same action keeps the same name through the flow ("Publish" →
  "Published").
- Destructive actions name the object and consequence; prefer undo over
  confirmation when recovery is safe; confirmations repeat the action on the
  button, never "Yes / OK / Submit".
- Forms: persistent labels (placeholders are examples), requirements before
  submission, errors that say what needs attention and how to fix it.
- Errors answer what failed, why (when useful), and how to recover. No vague
  apologies, no internal codes as the main message.
- Loading names the real operation; never fake progress. Success is brief.
- Say each idea once. If the heading explains it, the intro adds new information
  or goes.
- Sentence case, plain verbs, no filler. Tone adapts to the moment; voice stays
  consistent. Warmth is welcome around payments, privacy and deletion; jokes are
  not.
- Write translatable whole messages; allow text expansion.
