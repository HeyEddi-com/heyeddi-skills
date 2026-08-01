# Skill scripts

CLI contract for Cursor and Cloud Run (Pydantic AI / LangChain):

- Accept `--project-root` (or `PROJECT_ROOT` env).
- Print human-readable or JSON to **stdout**.
- Errors go to **stderr**; non-zero exit on failure.
- **Idempotent**: safe to re-run.
- Prefer **Python** (`.py`) for Cloud Run parity; shell for npm-only steps.

Invocation from cloud agent: see `../../docs/cloud-agent-integration.md`.
