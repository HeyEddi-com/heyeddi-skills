# Critique: evaluate existing UI (then fix — default)

**Scope:** Designer-eye review of **implemented** UI, then **automatic** next step: either **local polish-path fixes** or **`shape` redesign** when ambition fails.

Critique answers: *what's wrong, why it feels off, what to fix first.* **Do not stop after the report** unless the user explicitly said "critique only, no code".

## When to use

- User says *critique*, *review*, *what's wrong*, *this looks bad*, *audit the UI*, *fix this page*
- User says *better design*, *make it better*, *redesign*, *new look*, *overhaul*, *wow*, *top notch* on an **existing** route (ambition gate usually → `shape`)
- **Before `polish`** on any route (mandatory unless critique written this session)
- Brownfield: existing UI looks unprofessional

## Ambition gate (before choosing polish vs shape)

After reading the UI, decide **Escalate: shape** vs **Stay: polish**. Do not default to spacing tweaks when the user wanted a better design.

**Escalate to `shape` → craft** when **any** of these are true:

1. User phrased **redesign intent**: better design, make it better, redesign, new look, overhaul, major improvement, wow, top notch, artistic, impressive
2. **Name-swap test fails**: UI could belong to another product after swapping the logo/name
3. **Template / scaffold tells**: default PrimeVue admin chrome, flat gray shell, undifferentiated cards/tables, system-font sameness, generic AI SaaS look (`aesthetic-direction.md`)
4. **No Design signature** in brief / Decision log for this flagship route, or signature not visible in the UI
5. **IA / hierarchy wrong**: wrong primary action, wrong information architecture, or layout that polish cannot fix
6. Ambition checklist (`design-ambition.md`) would fail **2+** items even after local P0/P1 fixes

**Stay on polish-path** only when: user asked for local fix (fix / polish / tweak / looks bad) **and** none of 2–6 apply **and** a sharpened signature is already present.

When escalating: write the critique with `Recommended next step: shape`, then run `reference/shape.md` (confirm Design signature) → `craft` → stack implementer. **Do not** apply polish-only code as the response to redesign intent.

## Steps

1. Run `load_context.py`: `.heyeddi/product.md`, `.heyeddi/design.md`, route/component paths.
2. Read the target implementation files. Note drift from `design.md`.
3. Run `@visual-auditor` at 375/768/1440 if dev server available — fold captures into critique.
4. Compare against `surface-completeness.md`, `audience-fit.md`, `aesthetic-direction.md`, `design-ambition.md`, and `design.md`.
5. **Run ambition gate** (above). Record Escalate / Stay in the critique.
6. **Write** `.heyeddi/docs/<feature>-critique.md` (kebab-case from route).

## Critique report structure

```markdown
# Critique: <Route> (<date>)

## First impression
<2-4 sentences>

## Ambition gate
- Verdict: ESCALATE shape | STAY polish
- Triggers: <which criteria matched, or none>

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
- [ ] `shape` → craft → implement (ambition gate escalate / redesign intent)
- [ ] stack implementer: P0/P1 code fixes (stay polish)
- [ ] `@visual-auditor`: capture + contrast + fix
- [ ] `polish`: design.md / brief updates if tokens need doc sync
```

7. **Present critique summary in chat** + file path.
8. **Immediately chain the recommended path** (default — do not ask):
   - **Escalate:** `shape` (confirm brief + Design signature) → `craft` → stack implementer → `@visual-auditor`
   - **Stay:** stack implementer applies P0/P1 (`implement-routing.md`) → `@visual-auditor` → `polish` if design.md / brief needs sync

## Boundaries

- Approved designer mockups → `@heyeddi-handoff`, not critique-first.
- Designer voice, tied to `design.md` — not a linter dump.
- Do not rewrite IA in the polish path — escalate to `shape` instead.
- Never answer "better design" with spacing/token-only diffs when the ambition gate says escalate.

## Routing (no sub-command)

| User intent | Route to |
|-------------|----------|
| "Critique the login page" (only) | critique → ambition gate → implement or shape unless report-only |
| "This settings page looks terrible, fix it" | critique → gate → polish-path **or** shape if template-like |
| "Better design" / "make it better" / "redesign" | critique → **usually shape** → craft → implement |
| "Design a new settings page" | discover / shape |
