# Context recall

**Date:** 2026-11-27

A project's memory is the markdown in its own `.heyeddi/`, committed and reviewed like code. There is no database, background service, or automatic capture.

## Read: index first, entry on demand

```bash
python3 .agents/skills/heyeddi/scripts/context_index.py --project-root .
python3 .agents/skills/heyeddi/scripts/context_index.py --project-root . --query auth
python3 .agents/skills/heyeddi/scripts/context_index.py --project-root . --type gotcha
```

One line per entry: date, type, approximate tokens, `path:line`, title. Open only the entries that apply to the task. `--query` searches titles and bodies.

Sources: `.heyeddi/docs/engineering/decisions.md` and the **Decision log** in `.heyeddi/design.md`. Only `###` headings that start with a date count.

## At session start

`worktree_guard.py --install` also registers a Claude Code `SessionStart` hook that adds the newest 30 lines of the index to the session. It is silent in a project with no entries, reads nothing above the git root, and marks the titles as untrusted data. Hosts without hooks follow the **Recall** rule in the always-on block.

## Write

```bash
python3 .agents/skills/engineering-excellence/scripts/append_decision.py --project-root . \
  --type gotcha --title "..." --context "..." --decision "..."
```

| Type | Record it when |
|------|----------------|
| `decision` | You picked an approach someone could reasonably question |
| `trade-off` | You gave something up on purpose |
| `gotcha` | Something surprised you and cost time |
| `how-it-works` | You had to trace how a part works, and the code does not say it |

`--decision` carries the body for every type. Keep an entry to a few lines and commit it with the change it came from.

## Secrets

These files are committed and fed back to agents. `append_decision.py` refuses an entry that holds a credential, and `@pre-merge-gate` fails on one in either source (`context_index.py --check`). The patterns cover common key formats and passwords in URLs. They are not a full secret scanner.
