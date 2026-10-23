# Penpot API MCP

Load at the start of ACT when `design.penpot` is not `off`.

Designer visuals and demos use the **Penpot API MCP** (`penpot-api` / `penpot-api-mcp`). That server talks to the Penpot REST API. It does not need a browser tab.

Do **not** use the plugin MCP:

- package `@penpot/mcp`
- tools `execute_code`, `high_level_overview`, `penpot_api_info`, `export_shape`, `import_image`
- a Penpot plugin window, WebSocket session, or `http://localhost:4401/mcp`

If those plugin tools are the only Penpot tools in the session, say so in one line and continue with ACT 2.6. Do not draw through them.

## Configure

The API server is HTTP-only. Default listen address is `http://127.0.0.1:3051/mcp`.

```bash
# PENPOT_ACCESS_TOKEN must already be in the environment. Do not print it.
uvx --from penpot-api-mcp python -m penpot_api_mcp start --force
```

```json
{
  "mcpServers": {
    "penpot-api": {
      "type": "http",
      "url": "http://127.0.0.1:3051/mcp"
    }
  }
}
```

| Variable | Role |
|----------|------|
| `PENPOT_ACCESS_TOKEN` | Preferred auth. Never write it into the repo, a skill file, or chat. |
| `PENPOT_EMAIL` + `PENPOT_PASSWORD` | Fallback only when a token is not available. Do not ask the user to paste a password into chat. |
| `PENPOT_BASE_URL` | Self-hosted API. Default `https://design.penpot.app/api`. |

## Tools

| Tool | Use |
|------|-----|
| `list_projects` | Find the designer's project. |
| `get_project_files` | List files in that project. |
| `get_file` | Read file content, including tokens and pages when the payload includes them. |
| `get_object_tree` | Hierarchy for the focused file. |
| `search_objects` | Find a board or component by name or type. |
| `export_object` | PNG or SVG for a designer review or a demo still. |

Trust the live tool schema if it disagrees with this table.

## Read, then export

1. `list_projects`, then `get_project_files`.
2. `get_object_tree` and `search_objects` before assuming a board is missing.
3. `export_object` the board the user cares about and look at the image.
4. Summarize what exists, what can be reused, and what is inconsistent.

## Demos

`penpot-api-mcp` 0.4.3 reads, searches, and exports. It does not create shapes. A demo is:

1. An export of the current board when the file exists.
2. `.heyeddi/designs/<feature>/penpot-demo.md` describing the boards to add or change: name, width (375 / 768 / 1440), regions, and token roles mapped to the Aura bridge (`--app-bg`, `--app-surface-card`, `--app-text-main`, `--q-primary` ← `--p-primary-color`).
3. A note that the designer applies the demo in Penpot. The next pass exports it. Do not switch to the plugin MCP to draw it.

## Fallback

If `penpot-api` is not connected, say so in one line and follow ACT 2.6 in `SKILL.md`. The written spec and HTML+CSS use the same token roles. Implementation still follows `@vue-design-system`.
