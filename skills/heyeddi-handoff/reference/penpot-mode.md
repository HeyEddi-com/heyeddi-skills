# Penpot mode

Designer visuals and demos use the **Penpot API MCP** (`penpot-api`).

- Read, search, and export with `list_projects`, `get_project_files`, `get_file`, `get_object_tree`, `search_objects`, `export_object`.
- Write the demo contract to `.heyeddi/designs/<feature>/penpot-demo.md` (`@taste-penpot`).
- Do not use the plugin MCP (`@penpot/mcp`, `execute_code`, a browser plugin session).

Implementation of the exported layout still follows `@vue-design-system`: Quasar for the shell, PrimeVue Aura for data, `@aura-design-tokens` for color, `@motion-physics` for springs.

Screenshot mode remains valid when no Penpot file is connected.
