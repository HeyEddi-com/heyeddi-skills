# Audience-driven design direction

**Date:** 2026-07-04

Read with `product.md` **Personas** and **Per-route intent** before `research`, `shape`, `craft`, or `polish`.

`modern-reference.md` = **how** (CSS, surfaces, type).  
This file = **who** and **why**: which direction fits this product.

## Step 1: Identify primary persona for this route

From `product.md` → **Per-route intent** → `primary_persona`.  
If missing: in a build request, derive it from product.md and the repo, record the assumption, and continue; in a design request, run `discover` or `@heyeddi-intake`.

## Step 2: Map signals → direction

| Audience signal | Design direction | Borrow (pattern) | Avoid |
|-----------------|------------------|------------------|-------|
| B2B team lead, ops | Calm density, trust | Stripe Dashboard, Linear app | Playful gradients, consumer gamification |
| SMB founder / small team | Warm, approachable | Notion marketing, Superhuman settings | Enterprise table sprawl, cold gray admin |
| IC / daily user | Focus, speed | Linear, Superhuman | Marketing hero on app routes |
| Evaluator / buyer (homepage) | Credibility, clarity | Vercel marketing, Stripe.com | Feature dump, stock photo hero |
| Power user | Keyboard, density | Raycast, Linear | Oversized padding, wizard flows |
| Regulated / HR / finance | Conservative, accessible | Stripe, gov.uk patterns | Trendy glass, bold color blocks |

Pick **one primary row** + at most **one secondary** for the route. Document in brief + Decision log.

## Step 3: Register × persona

| Register | Persona mindset | Layout | Copy |
|----------|-----------------|--------|------|
| **brand** (`/`, marketing) | Skeptical, comparing | Editorial width, hero + proof | Outcome-led, social proof |
| **product** (app routes) | Task-focused, time-poor | Shell + focused main | Verbs, status, no fluff |
| **handoff** (settings) | Wants control, low anxiety | Card stack, one save | Labels plain, errors helpful |

## Step 4: Competitors (differentiate, don't clone)

From `product.md` **Competitors**:

- Name **one thing** users like about each competitor
- Name **one thing** TaskFlow/your product does differently for **this persona**
- Reflect differentiation in hero copy, dashboard density, or settings IA: not logo colors

## Step 5: Voice & tone

From `product.md` **Voice & tone**:

- Headlines: match energy (confident vs friendly vs technical)
- Buttons: verb-first (`Start free trial` not `Submit`)
- Empty states: speak to persona anxiety from the Personas table

## Step 6: Research queries (audience-aware)

Form searches like:

- `"<persona role> <job> software UI 2026"`
- `"<competitor> vs <category> dashboard patterns"`
- `"<industry> SaaS trust signals homepage"`

Synthesize in `research.md` → **Audience fit** section (required).

## Brief requirement

Every `designs/<feature>/brief.md` must include:

```markdown
## Audience
- **Primary persona:** …
- **Route intent:** mindset + success feeling (from product.md)
- **Direction row:** (from table above)
- **Differentiation:** one line vs competitors
```

## Craft checklist (in addition to modern-reference)

- [ ] First 5 seconds: would **primary persona** understand what this is for?
- [ ] Primary action matches **primary job** in Personas table
- [ ] Copy tone matches Voice & tone
- [ ] Does NOT look designed for anti-audience in product.md
- [ ] Decision log: persona + pattern borrowed + competitor differentiation

## Related

- `modern-reference.md`: technique execution
- `audience-fit.md`: post-build critique rubric
- `discover.md`: fill gaps in product.md
