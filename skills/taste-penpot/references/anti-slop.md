# Anti-slop reference

Load during PLAN (to steer away) and during CRITIQUE (check 11). These are the
category's defaults, not universal bans: an explicit brief can ask for any of them
except where marked **always**. Reaching for one when the axis is free means you
were not deciding. The fix is to rewrite the element, not soften it.

---

## 1. Calibration: the AI look

Generated interfaces cluster around a few looks regardless of subject. If the
brief does not ask for one of these, landing in one means the direction failed:

1. Warm cream ground, high-contrast serif display (often with italic accents),
   terracotta or signal-red accent, "lamplight" warmth.
2. Near-black ground with a single neon accent and glowing edges.
3. Broadsheet editorial: hairline rules, italic display serif, small tracked
   monospace labels, zero radius, dense newspaper columns.
4. Flat saturated ink with black boxes, hard offset shadows and heavy condensed
   display type, used without a real neobrutalist reason.
5. The SaaS card kit: content chopped into identical rounded cards, one radius on
   everything, the same soft grey shadow under each, gradient washes as decoration.
6. Dark glass: deep black, blurred translucent cards, purple-to-cyan mesh orbs.

Self-test: could someone guess your aesthetic from the category alone, or from the
category plus "avoid the obvious"? If yes, rework. Warm, bookish, family or
child-facing subjects pull hardest toward look 1: treat cream + serif as already
spent unless the brief pinned it, and go to the subject's saturated materials.

## 2. Over-used display faces (Persuade / Experience)

Naming one of these needs a reason no other face could satisfy; a subject
association (books → serif, tech → mono) is not a reason:

Fraunces, Playfair Display, Cormorant, Lora, Crimson, Newsreader, Syne,
Space Grotesk, Space Mono, IBM Plex, Inter used as display, DM Sans, DM Serif,
Outfit, Plus Jakarta Sans, Instrument Sans.

Operate and Read surfaces may happily use system stacks and workhorse UI faces.
A platform default face as the display voice of an own-world marketing page is a
failure, not a fallback.

## 3. Page scaffolds to refuse

- Same-size cards of icon + heading + text as the page structure. Cards are the
  lazy container; **nested cards are always wrong**.
- The hero-metric template: big number, small label, supporting stats, accent.
- **Always:** a kicker / eyebrow label above a heading. The heading carries its
  own weight.
- Section numbers (01 / 02 / 03) unless the content really is a sequence the
  reader needs.
- Split hero (copy left, device right, badge row below) or centred headline over a
  row of equal cards, as the default skeleton.
- A "trusted by" strip of evenly spaced grey logos when there are no real
  customers to show.
- A three-tier pricing grid with the middle card highlighted by a gradient border,
  by reflex.
- A modal for a task that needs neither interruption nor protected focus.
- A FAQ accordion as the last block before the footer, by reflex.

## 4. Surface habits to refuse

- Gradient text. Emphasis comes from weight or size.
- Glass and blur as decoration rather than a specific effect.
- A coloured left or right border thicker than 1px on cards, list items, callouts
  or alerts.
- Hard offset zero-blur shadows outside a world that chose neobrutalism.
- Zero-offset coloured glows/halos posing as depth.
- Sparklines, progress rings and soft rounded rectangles standing in for content.
- Monospace as a costume for "technical" rather than for code, data or
  measurement.
- Unicode glyphs or emoji standing in for an icon system.
- Geometric masks (circles, polygons) approximating a photo subject's edge;
  derive a real cut-out instead or omit it.
- Purple-to-pink or purple-to-blue gradients on hero buttons by reflex.
- Abstract low-opacity gradient blobs as a background idea.
- Harsh borders that are the first thing you see; dramatic surface jumps;
  dramatic drop shadows; thick decorative borders; large radius on small elements.
- Multiple accent colours; different hues for different surfaces; colour or
  gradients with no meaning.
- Mixed depth strategies; inconsistent spacing; monotone layout (same card size,
  gap and density everywhere); flat hierarchy (everything one size and weight).
- Template chrome regardless of subject: tracked all-caps labels everywhere,
  "A · B · C" meta strings, an arrow appended to every link and button, tinted
  near-black standing in for black by habit.
- Light or dark chosen by category instead of by the use scene.
- One identical fade-and-rise entrance on every section; hover lift on every card.
- Structural hacks in code handoffs: negative margins undoing parent padding,
  escape-hatch calculations, absolute positioning to dodge layout.

## 5. Copy to refuse

- Hype clichés: "Elevate", "Seamless", "Unleash", "next-gen", "Game-changer",
  "Revolutionize your workflow", "Supercharge", "Delve", "Built for modern teams",
  "Make every screen better". Name the user, the task and the outcome instead.
- Placeholder people and companies: "John Doe", "Jane Smith", "Acme Corp",
  lorem ipsum. Use plausible, specific content and label it as placeholder.
- Invented proof: fake logos, metrics, testimonials, awards, prices or customer
  counts. **Always** refused unless the user supplied them.
- Accenting a single word of a headline (one word italic, bold or coloured) as the
  only idea.
- Generic buttons: "Submit", "Learn more" everywhere, "Get started" with no object.
- Errors that apologise without saying what happened or how to fix it.

## 6. Operate-specific tells

- Display faces in labels, buttons, tables.
- Reinvented standard controls for flavour.
- Inconsistent buttons or form controls between screens.
- Full-saturation accents on inactive states.
- Spinners in the middle of content instead of skeletons.
- "Nothing here" empty states with no next action.
- Animation on actions people repeat many times a day.
