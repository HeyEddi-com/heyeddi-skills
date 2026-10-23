# Vocabulary

- **GUI surface:** a screen a person sees in the browser, Capacitor, or Tauri. Route it to Quasar or PrimeVue, then motion.
- **Shell:** headers, drawers, page containers, tab bars, and native safe areas. Quasar only.
- **Data surface:** tables, trees, pickers, menus, badges, and dense forms. PrimeVue Aura only.
- **Token bridge:** `--app-*` variables in `src/assets/design-tokens.css` that read PrimeVue `--p-*` and set Quasar `--q-*`.
- **Penpot API MCP:** the `penpot-api` server (`penpot-api-mcp`) used to list, read, search, and export designer files. Not the plugin MCP.
- **Visual verification:** Playwright MCP screenshots of the Vite server after GUI motion. Not the CLI path. Not Puppeteer.
- **Plugin MCP:** `@penpot/mcp` plus a browser plugin and `execute_code`. Do not use it.
