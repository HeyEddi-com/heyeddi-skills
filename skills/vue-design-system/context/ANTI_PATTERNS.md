# Anti-patterns

- Adding React, Tailwind CSS, Bootstrap, or a second component kit for the same primitive.
- Building a page shell with PrimeVue layout components, or a data grid with Quasar tables.
- Writing hex colors or `style="..."` coordinates in `.vue` files.
- Using `ease-in-out` or `linear` for `x`, `y`, or `scale`.
- Rendering CLI prompts as HTML.
- Connecting Penpot through unscoped `penpot-mcp-server`, `@penpot/mcp`, or the Penpot MCP plugin. The only server is `@zcubekr/penpot-mcp-server`, installed after the user approves.
- Treating `@primevue-openprops-architect` as a reason to add OpenProps.
