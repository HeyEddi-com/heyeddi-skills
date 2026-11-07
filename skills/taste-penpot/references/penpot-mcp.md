# Penpot MCP

Load at the start of ACT when `design.penpot` is not `off`.

Designer visuals use **`@heyeddi/penpot-mcp-server`** (GitHub `HeyEddi-com/penpot-mcp-server`), the HeyEddi fork of `@zcubekr/penpot-mcp-server`. It talks to the Penpot API, nests children with `parentId`, and sets Flex/Grid via `set_frame_layout` / `create_frame` layout fields. It does not need a browser tab.

A connected Penpot server counts when its tools include `list_teams` and `create_frame`. Prefer the HeyEddi fork when `set_frame_layout` or `parentId` on create tools is present (hi-fi in Penpot). Upstream `@zcubekr/penpot-mcp-server` still works for absolute sketches only; then Gate C HTML remains mandatory.

## Design system first (not blind drawing)

Order of work on a connected file:

1. **Read** — `list_projects` → `list_files` → `get_file` / `list_pages`. Reuse the app's project.
2. **System** — if refining, reuse library colours and typographies. If new or redesign: `add_color` and `add_typography` for the token roles **before** any phone board. Confirm fonts with `list_font_variants` (or fonts already in the file). Never invent faces (Sora/Nunito/etc.) that Penpot does not have.
3. **Components** (when the surface repeats) — create/update components for nav, field row, CTA; instantiate instead of redrawing.
4. **Boards** — phones at 375 / 768 / 1440 using those tokens. Prefer library-bound fills and type.
5. **Layout proof** — `set_layout_item` + read-back. If Flex children stay at `0,0`, switch to absolute 8px (Gate F). Do not rebuild nested Flex.
6. **Pixels** — `export_shape` and **look at the PNG** (Gate D). No PNG / Cloudflare ⇒ not done. `audit_board` is a hint, never the ship signal.
7. **Hygiene** — do not leave empty Look/dated shells as the demo surface (Gate G).

Full reject rules: `references/layout-hard-gates.md` Gates A–G.

## Known MCP limits

Treat these as constraints, not bugs to ignore:

| Limit | Skill response |
|---|---|
| Flex flags save; children stay at `0,0` (no API reflow) | Gate F: one Flex try → absolute 8px or HTML. Never claim hi-fi Flex. |
| `layoutItem*` on create often `null` | Always `set_layout_item`, then read back. |
| `create_image` weaker than rect fills | Prefer rect + cover image fill. Media paint may need `PENPOT_AUTH_TOKEN` (see MCP README), not access token alone. |
| `export_shape` / auth can hit Cloudflare | Gate D fail. Report block. Do not ship on API success. |
| `audit_board` noisy (label-on-button) / false pass after hand coords | Hint only. PNG decides. |

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

For image fills / export that must match the canvas, the MCP README may also require `PENPOT_AUTH_TOKEN`. Do not invent workarounds that skip Gate D.

Tell the user to enable the new `penpot` server. After `list_teams` is available, use that server.

On no, follow ACT 2.6 in `SKILL.md`. `design.penpot: off` skips this section. Do not ask, and do not install.

## Tools for this skill

Trust the live tool schema if a name differs.

| Tool | Use |
|------|-----|
| `list_teams` | Confirms API MCP access. |
| `list_projects` / `search_projects` | Pick the app project. |
| `list_files` / `get_file` | Read before writing boards. |
| `list_pages` / `add_page` / `rename_page` | Scope pages; rename instead of leaving empty shells (Gate G). |
| `create_project` / `create_file` | Scope containers. |
| `add_color` / `add_typography` | Design system roles **before** phones (Gate E). |
| `list_font_variants` / font upload tools | Prove a face exists before `create_text`. |
| `create_component` / `instantiate` / variants | Repeated UI (nav, field, CTA). |
| `create_frame` | Board at 375 / 768 / 1440. Pass `layout: "flex"` or `"grid"` plus gap/padding/dir when using HeyEddi — then prove reflow (Gate F). |
| `create_text` / `create_rectangle` / `create_circle` | Pass **`parentId`** of the board. Separate nodes per field (no text-wall). Do not trust create-time `layoutItem*` alone. |
| `set_frame_layout` | Enable Flex/Grid on an existing board (HeyEddi). |
| `set_layout_item` | Fit / Fill / Fix a child (HeyEddi). **Required** after create; read back. |
| `reparent_shape` | Move a shape under a board (HeyEddi). |
| `update_shape` | Position, style, and layout fields. Absolute 8px escape uses this. |
| `get_shape_properties` | Read back `parentId`, `layout`, `x`, `y`, `layoutItem*`, fill size. Required after layout changes. Missing `layout` or children at `0,0` means not Flex hi-fi. |
| `export_shape` | Renders the board and returns the PNG. **Look at that image** for Gate D. Cloudflare / missing = not done. HTML does not replace it. |
| `audit_board` | Hint for overlaps and empty screens. Fix real issues. Ignore noisy stacking when the PNG is correct. Never ship on audit alone. |

## Several projects

`list_projects` can return more than one project. Choose the project whose name matches the app. Do not write boards into a different product's file. When two projects could match, say which one you will use and continue.

## Do not delete

Do not call `delete_project`, `delete_file`, `delete_team`, `delete_page`, or `delete_shape` unless the user named that exact target in this turn. A redesign adds or updates the boards in scope. It does not wipe a library. Prefer rename / replace content for empty shells (Gate G).

## Record

Write `.heyeddi/designs/<feature>/penpot-demo.md` with project, file, **page id that `list_pages` returned**, board names, widths, token roles, library colour/typography ids, and the layout-engine table from `references/flex-grid.md`.

Mark **hi-fi / Flex** only when a read-back in this turn shows `layout` of `flex` or `grid` on the board, `parentId` of the copy on that board, **and** children are not stuck at `0,0`. Quote those values. If Flex reflow failed and you used absolute 8px, mark **hi-fi / absolute 8px** only after Gate D PNG. Absolute geometry without that PNG is **low-fi / absolute sketch**.

If the API rejected a fill or a reparent, the board is not hi-fi. A divider on a board or rectangle is a per-side stroke (`references/strokes-and-tokens.md`). Do not call `@penpot/mcp`.

## Text on boards (no walls)

Prefer many `create_text` / `create_rectangle` calls nested with `parentId` on an **8px grid** (separate label, value, helper, CTA) over one multiline string in a gray card. Text-wall is a hard reject (`references/layout-hard-gates.md` Gate A).

## Hi-fi path

1. **Design system** (Gate E) → boards with library tokens.
2. **HeyEddi MCP with Flex/nest:** `layout` + `parentId` + `set_layout_item` → read parent, layout, child x/y back. If children at `0,0`, absolute 8px escape (Gate F). Then `export_shape` and look at the PNG (Gate D). If export is blocked, stop and say so. `hifi.html` does not prove the file.
3. **Upstream zcubekr only (absolute):** boards are low-fi; ACT 2.6 `hifi.html` is **mandatory** (Gate C). Do not label them hi-fi.
4. **`design.penpot` off or install declined:** ACT 2.6 only.

Implementation still follows `@vue-design-system`. Full reject rules: `references/layout-hard-gates.md`.
