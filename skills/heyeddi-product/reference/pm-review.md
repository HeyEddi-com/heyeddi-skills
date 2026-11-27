# Holistic product review

**Date:** 2026-07-06

PM work is **not** backlog hygiene only. Each review answers:

| Question | Evidence sources |
|----------|------------------|
| **Does it work?** | `check_features`, `@ux-flow-auditor` traces, acceptance criteria |
| **Is it useful?** | Persona jobs, competitor frame in `product.md`, UX critique |
| **Would something else be better?** | Synthesis across UX + design + engineering findings |

## Review types

### Intake review (post-`@heyeddi-intake`)

```
audit_product --check
write_feature_spec (per route)
```

Block `@heyeddi-design craft` on flagship routes until feature specs exist.

### Build review (mid-implementation)

```
check_features
write_review_plan
delegate critique + trace_flow + audit_contrast
update recommendations table
```

### Release review (pre-ship)

```
verify_product --check
build every open review plan row; waive only what The only pauses block
```

## Waiver

A gap you can close, you close. Only an item blocked per `@heyeddi` `reference/autonomy.md` (The only pauses) may ship open: mark it `blocked` with `backlog.py block` and its persona impact. **Out of scope** holds only what the request or `product.md` excludes.
