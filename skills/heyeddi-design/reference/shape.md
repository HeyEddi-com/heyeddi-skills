# Shape: full design planning flow

**Scope:** Plan before pixels or code. Output is a **confirmed design brief** + artifacts.

**Replaces:** impeccable `shape`. Orchestrates discover → research → explore → brief.

## Pipeline

```
identity gate (designer thinking → 3–5 options → user picks)
  → discover → research → explore → brief → user confirms → hand off to craft
```

Load and follow each phase in order:

0. **Identity gate (hard when unset):** Load `@taste-penpot` → `references/identity-gate.md`. If no pinned style and not refining an existing `design.md` identity: write identity-thinking under `.heyeddi/designs/`, ask if blocked, present **3–5** What/Why/How options, **end the turn**, wait for A–E. Do not invent a look. Scaffolding never skips. Skip only when refine preserves an existing system or the user already pinned/chose an identity.
1. `reference/discover.md`: discovery interview (personas if missing from product.md)
2. `reference/research.md`: web trend research → `designs/<feature>/research.md` (**Audience fit** section required)
3. `reference/explore.md`: concept images + wireframes + **visual tools** (`reference/visual-tools.md`) — probes must match the **chosen** identity, not open a second identity contest
4. Read `reference/audience-design.md`: pick direction row before writing brief
4b. Read `reference/brief-language.md`: subject/metaphor, hard rejects, hero/type/accent/responsive/SSOT — adjective-only briefs are incomplete
4c. Read `reference/design-ambition.md`: draft **Design signature** for flagship routes
4d. Read `reference/aesthetic-direction.md`: subject/job, thesis hero, type, motion, one aesthetic risk; run two-pass uniqueness check before locking the brief
5. **Brief** (below) → `designs/<feature>/brief.md`
6. **Stop and wait** for explicit user confirmation of the brief (separate from identity pick)

User may opt out of research or explore with explicit consent: note skips in the brief. They may **not** opt out of the identity gate when it applies.

## Design brief

After phases 1-3, write the brief to `designs/<feature>/brief.md` and present in chat.

**Choose format:**

- **Compact (3-5 bullets)** when discovery was crisp and scope is one screen
- **Full structured form** when multi-screen, ambiguous, or standalone shape run

### Full brief structure

1. **Feature summary**: what, who, outcome (2-3 sentences)
2. **Audience**: primary persona, route intent, direction row, differentiation (from `audience-design.md`)
3. **Design signature** (`design-ambition.md` + `brief-language.md` + `aesthetic-direction.md`): **required on flagship routes**
   - Aesthetic energy; **subject / metaphor** (one concrete world); audience; single page job
   - Signature moment; **one aesthetic risk**
   - **Borrow:** 3 references + what to steal (X not Y)
   - **Hard rejects / Avoid:** explicit anti-defaults (not "don't be generic")
   - **Hero composition** (brand register): full-bleed?, brand loudest?, headline/lede/CTAs/visual
   - **Typography roles**; **accent vs edge**; **responsive contract** (desktop vs mobile stack)
   - **Token SSOT**; intensity dial; motion budget (2–3); memorable detail
4. **Primary user action**: single most important action or understanding
5. **Design direction**: color strategy, scene sentence, anchors; note research-informed choices and winning probe direction if explore ran
6. **Scope**: fidelity, breadth, interactivity, time intent
7. **Layout strategy**: hierarchy, emphasis, information flow (not CSS) — structure encodes information, not fake 01/02/03 chrome; first-viewport checklist when marketing
8. **Key states**: default, empty, loading, error, success, edge cases
9. **Interaction model**: clicks, navigation, feedback, flow entry → completion; motion budget if any
10. **Content requirements**: labels, microcopy, dynamic ranges
11. **Component map**: PrimeVue + layout blocks per region (from wireframes)
12. **`## Deferred wiring`**: UI shipped now vs backend/API later (see `surface-completeness.md`)
13. **Done gate**: logo-off brand test + `@visual-auditor --preset done` widths before ship
14. **Open questions**: only genuinely unresolved items

**Completeness:** Read `reference/surface-completeness.md`: map all regions and archetype affordances in the brief. Do not defer UI to "later" without still designing it; record wiring in **Deferred wiring**.

## Confirmation gate

- Present the brief and **end the response**.
- Do **not** implement in the same turn as the brief.
- If user disagrees, revisit the relevant phase.
- Shape is incomplete until explicit confirmation ("yes", "proceed", "looks good").

## After confirmation

Recommend:

```
@heyeddi-design craft <feature or route>
```

Or user may implement manually using the brief.

If `DESIGN.md` is missing or stale after shape, recommend `@heyeddi-design document` before craft.
