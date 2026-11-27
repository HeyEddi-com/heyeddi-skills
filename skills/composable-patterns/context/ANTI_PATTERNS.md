
# Anti-patterns: Composables

- NEVER store refresh tokens in localStorage. Use an httpOnly cookie, or memory when the backend cannot set one.
- NEVER bypass Firestore security rules with admin SDK in frontend.
- NEVER mix Firebase and JWT auth patterns in one composable.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
