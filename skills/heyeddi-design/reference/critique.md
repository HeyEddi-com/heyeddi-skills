# Critique: evaluate existing UI (before improving)

**Scope:** Designer-eye review of **implemented** UI. **No code changes** unless the user explicitly asks to fix issues after the critique.

Critique answers: *what's wrong, why it feels off, and what to fix first.* **Polish**, **craft**, and **document** consume this output: do not skip critique when improving existing screens.

## When to use

- User says *critique*, *review*, *what's wrong*, *this looks bad*, *audit the UI*: even **without** a sub-command
- **Before `polish`** on any route (mandatory unless you wrote a critique in this session)
- Brownfield: existing Vue looks unprofessional but IA is fine

## Steps

1. Run `load_context.py`: `.heyeddi/product.md`, `.heyeddi/design.md`, route/component paths.
2. Read the target: `*View.vue`, layout components, scoped styles, `tokens.css`. Note drift from `design.md`.
3. Optional: `@visual-auditor` at 375/768/1440 if dev server available: fold captures into critique.
4. Compare against `reference/surface-completeness.md`, `reference/audience-fit.md`, `reference/aesthetic-direction.md`, and `design.md` **Components** / **Layout**.
5. **Write** `.heyeddi/docs/<feature>-critique.md` (kebab-case from route, e.g. `login-critique.md` for `/login`).

## Critique report structure

```markdown
# Critique: <Route> (<date>)

## First impression
<2-4 sentences: how it feels today>

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
Run `reference/audience-fit.md`: include rubric table and PASS/REVISE verdict.

## Aesthetic direction
Run `reference/aesthetic-direction.md` checklist: subject/thesis, type personality, fake structure chrome, motion spam, generic AI look clusters, missing aesthetic risk / signature.

## Recommended next step
- [ ] `polish`: spacing, PrimeVue, tokens (most common)
- [ ] `shape`: IA wrong, needs replan
- [ ] `document`: design.md out of sync
```

6. **Present the critique in chat**: summary + path to the file.
7. **Stop** unless user asks to fix. If they want fixes → run `reference/polish.md` using this critique as the backlog.

## Boundaries

- **Not** for approved designer mockups → `@heyeddi-handoff` (`interpret` = critique of **target** mockups, then brief).
- **Not** a linter dump: designer voice, tied to `design.md` tokens and PrimeVue catalog.
- Do not rewrite IA in critique without flagging `shape` first.

## Routing (no sub-command)

If the user critiques **existing code** (not vague greenfield intent), load **this file**: not `discover.md`.

| User intent | Route to |
|-------------|----------|
| "Critique the login page" | **critique**: stop after report |
| "This settings page looks terrible, fix it" | **critique** → then **polish** |
| "Design a new settings page" | **discover** / **shape** |
