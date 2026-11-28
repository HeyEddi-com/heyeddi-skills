---
name: heyeddi-intake
description: "Translates vague user prompts into HeyEddi product docs (personas, route intent, voice), route-specific handoff artifacts (wireframes, user mockups, or briefs), and skill-routing under .heyeddi/. Use first on new projects before @heyeddi-design, @heyeddi-handoff, or @flutter-engineering. Never hand-write product.md: use write_product."
version: 1.3.2
product-version: 3.9.0
author: HeyEddi-com
paths:
  - ".heyeddi/**"
  - "PRODUCT.md"
---

# HeyEddi Intake

**Upstream intake agent**: turns vague user language into `.heyeddi/product.md`, handoff artifacts, and skill routing for downstream HeyEddi skills.

This skill does not write feature code. You interpret, document, produce handoff artifacts, route, and **verify**. In a build request the run continues after intake: `@heyeddi-product` writes the specs and backlog, then the Backlog loop builds every item.

## When to use

- New project or empty / thin `.heyeddi/product.md`
- User describes an app in plain language
- **User attached images** → `ingest_mockups` (screenshots, sketches, competitor refs)
- **No images** → `generate_wireframe` per handoff route (default)
- Before any `@heyeddi-design` / `@heyeddi-handoff` / scaffold work

## Mockup decision tree

Read **`reference/mockup-strategy.md`** (mandatory).

| Situation | Action |
|-----------|--------|
| User gave screenshots / mockups | `ingest_mockups` → tailor `mockup-brief.md` to their layout |
| No images, route needs handoff | `generate_wireframe` → **refine** `wireframe.md` for this product → `seed_brief --force` |
| No images, polished PNG handoff needed | `prepare_mockup_prompts` → **AI-generate** `desktop.png` / `mobile.png` (see `reference/ai-mockup-images.md`) → `seed_brief --force` |
| No images, route needs visual design first | Route `@heyeddi-design`: do not emit template PNGs |

**The skill package does not ship sample PNGs** and has **no Pillow/template PNG drawer**. Eval hub tooling (`uv run poe mockups`) is maintainer-only: not part of this skill.

## Mandatory pipeline

See **`reference/pipeline.md`**. Summary:

1. `load_intake`
2. Draft **`product-translation.json`** (`reference/audience-intake.md`): template: `reference/product-translation.template.json`
3. **`write_product --json … --force`**: validates schema; writes `product.md` + saves JSON
4. `write_translation`
5. Handoff features: **`generate_wireframe`** (or `ingest_mockups` / AI PNGs per strategy) → **`seed_brief --force`**
6. **`build_routing --write --save-input`**
7. **`verify_intake --check`**: must pass before intake is complete
8. Build request: `@heyeddi-product` (specs, `backlog.md`, Backlog loop)

## Never

- Hand-write `product.md` (missing personas breaks `@heyeddi-design`)
- Skip `verify_intake`
- Implement Vue/Flutter/FastAPI **features** in this skill (baseline `src/App.vue` shell on scaffolded repos is OK)
- Delete `src/App.vue` or break `npm run build` to pass verify
- Use `write_routing` unless overriding `build_routing` output
- Bundle or draw cookie-cutter PNG mockups from skill scripts

## Outputs (`.heyeddi/`)

| Path | Tool |
|------|------|
| `docs/intake/product-translation.json` | `write_product` (canonical) |
| `product.md` | `write_product` |
| `docs/intake/translation-*.md` | `write_translation` |
| `docs/intake/skill-routing.json` | `build_routing --write` |
| `designs/<feature>/wireframe.md` | `generate_wireframe` (default without user images) |
| `designs/<feature>/mockup-prompts.json` | `prepare_mockup_prompts` (before AI image gen) |
| `designs/<feature>/desktop.png` | `ingest_mockups` or **agent AI image gen** after prompts |
| `designs/<feature>/mockup-brief.md` | `seed_brief` (Audience + Implementation spec) |

## Clarify before act

Read `reference/clarify-before-act.md`. A discovery request: one round if personas/competitors are missing from the user prompt. A build request: infer them from the repo, record them, and continue.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi-intake --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.

## Related

- `reference/audience-intake.md`: JSON schema
- `reference/downstream-routing.md`: routing examples
- `reference/mockup-strategy.md`: when wireframe vs ingest vs AI PNG
- `reference/ai-mockup-images.md`: AI generation workflow (no bundled PNGs)
- `reference/mockup-quality.md`: quality bar per format
- `@heyeddi`: `write_skills_index` after intake (integration eval)
