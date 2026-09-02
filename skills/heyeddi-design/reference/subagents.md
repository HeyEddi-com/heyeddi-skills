# Subagent delegation: heyeddi-design

**Default:** main chat routes sub-commands; delegate heavy or isolated phases.

| Sub-command / step | Subagent | Readonly | Worker prompt |
|--------------------|----------|----------|---------------|
| `discover` / `shape` Q&A | main |: | Short: conversational |
| `research` (web + trends) | `generalPurpose` | yes | `@heyeddi-design research` for feature X; write `research.md` only |
| `explore` (wireframes + visuals) | `generalPurpose` | no | GenerateImage probes + optional Canvas; wireframes under `.heyeddi/designs/<feature>/wireframes/` per `visual-tools.md` |
| `critique` | `generalPurpose` | yes | `@heyeddi-design critique` route; read PNGs if exist; write `.heyeddi/docs/<feature>-critique.md`; no code |
| `craft` (full route) | `generalPurpose` | no | Confirmed brief + `design.md`; one route; surface-completeness |
| `polish` | `generalPurpose` | no | After critique exists; target route only |
| `document` (scan codebase) | `explore` | yes | Extract tokens/components for `design.md` |
| `validate_vue` / npm test / build | `shell` | no | `@primevue-openprops-architect` scripts |
| Visual proof | `shell` | yes | `@visual-auditor`: **always delegate**, never inline Playwright |

## Flow examples

**Critique → polish:** orchestrator runs critique subagent → user confirms → polish subagent with critique path attached.

**Shape → craft:** orchestrator confirms brief in main chat → craft subagent with brief path.

Optional: `bugbot` on craft diff; `security-review` for login/auth routes.
