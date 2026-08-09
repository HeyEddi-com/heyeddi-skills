# Examples: HeyEddi CI fails

## Diagnose only

```
fetch_failing_checks --pr 42
write_ci_fails_report --pr 42 --force
```

Fill cause/fix from the linked Check logs. Offer `/heyeddi fails` if they want App analysis.

## Fix loop

After user asks to fix: change code, `discover_and_verify --run`, `assert_no_merge --check`. Do not merge.
