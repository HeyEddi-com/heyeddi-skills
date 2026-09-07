# Vocabulary: HeyEddi CI config

- **eddi-ci.yaml** — Repo-root policy file. Schema version `"1.0"` only.
- **Living contract** — JSON from `GET /api/public/eddi-ci-policy` (production: `https://cihook.heyeddi.com/api/public/eddi-ci-policy`). Always load via `load_policy_contract` before writing YAML.
- **Docs** — Human narrative at `https://ci.heyeddi.com/docs#policy` (`docs_url` in the contract).
- **Safe defaults** — Missing/invalid YAML → no runners, `on_ci_failure: false`, `allow_external_prs: false`.
- **Reviewer knobs** — Under `ai_review` (e.g. `validation_max_attempts`, `on_ci_failure`).
- **Runners / pipeline** — Sealed Spot jobs under `pipeline.<job_id>` (`stage`, `image`, `run`, optional `filter.paths` / `needs`). Prefer GHA + `HEYEDDI_RUNS_ON` when workflows exist; keep `pipeline: {}` then.
- **GHA on Spot** — Workspace `gha_spot_mode` (`off` | `overflow` | `always`); not declared as pipeline jobs.
- **External PRs** — Fork PRs into an installed repo; controlled by `policy.allow_external_prs`.
- **@heyeddi-ci-config** — This skill; App PR CTA points authors here instead of pasting guessed YAML.
