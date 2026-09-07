# Examples: HeyEddi CI runners

## Repo has GitHub Actions (common)

1. Load contract; keep or write Reviewer-only `eddi-ci.yaml` with `pipeline: {}`
2. Add `runs-on: ${{ vars.HEYEDDI_RUNS_ON || 'ubuntu-latest' }}` on every Linux job
3. Tell user to set workspace Runners mode to `overflow` or `always` on ci.heyeddi.com
4. Do **not** copy workflow commands into `pipeline:`
5. Run `assert_runners_claims --check` on your summary

## Repo has no GHA; user wants Spot tests

1. Load contract + `inspect_repo`
2. If evidenced `pytest` and `backend/**` paths exist, add sealed `pipeline:` jobs via `@heyeddi-ci-config`
3. Explain Checks will appear as `HeyEddi Runner: {job_id}` when entitled + Spot live
4. Do not claim a run until Checks show a conclusion

## User asks "did my job pass?"

Look up Checks (`gh pr checks` / `@heyeddi-ci-fails`). Cite the Check name and conclusion. If none, say status is unknown — do not infer from YAML alone.
