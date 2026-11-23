# Setup prefs (always-on)

**Date:** 2026-11-23

`@heyeddi-setup` is **always on** for any chat that assumes git, CI, branches, or agent permissions. Missing prefs never stop a task.

## Rule

Before the first git action of a session:

```bash
python .agents/skills/heyeddi-setup/scripts/verify_setup.py --project-root . --check
```

| Result | Agent must |
|--------|------------|
| Exit 0 (`complete`) | Honor `stack.json` prefs |
| Exit 1 (`setup incomplete`) | Run `write_setup.py --project-root . --defaults`, keep working, and name the detected defaults in the final summary |

`--defaults` keeps every answer already in the file. It fills the rest from the repo: trunk on the default branch, `balanced` agent preset. The interview runs only when the user asks for setup.

## Permissions

Commit, push, PR, merge, release, and env reads and writes are decided by `@heyeddi-local-first` `check_permission.py`. It reads `agent.preset` and `agent.permissions`. No policy in the file means `balanced`.

## Who must bookend

| Skill | When |
|-------|------|
| `@heyeddi` | Session start: `verify_setup --check`, defaults on failure |
| `@project-engineering` | Before scaffold claims about git/CI |
| `@flutter-engineering` | Same as project-engineering |
| `@heyeddi-pr-respond` | `check_permission` before commit + push |
| `@pre-merge-gate` | Runs `verify_setup --check` (required; emergency `--skip-setup-audit` only) |

## Related

- Hub policy: `docs/always-on-skills.md`
- Schema: `reference/stack-schema.md`
- Orchestrator: `reference/always-on.md`
