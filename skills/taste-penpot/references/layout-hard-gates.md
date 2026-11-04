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

**Fail:**

- Demo brief or chat claims "Flex column" / "CSS Grid" when frames are only
  absolute geometry (no layout attrs, no Shift+A)
- Inspect CSS handoff invented from absolute boards without HTML or real Flex

**Pass:**

- Boards with MCP Flex/Grid set are labelled **hi-fi** in `penpot-demo.md`
- Absolute-only boards are labelled **low-fi / absolute sketch**
- Implementation CSS comes from Penpot Inspect (real Flex/Grid) or from
  `hifi.html` (Gate C)

---

## Gate C - HTML ACT 2.6 when MCP cannot Flex

**Trigger (any of these):**

- Live schema cannot set flex/grid or nest with `parentId` (upstream zcubekr-only)
- `design.penpot` is `off`
- User declined Penpot install

**Waived when:** HeyEddi MCP (or equivalent) set Flex/Grid on the boards and nested
children with `parentId`, and Gate D passed on those exports.

**Required output when triggered:**

1. Five-line brief + token table (`--app-*` roles)
2. Layout-engine table (Flex/Grid per region, gap, Fit/Fill/Fix)
3. **Self-contained HTML+CSS** at `.heyeddi/designs/<feature>/hifi.html`
4. Optional low-fi MCP sketches do not replace this file

Skipping HTML because "Penpot was connected" while MCP lacked Flex is a **process
fail**.

---

## Gate D - Visual QA before done

**Fail:** Claiming done without looking at pixels.

**Pass (minimum):**

1. `export_shape` of Flex boards **and/or** render `hifi.html`
2. **Read the image** (Read tool on PNG, or screenshot)
3. CRITIQUE: Gate A, hierarchy, 8px rhythm, mode fit
4. Fix every 0; re-check once
5. Then present and hand to `@heyeddi-design`

When Vue exists for the route, also chain `@visual-auditor`.

---

## Done checklist (copy into CRITIQUE)

- [ ] No text-wall (Gate A)
- [ ] Absolute boards not sold as Flex (Gate B)
- [ ] Flex/Grid boards via HeyEddi MCP **or** `hifi.html` (Gate C)
- [ ] Pixels reviewed and CRITIQUE fixed (Gate D)
- [ ] `penpot-demo.md` records low-fi vs hi-fi and Aura token roles

Any unchecked box → **not done**.
