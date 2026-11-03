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

**Prerequisite:** Identity already locked via `@taste-penpot` `references/identity-gate.md` (or gate correctly skipped). Explore does **not** replace the identity gate. If identity is still unset, stop and run the gate first.

Generate **2-4** probes that vary hierarchy, density, nav topology, or composition **inside the chosen identity**: **not** three unrelated brands and **not** palette-only swaps.

Each probe should answer: *Would this still feel like the chosen identity, or a different product?* Reject lanes that abandon the locked metaphor/type/colour roles.

Base probes on:

- The **chosen** identity (metaphor, type, hex roles, hard rejects)
- Discovery: scene sentence, anchors, anti-goals
- Research: trends and patterns to adopt/avoid

**Use native image generation** when the harness provides it. See **`reference/visual-tools.md`** for GenerateImage, Canvas, and when each is mandatory.

After generating:

- Ask which **composition / density** feels closest within the locked identity
- Do not treat images as final spec: they refine the brief, not reopen identity

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
