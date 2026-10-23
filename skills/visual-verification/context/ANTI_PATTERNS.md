# Anti-patterns

- Calling `@primevue/mcp` or `@quasar/mcp` a visual check. They do not render pixels.
- Puppeteer, `puppeteer_navigate`, `puppeteer_screenshot`, or `@modelcontextprotocol/server-puppeteer`.
- Declaring a layout done without a screenshot of `localhost:5173`.
- Using the browser loop on a CLI. Run the script and read stdout instead.
- Passing width and height to `browser_take_screenshot`. Resize with `browser_resize` first.
- Skipping `@visual-auditor` when the pipeline still requires the recorded review.
