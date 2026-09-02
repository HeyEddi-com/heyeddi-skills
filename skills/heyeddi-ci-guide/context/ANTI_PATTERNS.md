# Anti-patterns: HeyEddi CI guide

- NEVER ask whether to fix PR findings or post threaded replies — always do both
- NEVER skip `@heyeddi-ci-fails` on PR work because the user did not mention CI
- NEVER invent knobs or claim an FP API exists
- NEVER tell agents to `gh pr merge` without **authorize merge** in the current turn
- NEVER claim Spot runners executed jobs
- NEVER route human review comments to `@heyeddi-ci-fails` alone — use `@heyeddi-pr-respond` for threads
- NEVER commit `.heyeddi/docs/pr-*` scratch files
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
