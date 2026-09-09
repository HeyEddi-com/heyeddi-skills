# Setup prefs (always-on hard gate)

**Date:** 2026-09-08

`@heyeddi-setup` is **always on** for any chat that assumes **git, CI, commit, push, or agent autonomy**. Incomplete prefs are a **hard stop** for those actions — not a soft suggestion.

## Fail rule

Run before commit, push, PR base assumptions, branch/env mapping, or reading `agent.commit` / `agent.push`:

```bash
python .agents/skills/heyeddi-setup/scripts/verify_setup.py \
  --project-root . --check
```

| Result | Agent must |
|--------|------------|
| Exit 0 (`complete`) | Honor `stack.json` prefs |
| Exit 1 (`setup incomplete`) | **Stop** git/CI/agent assumptions; run `@heyeddi-setup` until `verify_setup --check` passes |

Non-git work (design critique, product specs, pure code edits without commit) may continue. Do **not** invent branch names, PR bases, or auto-commit/push when prefs are missing.

## Session start

`@heyeddi-orchestrator` must treat failed `verify_setup --check` as a **hard route** to `@heyeddi-setup` before assuming project prefs.

## Who must bookend

| Skill | When |
|-------|------|
| `@heyeddi-orchestrator` | Session start / ambiguous tasks: fail → setup first |
| `@project-engineering` | Before scaffold claims about git/CI; before any commit |
| `@flutter-engineering` | Same as project-engineering |
| `@heyeddi-pr-respond` | Before commit + push |
| `@pre-merge-gate` | Runs `verify_setup --check` (required; emergency `--skip-setup-audit` only) |

## Related

- Hub policy: `docs/always-on-skills.md`
- Schema: `reference/stack-schema.md`
- Orchestrator: `reference/always-on.md`
