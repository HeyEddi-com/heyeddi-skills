# Browser platform (frontend and design)

Load this whenever a **frontend or design** skill runs: `@taste-penpot`, `@heyeddi-design`, `@vue-design-system` and the skills it routes (Quasar, PrimeVue Aura, motion, morph, tokens, fancy UI), `@heyeddi-handoff`, `@design-handoff-flutter`, `@visual-verification`, `@visual-auditor`, `@ux-flow-auditor`.

Two Chrome packs sit beside those skills. They do not replace them.

| Pack | Job |
|------|-----|
| **Modern Web Guidance** | Guides for accessibility, forms, motion, performance, security, and Baseline. Includes the modernization scan that **finds problems** in existing HTML, CSS, JS/TS, Vue/framework files, and `package.json`. |
| **Chrome DevTools for agents** | Live Chrome: performance traces, memory, throttled CPU, `prefers-reduced-motion`, console. Localhost only. |

Playwright stays the screenshot and signed-in flow tool (`@visual-verification`, `@visual-auditor`, reproduce-first tests). DevTools does not replace those captures.

## Install (app repo, once)

From the app root, not this skills hub:

```bash
npx modern-web-guidance@latest install
```

Add the DevTools MCP on a **fresh Chrome profile** (no personal login):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

If either command is missing, say so and continue with Playwright. Do not block a design-only pass (Penpot, brief, tokens) on a browser install.

## Find problems (modernization)

On an **existing** frontend, before craft, polish, or a handoff fix, scan the files you will touch. Do not scan the whole monorepo unless the user asked to modernize the repo.

```bash
npx modern-web-guidance legacy-scan <path> --json
```

Or ask in natural language: modernize this folder with Modern Web Guidance, scan for legacy patterns, verify findings, and propose a plan before edits.

Then:

1. **Scan.** `legacy-scan` is the find-problems step. It is static. It covers the guide subset with deterministic rules.
2. **Verify.** Drop matches the rubric marks as intentional (`@supports`, a real virtual scroller, a library behavior you must keep).
3. **Report** verified findings before editing, unless the user already asked to apply them.
4. **Fix from the guide.** `npx modern-web-guidance retrieve <guide-id>`. Re-run `legacy-scan` on the files you changed. Run the project test for those files.

Naming one component is a guide lookup, not a repo scan.

## While building

For new UI, retrieve the matching Modern Web Guidance guide before inventing a JavaScript workaround for a platform feature (dialog motion, autofill, focus, reduced motion, sanitization, CSP, long tasks). Baseline in the guide is the support bar. The project `browserslist` wins when it is stricter.

**HeyEddi stack wins the component.** Shells stay Quasar. Dense data and forms stay PrimeVue Aura. Tokens stay `@aura-design-tokens`. Motion stays a `@motion-physics` spring. Do not replace those with a raw `<dialog>`, Popover, or extra CSS system because a guide shows the platform primitive. Apply the guide **inside** that component: autocomplete tokens, `:user-invalid`, IME-safe Enter, `prefers-reduced-motion`, focus and inert, image priority, no layout-thrashing measurement when CSS can do the job.

## Runtime (local only)

After a GUI change, use Chrome DevTools on `http://localhost` (or the project dev URL) when the question is performance, memory, or a media preference:

- Long tasks / INP: trace with a slowed CPU. Target tasks under 50ms.
- Animations: record the motion, then repeat with `prefers-reduced-motion: reduce`.
- Cached views: confirm memory does not climb without bound.

Use a clean profile. Do not attach the user's logged-in Chrome. On a test or production URL: look and navigate only. No writes, no form submits, no account changes. Same rule as `@heyeddi` `reference/reproduce-first.md`.

## Skip

CLI skills (`@cli-interface-design`) do not load this. Docs-only and token-only edits skip the scan. A design pass that does not touch app source skips `legacy-scan` and DevTools.
