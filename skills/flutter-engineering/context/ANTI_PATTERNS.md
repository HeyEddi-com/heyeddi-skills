# Anti-patterns: Flutter engineering

- Do not mix Vue (`package.json` + `pubspec.yaml`) as co-primary frontends: pick one `frontend` in `stack.json`.
- Do not hardcode API port **8000**: use `8090` / `lib/config/env.dart`.
- Do not put business logic in `build()`: use providers/repositories.
- Do not skip `Card` padding on settings screens: match design brief spacing (16dp+).
- Do not leave dev servers running: start them in the background and stop them when the work is done.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
