# Backlog and documents: where they live and how they are kept

**Date:** 2026-11-26

## Per-repository choices

Machine-readable choices live in `.heyeddi/stack.json`. Why a choice was made goes to `.heyeddi/docs/engineering/decisions.md` (`@engineering-excellence` `append_decision.py`). Commit `stack.json` in app repositories so every worktree and machine reads the same choices.

```json
{
  "backlog": { "provider": "local" },
  "docs": { "provider": "repo", "keep": ["README.md", ".heyeddi/product.md", ".heyeddi/docs/"] }
}
```

External provider:

```json
{ "backlog": { "provider": "mcp", "mcp": { "server": "<server name>", "project": "<project id>" } } }
```

## Operations

Every provider supports the same four. An item has `priority`, `feature`, `story`, `status` (`planned`, `done`, `blocked`) and `notes` (PR link, documents).

| Operation | `local` | `mcp` |
|-----------|---------|-------|
| `next` | Highest-priority row that is not done or blocked | List open tasks in the project, take the highest priority |
| `add` | New row | Create a task |
| `done` | Status `done` plus notes | Close the task, put the notes on it |
| `block` | Status `blocked` plus the reason | Mark it blocked, put the reason on it |

`backlog.py` cannot call MCP. With `provider: mcp` it prints `status: external` with the operation and fields, and the agent runs it with the server's tools. Server unavailable: rerun with `--local`, then copy the changes over when it returns.

## Documents

An item is not done until the documents it affects say what is now true. `done` takes `--docs <files, titles, or links>` or `--docs-none "<reason>"`.

| `docs.provider` | Where | Agent does |
|-----------------|-------|------------|
| `repo` (default) | Files named in `docs.keep` | Edit them on the item's branch. `done` checks the files exist |
| `mcp` | A docs tool: `docs.mcp.server`, `docs.mcp.space` | Update the pages with the server's tools, pass their titles or links |
| `external` | `docs.location` (a URL or a place the user named) | Update it there if there is access; otherwise say which page is stale under **Needs you** |

```json
{ "docs": { "provider": "mcp", "mcp": { "server": "<server name>", "space": "<space or folder>" } } }
```

`.heyeddi/` files that skills read (`product.md`, `design.md`, `stack.json`) stay in the repo whatever the provider is.
