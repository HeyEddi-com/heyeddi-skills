# Examples: Pre-merge gate

## Local smoke (no PR attach)

```bash
python scripts/pre_merge_gate.py --project-root . --skip-visual-audit
```

## Merge sign-off (preferred)

```bash
python scripts/pre_merge_gate.py --project-root . --signoff
```

Auto-detects the open PR via `gh`, then requires: clean tree, pushed branch, green `gh pr checks`, no unresolved review threads, and bans emergency skips.

## Pin a PR

```bash
python scripts/pre_merge_gate.py --project-root . --pr 42
```

## Sample report

```markdown
# Pre-merge Gate Report

- **PR:** 42
- **Sign-off mode:** yes

| Check | Status | Summary |
|-------|--------|---------|
| git-clean | PASS | working tree clean |
| git-pushed | PASS | branch synced with upstream |
| pr-checks | PASS | all green |
| pr-review-threads | PASS | no unresolved review threads |
| setup-audit | PASS | complete |
| test | PASS | …
| build | PASS | …
| engineering-audit | PASS | …
| prose-audit | PASS | …

**Overall:** OK (0 failures, 2 skips)
```
