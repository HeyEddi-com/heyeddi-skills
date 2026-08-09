# Skill-generated documents live here.

**Date:** 2026-08-09

## Durable vs ephemeral

| Kind | Examples | Commit? |
|------|----------|---------|
| **Durable product docs** | `product.md`, `.heyeddi/docs/product/**`, design briefs you keep | Yes, when they are real project docs |
| **Ephemeral PR scratch** | `pr-<N>-tracking.md`, `pr-<N>-replies.md`, `pr-<N>-posted.json`, `pr-<N>-comments.json`, `pr-<N>-context.json`, `pr-<N>-review.md`, `pr-<N>-ci-*` | **No** — gitignore; GitHub is SSOT |

Skills write ephemeral files so verify gates can run in the current agent turn. Agents must **not** `git add` them.

## Examples (ephemeral)

- `pr-42-tracking.md`
- `pr-42-replies.md`
- `pr-42-ci-fails.md`
