# Anti-patterns: HeyEddi CI config

## Shared CI safety

- NEVER merge into production before the user says **authorize merge** in the current turn. Below production, merge once `@pre-merge-gate --signoff` exits 0
- NEVER enable or invent `auto_merge` (schema rejects unknown keys; product law forbids agent merge)
- NEVER enable billable knobs (`ai_review.on_ci_failure`, sealed Spot `pipeline` jobs) without explicit opt-in
- NEVER invent knobs from memory - always run `load_policy_contract` first
- NEVER claim Spot/GHA jobs executed without Check or Spot evidence (`@heyeddi-ci-runners`)

## Config-specific

- NEVER create `eddi-ci.yaml` only because the file is missing **unless** `inspect_repo` shows HeyEddi product markers (or the user opts in) - see SKILL.md decision gate
- NEVER treat a PR CTA mention of `@heyeddi-ci-config` as a request to write the file - without a request, leave the safe defaults and carry on
- NEVER skip `inspect_repo` before deciding add vs skip - product detection lives there
- NEVER paste a full guessed `eddi-ci.yaml` from a PR review comment
- NEVER enable `ai_review.on_ci_failure` without explicit user opt-in (billable)
- NEVER add `pipeline` jobs without evidenced test commands and path filters
- NEVER duplicate the same CI in `pipeline:` and `.github/workflows/`
- NEVER invent `pytest` / `npm test` / `go test` when the repo shows no such tooling
- NEVER put secrets, tokens, or credentials in `eddi-ci.yaml`
- NEVER use unknown top-level keys (schema `extra=forbid` - e.g. no `auto_merge`)
- NEVER treat missing `eddi-ci.yaml` as an error - safe defaults are intentional
- NEVER “improve” an existing valid config the user did not ask to change
- NEVER enable `policy.allow_external_prs` without explaining fork-PR billing risk
- NEVER treat YAML lint as proof that Spot jobs ran
