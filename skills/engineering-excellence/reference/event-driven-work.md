# Event-driven work

Timed and background work (retries, timeouts, expiries, queue drains, failure handling) runs when something happens, not on a loop that checks. This keeps the system correct as data grows, recovers what an event misses, and makes idle cost close to nothing.

`check_engineering_plan.py` warns when a plan polls for work (cron, Cloud Scheduler, `setInterval`, "every minute") and names no event path.

## Rules

1. **Wake up at the due time.** When code stores a row with a due time (a retry, a wait, a timeout, an expiry), it also schedules a wake-up for that time. On GCP that is a Cloud Tasks task. Name the task after the row and the due minute so a second enqueue of the same work is a no-op. Cloud Tasks retries a failed run on its own.
   - Reliability: work runs on time, not up to a polling interval late, and a retry storm cannot start from a loop.
2. **Failures arrive as events.** VM preemptions through a log sink, Pub/Sub messages, provider webhooks, callbacks from the worker. Do not rediscover failures by listing everything and comparing.
3. **Read only live rows.** Query by the field you need (`job_id == X`), filter to live states (`state in LIVE_STATES`), add a limit, and delete or expire (TTL) rows nobody reads again.
   - Reliability: a query that reads all history gets slower every day until it times out or exhausts its retries, with no code change. A query over live rows stays the same size forever.
4. **Keep one bounded backstop.** A scheduled sweep catches what an event missed: a lost webhook, a failed enqueue. It reads only live, overdue rows (rule 3), so it can run every 5 to 15 minutes for pennies. Pick the interval from how long a missed item may wait.
5. **Scale to zero.** Services and jobs keep no warm instance unless a measured latency need says otherwise.
6. **Check the bill after the change.** After a change that adds traffic, a schedule, or a collection, look at the numbers that drive cost: Firestore `document/read_count`, job executions and their duration, egress. A sudden jump is often the first sign of a runaway loop or retry storm. A billing budget alert (`budget-gate.md`) turns that into a page.

## Review questions

- What runs when nobody uses the product, and what does it cost per day?
- Does any query's cost or latency grow with history instead of with live work?
- If an event is lost, what catches it, and how long can the item wait?
- If the same work is enqueued twice, what stops it from running twice?

## Example: HeyEddi CI, November 2026

Firestore reads reached 54M to 155M a day, roughly $30 to $90 a day, with little CI traffic. Two lookups listed every destroyed runner host and every finished job, and a drain job ran every minute, re-polling GitHub across 47 repos. The fix: query live rows only, schedule a Cloud Tasks wake-up for each due row, route VM preemptions through a log sink, and keep one backstop drain. Reads fell to about 1M a day, close to $1.
