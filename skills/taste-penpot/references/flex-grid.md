# Penpot Flex and CSS Grid

Load during PLAN when a surface has structure, and again in ACT when writing boards, `penpot-demo.md`, or the HTML fallback.

Penpot lays out with the same engines browsers use: **CSS Flexbox** and **CSS Grid**. Match the dimensionality of the region to the engine. Record the choice so Inspect CSS and the Vue spec stay the same declaration.

| | Flex (`Shift + A`) | CSS Grid (`Ctrl/Cmd + Shift + A`) |
|---|---|---|
| Dimensionality | 1D: row or column | 2D: rows and columns together |
| Use for | Components, stacks, buttons, navbars, chip rows | Page skeletons, dashboards, card galleries, data sheets |
| Sizing | Content-out: children dictate flow | Layout-in: tracks and areas place children |
| Wrap | Items wrap to the next line | Tracks distribute across rows and columns |
| Axes | Main axis and cross axis | Horizontal tracks and vertical tracks |

Do not build a stack or a page skeleton out of absolutely positioned rectangles. Absolute position is only for an overlay that must leave the flow (badge, close icon, tooltip).

Gap and padding use the spacing scale (4, 8, 12, 16, 24, 32, 48, 64, 96). Write pixels in Penpot. Write the same steps as tokens in Vue.

## Flex

One direction at a time. Use it inside components, lists, and toolbars.

Activate on a group, board, or multi-selection with **Shift + A** (or Flex in the Design panel).

- **Direction:** Row, Column, Row Reverse, or Column Reverse.
- **Justify content** (main axis): Start, Center, End, Space Between, Space Around, Space Evenly. A header uses Space Between so the logo stays at the start and actions stay at the end.
- **Align items** (cross axis): Stretch, Start, Center, End, Baseline. A row header uses Center.
- **Gap and padding:** independent horizontal and vertical gap. Padding is uniform or per side (top, right, bottom, left).
- **Wrap:** on for tags, filter chips, and badge clouds so overflow goes to the next line.
- **Absolute position:** on one child, to float a badge or close icon without taking a flex slot.
- **Z-index:** stacking for overlaps. Do not reorder the layer tree just to change paint order.

Each child has its own width and height. Set both axes. The panel labels and the file-format values are different words:

| Panel | `layoutChild` sizing | CSS |
|---|---|---|
| Fit Content | `auto` | `max-content` / hug text or vectors |
| Fill | `fill` | `flex-grow: 1` inside a flex parent |
| Fix | `fix` | a locked px size |

`fill` only works when the parent is already a flex or grid layout. On a grid **track**, free space is track type `flex` (that is `1fr`), not this child field.

## CSS Grid

Two dimensions. Use it when rows and columns must stay aligned with each other.

Activate on a board or container with **Ctrl/Cmd + Shift + A** (or Grid in the Layout dropdown). The canvas shows column and row tracks.

Track sizes, on columns and on rows. The track type `flex` means `fr`. It does not make the track a flex container. Child sizing `fix` is a different word from track type `fixed`.

| Track type | CSS | Use |
|---|---|---|
| `fixed` | px | Sidebars, icon rails, header height |
| `flex` | fr | Share of free space. `1` and `3` is 25% and 75% |
| `auto` | fit-content of the largest cell | The track hugs its biggest child |
| `percent` | % of the grid | A share that does not depend on free space |

`minmax(250px, 1fr)` is the CSS form of a column that never collapses below 250px and still grows. The plugin track list has no minmax type. Write that bound in the spec and in the Vue CSS.

Placement:

- **Auto:** new children fill the next open cell.
- **Manual:** drag a child across cells to span. A hero can span `1 / -1` (full width). Cards under it occupy one cell each.
- **Row gap** and **column gap** are independent.

## What to write down

In `.heyeddi/designs/<feature>/penpot-demo.md`, and in the Layout section of `.heyeddi/design.md`, name the engine per region:

```markdown
| Region | Engine | Tracks or direction | Gap / padding | Children |
|---|---|---|---|---|
| App shell | Grid | cols: sidebar `fixed` + `flex` 1; rows: header `fixed` + `flex` 1 | column gap 0 | sidebar `layoutCell.rowSpan` 2 |
| Header | Flex row | justify: space-between; align: center | padding from scale | logo fit; actions fit |
| Nav | Flex column | align: stretch | gap 16 | links fill width, fit height |
| Cards | Grid | `repeat(auto-fit, minmax(250px, 1fr))` | row and column gap 16 | card fill |
```

If the live `@zcubekr/penpot-mcp-server` schema can set flex or grid on a frame, set it with the names in **File format** below. `create_frame` today sets geometry, fill, and radius only. It does not take `layoutChild` or grid tracks. When those fields are absent, the table above is the instruction for **Shift + A** or **Ctrl/Cmd + Shift + A**. Do not switch to `@penpot/mcp` or `execute_code` to call `penpot.createBoard()`. The HTML fallback in ACT 2.6 uses the same `display`, `gap`, tracks, and child sizing. No external CSS.

Inspect in Penpot emits production CSS (`display: flex; gap: 16px` or `display: grid; grid-template-columns: …`). That CSS is what `@heyeddi-handoff` copies into the Implementation spec. Do not translate it into margin stacks.

## Recipes

Widths below are patterns. Pick the fixed tracks from the product (a sidebar that serves content is nearer 240–280px than a peer column).

### Dashboard shell

Penpot board, for example 1440×900, **Grid**:

- Columns: track `fixed` sidebar + track `flex` 1 (`1fr`) main.
- Rows: track `fixed` header + track `flex` 1 body.
- Sidebar: column 1, spans both rows. Inside, **Flex column**, gap 16, nav links.
- Header: column 2, row 1. **Flex row**, justify space-between, align center.
- Body: column 2, row 2. Nested grid, or a scrolling flex column.

Vue keeps the app frame on Quasar (`q-layout`, `q-drawer`, `q-header`, `q-page`). The drawer width is the sidebar track. The header height is the header track. Do not replace that frame with a second CSS grid. Interiors of the page use the engine named in the spec: grid for a 2D body, flex for a 1D stack.

That shell is `view="lHh Lpr lFf"`: the header row's left cell is `l`, so the drawer owns the full height and the header sits in the main column. Use `h` in that left cell only when the spec says the header spans the full width. `show-if-above` keeps the drawer closed below the breakpoint.

At 375 the sidebar track becomes the drawer. Do not leave a fixed sidebar column on a 375 board.

### Equal-height cards

Card is **Flex column**, padding 24, gap 16.

- Image: width Fill, height Fix (the shared media height).
- Title and description: width Fill, height Fit Content.
- Description, or a spacer: height Fill (`flex-grow: 1`).
- CTA: width Fill, last in the column.

The growing middle keeps buttons on one baseline across cards with different text lengths. The parent of the cards is Grid with `minmax`, so columns reflow instead of shrinking to unreadability.

## File format

These are the Penpot file fields and the plugin object model (`layoutChild`, `addColumn`, `appendChild`). Use them when a tool schema exposes them. Colors and type still come from the token table, not from a sample hex or a sample font.

Child of a flex or grid parent, both axes: `layoutItemHSizing` and `layoutItemVSizing` (plugin: `layoutChild.horizontalSizing` and `verticalSizing`). Values are `fix`, `fill`, or `auto`.

Do not set `x`, `y`, `width`, or `height` on a child the layout owns. Assigning the board's width stops the layout from propagating.

Grid tracks are `layoutGridColumns` and `layoutGridRows`. Each track is `{ type, value }` with type `fixed`, `flex`, `auto`, or `percent`. Plugin calls are `addColumn(type, value)` and `addRow(type, value)`. A 260px sidebar plus a main column is `fixed` 260, then `flex` 1. A 72px header plus a body row is `fixed` 72, then `flex` 1.

Placement is zero-indexed, **row then column**: `appendChild(child, row, column)`. The header in column 1, row 0 is `appendChild(header, 0, 1)`. The body in column 1, row 1 is `appendChild(body, 1, 1)`. The sidebar in column 0, row 0 is `appendChild(sidebar, 0, 0)`.

Span lives on the cell, not the child sizing object: `layoutCell.rowSpan` and `layoutCell.columnSpan` (file cells use `rowSpan` and `columnSpan`). A full-height sidebar sets `rowSpan` to 2. It does not set `layoutChild.rowSpan`.

A flex board inside a grid cell sets horizontal sizing to `fill` so it uses the track. After text is written, set `growType` (`auto-width` or `auto-height`) and the child sizing. A label is `auto` / `auto`. A card title is horizontal `fill`, vertical `auto`. The text block that pins a button to the bottom is horizontal `fill`, vertical `fill`. That button is horizontal `fill`, vertical `fix`.

Before leaving the board:

- No `x`, `y`, `width`, or `height` on children the layout owns.
- A flex container inside a grid cell is horizontal `fill`.
- Text `growType` matches the sizing just set.
- Gap, padding, and radius are steps on the spacing scale.
- A text block that clips is `auto` or `fill`, not a short `fix`.

## Boards

Responsive surfaces still get boards at 375, 768, and 1440. Each width is the same engines with different tracks (stack, wrap, or a collapsed sidebar), not a separate absolute composition.
