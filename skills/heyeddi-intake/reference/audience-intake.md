# Audience intake: product.md schema

**Date:** 2026-07-04

`write_product` must produce these sections for greenfield products. Downstream design skills **block craft** on flagship routes if missing.

## Required sections

### Personas

| Name | Role | Primary job | Anxiety | Design implication |
|------|------|-------------|---------|-------------------|
| … | … | … | … | … |

Minimum **2 personas** for B2B SaaS (buyer/evaluator + daily user).

### Per-route intent

| Route | Register | Primary persona | User mindset | Success feeling |
|-------|----------|-----------------|--------------|-----------------|
| `/` | brand | … | … | … |
| `/dashboard` | product | … | … | … |

### Competitors

- Users compare us to: …
- We win on: …
- We intentionally avoid: …

### Anti-audience

Who this product is **not** for (prevents wrong aesthetic).

### Voice & tone

One paragraph: plain/confident/technical; verb-first buttons; error voice.

## JSON for `write_product --json`

```json
{
  "product_name": "TaskFlow",
  "audience_summary": "Small B2B teams (5-30 people) coordinating work.",
  "personas": [
    {
      "name": "Jordan",
      "role": "Team lead",
      "primary_job": "See blockers and team capacity",
      "anxiety": "Missing updates, tool sprawl",
      "design_implication": "Calm dashboard density, clear status"
    },
    {
      "name": "Riley",
      "role": "IC contributor",
      "primary_job": "Update tasks quickly",
      "anxiety": "Clutter, slow flows",
      "design_implication": "Focused app chrome, minimal marketing in app"
    }
  ],
  "route_intent": [
    {
      "route": "/",
      "register": "brand",
      "primary_persona": "Jordan",
      "mindset": "Skeptical, comparing tools",
      "success_feeling": "This looks trustworthy and focused"
    }
  ],
  "competitors": ["Asana", "Linear"],
  "competitive_edge": "Simpler team roster view without project-management sprawl",
  "anti_audience": "Enterprise IT with mandatory SSO-only procurement",
  "voice_tone": "Plain, confident, no buzzwords; verb-first CTAs",
  "pages": [],
  "design_references": [],
  "anti_references": []
}
```

## Clarify round

In a build request, infer personas and competitors from the repo and the prompt, record them as assumptions, and continue. In a discovery request (`@heyeddi-intake` from the user) with no audience hints, ask **one round** (2-3 questions):

- Who uses this daily vs who buys/evaluates?
- What do they compare you to?
- What should it **not** feel like?

Then write product.md: do not guess personas silently.
