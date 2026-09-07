# Anti-patterns: HeyEddi CI runners

## Shared CI safety

- NEVER `gh pr merge` without **authorize merge**
- NEVER enable `auto_merge`
- NEVER enable billable knobs / sealed `pipeline:` without opt-in
- NEVER invent knobs — always `load_policy_contract`
- NEVER invent test commands / path filters

## Runner-specific

- NEVER duplicate the same CI in `.github/workflows/` and `pipeline:`
- NEVER prefer sealed `pipeline:` when the repo already has GHA for the same checks
- NEVER claim a Spot/GHA job ran without Check or Spot evidence
- NEVER treat YAML lint as proof of execution
- NEVER invent invoke/status APIs beyond product Checks / docs
- NEVER put secrets in `eddi-ci.yaml`
- NEVER promise overflow always succeeds without evidence (reliability can gap)
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`
