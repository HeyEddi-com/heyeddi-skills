# Design team

`@taste-penpot` is the general design skill. When no style is pinned, it runs the **identity gate** (`references/identity-gate.md`: project/peers/stance in `.heyeddi/`, then **3–5** What/Why/How options, wait for A–E). After identity is locked, it chooses the look in one pass and writes tokens. Penpot is an optional designer visual (API MCP), not a second design skill.

`@heyeddi-design` records personas, the route job, and those tokens in `.heyeddi/design.md`, then hands implementation to `@heyeddi-handoff` or `@design-handoff-flutter`.

`@heyeddi` calls them in that order.

This skill does not run a second aesthetic search or a second identity contest. If identity/tokens are missing, load `@taste-penpot` (identity gate first when required) and wait for the user's pick when the gate applies. `@vue-design-system` maps those tokens onto Vue 3: Quasar shells, PrimeVue Aura data, spring motion, and the Aura token bridge. They do not replace the look.

Penpot boards use Flex for 1D flow and CSS Grid for 2D tracks (`../taste-penpot/references/flex-grid.md`). Inspect CSS is the handoff contract. Penpot is the designer visual and demo surface. `.heyeddi/stack.json` `design.penpot`: `auto` (default), `on`, or `off`. `design.taste` stays `on`. The only connection is `@zcubekr/penpot-mcp-server`. When it is missing, `@taste-penpot` asks once and installs it after the user approves. Unscoped `penpot-mcp-server`, `@penpot/mcp`, and `penpot-api-mcp` are never used. A redesign or from-scratch request starts in `@taste-penpot` `references/code-to-design.md`.
