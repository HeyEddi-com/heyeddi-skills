# Code to design

**Date:** 2026-10-23

Use this when the user asks to redesign an existing app, from scratch, or to fix the design of the whole product, some pages, or one page. This pass reads the code and proposes the new look. It does not edit Vue, CSS, or HTML until the user asks to build.

## Scope

Follow the ask.

| The user names | Scope |
|----------------|-------|
| The app, the product, everything, from scratch | Every routed page |
| A list of pages or areas | Those pages only |
| One page or one route | That page only |

If they name nothing, analyze the shell and the routes, then propose which pages change. Do not redesign every route in silence.

## Analysis

Read the scoped source before choosing a look. Write `.heyeddi/designs/<feature>/code-audit.md`.

1. **Structure.** For each page in scope, list the route, the view file, and the components it mounts. Separate the app shell (`q-layout`, drawer, header) from the page content.
2. **CSS.** Note raw hex or rgb in components, missing `--app-*` tokens, Tailwind or Bootstrap classes, and Quasar primitives used for dense data (`q-table`, `q-input`) where PrimeVue Aura should own the control.
3. **Load when needed.** A page component belongs in a route-level dynamic import. A heavy panel, chart, or 3D accent belongs in `defineAsyncComponent` when the user opens it. Flag a static import that pulls a page or a heavy widget into the first bundle. Flag a lazy import that wraps a tiny control used on first paint. Propose the import change for each flag.
4. **Fixes.** One proposed fix per issue. The fix names the file and the change. Do not apply it in this pass.

## Redesign proposal

After the audit, `@taste-penpot` replaces the look for the scoped pages. Product behavior, routes, and real copy stay. The current palette, type, and layout are a hard reject for that scope. "Existing system first" does not apply to the visual system on a from-scratch or redesign request.

Record the proposal in `.heyeddi/designs/<feature>/redesign.md`:

- Five-line brief and token table for the new look
- Which pages change, and what stays
- Quasar shell versus PrimeVue content versus `@layout-morph` or `@fancy-ui-craft` only where the page needs them
- Penpot project and file for this app, and the boards to create (375, 768, 1440 for responsive pages)

Then draw the boards with the Penpot MCP in `references/penpot-mcp.md`. Several projects can be open. Use the project for this app. Do not delete a project, file, or team.

`@heyeddi-design` copies the tokens and the page list into `.heyeddi/design.md`. It does not invent a second palette.

Stop. Building is a later request. When the user asks to build, `@vue-design-system` implements only the scoped pages, then `@visual-verification` screenshots them.
