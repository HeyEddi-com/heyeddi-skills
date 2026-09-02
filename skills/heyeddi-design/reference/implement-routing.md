# Implement routing: design → stack skill

**Date:** 2026-09-01

`@heyeddi-design` is **stack-agnostic**. It produces briefs, critiques, and `design.md` updates — **not framework code**.

After a confirmed brief or critique-with-fixes, route implementation to the project's **frontend stack**.

## Detect stack

Read `.heyeddi/stack.json` → `frontend` (fallback: `package.json` → Vue; `pubspec.yaml` → Flutter).

| `frontend` | Implement skill | When |
|------------|-----------------|------|
| `vue` | `@heyeddi-handoff` | Mockups/PNGs in `.heyeddi/designs/<feature>/` |
| `vue` | `@heyeddi-handoff` | Brief only (no PNGs): implement from `brief.md` + wireframes |
| `flutter` | `@design-handoff-flutter` | Mockups or brief in `.heyeddi/designs/<feature>/` |
| missing / thin repo | `@project-engineering` or `@flutter-engineering` | Scaffold first, then handoff skill |

## Mandatory chain after implement

```
<stack implementer>
→ @primevue-openprops-architect   (Vue only, when editing .vue/.css)
→ @visual-auditor                 (always: capture, contrast, fix, document)
→ @ux-flow-auditor                (flagship routes: task completes in click budget)
```

## Design skill boundaries

| Output | Owner |
|--------|-------|
| Brief, wireframe, research, critique report | `@heyeddi-design` |
| `design.md` Decision log | `@heyeddi-design` |
| `.vue`, `.dart`, `.tsx` files | Stack implementer |
| Token/CSS in `tokens.css` | Stack implementer (Vue); design approves in Decision log |
| Screenshot QA fixes | `@visual-auditor` |

## `craft` sub-command (design)

`craft` means **brief is ready → hand off to implementer**. The design skill:

1. Confirms brief + Design signature (`design-ambition.md`)
2. Updates `design.md` Decision log
3. **Invokes** the stack implementer for the route (do not write Vue/Flutter in the design turn)

## Critique → fix (default, no confirmation)

When user says "looks bad", "fix this page", "improve UI":

1. `@heyeddi-design critique` → write `.heyeddi/docs/<feature>-critique.md`
2. **Immediately** stack implementer applies P0/P1 code fixes from critique
3. `@visual-auditor` full fix loop
4. `@heyeddi-design polish` only if IA/token spec still needs design-doc updates

Do **not** stop after critique and ask whether to fix.

## PR work (orthogonal)

UI fixes from PR review use `@heyeddi-pr-respond` (includes `@heyeddi-ci-fails` first). Design critique is for intentional UI work, not review threads.
