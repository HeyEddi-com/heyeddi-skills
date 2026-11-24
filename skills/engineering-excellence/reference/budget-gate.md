# Budget gate

Every change that touches infra, model calls, schedules, CI, or polling gets a monthly cost estimate before it merges. The point is a cheap default and a visible price for anything that is not cheap. The estimate never stops the work: the change lives on a branch, and the merge is where the user decides.

## Run it

```bash
python .agents/skills/engineering-excellence/scripts/estimate_change_cost.py --project-root .
```

During work, run it without `--check`. `@pre-merge-gate` adds `--check`, which exits 1 over budget.

It diffs the working tree against the merge base with `origin/main` (or `main`), plus untracked files. `--base <ref>` picks another base. `--diff-file` reads a saved diff.

Output: JSON on stdout and `.heyeddi/docs/cost-estimate-<date>.md`.

## What it prices

| Driver | Detected from | Priced as |
|--------|---------------|-----------|
| terraform | `resource "<type>"` added or removed in `*.tf` | rate row per type; removal is a saving |
| always-on | `min_instance_count`, `min_instances`, `minInstances`, `minScale`, `--min-instances`; CPU always allocated | warm instance × count |
| llm | model ids added or removed (`claude-*`, `gpt-*`, `gemini-*`) | calls × tokens × $/MTok; a swap shows the delta |
| schedule | cron strings | runs per month; CI cron × minutes × runner rate |
| ci | `runs-on` macOS or larger runners in `.github/workflows/` | runs × minutes × runner rate |
| polling | `setInterval`, `refetchInterval`, `pollInterval` under 30 s | open clients × requests × request fee |
| firestore | `onSnapshot`, `getDocs`, `getDoc`, `.stream()`, `.snapshots()`, `useCollection`, `collectionGroup` | reads per day (see below), then $ per 100k reads |

Docs, tests, and fixtures are skipped. Anything with no rate shows up as "unknown" and counts in `unknown_count`. Do not hide it: say what it depends on.

## Firestore reads

Firestore bills per document read, so the cost sits in the code, not in Terraform. One unbounded listener or a query in a loop can run to tens of millions of reads a day. The detector estimates reads per day for each read site:

| Pattern | Reads per day |
|---------|---------------|
| listener, no `limit()` | sessions × docs in the collection + open clients × doc changes |
| listener with `limit(n)` | sessions × n + open clients × doc changes |
| listener on one `doc()` | sessions + open clients × doc changes |
| `getDocs` / `.stream()` with no `limit()` | sessions × docs in the collection |
| any read on a timer | open clients × runs per day × docs per run |
| any read inside `for` / `map` / `forEach` | the above × loop iterations (N+1) |

It also warns on a Firestore trigger that writes back to Firestore, since a write can retrigger it.

The estimate is over budget when it passes `firestore_reads_per_day_limit` (default 1,000,000), whatever the dollar figure says. The first 50,000 reads a day are free per project, so a few hundred thousand is a small bill and tens of millions is not. Set the assumptions in `budget.json` to what the app really has, especially `firestore_docs_per_query`.

Fixes, in the order to try them: add `limit()` and paginate; listen to one small summary document; unsubscribe when the view closes; replace the loop with a single `where in` query or `getAll`; cache or aggregate server-side with `count()`.

## Runtime guardrail

An estimate from code cannot see everything: a loop you did not touch, a bot hitting an open endpoint, a listener left open in a background tab. Cloud Billing budgets give the second line of defence. When a change adds Firestore, model-call, or polling cost and the repo has no `google_billing_budget` in Terraform, the gate warns. Write the budget locally with alert thresholds (for example 50, 90, and 100 percent) and let the pipeline apply it. A budget alert notifies; it does not stop spend. To stop it automatically, connect the budget's Pub/Sub topic to a function that disables billing or the service, and decide that trade-off with the user first. Once the alert exists, or the user decides against one, set `billing_alert_acknowledged` to true in `budget.json`.

## Budget file

`.heyeddi/docs/engineering/budget.json` (created by `init_engineering_docs.py`):

| Key | Meaning |
|-----|---------|
| `change_warn_monthly` | Warn above this added $/month |
| `change_error_monthly` | Fail `--check` above this added $/month |
| `monthly_limit` + `current_monthly` | Fail when current spend plus this change passes the limit |
| `firestore_reads_per_day_limit` | Fail when the estimated Firestore reads per day pass this (default 1,000,000; `null` turns it off) |
| `billing_alert_acknowledged` | Silences the "no billing budget alert" warning |
| `assumptions` | LLM calls and tokens, CI runs and minutes, open clients. Set real numbers when you know them. |
| `rates` | Overrides for any row in `reference/cost-rates.json` (for example a negotiated price or a new model) |

The gate uses the **high** end of the range. A rough estimate that errs high is the safer mistake.

## Validate instead of guess

The script never calls a cloud or pricing API. To replace the Terraform guess with real numbers:

- `terraform plan -out plan.out && terraform show -json plan.out > plan.json`, then `--terraform-plan-json plan.json`. `terraform plan` is allowed by `@heyeddi-local-first`.
- `infracost diff --path . --format json > infracost.json`, then `--infracost-json infracost.json`. Infracost sends resource metadata to its pricing API, so the user runs it, or approves running it.

Infracost wins over the plan, and the plan wins over the diff guess.

## Over budget

1. Keep working. Apply a smart default below when it fits the request without changing what the user asked for, and rerun the estimate.
2. Still over: finish the change on the branch. Make `summary_warning` the first line of the final summary: the range, the top drivers, and the cheaper option for each. Do not raise a limit in `budget.json` to make it pass.
3. At merge, `@pre-merge-gate` fails the cost row. If the user accepts the cost, rerun with `--approved "<their reason>"`. That writes a "Cost approved over budget" ADR to `decisions.md` and passes.

If the user asked to hear about cost before building, warn first and build after their answer.

## Smart defaults

Pick these unless the plan says why not:

- Scale to zero. Min instances 0; keep one warm only on the service users wait on.
- Serverless before clusters. Cloud Run before GKE; a managed DB at the smallest tier before AlloyDB or Spanner.
- No NAT for Google APIs. Private Google Access is free.
- Model calls: prompt caching on the stable prefix, Batch API for work that can wait, lower effort. Measure a smaller model on real requests before you switch; do not swap models silently.
- Schedules and polling: as slow as the user can tolerate; event triggers or SSE over timers. For retries, timeouts, and background jobs follow `event-driven-work.md`: a wake-up at each due time, live rows only, one bounded backstop.
- CI: `ubuntu-latest` unless the job needs more.
- Non-prod: stop or shrink it outside working hours.

## Plan gate

`check_engineering_plan.py` warns when a plan names a cost driver (min instances, GKE, Cloud SQL, Redis, NAT, cron, polling, Firestore listeners, LLM, GPU, larger runners) and gives no cost line. Add the $/month and the cheaper option you rejected.
