# Examples

## Identity gate (no style pinned)

```
Design Margin — an EPUB/PDF/MD reader. Make it fancy and cool.
```

**Pass:** Write `.heyeddi/designs/margin-reader/identity-thinking.md` (job, audience, peer e-readers, follow vs unique). Ask if needed. Offer **3–5** What/Why/How options in chat + `identity-options.md`. **Stop.** After A–E, PLAN → ACT.

**Reject:** Skip taste, pick Fraunces + Literata + teal while scaffolding, call it done.

## Pinned metaphor (gate skipped)

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
