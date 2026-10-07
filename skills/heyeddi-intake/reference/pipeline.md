# Intake pipeline (mandatory order)

**Date:** 2026-07-06

Never hand-write `.heyeddi/product.md`. Always use tools.

```
load_intake --prompt-file USER_PROMPT.md
    ↓
Draft product-translation.json (see audience-intake.md) → save to .heyeddi/docs/intake/
    ↓
write_product --json .heyeddi/docs/intake/product-translation.json --force
    ↓
write_translation --user-prompt "..." --summary "..." --decisions '[...]'
    ↓
Per handoff feature (e.g. settings):
  User images? → ingest_mockups
  Else         → generate_wireframe --feature settings --route /settings --force
                 (agent refines wireframe.md for this product)
  Or PNG handoff needed → prepare_mockup_prompts → AI-generate desktop.png + mobile.png
  seed_brief --feature settings --app-name TaskFlow --force
    ↓
build_routing --write --save-input
    ↓
verify_intake --check
```

## Hard rules

| Rule | Why |
|------|-----|
| Use `write_product` only | Validates personas + route_intent; saves canonical JSON |
| ≥2 personas | Buyer + daily user minimum |
| route_intent covers every page route | `@heyeddi-design` audience gates |
| `seed_brief` after wireframe or ingest | Fills Audience from product.md |
| `build_routing` after product + handoff artifacts | Settings → heyeddi-handoff when wireframe or PNG exists |
| `verify_intake --check` last | Single pass/fail for eval and CI |
| No feature Vue in intake | Block `src/views/**` and components: **keep** baseline `src/App.vue` shell |
| Repo must build | When `node_modules` exists, `verify_intake` runs `npm run build` |
| **No bundled PNG templates** | Skill does not ship or draw preset PNGs: wireframe, ingest, or AI |

## Optional overrides

- User supplied PNGs → `ingest_mockups` instead of `generate_wireframe`
- Polished PNG without user images → `prepare_mockup_prompts` + AI image gen (`reference/ai-mockup-images.md`)
- Custom routing → edit `skill-routing-input.json` then `write_routing --json ...`

## After intake (not this skill)

```
@heyeddi-product       init_product_docs → audit_product → write_feature_spec (per route)
@heyeddi    init_workflow_sync
@heyeddi    write_skills_index
@project-engineering scaffold_stack
@heyeddi-design document → shape → craft (per routing)
@heyeddi-handoff (settings or wireframe routes)
```
