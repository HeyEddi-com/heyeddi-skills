# Engineering excellence (always on)

**Date:** 2026-09-04

This skill is **always on** for every chat that plans or changes code. Not only when the user types `@engineering-excellence`.

## Two gates

### 1. Plan gate (before coding)

Every implementation plan must pass:

1. `init_engineering_docs` if `.heyeddi/docs/engineering/` is missing
2. Read `reuse-catalog.md` before proposing new components/composables/services
3. Run:

   ```bash
   python .agents/skills/engineering-excellence/scripts/check_engineering_plan.py \
     --project-root . --check [--plan-file path/to/plan.md]
   ```

4. Reject or rewrite plans that add abstractions without a second call site, duplicate UI/API helpers, or fatten routers/views with business rules

### 2. Change gate (after edits)

After meaningful code changes (and before claiming done / merge):

```bash
python .agents/skills/engineering-excellence/scripts/audit_engineering.py \
  --project-root . --check
```

- **`--check`**: exit 1 on **error** severity only
- **Warns / info**: advisory; fix or ADR, do not block unless `--strict`
- Update `architecture.md` / reuse rows when modules change
- `append_decision` for non-obvious trade-offs

## Who must bookend

| Skill | Plan gate | Change gate |
|-------|-----------|-------------|
| `@project-engineering` | before feature code | after scaffold/feature edits |
| `@flutter-engineering` | before feature code | after scaffold/feature edits |
| `@heyeddi-handoff` | before Pass 2 Vue | after route complete |
| `@design-handoff-flutter` | before widget build | after route complete |
| `@heyeddi-pr-respond` | when planning fixes | after code fixes, before push |
| `@pre-merge-gate` | — | runs `audit_engineering --check` |

## Severity policy

| Severity | Examples | Gate |
|----------|----------|------|
| **error** | Missing required engineering doc files; extreme oversized modules | Fails `--check` |
| **warn** | Large files, fat handlers, stub docs | Advisory |
| **info** | Abstraction name hints, missing smoke specs | Advisory |
