# Anti-patterns

- **Skipping always-on router**: every session start / ambiguous task needs catalog or suggest_skills first.
- **Chat-only `@heyeddi`**: never answer or route under this skill without first running `ensure_always_on_agents.py` or `sync.py` for the project root.
- **Relying on skill ALWAYS-ON text alone**: every-chat enforcement needs project `AGENTS.md` + `.cursor/rules/heyeddi-always-on.mdc`; keep them via sync / `ensure_always_on_agents`.
- **Deleting the managed always-on block**: edit outside `<!-- heyeddi-always-on:* -->`; sync replaces the marked section.
- **Skipping SKILL.md**: suggestions are pointers; always read the target skill before tools.
- **Loading every skill at once**: wastes context; use catalog + 1-3 reads.
- **Ignoring skill-routing.json**: when present, it overrides keyword guesses.
- **Implementing in orchestrator**: this skill routes only; no product/design/code output.
- **Hardcoding skill list in chat**: run `load_catalog` so descriptions stay in sync with registry.
- **Central trigger map in orchestrator**: each skill owns optional `reference/triggers.md` instead.
- **Skipping engineering excellence**: after routing, plan/change gates are mandatory (see `docs/always-on-skills.md`).
- **Live infra from the agent**: before Terraform, gcloud, Firebase, Kubernetes, or Google account changes, run `@heyeddi-local-first` `classify_command.py --check`. Exit 1 means do not run the command. `terraform plan` is allowed and must be summarized.
- **Silent skills self-update**: never run `npx skills add` / `npx skills update` without explicit user approval after `check_skills_update` reports `ask_user`.
- **Assuming host tools**: never require canvas / plan UI / image gen / browser when the session tool list lacks them; degrade per `reference/host-surfaces.md`.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully on any prose you author. NEVER waive for books/manuscripts or "UI-only" framing.
