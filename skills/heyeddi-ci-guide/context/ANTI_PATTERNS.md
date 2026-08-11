# Anti-patterns: HeyEddi CI guide

- NEVER invent knobs or claim an FP API exists
- NEVER tell agents to `gh pr merge` without **authorize merge** in the current turn
- NEVER claim Spot runners executed jobs
- NEVER use a separate CI respond skill — `@heyeddi-pr-respond` handles human and HeyEddi CI
- NEVER commit `.heyeddi/docs/pr-*` scratch files
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
