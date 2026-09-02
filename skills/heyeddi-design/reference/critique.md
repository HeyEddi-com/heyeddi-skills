# Critique: evaluate existing UI (then fix — default)

**Scope:** Designer-eye review of **implemented** UI, then **automatic** code fixes via stack implementer + `@visual-auditor`.

Critique answers: *what's wrong, why it feels off, what to fix first.* **Do not stop after the report** unless the user explicitly said "critique only, no code".

## When to use

- User says *critique*, *review*, *what's wrong*, *this looks bad*, *audit the UI*, *fix this page*
- **Before `polish`** on any route (mandatory unless critique written this session)
- Brownfield: existing UI looks unprofessional but IA is fine

## Steps

1. Run `load_context.py`: `.heyeddi/product.md`, `.heyeddi/design.md`, route/component paths.
2. Read the target implementation files. Note drift from `design.md`.
3. Run `@visual-auditor` at 375/768/1440 if dev server available — fold captures into critique.
4. Compare against `surface-completeness.md`, `audience-fit.md`, `aesthetic-direction.md`, and `design.md`.
5. **Write** `.heyeddi/docs/<feature>-critique.md` (kebab-case from route).

## Critique report structure

```markdown
# Critique: <Route> (<date>)

## First impression
<2-4 sentences>

## What's working
- …

## Issues (priority)

### P0: ship blockers
| Issue | Evidence | Fix direction |
|-------|----------|---------------|

### P1: hierarchy / polish
| Issue | Evidence | Fix direction |
|-------|----------|---------------|

### P2: nice-to-have
- …

## Token & component drift
- design.md says … / code does …

## Audience fit
Rubric table + PASS/REVISE per audience-fit.md.

## Aesthetic direction
Checklist from aesthetic-direction.md.

## Recommended next step
- [ ] stack implementer: P0/P1 code fixes
- [ ] `@visual-auditor`: capture + contrast + fix
- [ ] `polish`: design.md / brief updates if IA tokens need doc sync
- [ ] `shape`: IA wrong, needs replan
```

6. **Present critique summary in chat** + file path.
7. **Immediately chain fixes** (default — do not ask):
   - Stack implementer applies P0/P1 from critique (`implement-routing.md`)
   - `@visual-auditor` full fix loop
   - `@heyeddi-design polish` if design.md / brief needs sync

## Boundaries

- Approved designer mockups → `@heyeddi-handoff`, not critique-first.
- Designer voice, tied to `design.md` — not a linter dump.
- Do not rewrite IA in critique without flagging `shape` first.

## Routing (no sub-command)

| User intent | Route to |
|-------------|----------|
| "Critique the login page" (only) | critique → **still** implement + visual unless user said report-only |
| "This settings page looks terrible, fix it" | critique → implement → visual-auditor |
| "Design a new settings page" | discover / shape |
