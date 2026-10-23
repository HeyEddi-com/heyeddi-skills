# Prose anti-slop (HeyEddi skills)

**Date:** 2026-07-16

**Rule:** If it sounds like a LinkedIn post, a launch blog, or ChatGPT, rewrite it. Visual UI anti-slop stays in `@heyeddi-design` `reference/modern-reference.md`. This file is about **words**.

Agents must apply this to product copy, design docs, PR replies, handoff briefs, skill stdout, chat, and UI strings.

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

- Short sentences. One idea each.
- Concrete nouns: routes, files, personas, acceptance criteria.
- Match `product.md` Voice & tone when defined.
- UI strings: product voice, not marketing cadence.
- Prefer verbs humans say out loud.

---

## 6. Where this applies

| Surface | Rule |
|---------|------|
| `.heyeddi/product.md`, feature specs, reviews | Required |
| `.heyeddi/design.md`, briefs, critiques, Decision log | Required |
| Mockup briefs / handoff notes | Required |
| PR review docs and GitHub comment replies | Required |
| Skill stdout hints and maintained `SKILL.md` text | Required |
| Chat replies while running these skills | Required |
| Code comments | Prefer none; if needed, same rules |

---

## 7. Finish checklist

- [ ] No em dash (U+2014) or en dash (U+2013)
- [ ] No banned words/phrases from sections 2 to 3
- [ ] No chatbot openers or "I hope this helps"
- [ ] No emoji theater or triad padding
- [ ] Every claim names a file, route, persona, or measurable outcome
- [ ] Reads like a sharp teammate, not a launch blog

**Smell test:** Would you paste this into Slack to a tired coworker? If it would get an eye-roll, rewrite.

---

## Related

- UI craft anti-slop: `@heyeddi-design` `reference/modern-reference.md` (when installed)
- Hub canonical: repo `docs/prose-anti-slop.md`
- Code slop (comments / `any` / nesting): Cursor team-kit `deslop` skill
