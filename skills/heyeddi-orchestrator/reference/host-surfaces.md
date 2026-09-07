# Host surfaces (prefer native, degrade portable)

**Date:** 2026-09-06

Skills run on many hosts: Cursor, other IDEs, agent CLIs, Cloud Run / custom agents. Do **not** hardcode one product's APIs. Prefer whatever the **current session** already exposes; otherwise use portable artifacts.

## Discovery (no probe script)

1. Trust this turn's **injected tool list** and any MCP / dynamic catalog the host provides.
2. If a surface is listed → prefer it for the matching intent below.
3. If it is missing → degrade. Do not invent a fake probe, and do not fail the task.
4. Optional: say in one line that the host lacks X and what you wrote instead.

Hosts that own the agent (CLI, Cloud Run) may inject a capabilities block at startup. Skill scripts must **not** guess IDE tools from the filesystem.

## Intent → prefer → fallback

| Intent | Prefer when present | Portable fallback |
|--------|---------------------|-------------------|
| Plan before act | Host plan / todo / task UI | Short checklist in chat + plan under `.heyeddi/docs/` when durable |
| Long-running objective | Host goal / loop (only if user asked) | Restate objective; keep working until done |
| Show structured data | Host interactive artifact (canvas, MCP app, notebook) | Markdown / JSON / HTML under `.heyeddi/` or agreed artifact dir |
| Show visual direction | Host image generation | ASCII or markdown wireframes (see `@heyeddi-design`) |
| Prove live UI | Host browser or computer-use | Playwright / skill scripts → screenshot paths |
| Extend tools | Host MCP / plugin tools | Skill `manifest.json` scripts only |

## Rules

- **Portable core stays scripts** (`manifest.json` + `scripts/`). Host surfaces are accelerators.
- **Never require** canvas, plan mode, image gen, or browser for Cloud Run / headless CLI success.
- **Cursor examples** (when those tools appear): Plan mode / `TodoWrite` for planning; `.canvas.tsx` for data-heavy demos; `GenerateImage` for design probes. Same intents apply under other names on other hosts.
- Design-specific gates: `@heyeddi-design` → `reference/visual-tools.md`.

## Anti-patterns

- Assuming Cursor (or any IDE) tools exist on CLI / Cloud Run.
- Building a skill-side "capability probe" that cannot see the host tool list.
- Dumping large tables in chat when an interactive host surface is available.
- Skipping portable wireframes / `.heyeddi` docs because a host visual tool ran.
