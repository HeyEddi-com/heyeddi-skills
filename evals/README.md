# Agent-based skill evals

Unlike `scripts/test-skills.py` (CLI smoke tests), **agent evals** run a real agent against a **fresh project copy** with skills installed, then an **agentic judge** reviews all changes and command output (default). Legacy `--deterministic` mode uses file/regex assertions.

## Quick start (local PC)

```bash
./scripts/setup-evals.sh
uv run poe test
uv run poe eval-list
uv run poe eval-heyeddi-handoff   # example: one skill, one command
```

### Poe commands

One command per eval — no generic `eval-case`, no composite bundles.

| Command | Skill(s) under test |
|---------|---------------------|
| `uv run poe eval-integration` | Full pipeline (7 turns, all skills) |
| `uv run poe eval-translator` | heyeddi-intake |
| `uv run poe eval-orchestrator` | heyeddi |
| `uv run poe eval-scaffold` | project-engineering |
| `uv run poe eval-api` | backend-type-bridger, composable-patterns |
| `uv run poe eval-primevue` | primevue-openprops-architect |
| `uv run poe eval-pr` | heyeddi-pr-respond |
| `uv run poe eval-pr-submission` | heyeddi-pr-review |
| `uv run poe eval-engineering` | engineering-excellence |
| `uv run poe eval-ux-flow` | ux-flow-auditor |
| `uv run poe eval-flutter` | flutter-engineering |
| `uv run poe eval-flutter-api` | dart-type-bridger, flutter-patterns |
| `uv run poe eval-flutter-handoff` | design-handoff-flutter |
| `uv run poe eval-heyeddi-handoff` | heyeddi-handoff |
| `uv run poe eval-heyeddi-design-scratch` | heyeddi-design (greenfield) |
| `uv run poe eval-heyeddi-design-polish` | heyeddi-design (polish existing) |

| Utility | What |
|---------|------|
| `uv run poe eval-list` | List case ids |
| `uv run poe eval-dry-run` | Plan all cases (no agent) |
| `uv run poe eval-all` | Run every case (slow) |
| `uv run poe setup` | Install eval deps + Playwright |
| `uv run poe verify-agent` | Check `agent login` |
| `uv run poe mockups` | Regenerate handoff PNGs |
| `uv run poe eval-clean` | Remove old runs (keeps 1 recent) |

```bash
./scripts/setup-evals.sh
uv run poe eval-heyeddi-handoff
uv run poe eval-integration
```

The agent step can take **5–15+ minutes**. You should see streaming progress (`▶ started`, `⚙ shell: …`, `✓ …`, heartbeat every 30s).

Design evals use `agent_timeout: 1200` in case YAML (20 min). Worker prompts tell the agent **not** to run Playwright/`@visual-auditor` — the harness does visual QA after the turn.

### Inspect what the agent built

By default sandboxes live in `/tmp` and are deleted when the run finishes. To keep them:

```bash
uv run poe eval-heyeddi-handoff   # add --keep-sandbox via run-evals.py directly:
python3 scripts/run-evals.py --keep-sandbox heyeddi-handoff-only
```

Sandboxes kept under `evals/runs/<timestamp>/<case-id>/`:

```bash
cursor evals/runs/<latest>/heyeddi-handoff-only
cd evals/runs/<latest>/heyeddi-handoff-only && npm ci && npm run dev
```

## Current eval cases (15)

| Poe command | Case ID |
|-------------|---------|
| `eval-integration` | `full-product-integration` |
| `eval-translator` | `heyeddi-intake-intake` |
| `eval-orchestrator` | `heyeddi-suggest` |
| `eval-scaffold` | `project-engineering-scaffold-vue` |
| `eval-api` | `backend-type-bridger-users` |
| `eval-primevue` | `primevue-fix-violations` |
| `eval-pr` | `heyeddi-pr-respond-workflow` |
| `eval-pr-submission` | `heyeddi-pr-review-workflow` |
| `eval-engineering` | `engineering-excellence-audit` |
| `eval-ux-flow` | `ux-flow-auditor-init` |
| `eval-flutter` | `flutter-engineering-scaffold` |
| `eval-flutter-api` | `flutter-backend-bridger-users` |
| `eval-flutter-handoff` | `design-handoff-flutter-settings` |
| `eval-heyeddi-handoff` | `heyeddi-handoff-only` |
| `eval-heyeddi-design-scratch` | `heyeddi-design-from-scratch` |
| `eval-heyeddi-design-polish` | `heyeddi-design-polish-existing` |

All **20** registry skills are covered: 15 dedicated cases + skills chained in `eval-integration`.

## Smoke vs agent tests

| | `test-skills.py` | `run-evals.py` |
|--|------------------|----------------|
| Speed | ~30s all skills | 5–30+ min per case |
| What it checks | Structure + script smoke | Real agent + judge |
| When to run | Every PR / before push | Before release, after skill changes |

See also: [docs/agent-evals.md](../docs/agent-evals.md), [docs/eval-philosophy.md](../docs/eval-philosophy.md).
