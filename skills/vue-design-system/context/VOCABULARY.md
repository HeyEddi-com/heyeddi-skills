# Vocabulary

- **GUI surface:** a screen a person sees in the browser, Capacitor, or Tauri. Route it to Quasar or PrimeVue, then motion.
- **Shell:** headers, drawers, page containers, tab bars, and native safe areas. Quasar only.
- **Data surface:** tables, trees, pickers, menus, badges, and dense forms. PrimeVue Aura only.
- **Token bridge:** `--app-*` variables in `src/assets/design-tokens.css` that read PrimeVue `--p-*` and set Quasar `--q-*`.
- **Penpot MCP:** `@zcubekr/penpot-mcp-server` only. Lists projects and creates files, pages, and frames. Install after user approval when it is missing. Unscoped `penpot-mcp-server`, `@penpot/mcp`, and `penpot-api-mcp` are the wrong servers.
- **Visual verification:** Playwright MCP screenshots of the Vite server after GUI motion. Not the CLI path. Not Puppeteer.
- **Wrong Penpot servers:** unscoped npm `penpot-mcp-server` (`get_board`, `get_tokens`) and `@penpot/mcp` (`execute_code`). Do not install or call them.
