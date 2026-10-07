# Per-skill triggers (optional)

The orchestrator scores **every installed skill** from:

1. **SKILL.md `description`**: token and phrase overlap with the user prompt
2. **Skill name**: hyphen segments (`heyeddi-handoff` → `design`, `handoff`)
3. **`reference/triggers.md`** (optional): extra phrases owned by each skill

No central hardcoded map. New skills work automatically if they have a good description.

## Add triggers to your skill

Create `reference/triggers.md` in the skill folder:

```markdown
# Triggers
new app
greenfield
/no mockups yet/i
regex:\bproduct idea\b
```

| Line format | Match |
|-------------|-------|
| Plain text | Case-insensitive substring in prompt |
| `/pattern/i` | Regex (flags after closing `/`) |
| `regex:...` | Regex |

Also supported: `reference/triggers.txt`, root `triggers.txt`.

## Priority order

1. **`skill-routing.json`** (score 100): from `@heyeddi-intake`
2. **Description + triggers**: dynamic per installed skill

## Tips for descriptions

Write the frontmatter `description` with **verbs and nouns users actually say**:

- Good: "Screenshot-first design implementation (Vue). Use when mockups or handoff PNGs exist."
- Weak: "Design skill for the hub."

Cursor skill discovery and orchestrator scoring both read this field.
