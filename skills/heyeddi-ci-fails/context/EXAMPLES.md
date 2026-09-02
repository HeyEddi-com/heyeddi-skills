# Examples: HeyEddi CI fails

## Default: diagnose + fix (PR work)

```
fetch_failing_checks --pr 42
write_ci_fails_report --pr 42 --force
```

Fill cause/fix from the linked Check logs. Apply fixes automatically when actionable. Then `discover_and_verify --run`, commit + push, `assert_no_merge --check`. Do not merge.

Offer `/heyeddi fails` if they also want hosted App analysis (billable when that path applies).

## Diagnose only (exception)

Use diagnose-only when the user explicitly says not to change code, or when failures are environmental / outside repo scope (e.g. flaky infra with no local fix). Still fetch and report — do not skip the check.
