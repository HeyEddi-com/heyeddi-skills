# Clarify before act (all HeyEddi skills)

**Date:** 2026-11-23

Every skill follows this order when information is missing. It is the "missing information" part of `@heyeddi` `reference/autonomy.md`.

```
1. Read .heyeddi/     product.md, design.md, routing, skills-index, handoffs
2. Run load/audit     your skill's readonly script
3. Inspect repo       code, openapi, tests: objective facts
4. Decide + record    the documented default or the complete working version;
                      append_decision.py when it matters, else Assumptions in the summary
5. Act                keep going
```

Never guess API field names: sync OpenAPI instead. Never guess routes: read routing and the router.

## When a question is worth a pause

Only when the repo cannot settle it and a wrong guess is expensive to undo:

- Two readings lead to a different data model, public API, or irreversible migration
- Irreversible stack choice (Flutter vs Vue, Firebase vs API-only) on a greenfield project
- The user's message conflicts with `product.md` on what the product is for

Build everything that does not depend on the answer first, then ask once, in the final summary under **Needs you**.

Design and discovery conversations (`@heyeddi-design discover` / `shape`, `@heyeddi-intake`) ask their interview questions because the user asked for that conversation.

## Anti-patterns

- Ending the turn to ask something `.heyeddi/`, OpenAPI, or tests answer
- Asking which of two reasonable options to use: pick the recommended one and record why
- Dumping 10 questions at once: batch the few that matter
