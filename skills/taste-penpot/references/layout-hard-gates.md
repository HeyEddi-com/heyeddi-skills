# Layout hard gates (hi-fi bar)

Load during ACT and again before CRITIQUE claims done. These gates are **reject
rules**, not advice. A Suite, settings screen, form, dashboard, or any Operate
surface that fails any gate is **not done**. Do not hand off to
`@heyeddi-design` craft / `@heyeddi-handoff` until every gate passes.

Human designers ship **aligned fields on a grid**, not a paste of copy inside one
gray rectangle. Match that bar.

---

## MCP capability (detect live)

Prefer **`@heyeddi/penpot-mcp-server`** (`github:HeyEddi-com/penpot-mcp-server`):

- `parentId` on create tools (nest into a board)
- `set_frame_layout` / `layout` on `create_frame` (Flex or Grid)
- `layoutItemHSizing` / `layoutItemVSizing` (`fill` | `fix` | `auto`)
- `reparent_shape`, `set_layout_item`

**Upstream `@zcubekr/penpot-mcp-server` alone** still places absolute frames/rects/text
only. Absolute boards are **low-fi sketches**. Do not claim Flex from them.

Detect capacity from the live tool list this session:

| Live tools | Hi-fi path |
|---|---|
| `set_frame_layout` or `create_frame` accepts `layout` + `parentId` | Penpot Flex/Grid boards (Gate C HTML optional) |
| Only absolute create_* (no parentId / no layout) | Mandatory ACT 2.6 `hifi.html` |

Flex in the Penpot UI remains **Shift+A** (Grid: **Ctrl/Cmd+Shift+A**) if a human
finishes layout by hand.

---

## Gate A - Text-wall reject

**Fail (reject immediately):**

- One multiline `create_text` (or one HTML blob) that lists labels, values, and
  helpers as a single string inside a gray/raised rectangle
- A "card" that is only a filled rect + wall of copy
- Settings / profile / form / suite panels that look like a paste, not a UI

**Pass:**

- Separate elements per control: label, field (or field stand-in), helper,
  trailing action / chevron, section title, primary CTA
- Spacing on the **8px grid** (4/8/12/16/24/32...): tight inside a row, generous
  between sections
- Operate density like a real settings screen (People · Designed grade): rows
  align, baselines match, not a prose dump

With HeyEddi MCP: nest each field under the card/board via `parentId` and size with
`layoutItemHSizing` / `layoutItemVSizing`. Never one wall of copy.

---

## Gate B - Absolute ≠ Flex claim

Calling `set_frame_layout` is not proof. Label **hi-fi / Flex** only after you
read the board back in the same turn (`get_shape_properties` on the frame and
on the copy that belongs on it).

**Fail:**

- The brief says "Flex column" / "CSS Grid" and the read-back has no `layout`
  of `flex` or `grid`
- Copy, nav, or a card that belongs on a phone has no `parentId` of that phone
  (or of a frame parented to that phone). Shapes stored at 0,0 on the page, or
  a header whose y sits under the phone, are not on the board
- `penpot-demo.md` says hi-fi after the API rejected the change, or quotes a
  page id that `list_pages` does not return
- Inspect CSS invented from absolute boards

**Pass:**

- Read-back shows `layout` on the phone and `parentId` of the type, form, and
  nav. `penpot-demo.md` quotes that read-back (page id, layout, parent ids)
- Absolute geometry is labelled **low-fi / absolute sketch**, not hi-fi
- If the shape read omits `parentId` and `layout`, you cannot claim Flex. The
  board stays low-fi until a read shows both

---

## Gate C - HTML is not the Penpot file

`hifi.html` is a different artifact. It never proves a board in the Penpot file.

**Write HTML only when no Penpot boards were created:**

- Live schema cannot set flex/grid or nest with `parentId` (upstream zcubekr-only)
- `design.penpot` is `off`
- User declined Penpot install

**Required in that case:**

1. Five-line brief + token table (`--app-*` roles)
2. Layout-engine table (Flex/Grid per region, gap, Fit/Fill/Fix)
3. **Self-contained HTML+CSS** at `.heyeddi/designs/<feature>/hifi.html`
4. Optional low-fi MCP sketches do not replace this file

Skipping HTML because "Penpot was connected" while MCP lacked Flex is a **process
fail**.

Writing HTML and then calling Penpot boards done is also a **process fail**.
If the file has frames, Gate B and Gate D are about those frames.

---

## Gate D - The canvas, not the HTML mirror

**Fail:**

- `hifi.html` is treated as proof of the Penpot file
- `export_shape` is missing, and the pass still calls the boards done without
  reading the canvas. A board that does not show its own type fails: the copy
  can be in the file and still be absent on the phone
- The PNG or the canvas shows a photo as a thumbnail in the corner. Attaching
  a media id is not a cover fill. A rejected fill replacement means the board
  still fails
- Children still at 0,0, unparented, while the write-up says hi-fi

**Pass:**

1. If `export_shape` exists, call it on each phone and **read the PNG**. The
   image shows the type, the form, and the nav. A corner thumbnail fails
2. If `export_shape` is missing, read `get_shape_properties` for the frame and
   each child (`parentId`, `layout`, `x`, `y`, fill width/height versus the
   shape) and look at the canvas. HTML does not replace this step, and you
   still may not mark the board hi-fi
3. When `audit_board` exists, it reports nothing. Fix every line and run it again
4. CRITIQUE, fix every 0, re-check once, then hand to `@heyeddi-design`

When Vue exists for the route, also chain `@visual-auditor`.

---

## Done checklist (copy into CRITIQUE)

- [ ] No text-wall (Gate A)
- [ ] Read-back shows `layout` and `parentId` before any hi-fi label (Gate B)
- [ ] `hifi.html` was not used as proof of the Penpot file (Gate C)
- [ ] Canvas read: PNG or shape read. Type is visible on the phone. No corner thumbnail (Gate D)
- [ ] `penpot-demo.md` quotes the read-back and does not call absolute geometry hi-fi

Any unchecked box → **not done**.
