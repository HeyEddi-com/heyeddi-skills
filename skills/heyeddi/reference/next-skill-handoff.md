# Next skill handoff (task complete)

**Inside the request, chain; don't hand back.** When the next pipeline skill is part of what the user asked for ("implement /settings" covers handoff, engineering audit, visual QA, and the PR), run it yourself in the same run (`reference/autonomy.md`). `suggest_next_skill.py` tells you which skill that is.

**Backlog loop.** In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`. Build the returned item on its own branch, pass `@pre-merge-gate --signoff`, merge into dev / test / staging, mark it with `backlog.py done`, and ask again. The run ends when `next` returns no item. Only a production merge needs the user. See `@heyeddi-product` **Backlog loop**.

Only when the request is done and the next step is **new work** the user did not ask for, suggest it with the **exact prompt** to paste in chat (`shape`, `craft`, `audit`, `sync`, `review`, etc.). Do **not** add this after every tool call or subagent phase.

## When to use

| Do | Don't |
|----|-------|
| `@heyeddi-design shape` finished: brief confirmed | After `load_context.py` |
| `@heyeddi-handoff`: route built and verified | After pass 1 interpret only |
| `@heyeddi-intake`: product.md + routing ready | After `write_product` alone |

## Agent workflow

1. Complete the skill's work for the user's task.
2. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py \
     --current-skill <skill-you-finished> \
     --project-root .
   ```

   Optional:
   - `--route /settings`: route you finished
   - `--mode shape`: sub-command you just ran (improves suggestion, e.g. shape → craft)

3. Next skill still inside the request or the backlog: run it now. New work nobody asked for: one line under **Next** in the final summary. Never list leftovers there.

## Response format

Only for new work, one line:

```markdown
**Next:** `@heyeddi-design critique /pricing` (new work, not part of this request)
```

## Examples by pipeline

| Finished | Typical next prompt |
|----------|---------------------|
| `@heyeddi-setup` | `@heyeddi-intake: describe the app in plain language` |
| `@heyeddi-intake` | `@heyeddi-product audit the product, write feature specs, and fill the backlog` |
| `@heyeddi-product` | Backlog loop: `backlog.py next`, then build that item |
| `@heyeddi-design shape` | `@heyeddi-handoff implement <route>` (or `@design-handoff-flutter` when `stack.json` → flutter) |
| `@heyeddi-design craft` | Same as shape — stack implementer from brief |
| `@heyeddi-design critique` | `@visual-auditor review and fix <route>` |
| `@heyeddi-handoff` | `@engineering-excellence audit_engineering --check after implementing <route>` |
| `@design-handoff-flutter` | `@engineering-excellence audit_engineering --check after Flutter handoff` |
| `@engineering-excellence` | `@visual-auditor review and fix <route>` |
| `@visual-auditor` | `@pre-merge-gate run the merge readiness checklist` |
| `@pre-merge-gate` | Merge below production, then `backlog.py next` |
| `@heyeddi sync` | `@heyeddi-setup: confirm stack + prefs in stack.json` |

## Priority order

1. **`--mode`** sub-command chain (e.g. design `shape` → `craft`)
2. **`.heyeddi/docs/intake/skill-routing.json`**: next route
3. **Default pipeline** in `_next_skill.py`
4. **Fallback**: `@heyeddi`

## Pipeline skills

`heyeddi-setup`, `heyeddi-intake`, `heyeddi-product`, `heyeddi`, `heyeddi-design`, `heyeddi-handoff`, `design-handoff-flutter`, `project-engineering`, `flutter-engineering`, `engineering-excellence`, `visual-auditor`, `pre-merge-gate`, `heyeddi-pr-review`, `heyeddi-pr-respond`

Utility skills (`verify-build`, `backend-type-bridger`, …) are mid-pipeline: no handoff unless that was the whole user request.
