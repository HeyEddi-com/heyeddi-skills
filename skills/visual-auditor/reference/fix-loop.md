# Fix loop: visual auditor

**Date:** 2026-07-06

**Capture → review → fix → document → re-verify.** Not capture-only.

## Loop

```
load_visual_context --route /settings --write-review
capture_screenshots --route /settings
audit_geometry --image .heyeddi/audits/visual/screenshots/<file>.png --check
audit_contrast --route /settings
READ screenshots + product + design + contrast report
FOR EACH issue (error + actionable warn):
  EDIT Vue / CSS / tokens (design.md semantic vars)
  append_fix_log --route /settings --issue "…" --fix "…" --files … --spec-ref "…"
finalize_visual_review --route /settings --check
```

## What you may fix

| Issue type | Where to fix |
|------------|--------------|
| Low contrast / same-hue text | Route CSS, semantic tokens, PrimeVue overrides |
| Wrong hierarchy vs brief | Template structure, heading order, card layout |
| Spacing vs design.md rhythm | `--size-*` padding/gap, `.p-card-body` overrides |
| Missing states | Add empty/loading/error per surface-completeness |
| Product copy wrong register | Microcopy in view: align voice_tone |

## What to escalate (do not guess)

- IA change (merge routes, new nav) → `@heyeddi-product` + `@heyeddi-design shape`
- New component not in design.md → update design.md Decision log first
- Backend missing for AC → `@project-engineering`

## Documentation (required)

| Artifact | Content |
|----------|---------|
| `fix-log.md` | Chronological fixes via `append_fix_log` |
| `fix-log.jsonl` | Machine-readable same |
| `reviews/<feature>-review-<date>.md` | Full review + issues + fixes + re-verify |

## Chain validation

After fixes, `finalize_visual_review --check` must pass contrast. Re-read widest + narrowest capture: confirm persona success feeling visually.
