# Examples: HeyEddi CI fails

## Default: diagnose + fix (PR work)

```
fetch_failing_checks --pr 42
write_ci_fails_report --pr 42 --force
```

Fill cause/fix from the linked Check logs. Apply fixes automatically when actionable. Then `discover_and_verify --run`, commit + push, and `gh pr checks 42 --watch` until green. Run `pre_merge_gate.py --signoff`; on exit 0 and a base below production, run `assert_no_merge --check --base <baseRefName> --planned-command "gh pr merge 42" --project-root .` and merge. A production base takes the user's **authorize merge**.

Offer `/heyeddi fails` if they also want hosted App analysis (billable when that path applies).

## Diagnose only (exception)

Use diagnose-only when the user explicitly says not to change code. For a flaky or infrastructure failure, run `gh run rerun <run-id> --failed` and watch again. If it still fails for a cause outside the repo, report the exact error under **Needs you**.
