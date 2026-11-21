# Smoke review

**Date:** 2026-11-12  
**Scope:** full

PM-owned review: **does the product work, is it useful, is something else better?**  
You orchestrate specialists: you do not replace them.

## 1. Context (tools)

- [ ] `load_product_context.py`
- [ ] `audit_product.py`
- [ ] `check_features.py`

## 2. Delegate research

| Lens | Skill | Action | Findings (paste summary) |
|------|-------|--------|--------------------------|
| **Task completion** | `@ux-flow-auditor` | `trace_flow` on critical `.flow.json` tasks | |
| **UX / persona fit** | `@heyeddi-design` | `critique` on flagship routes | |
| **Legibility / layout** | `@visual-auditor` | `audit_contrast --check` + screenshots | |
| **Engineering fit** | `@engineering-excellence` | `audit_engineering` | |
| **Duplicate / waste** | `@no-duplicate-ui` | scan if UI sprawl suspected | |

## 3. PM judgment (you write)

### Does it work?
- What breaks or blocks the primary user job?
- Which acceptance criteria are not met?

### Is it useful?
- Does this solve the persona's `primary_job` from `product.md`?
- What would users do instead (competitors, spreadsheets, nothing)?

### Would something else be better?
- Simpler scope, different route structure, cut a feature, merge screens?
- Cite evidence from delegated findings: not gut feel alone.

## 4. Recommendations

| Priority | Change | Rationale | Owner skill |
|----------|--------|-----------|-------------|
| P0 | | | |
| P1 | | | |

## 5. Definition of done (this review)

- [ ] Every delegated row has findings or explicit N/A
- [ ] P0 recommendations have acceptance criteria
- [ ] `backlog.md` updated if priorities shift
- [ ] Feature specs updated if scope changes

