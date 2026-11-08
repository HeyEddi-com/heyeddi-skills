# Prose anti-slop (HeyEddi skills)

**Date:** 2026-11-07

**Rule:** If it sounds like a LinkedIn post, a launch blog, or ChatGPT, rewrite it. Visual UI anti-slop stays in `@heyeddi-design` `reference/modern-reference.md` / `@taste-penpot` `references/anti-slop.md`. This file is about **words**.

**Always on for every skill.** Apply these rules to **any prose the agent authors** in this session: chat, books, manuscripts, docs, READMEs, PR text, briefs, UI strings, skill stdout, code comments. HeyEddi skills are general-use. Writing anti-slop is not an app-only or `.heyeddi`-only gate.

There is **no carve-out** for manuscripts, GTM chapters, long-form, scaffolding, or "I matched the local voice by hand." If you write it, these rules apply. Pre-existing third-party or human text you did not edit is left alone unless the user asked for a rewrite pass.

---

## 1. Punctuation bans

- **Never use the em dash (Unicode U+2014) or en dash (U+2013).** Use a period, comma, colon, parentheses, or ASCII hyphen with spaces (` - `).
- **Never use curly smart quotes** in new docs unless the file already uses them. Prefer straight `"` and `'`.
- **Never spam ellipsis** (`…` or `...`) for fake drama.

---

## 2. Banned words (prefer plain English)

Do not use these unless quoting a user or a legal/brand name that forces them.

### Soft-focus verbs
delve, leverage, utilize, facilitate, underscore, foster, navigate (metaphor), harness, showcase, unpack, spearhead, bolster, embark, streamline (as hype), optimize (as empty hype), enhance (empty), elevate, unlock, empower, transform / transformative, revolutionize

### Soft-focus nouns
tapestry, landscape (as metaphor: "the landscape of…"), realm, synergy, paradigm, cornerstone, beacon, testament, journey (as metaphor for a feature), ecosystem (when you mean "stack" or "app"), discourse, confluence

### Soft-focus adjectives / intensifiers
robust, seamless, cutting-edge, state-of-the-art, groundbreaking, innovative (empty), holistic (except skill names that already say it), multifaceted, nuanced (as filler), pivotal, paramount, meticulous, comprehensive (as filler), actionable (as filler), overarching, unprecedented, quintessential, vibrant, rich (as filler for UI)

### Corporate sludge
stakeholders (say who), bandwidth (say time), circle back, move the needle, low-hanging fruit, value-add, best-in-class, next-generation, world-class, turnkey, frictionless (unless measuring real UX friction)

---

## 3. Banned phrases

### Throat-clearing / chatbot residue
- "Certainly!", "Absolutely!", "Great question!", "Of course!", "Happy to help"
- "I'd be happy to…", "Let me know if you need anything else", "I hope this helps"
- "As an AI…", "As a language model…", "As an assistant…"
- "Here is a comprehensive overview…", "Below is a breakdown…"

### Academic / blog filler
- "It is important to note that…", "It is worth noting / mentioning…"
- "In today's landscape / fast-paced world…"
- "In the realm of…", "When it comes to…"
- "Plays a crucial / critical / vital / key role in…"
- "This highlights the importance of…"
- "A wide range of…", "A myriad of…", "A plethora of…"
- "Navigating the complexities of…"
- "At its core…", "In essence…", "At the end of the day…"
- "That being said…", "With that in mind…"
- "In conclusion…", "In summary…", "To summarize…" (as a closing ritual)
- "Moreover…", "Furthermore…", "Additionally…" stacked as fake sophistication
- "Whether you are X or Y…", "There is something for everyone"

### Fake profundity
- "Not just X, but Y" / "It's not about X; it's about Y"
- "In a world where…"
- Three-adjective triads: "clear, concise, and compelling"
- Rhetorical Q then immediate soft answer: "So what does this mean? It means…"

---

## 4. Structure bans

- **No emoji decoration** in serious product/design/PR docs (✅❌🚀✨💡 unless the user asked for emoji).
- **No markdown theater:** giant horizontal rules, badge spam, or "TL;DR" boxes that restate the same fluff.
- **No symmetric list padding:** inventing a third bullet so every section has exactly three.
- **No hedge stacks:** "may potentially possibly be beneficial to consider…"
- **No empty section titles:** "Overview", "Key insights", "Final thoughts" with no concrete content under them.
- **No forced parallelism:** do not format every bullet as the same "Noun: Explanation" or "Imperative: Clarification" pattern.
- **No fence-sitting** on evaluation asks: take a stance unless the user asked for a neutral multi-perspective overview.
- **No throat-clearing openings or ribbon endings:** start with the point; stop when the point is made.

---

## 5. Positive defaults (what to do instead)

| Instead of | Write |
|------------|--------|
| delve into X | check X / read X / measure X |
| leverage Y | use Y |
| robust solution | works under Z load / handles Z errors |
| seamless experience | fewer clicks / no extra login |
| stakeholders | Jordan (PM) / eng / design |
| landscape of tools | the tools we use: A, B |
| groundbreaking UX | specific change: larger hit target, clearer empty state |

- Vary sentence length. Mix short blunt lines with longer ones when needed.
- Concrete nouns and verbs. Name the object, describe the action, move on.
- Contractions are fine (`don't`, `isn't`) unless the surface demands formal register.
- Write like a practitioner who did the work, not an observer at 30,000 feet.
- Match `product.md` Voice & tone when defined; otherwise stay plain and direct.
- Prefer verbs humans say out loud.

---

## 6. Where this applies

**Default: everything you author.** The table below is examples, not an allowlist. Missing from the table does **not** mean out of scope.

| Surface | Rule |
|---------|------|
| Chat replies in any skill session | Required |
| Books, manuscripts, chapters, worksheets, GTM long-form | Required for text you write or edit |
| READMEs, docs, guides, ADRs, notes | Required |
| `.heyeddi/product.md`, feature specs, reviews | Required |
| `.heyeddi/design.md`, briefs, critiques, Decision log | Required |
| Mockup briefs / handoff notes | Required |
| PR review docs and GitHub comment replies | Required |
| Skill stdout hints and maintained `SKILL.md` text | Required |
| UI strings (Vue, Flutter, locales) | Required |
| Code comments | Prefer none; if needed, same rules |

**Not an exemption:** "local voice", "editorial style already uses em dashes", "UI/product gate only", or substituting Cursor `deslop` (that skill is for **code** structure, not prose).

---

## 7. Finish checklist

- [ ] No em dash (U+2014) or en dash (U+2013) in text you authored
- [ ] No banned words/phrases from sections 2 to 3
- [ ] No chatbot openers or "I hope this helps"
- [ ] No emoji theater or triad padding
- [ ] Claims are concrete (named thing, measurable outcome, or clear instruction)
- [ ] Reads like a sharp teammate, not a launch blog

**Smell test:** Would you paste this into Slack to a tired coworker? If it would get an eye-roll, rewrite.

---

## Related

- Checker: `@heyeddi-design` `verify_prose.py --check` (default: Vue, locale JSON, `.heyeddi/product.md`, `.heyeddi/design.md`). For books or other paths: `--glob 'chapters/**/*.md'` (repeatable). Default globs stay narrow so whole lit trees do not explode; **behavior still applies** when you write those files.
- UI craft anti-slop: `@heyeddi-design` `reference/modern-reference.md` / `@taste-penpot` `references/anti-slop.md`
- Hub canonical: repo `docs/prose-anti-slop.md` (copy into every skill as `context/PROSE_ANTI_SLOP.md`)
- Code slop (comments / `any` / nesting): Cursor team-kit `deslop` skill — **not** a substitute for this file
