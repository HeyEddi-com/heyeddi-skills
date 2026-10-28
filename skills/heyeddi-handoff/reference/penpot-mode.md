# Penpot mode

Designer visuals and demos use **only** `@zcubekr/penpot-mcp-server` (`npx -y @zcubekr/penpot-mcp-server`).

- List teams and projects, then create or update the file and frames for the pages in scope.
- A redesign reads `skills/taste-penpot/references/code-to-design.md` before new boards.
- Write the demo contract to `.heyeddi/designs/<feature>/penpot-demo.md` (`@taste-penpot`).
- Do not call delete tools unless the user named that exact project, file, or page.
- If `list_teams` is missing, follow `@taste-penpot` `references/penpot-mcp.md`: ask once, then install `@zcubekr/penpot-mcp-server` into `.cursor/mcp.json` only after an explicit yes.
- Never use unscoped `penpot-mcp-server`, the plugin MCP (`@penpot/mcp`, `execute_code`), or `penpot-api-mcp`.

Implementation of the exported layout still follows `@vue-design-system`: Quasar for the shell, PrimeVue Aura for data, `@aura-design-tokens` for color, `@motion-physics` for springs, `@layout-morph` when a shared element moves, `@fancy-ui-craft` only when depth was requested.

Screenshot mode remains valid when no Penpot file is connected.
