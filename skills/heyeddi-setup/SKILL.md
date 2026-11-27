---
name: heyeddi-setup
description: "ALWAYS-ON prefs: ensures `.heyeddi/stack.json` holds git/env prefs and the agent permission preset. Missing prefs are filled with write_setup --defaults (no questions) so work never stops; the interview runs only when the user asks. Asks env layout, custom workflow escape hatch, worktrees, agent preset (cautious / balanced / autonomous). Tech stack is discovered by other skills. Use when setup is incomplete or the user says setup, preferences, or heyeddi-setup."
version: 1.2.1
product-version: 3.8.28
author: HeyEddi-com
paths:
  - ".heyeddi/stack.json"
---

# HeyEddi Setup

**Project working agreement** for agents: ensure `.heyeddi/stack.json` has **git/env + agent prefs**. Re-run anytime to update.

**Always on**: before the first git action of a session, `verify_setup --check`. Missing prefs get detected defaults, not a stop. See `reference/setup-always-on.md` and hub `docs/always-on-skills.md`.

Does **not** quiz frontend, backends, package manager, or CI: those are filled by scaffold / engineering / CI skills as the project evolves.

## When to use

- User says "setup", "preferences", or `@heyeddi-setup`: run the interview
- `verify_setup --check` fails during a task: run `write_setup --defaults`, keep working, mention it in the final summary
- Re-run to change env layout or the agent preset

## Hard gate

```bash
python .agents/skills/heyeddi-setup/scripts/verify_setup.py --project-root . --check
```

- **Exit 0**: honor prefs in `stack.json`
- **Exit 1**: run `write_setup.py --project-root . --defaults`. It keeps every answer already in the file and fills the rest from the repo: trunk on the default branch, `balanced` agent preset. No questions. Keep working.

Permissions (commit, push, PR, merge, release, env reads and writes) are decided by `@heyeddi-local-first` `check_permission.py`, which reads `agent.preset` and `agent.permissions`.

## Interview (only when the user asks for setup)

1. `load_setup`: current `stack.json` + `missing` paths
2. `list_questions`: all questions on re-run; `--missing-only` on first pass
3. Ask the user, all questions in one message, defaults shown
4. `write_setup --json '…'`
5. `verify_setup --check` must pass before you stop

## Questions (prefs only)

| # | Ask | Choices |
|---|-----|---------|
| 1 | Env / branch layout? | `main_staging_dev` (default) or `main_dev` |
| 2 | Different workflow? | no → keep preset; or describe (gitflow, trunk+tags, …) → `custom` |
| 3 | Git worktrees for parallel features? | yes / no |
| 4 | How much may agents do without asking? | `cautious` / `balanced` (default) / `autonomous` |
| 5 | Penpot as design source? | `auto` (default) / `on` / `off`. Taste always stays on. |

### Agent presets

| Preset | Commit, push feature branch, PR | Merge below production | Production merge or push | Release | Read staging / prod | Write staging | Write prod |
|--------|------|------|------|------|------|------|------|
| `cautious` | ask | ask | ask | ask | ask | deny | deny |
| `balanced` | auto | auto (after `pre-merge-gate`) | ask | ask | auto (look only) | ask | deny |
| `autonomous` | auto | auto (after `pre-merge-gate`) | ask | auto | auto | auto | ask |

A push to the staging branch follows `push_protected`: ask, or auto under `autonomous`.

Per-action overrides go in `agent.permissions` (see `reference/stack-schema.md`). Hard limits no preset lifts: force push or delete on a protected branch, destructive statements on prod, `gh repo delete`, prod writes set to `auto`.

### Git presets (always production + staging)

| Preset | Mapping |
|--------|---------|
| `main_staging_dev` | prod ← `main`, staging ← `staging`, dev ← `dev`; `pr_base` = `dev` |
| `main_dev` | prod ← `main`, staging ← `dev`; `pr_base` = `dev` |

## Tools

```bash
python .agents/skills/heyeddi-setup/scripts/load_setup.py --project-root .
python .agents/skills/heyeddi-setup/scripts/list_questions.py --project-root .
python .agents/skills/heyeddi-setup/scripts/write_setup.py --project-root . --json '{"git.preset":"main_staging_dev","git.custom_workflow":null,"git.worktrees":false,"agent.preset":"balanced"}'
python .agents/skills/heyeddi-setup/scripts/write_setup.py --project-root . --defaults
python .agents/skills/heyeddi-setup/scripts/verify_setup.py --project-root . --check
```

## Agents: always honor prefs

Read `.heyeddi/stack.json` before branch or PR-base assumptions:

- `git.environments`: which branch maps to production / staging / (optional) dev
- `git.pr_base` / `git.default_branch`
- `git.custom_workflow`: if set, follow that description over the preset
- Commit, push, PR, merge, release, env access: run `check_permission.py`; do not read `agent.*` by hand. Legacy `agent.commit` / `agent.push` keys are ignored; to make an agent ask, use `agent.preset` or `agent.permissions`.

## Never

- Ask frontend / backends / package manager / CI in this skill
- Put prefs outside `.heyeddi/stack.json`
- Claim setup done without `verify_setup --check`
- Stop a task to interview the user about prefs; use `--defaults` and keep going
- Replace `@project-engineering` / `@flutter-engineering` scaffold duties

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi-setup --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.

## Related

- `reference/setup-always-on.md`: hard gate policy
- `reference/stack-schema.md`: key list
- `@heyeddi`: hard-route setup when prefs incomplete
- `@pre-merge-gate`: runs `verify_setup --check`
- `@project-engineering` / `@flutter-engineering`: discover and write tech into `stack.json`
