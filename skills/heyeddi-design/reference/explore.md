# Explore: concept images and wireframes

**Scope:** Visual direction probes and wireframe-level layouts. No production Vue code.

**When:** After discovery + research, before the final brief. Part of **`shape`**.

## Skip conditions

Skip explore (announce in one line why) when:

- Fidelity is **sketch-only** planning, or
- User explicitly said no images / no wireframes, or
- Image generation is unavailable in the harness **and** Canvas is unavailable: proceed to brief with text-only wireframes (ASCII or markdown blocks).

Do not ask the user to install image APIs.

## Phase A: Visual direction probes (when available)

Generate **2-4** distinct direction probes differing in hierarchy, density, nav topology, typographic voice, or color strategy: **not** palette swaps or the same layout with different hues.

Each probe should answer: *Would this feel like a different product identity, or the same template recolored?* Reject lanes that only change primary color.

Base probes on:

- Discovery: color strategy, scene sentence, anchors, anti-goals
- Research: trends and patterns to adopt/avoid

**Use native image generation** when the harness provides it. See **`reference/visual-tools.md`** for GenerateImage, Canvas, and when each is mandatory.

After generating:

- Ask which direction feels closest, what's off, what should carry forward
- Do not treat images as final spec: they test lanes for the brief

## Phase B: Wireframes

Produce wireframes for **key screens/states** in the scoped breadth:

| Fidelity | Wireframe format |
|----------|------------------|
| Sketch | ASCII or markdown block layout in `designs/<feature>/wireframes/*.md` |
| Mid-fi+ | Simple HTML files in `designs/<feature>/wireframes/` (OpenProps spacing, grayscale, no polish) OR structured markdown with labeled regions |

Include at minimum:

- Default / happy path
- Empty state (if applicable)
- Mobile stack order (375px intent) noted per screen

Wireframes must label:

- Regions and component intent (e.g. "DataTable: recent orders", "Sidebar: org nav")
- Primary action per screen
- PrimeVue component mapping hints where obvious

## Exit

Revise discovery inputs if probes or wireframes reveal a mismatch. Then proceed to the design brief in `reference/shape.md` (Phase: Brief).
