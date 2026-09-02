# Next skill handoff (task complete)

When a **pipeline skill** finishes the user's requested work, suggest what `@skill` to run next and the **exact prompt** to paste in chat (`shape`, `craft`, `audit`, `sync`, `review`, etc.). Do **not** add this after every tool call or subagent phase.

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
   python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py \
     --current-skill <skill-you-finished> \
     --project-root .
   ```

   Optional:
   - `--route /settings`: route you finished
   - `--mode shape`: sub-command you just ran (improves suggestion, e.g. shape → craft)

3. Include the JSON **`user_block`** in your **final** reply. The user should be able to **copy the Prompt line** into chat.

## Response format

```markdown
### Next step
**Skill:** `@heyeddi-design`
**Prompt:** @heyeddi-design craft /settings from the confirmed brief
**Why:** Brief is confirmed: build the Vue screen before handoff or visual QA.
```

The **Prompt** is the main deliverable: natural language with `@skill` and sub-command, not a `python scripts/...` path unless the user explicitly asked for CLI-only work.

## Examples by pipeline

| Finished | Typical next prompt |
|----------|---------------------|
| `@heyeddi-intake` | `@heyeddi-product audit the product and write feature specs for each routed surface` |
| `@heyeddi-product` | `@heyeddi-design shape /dashboard from product.md personas` |
| `@heyeddi-design shape` | `@heyeddi-handoff implement <route>` (or `@design-handoff-flutter` when `stack.json` → flutter) |
| `@heyeddi-design craft` | Same as shape — stack implementer from brief |
| `@heyeddi-design critique` | `@visual-auditor review and fix <route>` |
| `@heyeddi-handoff` | `@visual-auditor review and fix /settings against product.md and design.md` |
| `@visual-auditor` | `@pre-merge-gate run the merge readiness checklist` |
| `@heyeddi-orchestrator sync` | `@heyeddi-intake: describe the app in plain language` |

## Priority order

1. **`--mode`** sub-command chain (e.g. design `shape` → `craft`)
2. **`.heyeddi/docs/intake/skill-routing.json`**: next route
3. **Default pipeline** in `_next_skill.py`
4. **Fallback**: `@heyeddi-orchestrator`

## Pipeline skills

`heyeddi-intake`, `heyeddi-product`, `heyeddi-orchestrator`, `heyeddi-design`, `heyeddi-handoff`, `design-handoff-flutter`, `project-engineering`, `flutter-engineering`, `visual-auditor`, `pre-merge-gate`, `heyeddi-pr-review`, `heyeddi-pr-respond`

Utility skills (`verify-build`, `backend-type-bridger`, …) are mid-pipeline: no handoff unless that was the whole user request.
