# Examples

## Session start (existing project)

```bash
python scripts/load_catalog.py --project-root .
python scripts/suggest_skills.py --project-root . --user-prompt "Polish the login page and verify build"
```

Expected top picks: `@heyeddi-design`, `@verify-build`.

## After heyeddi-intake

When `.heyeddi/docs/intake/skill-routing.json` lists `/settings` → `@heyeddi-handoff`, `suggest_skills` returns that route at priority 100 even if the prompt is vague.

## Greenfield

Prompt: "Build TaskFlow: Vue + FastAPI, no mockups yet"

→ `@heyeddi-intake` first (intake), then follow generated routing.
