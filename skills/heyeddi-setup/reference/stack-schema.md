# stack.json prefs schema (@heyeddi-setup)

**Date:** 2026-09-08

Setup owns **git/env + agent** prefs. Tech (`frontend`, `backends`, ports, package manager, CI) may live in the same file but is filled by other skills.

## Example (complete prefs)

```json
{
  "frontend": "vue",
  "backends": ["fastapi"],
  "git": {
    "preset": "main_staging_dev",
    "default_branch": "dev",
    "pr_base": "dev",
    "environments": {
      "production": "main",
      "staging": "staging",
      "dev": "dev"
    },
    "worktrees": false,
    "custom_workflow": null
  },
  "agent": {
    "commit": "ask",
    "push": "ask"
  },
  "design": {
    "taste": "on",
    "penpot": "auto"
  },
  "setup": {
    "version": 1,
    "updated": "2026-09-06"
  }
}
```

`main_dev` preset:

```json
"environments": {
  "production": "main",
  "staging": "dev"
}
```

## Required paths (verify_setup)

| Path | Values |
|------|--------|
| `git.preset` | `main_staging_dev` \| `main_dev` \| `custom` |
| `git.default_branch` | non-empty string |
| `git.pr_base` | non-empty string |
| `git.environments.production` | branch name |
| `git.environments.staging` | branch name |
| `git.worktrees` | boolean |
| `git.custom_workflow` | `null` or description string |
| `agent.commit` | `ask` \| `auto` |
| `agent.push` | `ask` \| `auto` |
| `setup.version` / `setup.updated` | stamped by write_setup |

Optional: `git.environments.dev` (present on `main_staging_dev`).

## Design prefs (stamped on write, not required to pass verify)

| Path | Values |
|------|--------|
| `design.taste` | `on` only. `@taste-penpot` always owns look. |
| `design.penpot` | `auto` (default) \| `on` \| `off` |

Missing keys mean the same as the defaults: taste on, Penpot when connected. `write_setup` fills them. Do not quiz which of the 27 skills to install. `@heyeddi` sees which packs are installed (`heyeddi-skills`, `heyeddi-ci-skills`, `heyeddi-design-skills`).

## Custom workflow

If the user wants gitflow or anything else: set `git.custom_workflow` to a short description and `git.preset` to `custom`. Still require production + staging environment branch names.
