# Anti-patterns

- **Skipping always-on router**: every session start / ambiguous task needs catalog or suggest_skills first.
- **Skipping SKILL.md**: suggestions are pointers; always read the target skill before tools.
- **Loading every skill at once**: wastes context; use catalog + 1-3 reads.
- **Ignoring skill-routing.json**: when present, it overrides keyword guesses.
- **Implementing in orchestrator**: this skill routes only; no product/design/code output.
- **Hardcoding skill list in chat**: run `load_catalog` so descriptions stay in sync with registry.
- **Central trigger map in orchestrator**: each skill owns optional `reference/triggers.md` instead.
- **Skipping engineering excellence**: after routing, plan/change gates are mandatory (see `docs/always-on-skills.md`).
- **Silent skills self-update**: never run `npx skills add` / `npx skills update` without explicit user approval after `check_skills_update` reports `ask_user`.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
