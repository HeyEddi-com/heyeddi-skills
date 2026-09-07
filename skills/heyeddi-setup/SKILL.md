---
name: heyeddi-setup
description: "Ensures `.heyeddi/stack.json` holds git/env and agent prefs. Asks a few preference questions (env layout, custom workflow escape hatch, worktrees, commit/push autonomy). Tech stack is discovered by other skills. Use when setup is incomplete or the user says setup, preferences, or heyeddi-setup."
version: 1.1.0
product-version: 3.4.8
author: HeyEddi-com
paths:
  - ".heyeddi/stack.json"
---

# HeyEddi Setup

**Project working agreement** for agents: ensure `.heyeddi/stack.json` has **git/env + agent prefs**. Re-run anytime to update.

Does **not** quiz frontend, backends, package manager, or CI — those are filled by scaffold / engineering / CI skills as the project evolves.

## When to use

- Missing `git` / `agent` / `setup` prefs in `stack.json`
- User says "setup", "preferences", or `@heyeddi-setup`
- Session start when `verify_setup --check` fails
- Re-run to change env layout or agent autonomy

## Mandatory pipeline

1. `load_setup` — current `stack.json` + `missing` paths
2. `list_questions` — ask all on re-run; `--missing-only` on first pass OK
3. Ask the user (defaults shown)
4. `write_setup --json '…'`
5. `verify_setup --check` — must pass before you stop

## Questions (prefs only)

| # | Ask | Choices |
|---|-----|---------|
| 1 | Env / branch layout? | `main_staging_dev` (default) or `main_dev` |
| 2 | Different workflow? | no → keep preset; or describe (gitflow, trunk+tags, …) → `custom` |
| 3 | Git worktrees for parallel features? | yes / no |
| 4 | Agent may commit without asking? | `ask` / `auto` |
| 5 | Agent may push without asking? | `ask` / `auto` |

### Presets (always production + staging)

| Preset | Mapping |
|--------|---------|
| `main_staging_dev` | prod ← `main`, staging ← `staging`, dev ← `dev`; `pr_base` = `dev` |
| `main_dev` | prod ← `main`, staging ← `dev`; `pr_base` = `dev` |

## Tools

```bash
python .agents/skills/heyeddi-setup/scripts/load_setup.py --project-root .
python .agents/skills/heyeddi-setup/scripts/list_questions.py --project-root .
python .agents/skills/heyeddi-setup/scripts/write_setup.py --project-root . --json '{"git.preset":"main_staging_dev","git.custom_workflow":null,"git.worktrees":false,"agent.commit":"ask","agent.push":"ask"}'
python .agents/skills/heyeddi-setup/scripts/verify_setup.py --project-root . --check
```

## Agents: always honor prefs

Read `.heyeddi/stack.json` before git/commit/push:

- `git.environments` — which branch maps to production / staging / (optional) dev
- `git.pr_base` / `git.default_branch`
- `git.custom_workflow` — if set, follow that description over the preset
- `agent.commit` / `agent.push` — if `ask`, confirm first

## Never

- Ask frontend / backends / package manager / CI in this skill
- Put prefs outside `.heyeddi/stack.json`
- Claim setup done without `verify_setup --check`
- Replace `@project-engineering` / `@flutter-engineering` scaffold duties

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py --current-skill heyeddi-setup --project-root .
```

Include the script's **`### Next step`** block in your final reply.

## Related

- `reference/stack-schema.md` — key list
- `@heyeddi-orchestrator` — suggest setup when prefs incomplete
- `@project-engineering` / `@flutter-engineering` — discover and write tech into `stack.json`
