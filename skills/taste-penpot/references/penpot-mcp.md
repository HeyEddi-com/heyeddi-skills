# Penpot MCP: verified facts and recipes

Load at the start of ACT. Facts below were checked against Penpot's official
documentation (https://help.penpot.app/mcp/, source:
https://github.com/penpot/penpot/blob/main/docs/mcp/index.md) and the official
MCP server source (https://github.com/penpot/penpot/tree/main/mcp, including
`packages/server/data/initial_instructions.md`, which the `high_level_overview`
tool returns). When anything here disagrees with what `high_level_overview` or
`penpot_api_info` returns in the session, trust the live tool.

---

## 1. How it works

- Three parts: the **MCP server** (exposes tools to your client), the **Penpot
  MCP plugin** running inside the open Penpot file (bridges the server to the
  file over WebSocket), and the **MCP client** (your agent).
- The agent works by sending JavaScript to `execute_code`, which runs in the
  Penpot plugin context using the Penpot Plugin API (`penpot` object plus a
  `penpotUtils` helper object and a persistent `storage` object for keeping
  values between calls).
- MCP always acts on the **currently focused page** in the one browser tab that
  owns the MCP connection. If the user switches page, the context follows.
- The plugin runs in the browser tab. If the tab sleeps or unloads, calls fail
  until the tab is focused again and reconnects.

## 2. Tools (local server)

| Tool | What it does |
|---|---|
| `execute_code` | Runs JavaScript in the Penpot plugin context: query, create, modify. |
| `high_level_overview` | Returns the usage instructions for the Penpot tools and API. Read once per session. |
| `penpot_api_info` | Returns API documentation for a given type and its members. |
| `export_shape` | Exports a shape (or its image fill) as PNG or SVG, so you can look at it; locally it can also save to a file. |
| `import_image` | Imports a local image file into Penpot as a rectangle with an image fill. |

Remote (hosted) mode has no local file-system access: `import_image` from local
paths is unavailable and `export_shape` cannot write to local paths.

## 3. Connecting (tell the user only if it is not connected)

- **Hosted (remote)**: Penpot → Your account → Integrations → MCP Server →
  enable, generate an MCP key (shown once; treat it like a password), copy the
  server URL (`https://<penpot-domain>/mcp/stream?userToken=…`), add it to the
  MCP client. Then in the design file: **File → MCP Server → Connect**.
- **Local**: run `npx @penpot/mcp@stable` (Node.js 22 tested; 20 should work) and
  keep it running; in Penpot open a file, **Plugins → Load from URL**
  `http://localhost:4400/manifest.json`, run the plugin, click **Connect to MCP
  server** and keep the plugin window open. Client endpoint:
  `http://localhost:4401/mcp`. Clients without HTTP transport can use the
  `mcp-remote` proxy. Some Chromium-based browsers block https → localhost; allow
  local network access or use another browser.
- Never ask for, print or store the user's MCP key.

## 4. Read recipes (run before any write)

```js
// pages and focused page structure
return { pages: penpotUtils.getPages(),
         page: penpotUtils.shapeStructure(penpot.root, 3) };
```

```js
// library inventory (local + connected)
const lib = penpot.library.local;
const pick = l => ({
  name: l.name,
  colors: l.colors.map(c => ({ name: c.name, color: c.color, opacity: c.opacity })),
  typographies: l.typographies.map(t => ({ name: t.name, fontFamily: t.fontFamily,
    fontSize: t.fontSize, fontWeight: t.fontWeight, lineHeight: t.lineHeight,
    letterSpacing: t.letterSpacing })),
  components: l.components.map(c => c.name) });
return { local: pick(lib), connected: penpot.library.connected.map(pick) };
```

```js
// tokens: set name -> type -> token names, plus active state
return { overview: penpotUtils.tokenOverview(),
         sets: penpot.library.local.tokens.sets.map(s => ({ name: s.name, active: s.active })) };
```

```js
// selection: copy immediately, it may change
storage.sel = penpot.selection;
return storage.sel.map(s => penpotUtils.shapeStructure(s, 2));
```

Then `export_shape` the relevant board as PNG and look at it.

## 5. Write recipes

Library colour and typography (hex in capitals):

```js
const c = penpot.library.local.createColor();
c.name = 'Text / Primary'; c.color = '#1D1A16';
const t = penpot.library.local.createTypography();
t.name = 'Body';
t.setFont(penpot.fonts.findByName('<Family Name>'));   // confirm it exists first
t.fontSize = '16'; t.lineHeight = '1.5'; t.fontWeight = '400'; t.letterSpacing = '0';
```

Check the font first: `penpot.fonts.findByName(name)` returns null when missing;
`.variants.map(v => v.fontWeight)` lists available weights.

Tokens (three tiers, semantic references global):

```js
const cat = penpot.library.local.tokens;
const set = cat.sets.find(s => s.name === 'core') || cat.addSet({ name: 'core' });
if (!set.active) set.toggleActive();
set.addToken({ type: 'color', name: 'color.base.ink.900', value: '#1D1A16' });
set.addToken({ type: 'color', name: 'color.text.primary', value: '{color.base.ink.900}' });
set.addToken({ type: 'spacing', name: 'space.6', value: '24' });
set.addToken({ type: 'borderRadius', name: 'radius.control', value: '6' });
```

Token types available: color, dimension, spacing, typography, shadow, opacity,
borderRadius, borderWidth, fontWeights, fontSizes, fontFamilies, letterSpacing,
textDecoration, textCase. There is no duration/easing type: keep motion specs on a
`spec/motion` board as text and in your message.

Apply tokens to shapes (asynchronous; check `shape.tokens` afterwards):

```js
const tok = penpotUtils.findTokenByName('color.text.primary');
shape.applyToken(tok, ['fill']);          // e.g. 'fill', 'strokeColor', 'rowGap',
                                          // 'paddingLeft', 'borderRadiusTopLeft', 'typography'
```

Boards, layout, text, components:

```js
const board = penpot.createBoard();
board.name = 'screens/pricing';
board.resize(1440, 900);
const flex = board.addFlexLayout();       // board.addGridLayout() for grids
flex.dir = 'column'; flex.rowGap = 24;
flex.topPadding = 96; flex.bottomPadding = 96;
flex.leftPadding = 64; flex.rightPadding = 64;
const title = penpot.createText('Plan by the hour, not the month');
title.name = 'title';
board.appendChild(title);                 // append in visual order
```

- Adding flex layout to a board that already has children: use
  `penpotUtils.addFlexLayout(container, dir)` to keep their visual order.
- A layout container that should hug its content: set the layout's sizing,
  e.g. `board.flex.verticalSizing = "auto"` (same for `horizontalSizing`).
- After `resize()` on text, set `growType` back to `"auto-width"` or
  `"auto-height"`.
- Read results of a change in the same call only after
  `await penpot.waitForLayoutUpdate()`.
- Component from shapes: `penpot.library.local.createComponent([shape])`, then set
  `.name = 'button/primary/default'`. Instance with `component.instance()`.
- Variants: `penpotUtils.createVariantContainer([{ shape, properties: { State: 'Default' } }, …])`.
- Fills are replaced whole: `shape.fills = [{ fillColor: '#1D1A16', fillOpacity: 1 }]`
  (setting a raw value removes a token binding).
- `remove()` permanently deletes; do not use it to move shapes (use
  `appendChild` on the new parent).

Handoff helpers: `penpot.generateStyle(shapes, { type: 'css', withChildren: true })`
and `penpot.generateMarkup(shapes, { type: 'html' })` produce CSS and HTML/SVG
from the design, useful when the user wants code that matches Penpot exactly.

## 6. Working discipline

- Read-only first, then small writes; verify each write with a structure read or
  `export_shape`.
- Keep individual `execute_code` calls small; split large builds into several
  calls and re-read state between them.
- Do not log what you also return (it duplicates output).
- Describe intended changes before broad renames, palette swaps or restructures.
- Name layers by function, components with slash paths, boards for handoff.
- Base spacing unit (4 or 8) everywhere; no hard values where a token exists.

## 7. Fallback: Penpot not connected

Say so in one line and continue with:

1. The five-line brief.
2. Token table: `name | value | role` (colour, type, space, radius, shadow,
   duration, easing).
3. Per section or screen: purpose, layout (ASCII wireframe), components and states.
4. Animation table: element, trigger, property, duration, easing, reduced-motion
   alternative.
5. Optionally one self-contained HTML file: semantic elements, plain CSS with
   custom properties named after the tokens (`--color-text-primary`), no external
   dependencies or build step, a `prefers-reduced-motion` block, visible focus
   styles, and real copy.
6. A note that the tokens can be written into Penpot once the plugin is connected.
