# Identity gate (mandatory before a new look)

**Date:** 2026-11-07

Design work starts like a real designer: **understand the product, study the
field, take a stance, then offer directions** — not pixels. If the user did not
pin a style, brand, or visual world, you must run this gate, document it under
`.heyeddi/`, and **stop until they choose**. Do not invent a look and ship it.

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
- Scaffolding a working app (reader, dashboard, CLI shell, …) that still needs
  a first look — **functionality never waives this gate**

## When the gate is skipped

Skip (state one line why) when **all** that apply hold:

- **Refine / polish / local fix** and `.heyeddi/design.md` (or Penpot file)
  already defines the identity, **and** the user did not ask to replace it
- User **pinned** fonts, colours, era, materials, metaphor, or a named brand
  system in this turn (obey that; do not open a second identity contest)
- User already **chose** an identity earlier in this chat (reuse it)

Refine preserves. Redesign replaces — and a replace always re-opens the gate
unless the user pinned the replacement identity themselves.

**Never skip because:** "MVP", "scaffold first", "EPUB/PDF works", "clean
workable UI", "I'll taste later", or "quick Fraunces + teal while shipping."

---

## Phase 0 — Designer thinking (before options)

Think out loud like a hired design lead. Do this **before** writing identity
options. Write the result into the consumer app's `.heyeddi/` folder (create
dirs as needed). Prefer:

`.heyeddi/designs/<feature>/identity-thinking.md`

Use kebab-case `<feature>` (e.g. `margin-reader`, `marketing-home`). If the
feature name is unclear, use `identity` for this pass.

### 0.1 What is this project?

From `.heyeddi/product.md` / `PRODUCT.md`, intake docs, README, and real nouns
in the repo (skip missing files quietly):

- **Job** — what the product does in one sentence
- **Audience** — who uses it, in what state of mind
- **Materials / rituals** — domain objects (books, margins, ledgers, stages…)
- **Surfaces in scope** — marketing, app shell, reader, both
- **Tone already claimed** — anything in product.md that must survive

If job or audience is missing and cannot be inferred safely: **ask 2–3
clarifying questions, document the answers into `identity-thinking.md`, and
wait** before Phase 0.2. Do not invent customers or capabilities.

### 0.2 What are others doing?

Name the **category default** (what peers look like in 2025–2026) in 3–6
bullets. Prefer web search when the category is unfamiliar; otherwise use
known anchors from `@heyeddi-design` `reference/modern-reference.md` and
state that you did. Cover:

- Typical type / density / chrome in this category
- Clichés users would recognise as "another X app"
- 1–2 reference products and **what** (not the whole brand) is worth borrowing

### 0.3 Follow the tendency or be unique?

State an explicit **stance** in 2–4 lines:

| Stance | When |
|--------|------|
| **Follow** | Trust and familiarity matter more than surprise (banking, medical, dense ops) |
| **Tilt** | Keep category cues; change one axis hard (type, material, or metaphor) |
| **Break** | Category look is exhausted or the product's world demands a different lane |

Recommend a default stance for this product, then let options span at least
two stances so the user can push back.

### 0.4 Document before pixels

`identity-thinking.md` must include sections: **Project**, **Peers**,
**Stance**, **Open questions** (answered or still waiting). Chat may
summarise; the file is the SSOT for this pass.

---

## Phase 1 — Present 3 to 5 options

Propose **3–5** identities (default **4** when the category has clear lanes;
never fewer than **3**, never more than **5**). They must differ in **world**,
not only hue. Bad: three blues. Good: atlas desk vs night ops console vs quiet
editorial instrument vs living paper theater.

For **each** option, use this block (skimable, ~10–14 lines):

```markdown
### Option A — <short name>
- **What it is:** plain-language world (who it is for, what place it feels like)
- **Why it is:** product job + audience + competitive stance (follow / tilt / break)
  and one sentence on the risk it takes
- **How it is:**
  - **Typography:** display + body (named), roles (logo / H1 / body / UI)
  - **Colour:** strategy (Restrained | Committed | Full | Drenched) + light/dark
    intent; canvas / surface / text / accent / border — **named hex values**
  - **Layout / material cues:** density, atmosphere, one signature device
  - **Hard rejects:** 2–3 things this lane refuses (anti-slop + category defaults)
- **Personality:** 3 adjectives + one tone sentence
```

Also state in one line which surfaces the choice covers (marketing, app shell,
both) and the mode (Persuade / Operate / Read / Experience).

After the options, add a short **compare** line: which option follows the
category, which tilts, which breaks — so the user can choose strategy, not
only aesthetics.

**Images:** optional. If GenerateImage (or equivalent) is available, you may
attach one probe per option. Text + hex + type is enough to choose. Never delay
the gate waiting on image APIs.

Also write the same options into:

`.heyeddi/designs/<feature>/identity-options.md`

so the choice is durable after chat scrolls away.

---

## Hard stop

After presenting the options:

1. Ask the user to pick **A / B / C / D / E** (or a hybrid: "A type + B colour").
2. **End the turn.** Do not PLAN tokens, open Penpot, write HTML, or craft UI
   in the same response.
3. Only after an explicit choice (`A`, `go with B`, `B but warmer accent`, …)
   continue PLAN → ACT with that identity locked.

If the user says "you choose", pick one, state which and why in two lines, then
proceed — that counts as a choice.

Clarifying questions in Phase 0 also **end the turn** when answers are needed.
Do not invent a look while waiting.

---

## After choice

1. Lock the five-line brief (Mode / Audience / Goal / Proof / Direction) using
   the chosen identity.
2. Append the choice + rationale to `.heyeddi/designs/<feature>/identity-options.md`
   and hand named tokens to `@heyeddi-design` for `.heyeddi/design.md`.
3. Write tokens from that identity only (`references/taste-rules.md`).
4. On redesign, keep product truth; replace the visual system for pages in scope
   (`references/code-to-design.md`).

## Anti-patterns

- NEVER ship a first look when the user only said "modern" / "clean" / "professional"
- NEVER skip Phase 0 and dump three palettes
- NEVER present three palette swaps of the same layout and call them identities
- NEVER continue to ACT before a choice (unless the gate was correctly skipped)
- NEVER ignore a pinned brand to run the gate "for completeness"
- NEVER invent a second identity after the user already chose in this chat
- NEVER waive the gate for scaffolding, readers, demos, or "workable" UI
- NEVER keep thinking only in chat — write `.heyeddi/designs/<feature>/identity-thinking.md`
  and `identity-options.md` before ACT
