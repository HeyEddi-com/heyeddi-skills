# Anti-patterns: HeyEddi CI guide

- NEVER invent knobs or claim an FP API exists
- NEVER tell agents to `gh pr merge` without **authorize merge** in the current turn
- NEVER claim Spot runners executed jobs
- NEVER route human review comments to `@heyeddi-ci-respond` (use `@heyeddi-pr-respond`)
- NEVER commit `.heyeddi/docs/pr-*` scratch files
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
