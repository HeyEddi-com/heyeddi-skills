# Vocabulary

- **Taste:** this skill. One PLAN → ACT → CRITIQUE pass. Owns look and tokens.
- **frontend-design:** Anthropic's short design note, vendored under `third-party/frontend-design/` (Apache-2.0). Loaded during PLAN.
- **Penpot:** optional designer boards. Controlled by `.heyeddi/stack.json` `design.penpot` (`auto` | `on` | `off`). Server is `@zcubekr/penpot-mcp-server` only. Install it after user approval when `list_teams` is missing. Unscoped `penpot-mcp-server` and `@penpot/mcp` are the wrong servers.
- **Flex layout:** Penpot's 1D engine (Shift+A). Rows, columns, wrap, Fit / Fill / Fix. Same CSS as `display: flex`.
- **CSS Grid layout:** Penpot's 2D engine (Ctrl/Cmd+Shift+A). Tracks in `fr`, `px`, `auto`, or `minmax`. Same CSS as `display: grid`.
- **Per-side stroke:** Penpot 2.19. Boards and rectangles set `strokeWidthTop`, `strokeWidthRight`, `strokeWidthBottom`, `strokeWidthLeft`. Inspect CSS is `border-*-width`. See `references/strokes-and-tokens.md`.
- **Shared token library:** One Penpot library file publishes the `design.md` roles. Other files subscribe. Not a second palette.
- **@heyeddi-design:** product and handoff partner. Consumes these tokens. Does not author a second look.
