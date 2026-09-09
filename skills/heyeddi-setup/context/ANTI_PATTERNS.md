# Anti-patterns

- NEVER quiz frontend, backends, package manager, or CI in this skill.
- NEVER store prefs outside `.heyeddi/stack.json`.
- NEVER skip `verify_setup --check` after writing.
- NEVER omit production or staging environment mappings.
- NEVER claim setup done when `missing` is non-empty.
- NEVER treat incomplete prefs as soft advice when committing, pushing, or assuming branches — that is a hard fail.
- NEVER invent `git.*` or `agent.*` values to bypass the gate.
- NEVER ship AI prose slop; follow `context/PROSE_ANTI_SLOP.md`.
