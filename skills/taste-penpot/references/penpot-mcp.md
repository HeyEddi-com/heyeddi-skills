# Penpot MCP

Load at the start of ACT when `design.penpot` is not `off`.

Designer visuals use **`@heyeddi/penpot-mcp-server`** (GitHub `HeyEddi-com/penpot-mcp-server`), the HeyEddi fork of `@zcubekr/penpot-mcp-server`. It talks to the Penpot API, nests children with `parentId`, and sets Flex/Grid via `set_frame_layout` / `create_frame` layout fields. It does not need a browser tab.

A connected Penpot server counts when its tools include `list_teams` and `create_frame`. Prefer the HeyEddi fork when `set_frame_layout` or `parentId` on create tools is present (hi-fi in Penpot). Upstream `@zcubekr/penpot-mcp-server` still works for absolute sketches only; then Gate C HTML remains mandatory.

## Never use these Penpot MCPs

Do not call their tools, do not keep them as the `penpot` entry, and do not install them.

| Server | How it shows up | Tools that identify it |
|---|---|---|
| Unscoped npm `penpot-mcp-server` (Mart1M). `npx penpot-mcp-server` without a scope installs this. | Default package name | `get_board`, `debug_board`, `get_tokens` |
| Official plugin `@penpot/mcp` | Penpot's own MCP, plugin window, `http://localhost:4401/mcp` | `execute_code`, `high_level_overview`, `penpot_api_info` |
| `penpot-api-mcp` | Older read-only server | read and export only |

If one of those is the server named `penpot`, treat the HeyEddi (or zcubekr) server as missing and follow Install.

## Install

When `design.penpot` is not `off` and `list_teams` is not in this session, stop and ask once:

> Penpot boards need `@heyeddi/penpot-mcp-server` (Flex/Grid + nesting). May I add it to this project's `.cursor/mcp.json`?

Wait for an explicit yes. Do not write config, run `npx`, or enable a server before that yes. A missing server is not a reason to call the unscoped package or `@penpot/mcp`.

On yes, merge this into the project `.cursor/mcp.json`. Keep every other server. If `penpot` already points at another package, replace that entry.

Preferred (npm, after publish):

```json
{
  "mcpServers": {
    "penpot": {
      "command": "npx",
      "args": ["-y", "@heyeddi/penpot-mcp-server"],
      "env": {
        "PENPOT_API_URL": "https://design.penpot.app"
      }
    }
  }
}
```

Until npm publish, use GitHub:

```json
{
  "mcpServers": {
    "penpot": {
      "command": "npx",
      "args": ["-y", "github:HeyEddi-com/penpot-mcp-server"],
      "env": {
        "PENPOT_API_URL": "https://design.penpot.app"
      }
    }
  }
}
```

Local clone:

```json
{
  "mcpServers": {
    "penpot": {
      "command": "node",
      "args": ["/absolute/path/to/penpot-mcp-server/dist/index.js"],
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

Trust the live tool schema if a name differs.

| Tool | Use |
|------|-----|
| `list_teams` | Confirms API MCP access. |
| `list_projects` / `search_projects` | Pick the app project. |
| `list_files` / `get_file` | Read before writing boards. |
| `create_project` / `create_file` / `add_page` | Scope containers. |
| `create_frame` | Board at 375 / 768 / 1440. Pass `layout: "flex"` or `"grid"` plus gap/padding/dir when using HeyEddi. |
| `create_text` / `create_rectangle` / `create_circle` | Pass **`parentId`** of the board. Separate nodes per field (no text-wall). Set `layoutItemHSizing` / `layoutItemVSizing`. |
| `set_frame_layout` | Enable Flex/Grid on an existing board (HeyEddi). |
| `set_layout_item` | Fit / Fill / Fix a child (HeyEddi). |
| `reparent_shape` | Move a shape under a board (HeyEddi). |
| `update_shape` | Position, style, and layout fields. |
| `get_shape_properties` | Read back `parentId`, `layout`, position, and fill size. Required after `set_frame_layout`. Missing `layout` means the board is not Flex. |
| `export_shape` | Renders the board and returns the PNG. Look at that image for Gate D. If this tool is missing, the HTML file does not replace it. |
| `audit_board` | Reports overlapping siblings, photos sitting in the corner, and empty screens. Fix every line before `export_shape`. |

## Several projects

`list_projects` can return more than one project. Choose the project whose name matches the app. Do not write boards into a different product's file. When two projects could match, say which one you will use and continue.

## Do not delete

Do not call `delete_project`, `delete_file`, `delete_team`, `delete_page`, or `delete_shape` unless the user named that exact target in this turn. A redesign adds or updates the boards in scope. It does not wipe a library.

## Record

Write `.heyeddi/designs/<feature>/penpot-demo.md` with project, file, **page id that `list_pages` returned**, board names, widths, token roles, and the layout-engine table from `references/flex-grid.md`.

Mark **hi-fi / Flex** only when a read-back in this turn shows `layout` of `flex` or `grid` on the board and `parentId` of the copy on that board. Quote those values. If the API rejected a fill or a reparent, the board is not hi-fi. Absolute geometry is **low-fi / absolute sketch**.

A divider on a board or rectangle is a per-side stroke (`references/strokes-and-tokens.md`). Do not call `@penpot/mcp`.

## Text on boards (no walls)

Prefer many `create_text` / `create_rectangle` calls nested with `parentId` on an **8px grid** (separate label, value, helper, CTA) over one multiline string in a gray card. Text-wall is a hard reject (`references/layout-hard-gates.md` Gate A).

## Hi-fi path

1. **HeyEddi MCP with Flex/nest** (`set_frame_layout` or `layout` on `create_frame` + `parentId` children): build the boards, then **read parent and layout back**. Hi-fi only if that read shows Flex and the copy is parented to the phone. Then `export_shape` and look at the PNG (Gate D). If `export_shape` is missing, look at the canvas anyway. `hifi.html` does not prove the file.
2. **Upstream zcubekr only (absolute):** boards are low-fi; ACT 2.6 `hifi.html` is **mandatory** (Gate C). Do not label them hi-fi.
3. **`design.penpot` off or install declined:** ACT 2.6 only.

Implementation still follows `@vue-design-system`. Full reject rules: `references/layout-hard-gates.md`.
