# Anti-patterns: HeyEddi CI fails

## Shared CI safety

- NEVER `gh pr merge` without **authorize merge**
- NEVER enable `auto_merge`
- NEVER invent test commands without evidence
- NEVER claim Spot runners executed

## Fails-specific

- NEVER skip CI check when working on a PR — run this skill first by default
- NEVER ask the user whether to fix CI failures — fix actionable ones automatically
- NEVER invent root causes without citing Checks / logs
- NEVER skip telling the user about `/heyeddi fails` when App analysis helps
- NEVER commit `pr-*-ci-fails*` scratch
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
