# Examples

```
Design the marketing home as an atlas desk. Cool paper, sea teal, no admin kit.
```

`@heyeddi` runs this skill first (one pass, tokens), then `@heyeddi-design` records the tokens in `.heyeddi/design.md` and hands off to Vue or Flutter.

## Operate / settings (hi-fi bar)

```
Design the settings suite: profile, notifications, billing.
```

**Reject:** one gray card per section with a multiline paste of labels and values.

**Pass:** `@taste-penpot` builds (or reuses) Penpot colours/typographies first, places separate field rows on an 8px grid with fonts from `list_font_variants`, calls `set_layout_item` and reads `layout` / `parentId` / child `x,y` back, escapes to absolute 8px if Flex stays at `0,0`, and looks at the **export PNG** before calling a board hi-fi. `audit_board` alone does not ship. `hifi.html` is only the hi-fi artifact when no Penpot boards were written. `@heyeddi-design` craft refuses text-walls and a Penpot file signed off from the HTML mirror.
