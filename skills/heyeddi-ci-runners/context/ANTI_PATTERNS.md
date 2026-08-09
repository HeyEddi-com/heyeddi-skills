# Anti-patterns: HeyEddi CI runners (placeholder)

## Shared CI safety

- NEVER `gh pr merge` without **authorize merge**
- NEVER enable `auto_merge`
- NEVER enable billable knobs without opt-in
- NEVER invent knobs — always `load_policy_contract`
- NEVER invent test commands / path filters

## Placeholder-specific

- NEVER claim Spot jobs ran, succeeded, or were dispatched
- NEVER invent invoke/status APIs ahead of product
- NEVER put secrets in `eddi-ci.yaml`
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
