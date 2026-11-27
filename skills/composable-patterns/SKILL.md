---
name: composable-patterns
description: "Provides FastAPI JWT and Firebase client composable patterns for consistent auth and data layers. Context-first skill: use when writing or reviewing Vue composables for API access."
version: 1.0.1
product-version: 3.8.28
author: HeyEddi-com
paths:
  - "**/composables/**"
  - "**/use*.ts"
---

# Composable Patterns

## When to use

- Writing `useAuth`, `useApi`, or Firestore data composables
- Choosing between FastAPI JWT vs Firebase client patterns
- Reviewing composable error handling and token refresh

## Instructions

0. Write the failing test first per `@heyeddi` `reference/testing.md` (unit for logic, component or Playwright for UI flows). A screenshot does not replace it.
1. Read `context/fastapi-jwt.md` for REST + JWT projects.
2. Read `context/firebase-client.md` for Firebase/Firestore projects.
3. Optional: `python .agents/skills/composable-patterns/scripts/validate_composable.py --project-root . --path src/composables/useX.ts`

## Notes

- Prefer context docs over improvising interceptors or security rules.
