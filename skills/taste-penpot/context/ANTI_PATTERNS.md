# Anti-patterns

- NEVER run a discover → research → shape pipeline. One pass only.
- NEVER invent a second palette after `@heyeddi-design` already has tokens from this pass.
- NEVER require Penpot when `design.penpot` is `off`. Write the spec and HTML+CSS.
- NEVER call unscoped `penpot-mcp-server`, `@penpot/mcp`, or `penpot-api-mcp`. The only Penpot server is `@zcubekr/penpot-mcp-server`.
- NEVER install or enable that server without an explicit yes. A missing server means ask once (`references/penpot-mcp.md`), then wait.
- NEVER override a pinned brief with taste or with the Anthropic refuse list.
- NEVER fake a stack or a page skeleton with absolutely positioned rectangles. 1D flow is Flex. 2D tracks are CSS Grid (`references/flex-grid.md`). Absolute position is for a badge, close icon, or tooltip that must leave the flow.
