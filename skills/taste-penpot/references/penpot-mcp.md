# Penpot MCP

Load at the start of ACT when `design.penpot` is not `off`.

Designer visuals use **zcube/penpot-mcp-server** (`@zcubekr/penpot-mcp-server`). It talks to the Penpot API, can open more than one project, and can create files, pages, and frames. It does not need a browser tab.

Do **not** use the plugin MCP:

- package `@penpot/mcp`
- tools `execute_code`, `high_level_overview`, `penpot_api_info`
- a Penpot plugin window or `http://localhost:4401/mcp`

Do **not** use the older read-only server `penpot-api-mcp`. If that is the only Penpot server connected, say so in one line and continue with ACT 2.6.

## Configure

`PENPOT_ACCESS_TOKEN` must already be in the environment. Never print it, and never write it into a repo, a skill, or chat.

```bash
npx -y penpot-mcp-server
```

```json
{
  "mcpServers": {
    "penpot": {
      "command": "npx",
      "args": ["-y", "penpot-mcp-server"],
      "env": {
        "PENPOT_API_URL": "https://design.penpot.app",
        "PENPOT_ACCESS_TOKEN": ""
      }
    }
  }
}
```

Leave the token value empty in any example. The running environment supplies it.

| Variable | Role |
|----------|------|
| `PENPOT_ACCESS_TOKEN` | Auth. Never echo it. |
| `PENPOT_API_URL` | Penpot origin. Default `https://design.penpot.app`. |

## Tools for this skill

Trust the live tool schema if a name differs.

| Tool | Use |
|------|-----|
| `list_teams` | See which teams the token can access. |
| `list_projects` | List projects. Pick the one for this app. |
| `search_projects` | Find a project by name when the list is long. |
| `list_files` | Files in the chosen project. |
| `get_file` | Read a file before adding boards. |
| `create_project` | Only when this app has no project yet. |
| `create_file` | A file for this feature when none exists. |
| `add_page` | One page per flow in scope. |
| `create_frame` | A board at 375, 768, or 1440. |
| `create_text` | Real copy. Label placeholders. |
| `create_rectangle` | Regions that map to Quasar shell or PrimeVue content. |
| `export_shape` | PNG of the board for the critique pass. |

## Several projects

`list_projects` can return more than one project. Choose the project whose name matches the app. Do not write boards into a different product's file. When two projects could match, say which one you will use and continue.

## Do not delete

Do not call `delete_project`, `delete_file`, `delete_team`, `delete_page`, or `delete_shape` unless the user named that exact target in this turn. A redesign adds or updates the boards in scope. It does not wipe a library.

## Record

Also write `.heyeddi/designs/<feature>/penpot-demo.md` with the project name, file name, board names, widths, and token roles (`--app-bg`, `--app-surface-card`, `--app-text-main`, `--q-primary` from `--p-primary-color`). The file is the handoff if the MCP disconnects.

## Fallback

If `penpot` is not connected, say so in one line and follow ACT 2.6 in `SKILL.md`. Implementation still follows `@vue-design-system`.
