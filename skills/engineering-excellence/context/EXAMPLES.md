
# Examples: Engineering excellence

## Plan gate (every chat before coding)

```bash
python scripts/check_engineering_plan.py --project-root . --check
python scripts/check_engineering_plan.py --project-root . --check --plan-file plan.md
```

## Init docs

```bash
python scripts/init_engineering_docs.py --project-root .
```

## Change gate (after edits / before merge)

```bash
python scripts/audit_engineering.py --project-root . --check
```

## Record ADR

```bash
python scripts/append_decision.py \
  --project-root . \
  --title "Single composable per API domain" \
  --context "Three views duplicated fetch logic" \
  --decision "Add useTasks composable; views import only that" \
  --consequences "Remove direct fetch from DashboardView"
```
