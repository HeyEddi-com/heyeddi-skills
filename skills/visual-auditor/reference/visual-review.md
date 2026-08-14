# Visual review: screenshots vs specification

**Date:** 2026-08-13

You **see** the UI through captures. Compare against **two** specs:

| Spec | Source | Check |
|------|--------|-------|
| **Product** | `.heyeddi/product.md`: route intent, page purpose, persona success feeling | Does this screen deliver the job? |
| **Design** | `.heyeddi/design.md` + `designs/<feature>/mockup-brief.md` | Hierarchy, spacing, tokens, components |

Mockup PNG colors are **layout only**: implementation colors come from `design.md` tokens.

## Review steps

1. `load_visual_context --route /path --write-review`
2. `capture_screenshots --route /path`
3. `audit_contrast --route /path` (automated legibility)
4. **Open each PNG** in `.heyeddi/audits/visual/screenshots/`
5. Fill **vs product.md** and **vs design.md** sections in the review doc
6. Merge contrast violations into issues table

## Flagship / marketing calm-wow lens

On marketing routes and app flagships (`/`, `/login`, Home, Planning entry, settings), also check:

| Check | Fail looks like |
|-------|-----------------|
| First viewport is a **thesis**, not KPI strip + gradient mush | Admin template hero |
| Atmosphere is **alive or intentionally still** (mesh drift / quiet status) | Dead flat fill with no hierarchy |
| Status craft uses **product truth** + brand accent only | Decorative neon dual-accent / acid glow |
| Motion respects **reduced-motion** and does not sit under body text | Pulse/glow washing illegible copy |
| App shell stays **calmer** than marketing | Dashboard competing with marketing showreel |

This lens audits **our** routes against product + design specs. It does **not** audit external inspiration sites.

## Issue severity

| Severity | Examples |
|----------|----------|
| **error** | Contrast fail, wrong IA vs brief, blocks persona job |
| **warn** | Spacing drift, weak hierarchy, motion-over-text risk |
| **info** | Polish opportunity within spec |

## Do not stop at notes

Every **error** and actionable **warn** gets a code fix in the same session unless user explicitly waives in review doc.
