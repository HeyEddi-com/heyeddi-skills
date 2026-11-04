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

**Pass:** `@taste-penpot` places separate field rows on an 8px grid (MCP low-fi optional), writes `.heyeddi/designs/settings/hifi.html` with Flex column sections and real field rows, exports/renders, reads pixels, then hands off. `@heyeddi-design` craft refuses text-walls and missing `hifi.html`.
