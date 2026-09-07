# Clarify before act (all HeyEddi skills)

**Date:** 2026-09-04

Every skill follows this order when information is missing:

```
1. Read .heyeddi/     product.md, design.md, routing, skills-index, handoffs
2. Run load/audit     your skill's readonly script
3. Inspect repo       code, openapi, tests — objective facts
4. Ask the user       1 focused question or numbered list (max one round unless blocking)
5. Act                never guess routes, API fields, or layout intent
```

## Always-on (every chat)

Before step 5 when planning or coding:

1. **`@heyeddi-orchestrator`** — route if session start or task is ambiguous
2. **`@engineering-excellence`** — `check_engineering_plan --check` before implement; `audit_engineering --check` after edits (errors fail; warns advisory)
3. **Prose anti-slop** — `verify_prose --check` when user-facing or `.heyeddi` prose changes

See `docs/always-on-skills.md`.

## When to ask

- Ambiguous product intent, missing persona, unclear register (brand vs app)
- Missing handoff (no mockup, no brief, no mobile)
- Irreversible stack choice (Flutter vs Vue, Firebase vs API-only)
- User message conflicts with `product.md`
- **Skills hub update available** (`check_skills_update` / `sync` reports `ask_user`): ask before `npx skills add`

## When not to ask

- Answer is in `.heyeddi/` — read it first
- OpenAPI / build / tests settle it
- Scaffold defaults exist (`stack.json`, foundations)

## Anti-patterns

- Guessing API field names → sync OpenAPI instead
- Dumping 10 questions at once → 2–3 per round
- Skipping `product.md` personas on design work → run `@heyeddi-intake` or `@heyeddi-design discover`
- Auto-updating installed skills without approval → detect with `@heyeddi-orchestrator` `check_skills_update`, then ask
- Skipping engineering excellence on a coding chat → always-on plan + change gates
