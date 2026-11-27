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
    "preset": "balanced",
    "permissions": {
      "merge": "ask",
      "write": { "staging": "ask" }
    }
  },
  "targets": {
    "prod": ["acme-prod-123", "gke_acme_prod"],
    "staging": ["acme-stg-456"]
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
| `setup.version` / `setup.updated` | stamped by write_setup |

Optional: `git.environments.dev` (present on `main_staging_dev`).

## Agent permissions (optional; read by `@heyeddi-local-first` `check_permission.py`)

| Path | Values |
|------|--------|
| `agent.preset` | `cautious` \| `balanced` (default) \| `autonomous` |
| `agent.permissions.<action>` | `auto` \| `ask` \| `deny` for `commit`, `push`, `push_protected`, `pr`, `merge`, `release` |
| `agent.permissions.read.<env>` | same levels for `dev`, `staging`, `prod` |
| `agent.permissions.write.<env>` | same levels; `write.prod` is never better than `ask` |
| `targets.<env>` | strings (GCP project, kube context, DB host) that mark a command as that env. A prod entry counts anywhere in the command; dev and staging entries count only in a target flag (`--project`, `--context`, `--host`, ...) or connection URL. Without them, names containing prod / staging / dev decide the same way, and an unnamed remote write counts as prod. |
| `agent.commit` / `agent.push` | legacy `ask` \| `auto`; accepted and ignored. Use `agent.preset` or `agent.permissions` |

Protected branches: `main`, `master`, `git.environments.production`, `git.environments.staging`, and `git.default_branch`.

## Design prefs (stamped on write, not required to pass verify)

| Path | Values |
|------|--------|
| `design.taste` | `on` only. `@taste-penpot` always owns look. |
| `design.penpot` | `auto` (default) \| `on` \| `off` |

Missing keys mean the same as the defaults: taste on, Penpot when connected. `write_setup` fills them. Do not quiz which of the 39 skills to install. `@heyeddi` sees which packs are installed (`heyeddi-skills`, `heyeddi-ci-skills`, `heyeddi-design-skills`).

## Backlog and documents (stamped on write, not required to pass verify)

| Path | Values |
|------|--------|
| `backlog.provider` | `local` (default) \| `mcp` |
| `backlog.mcp.server` / `backlog.mcp.project` | which MCP server and project, when `mcp` |
| `docs.provider` | `repo` (default) \| `mcp` \| `external` |
| `docs.mcp.server` / `docs.mcp.space` | which MCP server and space, when `mcp` |
| `docs.location` | where documents live, when `external` |
| `docs.keep` | repo documents to keep current with each backlog item |

Detail: `@heyeddi-product` `reference/backlog.md`. Commit `stack.json` in app repositories so every worktree reads the same choices. Record why in `decisions.md`.

## Custom workflow

If the user wants gitflow or anything else: set `git.custom_workflow` to a short description and `git.preset` to `custom`. Still require production + staging environment branch names.
