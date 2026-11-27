# Agent freedom and its limits

**Date:** 2026-11-26 · **Released in:** hub v3.8.27, CI pack v1.4.10

What an agent does on its own, what waits for you, and what enforces it. The rules agents read are `skills/heyeddi/templates/always-on/AGENTS.section.md` and `skills/heyeddi/reference/autonomy.md`; this page records why they changed.

## What went wrong

| Seen | Cause | Fix |
|------|-------|-----|
| Asked before commit and push | Old `agent.commit` / `agent.push: ask` keys overrode `balanced`, and the project scaffold still wrote them | Keys are ignored; scaffold writes `agent.preset` |
| "I haven't checked" | No rule said an allowed check is the agent's job | Run it and report the result |
| Left merges for the user | `merge` was `ask` for every branch | Below production: pass the gate, then merge |
| Called around a missing tool | No rule | Add the dependency, install it, run the project's script |
| Read and entered sibling folders | "Read-only" still allowed looking | Stay in the starting repo unless the user names another |
| Several sessions wrote in one worktree | `claim` let any session join, and contributors could commit and push | Only the owner writes; `claim` refuses others |
| Waited for a "go" mid-plan | Written rule only | Rule plus a Stop hook |
| Doable work stayed in the backlog | No rule | Do it, one branch and PR each |

When someone brings an agent's behavior to this repo, the fix belongs here: rules, scripts, hooks, tests. Do not go and do that agent's task.

## Merging

| Target | `balanced` |
|--------|------------|
| dev, test, staging, a stacked parent branch | `@pre-merge-gate --signoff` exits 0, then merge. No question |
| Production branch | Waits for you (**authorize merge**), under every preset |
| Unknown target, `--admin`, `gh api` merge, merge after `cd` | Treated as production |

The production branch is `git.environments.production` in `.heyeddi/stack.json`; without it, `main` and `master`. In a repo where `main` is production and pull requests target `main`, every merge still waits for you. A worktree without its own `stack.json` reads the main checkout's.

`check_permission.py` does not run the gate itself. It states the requirement, and the agent runs the gate.

To make an agent ask before commits, use `agent.preset: cautious` or `agent.permissions`.

## Hooks

Written rules can be ignored. Claude Code hooks enforce the ones that matter most and read project context back. Install once per machine from a checkout of this repo, then restart open sessions:

```bash
python3 skills/heyeddi/scripts/worktree_guard.py --install
```

This copies four scripts into `~/.claude/hooks/` and registers them in `~/.claude/settings.json`. Run it again after an update. The `SessionStart` hook arrived in hub v3.8.28.

| Hook | Event | Does |
|------|-------|------|
| `worktree_guard.py` | `PreToolUse` | Denies file edits and shell writes in a worktree another session owns, and edits to the marker. Asks you before any `--user-approved` call |
| `finish_guard.py` | `Stop` | Blocks, once, a turn that ends waiting for a "go". A second stop goes through, so real questions reach you |
| `context_index.py` | `SessionStart` | Adds the index of the project's decisions and gotchas ([context recall](../skills/heyeddi/reference/context-recall.md)). Reads only |

Limits:

- A path that a script builds while it runs is invisible to `worktree_guard.py`.
- A checkout with no session marker is not protected.
- The hooks are Claude Code only. Cursor and other hosts get the written rules.
- `finish_guard.py` matches English phrases, so a new wording can get past it.

To remove them, delete their three entries from `~/.claude/settings.json`.

## Handing a worktree over

A worktree whose owner session has ended stays read-only. Approve the handoff when the agent asks:

```bash
python3 .agents/skills/heyeddi/scripts/session_worktree.py handoff --path <worktree> --to <session> --user-approved
```
