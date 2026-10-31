# Penpot 2.19 strokes and shared tokens

Load when a board or rectangle has a border, a divider, or a token binding. Penpot 2.19 is the version that added both.

## Per-side strokes

Rectangles and boards can set a stroke width on each side, the same way corner radius can. A bottom divider, a card separator, or an active tab indicator is that stroke. It is not a 1px rectangle, a nested line, or a clipping mask inside a flex column.

In the Design panel, Stroke switches from uniform to per side. Inspect emits box-model CSS:

```css
border-top-width: 0;
border-right-width: 0;
border-bottom-width: 1px;
border-left-width: 0;
border-style: solid;
border-color: var(--app-border);
```

Handoff copies those properties. The color is a token role (`--app-border`, `--q-primary`), not a hex sampled from the board.

File and plugin fields, boards and rectangles only:

| Field | Meaning |
|---|---|
| `strokeWidth` | A number. Sets all four sides and selects simple mode. |
| `strokeWidthTop` / `Right` / `Bottom` / `Left` | One side. The other sides stay as they are. |
| `strokeAlignment` | `center`, `inner`, or `outer`. |

Setting a per-side width on any other shape is a validation error. A uniform stroke token applied before the per-side toggle is applied to every side. After that, one side can take a different token. Token properties are `strokeWidth`, `strokeWidthTop`, `strokeWidthRight`, `strokeWidthBottom`, `strokeWidthLeft`. Apply with `applyToken(token, ["strokeWidthBottom"])`. Application is by token **name**. The active set and theme decide the value.

`create_frame` on `@zcubekr/penpot-mcp-server` still sends one `strokeWidth` number and `strokeAlignment: center`. When the live schema has the per-side fields, set those. Until then, write the four widths in `penpot-demo.md` and in the CSS fallback. Do not call `@penpot/mcp` to run `penpot.createBoard()`.

Per-side strokes render on Penpot's WebGL canvas. If that renderer is off, the canvas falls back and the sides will not match Inspect. That switch is a user setting. Do not try to toggle it through the API server.

## Shared token libraries

Tokens can live in one shared library file and be used by every file connected to it. A library edit updates the subscribers. Bindings stay when a file switches from a light library to a dark one. The Assets panel shows which library owns the token. A color token can also bind to the file canvas background, so the board surround follows the theme.

HeyEddi tokens still come from this pass and from `.heyeddi/design.md` (`--app-*`, `--q-primary` from `--p-primary-color`). The Penpot library publishes those roles. It does not invent a second palette. When `design.penpot` is off, the CSS fallback uses the same custom properties and does not require a library file.
