# Anti-patterns: HeyEddi CI config

## Shared CI safety

- NEVER `gh pr merge` / merge the PR without the user saying **authorize merge** in the **current turn**
- NEVER enable or invent `auto_merge` (schema rejects unknown keys; product law forbids agent merge)
- NEVER enable billable knobs (`ai_review.on_ci_failure`, Spot `pipeline` jobs) without explicit opt-in
- NEVER invent knobs from memory — always run `load_policy_contract` first
- NEVER claim Spot runners executed jobs — runners are fail-closed / placeholder until the product ships them (`@heyeddi-ci-runners`)

## Config-specific

- NEVER create `eddi-ci.yaml` only because the file is missing **unless** `inspect_repo` shows HeyEddi product markers (or the user opts in) — see SKILL.md decision gate
- NEVER treat a PR CTA mention of `@heyeddi-ci-config` as automatic permission to write the file — confirm if intent is unclear
- NEVER skip `inspect_repo` before deciding add vs skip — product detection lives there
- NEVER paste a full guessed `eddi-ci.yaml` from a PR review comment
- NEVER enable `ai_review.on_ci_failure` without explicit user opt-in (billable)
- NEVER add `pipeline` jobs without evidenced test commands and path filters
- NEVER invent `pytest` / `npm test` / `go test` when the repo shows no such tooling
- NEVER put secrets, tokens, or credentials in `eddi-ci.yaml`
- NEVER use unknown top-level keys (schema `extra=forbid` — e.g. no `auto_merge`)
- NEVER treat missing `eddi-ci.yaml` as an error — safe defaults are intentional
- NEVER “improve” an existing valid config the user did not ask to change
- NEVER enable `policy.allow_external_prs` without explaining fork-PR billing risk
- NEVER claim runners will execute when the isolated runner product is still fail-closed
