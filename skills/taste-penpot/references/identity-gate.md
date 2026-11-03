# Identity gate (mandatory before a new look)

**Date:** 2026-11-02

Design work starts with an **identity**, not with pixels. If the user did not
pin a style, brand, or visual world, you must **propose at least three
identities**, explain them, and **stop until they choose**. Do not invent a
look and ship it.

This gate is owned by `@taste-penpot`. `@heyeddi-design` records the chosen
identity; it does not invent a fourth lane.

## When the gate runs

Run the gate **before** PLAN 1.4 (tokens), Penpot boards, HTML demos, craft,
or Vue edits when **any** of these are true:

- New surface / greenfield look with no pinned brand in the request
- Redesign, from scratch, new look, overhaul, "make it not generic"
- `.heyeddi/design.md` has no usable identity (no named subject/metaphor,
  type roles, and colour roles with values)
- User only gave vague adjectives: professional, clean, modern, nice, pretty,
  wow, better, SaaS-looking

## When the gate is skipped

Skip (state one line why) when **all** that apply hold:

- **Refine / polish / local fix** and `.heyeddi/design.md` (or Penpot file)
  already defines the identity, **and** the user did not ask to replace it
- User **pinned** fonts, colours, era, materials, metaphor, or a named brand
  system in this turn (obey that; do not open a second identity contest)
- User already **chose** an identity earlier in this chat (reuse it)

Refine preserves. Redesign replaces — and a replace always re-opens the gate
unless the user pinned the replacement identity themselves.

## Ground the options in the project

Before writing options, read what exists (skip missing files quietly):

- `.heyeddi/product.md` / `PRODUCT.md` — who, job, category, tone
- `.heyeddi/design.md` / `DESIGN.md` — current tokens (for contrast, not reuse
  on redesign)
- `.heyeddi/stack.json` — stack cues
- Intake / routing notes under `.heyeddi/docs/` when present
- Real product nouns (domain, materials, rituals) — never invent customers

Every option must feel like it belongs to **this** product. If someone could
guess the aesthetic from the category alone ("generic fintech blue", "purple
AI SaaS"), rewrite that option.

## Present at least three options

Propose **≥3** identities that differ in **world**, not only hue. Bad: three
blues. Good: atlas desk vs night ops console vs quiet editorial instrument.

For **each** option, use this block (keep it skimable, ~8–12 lines):

```markdown
### Option A — <short name>
- **Identity / metaphor:** one concrete world (who it is for, what place it feels like)
- **Personality:** 3 adjectives + one sentence of tone
- **Typography:** display face + body face (named), roles (logo / H1 / body / UI)
- **Colour:** strategy (Restrained | Committed | Full | Drenched) + light/dark intent
  - canvas / surface / text / accent / border — **named hex values**
- **Hard rejects:** 2–3 things this lane refuses (anti-slop + category defaults)
- **Why this product:** one sentence tied to product.md / audience / domain
```

Also state in one line which surfaces the choice covers (marketing, app shell,
both) and the mode (Persuade / Operate / Read / Experience).

**Images:** optional. If GenerateImage (or equivalent) is available, you may
attach one probe per option. Text + hex + type is enough to choose. Never delay
the gate waiting on image APIs.

## Hard stop

After presenting the options:

1. Ask the user to pick **A / B / C** (or a hybrid: "A type + B colour").
2. **End the turn.** Do not PLAN tokens, open Penpot, write HTML, or craft UI
   in the same response.
3. Only after an explicit choice (`A`, `go with B`, `B but warmer accent`, …)
   continue PLAN → ACT with that identity locked.

If the user says "you choose", pick one, state which and why in two lines, then
proceed — that counts as a choice.

## After choice

1. Lock the five-line brief (Mode / Audience / Goal / Proof / Direction) using
   the chosen identity.
2. Write tokens from that identity only (`references/taste-rules.md`).
3. Hand the named tokens to `@heyeddi-design` for `.heyeddi/design.md` — no
   second palette.
4. On redesign, keep product truth; replace the visual system for pages in scope
   (`references/code-to-design.md`).

## Anti-patterns

- NEVER ship a first look when the user only said "modern" / "clean" / "professional"
- NEVER present three palette swaps of the same layout and call them identities
- NEVER continue to ACT before a choice (unless the gate was correctly skipped)
- NEVER ignore a pinned brand to run the gate "for completeness"
- NEVER invent a second identity after the user already chose in this chat
