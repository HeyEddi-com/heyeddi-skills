# Discover: discovery interview

**Scope:** Understand the request deeply. No code, no wireframes, no `DESIGN.md` writes.

**Trigger:** Vague brief, first message with no sub-command, or `@heyeddi-design discover`.

## Rules

- **Do NOT** write code or make visual decisions during discovery.
- **Do NOT** dump all questions at once: natural dialogue, **2-3 questions per round**, then wait.
- Use the structured question tool when available; otherwise ask in chat and stop.
- Treat `PRODUCT.md` and `DESIGN.md` as anchors; skip questions they already answer.
- **Assert-then-confirm:** when one answer is obvious from context, state it and ask to confirm or override: don't offer four-option menus for settled choices.
- At least **one user-answer round** unless repo docs fully answer purpose, audience, personas, and scope.
- If `product.md` lacks **Personas** or **Per-route intent**, cover those in this interview (or route to `@heyeddi-intake`).

## Translate plain language

Users won't say "information architecture" or "Restrained color strategy." Map their words. Read **`reference/brief-language.md`** — adjective-only briefs are incomplete.

| User says | You clarify |
|-----------|-------------|
| "enterprise view" | B2B admin? density? data tables? sidebar nav? roles/permissions? |
| "clean / modern / professional" | **Not enough.** Force subject/metaphor + hard rejects + 2–3 named references (what to steal). Never craft on the adjective alone. |
| "like Notion / Linear / Salesforce" | What specifically: nav, density, typography, settings IA? Borrow X not Y. |
| "login" / "sign in" | Apply **sign-in** archetype in `surface-completeness.md`: recovery links, remember me, SSO?, invite-only? |
| "wow" / "alive" / "impressive" | Intensity dial + calm-wow translation (`aesthetic-direction.md`); still need subject + rejects |

**First-round priority (flagship / marketing):** in the first 2–3 questions, pin **subject/metaphor**, **hard rejects** ("do not look like X"), and **single page job**. Taste before chrome.

## Interview areas

Cover what's missing from `PRODUCT.md` / `DESIGN.md` / the user's prompt:

### Purpose & context
- What is this for? What problem does it solve?
- Who uses it specifically? (role, frequency, context: not "users")
- User's state of mind when they arrive (rushed, exploring, anxious, focused)
- What does success look like?

### Content & data
- What data or content appears on this surface?
- Realistic ranges (empty, typical, max: e.g. 0 / 5 / 500 rows)
- Edge cases: empty, error, first-time, power user
- Dynamic content and update frequency

### Design direction (skip only if DESIGN.md + brief already answer — see `brief-language.md`)
- **Subject / metaphor:** one concrete world (cartographer's desk, instrument panel, …) — not "SaaS dashboard"
- **Hard rejects:** explicit anti-defaults (fonts, palette kits, boxed heroes, opaque slabs, purple/cream AI looks, …)
- **Hero composition** (brand register): full-bleed? brand loudest? one headline / lede / CTA group / visual?
- **Typography roles:** which faces for logo/H1/H2 vs body; what wordmark treatments are forbidden
- **Accent system:** brand/UI accent vs edge/data accent (edges must read on the plane)
- **Responsive contract:** desktop vs mobile stack order (e.g. copy before graph on mobile)
- **Token SSOT:** one token file; change brand/edge once
- **Color strategy:** Restrained / Committed / Full palette / Drenched
- **Theme scene sentence:** who, where, ambient light, mood
- **3 references + what to steal** (borrow X not Y)
- **Intensity dial:** marketing atmosphere vs quieter app shell, same language
- **Motion budget:** 2–3 intentional motions; reduced-motion
- **Ambition / aesthetic risk:** one justified bold choice; memorable vs competitors

### Scope
- **Fidelity:** sketch / mid-fi / high-fi / production-ready
- **Breadth:** one screen / flow / whole surface
- **Interactivity:** static / prototype / shipped-quality
- **Time intent:** quick exploration vs ship-ready

### Constraints & anti-goals
- Mobile/responsive requirements (state the stack-order contract)
- Accessibility beyond WCAG AA?
- What should this **NOT** be? Biggest risk if wrong? (hard rejects go here if not already named)

## Exit

When discovery gaps are filled, either:

- User invoked **`discover` only** → summarize findings in 5-8 bullets and ask whether to continue to **`shape`** (research + explore + brief).
- User is in **`shape`** → proceed to `reference/research.md` automatically.

Do not write the final design brief until research and explore phases complete (unless user explicitly skips with "no research" / "skip images").
