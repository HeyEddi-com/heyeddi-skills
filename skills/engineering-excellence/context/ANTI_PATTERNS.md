
# Anti-patterns: Engineering excellence

- NEVER skip plan or change gates on chats that plan or edit code (always-on)
- NEVER write architecture notes at repo root: use `.heyeddi/docs/engineering/`
- NEVER mix engineering ADRs into `.heyeddi/design.md` Decision log
- NEVER add abstraction before second use case (YAGNI)
- NEVER skip `reuse-catalog.md` update when introducing shared module
- NEVER fatten router files with business rules (SOLID)
- NEVER treat **error**-severity audit findings as optional
- NEVER block merge solely on **warn**/info without user `--strict` ask
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
