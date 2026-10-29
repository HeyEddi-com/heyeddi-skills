# Penpot MCP

Load at the start of ACT when `design.penpot` is not `off`.

Designer visuals use **only** `@zcubekr/penpot-mcp-server` (GitHub `zcube/penpot-mcp-server`). It talks to the Penpot API, can open more than one project, and can create files, pages, and frames. It does not need a browser tab.

A connected Penpot server counts only when its tools include `list_teams` and `create_frame` from that package.

## Never use another Penpot MCP

These are the wrong servers. Do not call their tools, do not keep them as the `penpot` entry, and do not install them.

| Server | How it shows up | Tools that identify it |
|---|---|---|
| Unscoped npm `penpot-mcp-server` (Mart1M). `npx penpot-mcp-server` without `@zcubekr` installs this. | Default package name | `get_board`, `debug_board`, `get_tokens` |
| Official plugin `@penpot/mcp` | Penpot's own MCP, plugin window, `http://localhost:4401/mcp` | `execute_code`, `high_level_overview`, `penpot_api_info` |
| `penpot-api-mcp` | Older read-only server | read and export only |

If one of those is the server named `penpot`, treat `@zcubekr/penpot-mcp-server` as missing and follow Install.

## Install

When `design.penpot` is not `off` and `list_teams` from `@zcubekr/penpot-mcp-server` is not in this session, stop and ask once:

> Penpot boards need `@zcubekr/penpot-mcp-server`. May I add it to this project's `.cursor/mcp.json`?

Wait for an explicit yes. Do not write config, run `npx`, or enable a server before that yes. A missing server is not a reason to call the unscoped package or `@penpot/mcp`.

On yes, merge this into the project `.cursor/mcp.json`. Keep every other server. If `penpot` already points at another package, replace that entry.

```json
{
  "mcpServers": {
    "penpot": {
      "command": "npx",
      "args": ["-y", "@zcubekr/penpot-mcp-server"],
      "env": {
        "PENPOT_API_URL": "https://design.penpot.app"
      }
    }
  }
}
```

`PENPOT_ACCESS_TOKEN` must already be in the environment Cursor passes to the server. Never print it, and never write it into a repo, a skill, a chat, or `mcp.json`. If it is unset, ask the user to set it on the `penpot` server in Cursor and continue only after they confirm it is set.

Tell the user to enable the new `penpot` server. After `list_teams` is available, use that server.

On no, follow ACT 2.6 in `SKILL.md`. `design.penpot: off` skips this section. Do not ask, and do not install.

## Tools for this skill

Trust the live tool schema if a name differs. These names belong to `@zcubekr/penpot-mcp-server`.

| Tool | Use |
|------|-----|
| `list_teams` | See which teams the token can access. Confirms this is the zcubekr server. |
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

Also write `.heyeddi/designs/<feature>/penpot-demo.md` with the project name, file name, board names, widths, and token roles (`--app-bg`, `--app-surface-card`, `--app-text-main`, `--q-primary` from `--p-primary-color`). Include the layout-engine table from `references/flex-grid.md` (Flex or Grid, tracks or direction, gap, child Fit / Fill / Fix). The file is the handoff if the MCP disconnects. Inspect CSS from those frames is the implementation spec.

## Fallback

Use ACT 2.6 only when `design.penpot` is `off`, or the user declined the install. Implementation still follows `@vue-design-system`.
