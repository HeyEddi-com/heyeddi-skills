# Layout hard gates (hi-fi bar)

Load during ACT and again before CRITIQUE claims done. These gates are **reject
rules**, not advice. A Suite, settings screen, form, dashboard, or any Operate
surface that fails any gate is **not done**. Do not hand off to
`@heyeddi-design` craft / `@heyeddi-handoff` until every gate passes.

Human designers ship **aligned fields on a grid**, not a paste of copy inside one
gray rectangle. Match that bar.

**Design system first:** before drawing phones, create or reuse Penpot shared
colours and typographies (`add_color` / `add_typography`, or the file's existing
library). Blind drawing without a system is a process fail (Gate E).

---

## MCP capability (detect live)

Prefer **`@heyeddi/penpot-mcp-server`** (`github:HeyEddi-com/penpot-mcp-server`):

- `parentId` on create tools (nest into a board)
- `set_frame_layout` / `layout` on `create_frame` (Flex or Grid)
- `layoutItemHSizing` / `layoutItemVSizing` (`fill` | `fix` | `auto`)
- `reparent_shape`, `set_layout_item`
- `add_color` / `add_typography` / `list_font_variants` (design system)
- `export_shape`, `audit_board` (QA — see known limits below)

**Upstream `@zcubekr/penpot-mcp-server` alone** still places absolute frames/rects/text
only. Absolute boards are **low-fi sketches**. Do not claim Flex from them.

Detect capacity from the live tool list this session:

| Live tools | Hi-fi path |
|---|---|
| `set_frame_layout` or `create_frame` accepts `layout` + `parentId` | Penpot Flex/Grid boards **only if Gate B+F pass** (reflow real). Else absolute 8px layout. |
| Only absolute create_* (no parentId / no layout) | Mandatory ACT 2.6 `hifi.html` |

Flex in the Penpot UI remains **Shift+A** (Grid: **Ctrl/Cmd+Shift+A**) if a human
finishes layout by hand.

### Known MCP limits (do not paper over)

These are real API gaps. Skills treat them as hard stops, not as "try harder":

1. **Flex does not reflow selrects via API.** `layout: "flex"` can save while
   children stay at `x/y = 0`. Flags alone are not a laid-out board.
2. **`layoutItem*` on create often does not stick** (read-back `null`). Only
   `set_layout_item` then a read-back proves sizing.
3. **`create_image` is weaker than rect image fills.** Prefer a rectangle with a
   cover image fill. `PENPOT_ACCESS_TOKEN` alone may be incomplete for media
   paint — see `PENPOT_AUTH_TOKEN` in the MCP README when fills must match the
   canvas.
4. **`export_shape` / some auth paths can hit Cloudflare.** No PNG ⇒ Gate D
   fails. Do not mark done.
5. **`audit_board` is noisy.** Normal UI stacking (label on button, text on nav)
   can look like failure; a "pass" after hand-placed coords can still look wrong
   in the UI. Never ship on audit alone.

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
`set_layout_item` (do not trust create-time `layoutItem*` alone). Never one wall of
copy.

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
- `layout: "flex"` (or grid) is set, but **almost every child still reads
  `x/y = 0`** after create + `set_layout_item` — the API did not reflow. That is
  **not** hi-fi Flex. Switch to **absolute 8px layout** (or stop). Do **not**
  rebuild the same nested-Flex approach a second time
- `penpot-demo.md` says hi-fi after the API rejected the change, or quotes a
  page id that `list_pages` does not return
- Inspect CSS invented from absolute boards

**Pass:**

- Read-back shows `layout` on the phone and `parentId` of the type, form, and
  nav. Children have **non-zero stacked positions** (or proven layoutItem sizing
  that the canvas shows). `penpot-demo.md` quotes that read-back (page id,
  layout, parent ids, sample child x/y)
- Absolute geometry is labelled **low-fi / absolute sketch**, not hi-fi — unless
  you deliberately chose absolute 8px after Flex reflow failed, then label
  **hi-fi / absolute 8px** only after Gate D PNG proves the canvas
- If the shape read omits `parentId` and `layout`, you cannot claim Flex. The
  board stays low-fi until a read shows both **and** positions are real

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
- `export_shape` is missing **or** returns Cloudflare / auth error, and the
  pass still calls the boards done. **No PNG ⇒ not done.** Say so. Do not
  substitute API success or `audit_board` pass
- A board that does not show its own type fails: the copy can be in the file
  and still be absent on the phone
- The PNG or the canvas shows a photo as a thumbnail in the corner. Attaching
  a media id is not a cover fill. A rejected fill replacement means the board
  still fails. Prefer **rect + cover image fill** over `create_image` alone
- Children still at 0,0, unparented, while the write-up says hi-fi
- `audit_board` "pass" alone is treated as visual QA

**Pass:**

1. Call `export_shape` on each phone and **read the PNG**. The image shows the
   type, the form, and the nav. A corner thumbnail fails. Cloudflare / missing
   tool / empty bytes = **stop**; report the block; do not claim done
2. If `export_shape` is missing from the schema, you still may not mark hi-fi
   without looking at the live canvas. HTML does not replace this step. Prefer
   fixing export auth (`PENPOT_AUTH_TOKEN` / Cloudflare) over shipping blind
3. When `audit_board` exists, use it as a **hint** only. Fix real overlaps and
   empty screens. Ignore noisy "label on button" stacking if the PNG looks
   correct. Never ship on audit alone
4. CRITIQUE, fix every 0, re-check once (PNG again), then hand to
   `@heyeddi-design`

When Vue exists for the route, also chain `@visual-auditor`.

---

## Gate E - Design system before phones

**Fail:**

- Drawing boards without first creating or reusing shared colours and
  typographies in the Penpot file
- Inventing `fontFamily` values (e.g. Sora, Nunito) that are not in
  `list_font_variants` / the file's font library
- Skipping `add_color` / `add_typography` (or equivalent) when the file has no
  system yet, then painting ad-hoc hex on every shape

**Pass:**

1. `list_files` / `get_file` → reuse existing library colours and type roles when
   the brief is a refine
2. On a new system or redesign: `add_color` and `add_typography` (named roles
   matching the token table) **before** the first phone board
3. Fonts only from `list_font_variants` or fonts already in the file. Unknown
   faces → pick a proven Penpot font or upload via the MCP font tools; never
   hope the canvas has Sora/Nunito
4. Shape fills and text reference those library entries (or the same hex/roles
   already registered)

---

## Gate F - Flex reflow / layoutItem stickiness

**Fail:**

- Nested Flex + Flex children when read-back still shows children at `0,0`
- Trusting create-time `layoutItemHSizing` / `layoutItemVSizing` without
  `set_layout_item` + read-back (often `null`)
- Rebuilding the same Flex approach after one failed reflow pass

**Pass / escape hatch:**

1. After create: call `set_layout_item` for every Flex/Grid child; read
   `layoutItem*` and `x`/`y` back
2. If children remain at `0,0` (or sizing still null): **stop Flex**. Lay out
   with **absolute positions on the 8px grid** under the same phone
   `parentId`, or fall through to ACT 2.6. Label honestly in `penpot-demo.md`
3. One Flex attempt per board. Second attempt must change strategy (absolute
   8px or HTML), not deepen nesting

---

## Gate G - Page hygiene

**Fail:**

- Leaving empty or broken pages (`Look`, dated shells, duplicate empty phones)
  in the file so the next pass screenshots the wrong board
- Creating a new page for every try without renaming or replacing the in-scope
  boards

**Pass:**

- In-scope pages are the ones you mean to show. Empty shells from failed
  attempts are renamed, replaced, or left out of the demo brief
- `penpot-demo.md` lists only live page ids from `list_pages`
- Do not delete pages/shapes unless the user named that exact target; prefer
  rename / update / replace content on the boards in scope

---

## Done checklist (copy into CRITIQUE)

- [ ] No text-wall (Gate A)
- [ ] Read-back shows `layout` and `parentId` before any Flex hi-fi label; children not stuck at 0,0 (Gate B + F)
- [ ] `hifi.html` was not used as proof of the Penpot file (Gate C)
- [ ] Canvas PNG read (or explicit export block reported). Type visible. No corner thumbnail. Audit alone does not ship (Gate D)
- [ ] Shared colours + typographies exist; fonts from Penpot library only (Gate E)
- [ ] `set_layout_item` read-back, or absolute 8px escape after one Flex fail (Gate F)
- [ ] No orphan empty pages left as the demo surface (Gate G)
- [ ] `penpot-demo.md` quotes the read-back and does not call broken Flex hi-fi

Any unchecked box → **not done**.
