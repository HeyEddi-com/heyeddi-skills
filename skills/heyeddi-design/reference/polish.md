# Polish: refine existing screen

**Scope:** Improve an implemented route without changing core IA.

**Prerequisite:** Run **`critique`** first (`reference/critique.md`) and write `.heyeddi/docs/<feature>-critique.md`: unless you already critiqued this route in the current session. Polish addresses the P0/P1 items from that critique.

## Steps

1. Run `load_context.py`: DESIGN.md + PRODUCT.md (check `audience_ready`).
2. **Read the critique**: `.heyeddi/docs/<feature>-critique.md`. If missing, run **critique** before changing code.
3. Re-check `reference/audience-fit.md`: tone and persona alignment, not just spacing.
3b. Re-check `reference/aesthetic-direction.md`: thesis, type, motion, generic AI looks; sharpen **one** aesthetic risk rather than adding ornament.
4. Run **`@visual-auditor`** full fix loop: capture → review vs product + design → fix code → `append_fix_log` → `finalize_visual_review --check`.
5. Fix remaining P0/P1 from critique not covered by visual auditor; align tokens with `design.md`.
6. Re-run `@primevue-openprops-architect` validation.
7. Re-run `@visual-auditor` `finalize_visual_review --check` if tokens/CSS changed again.
8. **Append** to **Decision log** in `.heyeddi/design.md`: reference critique findings + what you fixed (`reference/design-talk.md`).

## Boundaries

- **Polish** does not replace **shape**: if critique flags IA problems, recommend `shape` + brief update first.
- Do not introduce new PrimeVue components without updating DESIGN.md component table.
