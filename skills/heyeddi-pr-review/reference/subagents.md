# Subagent delegation: heyeddi-pr-review

| Step | Subagent | Readonly | Worker prompt |
|------|----------|----------|---------------|
| `fetch_pr_context` | `shell` | yes | PR number; `--fixture` in evals |
| Read the diff and related call sites | `explore` | yes | Touched symbols; return path, line, severity, issue |
| `post_inline_review` | main | no | One review with every finding on its line |
| `verify_inline_review --check` | `shell` | yes | Same findings file |

Main chat owns the findings and the review event, and keeps the scope on the committed diff. The merge gate is not part of this skill: it runs after `@heyeddi-pr-respond`.
