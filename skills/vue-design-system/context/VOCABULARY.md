# Vocabulary

- **GUI surface:** a screen a person sees in the browser, Capacitor, or Tauri. Route it to Quasar or PrimeVue, then motion.
- **Shell:** headers, drawers, page containers, tab bars, and native safe areas. Quasar only.
- **Data surface:** tables, trees, pickers, menus, badges, and dense forms. PrimeVue Aura only.
- **Token bridge:** `--app-*` variables in `src/assets/design-tokens.css` that read PrimeVue `--p-*` and set Quasar `--q-*`.
- **Penpot MCP:** `penpot-mcp-server` (`@zcubekr/penpot-mcp-server`) used to list projects and create files, pages, and frames. Not the plugin MCP and not `penpot-api-mcp`.
- **Visual verification:** Playwright MCP screenshots of the Vite server after GUI motion. Not the CLI path. Not Puppeteer.
- **Plugin MCP:** `@penpot/mcp` plus a browser plugin and `execute_code`. Do not use it.
