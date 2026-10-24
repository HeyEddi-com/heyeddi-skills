# Penpot mode

Designer visuals and demos use **zcube/penpot-mcp-server** (`npx -y penpot-mcp-server`).

- List teams and projects, then create or update the file and frames for the pages in scope.
- A redesign reads `skills/taste-penpot/references/code-to-design.md` before new boards.
- Write the demo contract to `.heyeddi/designs/<feature>/penpot-demo.md` (`@taste-penpot`).
- Do not call delete tools unless the user named that exact project, file, or page.
- Do not use the plugin MCP (`@penpot/mcp`, `execute_code`) or the read-only `penpot-api-mcp` server.

Implementation of the exported layout still follows `@vue-design-system`: Quasar for the shell, PrimeVue Aura for data, `@aura-design-tokens` for color, `@motion-physics` for springs, `@layout-morph` when a shared element moves, `@fancy-ui-craft` only when depth was requested.

Screenshot mode remains valid when no Penpot file is connected.
