# Anti-patterns

- NEVER run a discover → research → shape pipeline. One pass only.
- NEVER invent a look when the user only said "modern" / "clean" / "professional" — run `references/identity-gate.md` (≥3 options, wait for choice).
- NEVER ship PLAN tokens, Penpot boards, or HTML demos before identity is locked (pinned, chosen, or refine-skip).
- NEVER present three hue swaps of the same world and call them identities.
- NEVER invent a second palette after `@heyeddi-design` already has tokens from this pass.
- NEVER require Penpot when `design.penpot` is `off`. Write the spec and HTML+CSS.
- NEVER call unscoped `penpot-mcp-server`, `@penpot/mcp`, or `penpot-api-mcp`. The only Penpot server is `@zcubekr/penpot-mcp-server`.
- NEVER install or enable that server without an explicit yes. A missing server means ask once (`references/penpot-mcp.md`), then wait.
- NEVER override a pinned brief with taste or with the Anthropic refuse list.
- NEVER fake a stack or a page skeleton with absolutely positioned rectangles. 1D flow is Flex. 2D tracks are CSS Grid (`references/flex-grid.md`). Absolute position is for a badge, close icon, or tooltip that must leave the flow.
- NEVER fake a divider, a card separator, or a tab indicator with a 1px rectangle inside a flex column. On a board or rectangle that is a per-side stroke (`references/strokes-and-tokens.md`).
