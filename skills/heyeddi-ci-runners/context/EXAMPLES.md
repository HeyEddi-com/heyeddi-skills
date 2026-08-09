# Examples: HeyEddi CI runners

## User wants runners

1. Load contract + inspect repo
2. If evidenced `pytest` and `backend/**` paths exist, add a Reviewer+pipeline stub with those commands
3. State clearly that jobs will not run until Spot ships
4. Run `assert_runners_placeholder --check` on your summary text

## User asks "did my job pass?"

Answer: no job ran — runners are placeholder / fail-closed. Point at Check evidence or `@heyeddi-ci-fails` for GitHub Actions failures instead.
