# Visual tools: show the design (IDE + agent)

**Date:** 2026-09-02

Use Cursor / agent tooling to **show** design direction — not only describe it in chat. This skill authorizes visual output during `explore`, `shape`, and `critique` without waiting for the user to say "generate an image."

Read `~/.cursor/skills-cursor/canvas/SKILL.md` before writing any `.canvas.tsx`.

## Tool matrix

| Tool | Use in design | Do not use for |
|------|----------------|----------------|
| **Cursor `GenerateImage`** | 2–4 **direction probes** (mood, hierarchy, nav topology, type voice) | Final spec, accessibility proof, production assets |
| **Cursor Canvas** (`.canvas.tsx`) | Direction comparison, brief review, token/type scale, critique summary, interactive wireframe map | Production Vue/Flutter, data charts, replacing `@visual-auditor` on live app |
| **`@visual-auditor`** | Implemented UI at 375/768/1440 — fix in code | Greenfield concept before code exists |
| **Markdown / ASCII wireframes** | `designs/<feature>/wireframes/` — always write these too | Replacing probes when image tools work |

## When mandatory

During **`explore`** (and `shape` before brief confirmation):

1. If **GenerateImage** is available → produce **2–4** distinct direction probes per `explore.md` (not palette swaps).
2. If **Canvas** is available and probes differ materially → open a **direction comparison** canvas (side-by-side lanes + short labels).
3. Always save **text wireframes** under `.heyeddi/designs/<feature>/wireframes/` even when images exist.
4. Before user confirms brief → optional **brief review canvas** (persona, regions, design signature, primary CTA).

Skip visuals only when user explicitly opts out ("no images", "text only", sketch-only) or the harness truly lacks both GenerateImage and Canvas — say so in one line.

## GenerateImage (direction probes)

**Authorized** during `@heyeddi-design explore` / `shape` — does not require a separate user image request.

Prompt each probe with:

- Product subject + page job (from discovery)
- Register: `product` (app) vs `brand` (marketing)
- Named borrow from `research.md` (what specifically — not "like Linear")
- One axis that **differs** from other probes (density, nav, type, atmosphere)
- Anti-goals from discovery (e.g. no purple SaaS hero, no generic KPI card)

Suggested `aspect_ratio`:

| Surface | Ratio |
|---------|--------|
| App shell / dashboard | `16:9` |
| Mobile-first screen | `9:16` |
| Marketing hero | `16:9` or `3:4` |
| Icon / mark exploration | `1:1` |

After generation:

- Ask which lane feels closest; what to carry forward
- Reference probe filenames or chat attachments in `brief.md` under **Visual direction**
- Images are **lanes to test**, not handoff mockups (`@heyeddi-handoff` needs Implementation spec)

## Canvas (interactive design artifacts)

Create `.canvas.tsx` in the workspace `canvases/` directory (see canvas skill for path rules).

**Good canvas deliverables for design:**

| Canvas | Contents |
|--------|----------|
| **Direction compare** | 2–3 columns: lane name, thumbnail or description, borrow, avoid |
| **Brief review** | Persona, route job, regions table, design signature, open questions |
| **Token preview** | Semantic tokens from `design.md` / brief — surfaces, type scale, one CTA example |
| **Critique dashboard** | P0/P1 table from critique report + fix direction (after critique, before implement) |
| **Wireframe map** | Labeled regions per viewport (375 / 768 / 1440 intent) |

Canvas rules for design:

- Flat, minimal UI — match `aesthetic-direction.md` (no gradient slop)
- Use `useHostTheme()` tokens per canvas SDK — no random hex
- Embed copy from brief — no lorem ipsum on flagship routes
- Tell user: **"Open the canvas beside chat to review direction."**

## Critique + polish

1. Write `.heyeddi/docs/<feature>-critique.md`
2. If Canvas available → **critique summary canvas** (optional but preferred for flagship routes)
3. Chain stack implementer + `@visual-auditor` on the **running app** — canvas does not replace screenshots

## Handoff boundary

| Stage | Show with | Build with |
|-------|-----------|------------|
| Explore / shape | GenerateImage, Canvas, wireframes | — |
| Brief confirmed | Brief review canvas | — |
| Implement | — | `@heyeddi-handoff` / `@design-handoff-flutter` |
| QA | — | `@visual-auditor` |

Never paste generated images as the only artifact — pair with wireframes + `brief.md`.

## Subagent note

`explore` may run in `generalPurpose` subagent: that worker must still call GenerateImage / write Canvas when the parent harness exposes those tools. Main chat should open Canvas when the subagent returns probe summaries.
