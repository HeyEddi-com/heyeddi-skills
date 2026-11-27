# Sessions and worktrees

**Date:** 2026-11-25

Several agent sessions often run at once on one machine, each in its own git worktree. Folder and branch names say what the work is, not who is doing it. After a long session is summarized, an agent can no longer tell its worktrees from another session's, and it starts committing, merging, or deleting work that isn't its own. The session marker fixes that.

## The rule

Act only on worktrees, branches, and PRs your session owns. Everything else is read-only: you may look and report, never commit, push, merge, rebase, or delete. This holds even when the other work looks finished or abandoned.

## The marker

`scripts/session_worktree.py` keeps one JSON file per worktree, inside that worktree's git directory (`.git/worktrees/<name>/heyeddi-session.json`; `.git/heyeddi-session.json` in a plain checkout). Git never tracks its own directory, so the marker can't be committed and needs no `.gitignore` entry.

The marker records the owner session, the task, the PR, the branch, every session that worked there, and a history of ownership changes. The session id comes from `--session`, `HEYEDDI_SESSION_ID`, or `CLAUDE_CODE_SESSION_ID`.

## Roles

| Role | Who | May |
|------|-----|-----|
| Owner | The session that created or first claimed the worktree | Everything: commit, push, rebase, force-push, merge, delete |
| Contributor | A session the user let in (`claim --user-approved`) | Read only. Writing takes a `handoff` |
| Not listed | Any other session | Read only |

Ownership moves only with `handoff`: by the owner, or with `--user-approved` after the user says so. When the owner session has ended, the worktree stays read-only until the user hands it over; list it under **Needs you** in the final summary.

## When to run it

```bash
S=.agents/skills/heyeddi/scripts/session_worktree.py   # or ~/.claude/skills/heyeddi/scripts/...
python3 $S claim --path <worktree> --task "fix login redirect"   # right after git worktree add
python3 $S claim --path <worktree> --pr <url>                    # after opening the PR
python3 $S check --path <worktree> --action merge                # before commit/push/merge/rebase/delete
python3 $S list --path <any checkout of the repo>                 # which worktrees are mine
python3 $S handoff --path <worktree> --to <session> --user-approved
```

`check` exits 0 when allowed, 1 when blocked, and 2 when the worktree has no marker. On 2, treat it as read-only, keep working, and list it under **Needs you** in the final summary so the user can say whose it is.

`claim` on another session's worktree is refused. To write there, the user has to approve a `handoff`. Otherwise make your own worktree on your own branch.

## The guard

`scripts/worktree_guard.py` is a Claude Code `PreToolUse` hook. It denies file edits and shell writes in a worktree another session owns, and asks the user before any `--user-approved` call. Install it once per machine:

```bash
python3 .agents/skills/heyeddi/scripts/worktree_guard.py --install
```

It cannot see a path that a script builds at run time.

## Stay in your repo

Work only in the repo you were started in and in worktrees your session owns. Don't list, read, search, fetch, or run anything in sibling folders unless the user names them. You may reason about where something came from using what the user pasted and what this repo holds; if that isn't enough, ask.
