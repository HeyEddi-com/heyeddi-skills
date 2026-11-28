# Batch 06 notes

### File-Integrity-and-Alerting-Tripwire-AIDE-Wazuh
Explains file integrity monitoring (baseline, then compare) with Tripwire, AIDE, Wazuh, auditd, osquery and fail2ban, plus a toy monitor you build and then defeat by forging its baseline. The core point is that a monitor living on the machine it watches can be lied to.
- Attack your own control before trusting it: list how it can be tampered with, bypassed, flooded, starved or forged, and name one countermeasure for each.
- Keep the source of truth where the thing being checked cannot rewrite it (separate host, signature with a key held elsewhere), and make accepting a new baseline a deliberate, reviewed, manual step.
- A check that stops running looks like "all clear", so alert on absence (heartbeat) as well as on findings.
- Every ignore list is a blind spot with a cost; keep it short, owned and dated, and ask who can write into the skipped places.
- Before switching an alert on, write its owner, first action, expected rate, tuning path and heartbeat.

### Rate-Limiting-at-Every-Layer
Walks through rate limiting algorithms, what to count by, and what each layer from ISP to database can and cannot see, with runnable labs showing spoofed headers, silent non-enforcement and false positives. It treats the limiter as something that fails, can be abused and needs logs.
- Name the problem being solved (volume, guessing, scraping, cost, weak backend) before picking a number, and choose the key the layer can actually trust; client-written values are claims, not facts.
- Place controls where the needed information exists: loose outer layers, stricter inner ones, and the weakest resource never the first to feel a surge.
- Decide fail open or fail closed on purpose per path, then test it by breaking the dependency.
- Roll out in dry-run mode, measure false positives against real users, then enforce; log every refusal and keep "slow down" distinct from "I am broken".
- Verify the control really runs (something earlier may answer first, an empty key may skip it, several instances may each count alone), and design the client side too (backoff, jitter, retry cap at one layer).

### Plan-for-Failure-Blast-Radius-and-Assuming-Breach
Argues for planning the day prevention fails: contain, detect, recover, using a blast radius graph and an honest table of which project controls are built versus only designed. Includes costs and limits of isolation.
- Ask of every system or credential: what can it reach if compromised, how would I know, how do I recover; an unanswered question is itself a finding.
- Draw reach as a graph that includes credentials; a boundary for changes (separate state) is not a boundary for a shared token.
- State the cost of each isolation cut next to its benefit, and share on purpose with the shared piece named and watched hardest.
- Include mistakes and outages in the threat picture, not only attackers.
- Obscurity (hidden ports, banners) does not reduce reach; do not count it as a layer.

### Attack-Surface-List-Shrink-Measure
Shows how to inventory attack surface in six categories, remove items rather than hide them, measure from outside, and decide what to log and alert on. It is careful to state exact versions of claims such as "zero inbound".
- Inventory first (ports, addresses, accounts, tokens, dependencies, people, plus internal answerers like metadata services); unlisted things are unguarded.
- Compare declared state with observed state; when they disagree, believe the observation and find out why.
- Build dangerous tools so they cannot be misused: the scanner accepts no target argument and discovers only owned hosts.
- Treat "cannot tell" as a failure, never a pass, and write down what a clean result does not prove.
- Say the precise claim ("zero inbound from the internet, one tagged rule") instead of the flattering shorthand.

### Attack-Surface-Map-Layer-by-Layer
Maps the system layer by layer, listing for each target the control, the test that guards it (or "None"), and what to log. The gaps cluster in vendor settings, unapplied controls and missing alerting.
- Pair every control with the check that would fail if it were removed, and write "None" openly where there is none.
- Settings held by a vendor cannot be tested from the repository; keep an explicit unverified list and a scheduled human check.
- Distinguish applied, built but off, and written but not applied; "tested against fakes" is the honest wording until it runs for real.
- A guard is only trustworthy if it has a hostile case that makes it fail.
- A passing test proves what is declared, not what the running system or vendor does.

### The-DMZ-and-Hardening-a-Host-That-Faces-the-Internet
Uses a designed (not built) public edge to teach isolate, harden and watch, including removing SSH entirely, egress control, off-host logs and sorting events into alert, log and noise. Every row is labeled with its status and test.
- Assume the exposed component will be compromised and decide in advance what that buys the attacker (no path inward, rebuild as recovery).
- Control egress deliberately and say where the boundary stops working (for example, it does not hold against root).
- Removing an access path has a price; record the open unknowns and make them gates before applying.
- Alert on things that should never happen by design (a login on a host with no logins); count internet noise, never page on it.
- Separate quoted design from your own inference, and leave untested proposed thresholds labeled as such.

### DMZ-Hardening-Checklist
A one-page checklist form of the DMZ lesson with status and covering test per item. It reminds the reader that a passing check proves declaration only.
- Turn guidance into a checklist where each item has a status and a verifying check or an explicit "None".
- Keep the checklist derived from one source lesson and say so, so it does not become a second authority.
- Include for each alert who gets it, what it means and the next action; admit when no delivery path exists.

### Deception-and-Honeypots-Start-Here
Hub page for the deception track: lesson order, what was actually run, and which parts need your own account or hardware. Safety comes before anything exposed.
- Order work so the safety and permission step is a prerequisite of the risky step, not an appendix.
- Publish exactly what was run, what was only read and what was left unwritten because it could not be verified.
- Show cost and prerequisites before anyone starts.

### Deception-and-Honeypots-What-Deception-Is
Defines decoys, honeytokens and honeypots and explains why a touch on an unused thing is a strong signal, with the conditions that make that true. Includes how to read vendor claims.
- Find the hidden condition inside words like "almost", "virtually" or "any" and write it next to the claim, with a way to test it.
- A signal is only clean if automated actors (backup, scanner, indexer) and people who know about it are accounted for.
- Test a detector on purpose, because silence can mean healthy or broken.
- Every added defense is also something to maintain and a possible new risk or confusion; list that cost.
- Argue from the opposing side to find how your control would be noticed or avoided.

### Deception-and-Honeypots-Safety-and-Law
Eight minimum safety rules for anything attracting attackers, a decision tree and a one-page plan a reviewer can refuse. Says clearly it is not legal advice.
- Separate low-risk from high-risk variants of an activity so nobody drifts from one to the other unnoticed.
- Write the end date and kill switch before starting an experiment.
- Prepare a one-page plan a reviewer can say yes or no to; unanswered items mean "not yet".
- Read the contract or policy and quote the clause, or record "not read yet".
- Collect the minimum, decide retention up front, publish aggregates rather than raw data about third parties.

### Deception-and-Honeypots-Plant-a-Canary
Builds a local tripwire (bait file, link, fake login) and shows what a trip can and cannot tell you, then a hosted option behind a terms review. Includes hostile client input staying inert.
- Handle input from strangers defensively: bound body size and time, reject malformed lengths, serialize with a real encoder.
- Do not log secrets that are attempted; log only what is needed to act.
- Before sending data to a third party, find its policy; if you cannot, do not use it.
- Evidence has limits: an address and client string are a reason to look, never proof of identity.
- Make one unique marker per placement so a signal says where it came from.

### Deception-and-Honeypots-Honeyfiles-on-Your-Host
Builds a file watcher, tests which actions raise events, and shows a hostile file name forging log lines, including why a first timestamp-based fix was not enough. Compares with the audit framework.
- Learn a tool's real behavior by predicting and then trying each action (reads and copies look identical; metadata access raises nothing).
- When a bug appears, test whether the obvious fix can also be bypassed; fix the class (use a real parser) rather than the instance.
- Never splice attacker-chosen text into your own record format.
- A user-space watcher can be killed; watch the watcher.
- State what the tool cannot know (which person, which program) instead of implying it.

### Deception-and-Honeypots-Alerts-in-the-SIEM
Writes two detection rules as a small program over synthetic events, then drafts Wazuh equivalents labeled unverified, with an ordered list of what to test. Emphasizes field matching and negative cases.
- Match on parsed fields, never on substrings of raw input.
- Test that a rule stays quiet and fires exactly at the boundary, not only that it fires.
- Bound memory and survive bad lines: size limits, count and drop malformed input rather than crash or silently skip.
- Label drafts that never ran, and list the unverified assumptions in the order you would test them.
- Do not over-claim classification (a fake account accepted is not valid account abuse).

### Deception-and-Honeypots-Design-a-Honeynet
Designs an isolated segment in layers and tests the firewall policy with a small model checker, then breaks the rules deliberately to see which expectations catch it. States what the model cannot prove.
- Write expectations (allow and deny) separately from rules and check one against the other; an empty expectation list must fail.
- Mutate the configuration on purpose to prove the checker catches broad rules, ordering mistakes and forgotten temporary openings.
- A model passing is necessary, not sufficient; test the real system before installing anything on it.
- Make temporary openings narrow, dated and covered by an expectation that fails while open.
- A missing expectation means silence, so the checker is only as good as the cases you thought of.

### Deception-and-Honeypots-T-Pot-at-Home
Reading-based guide to installing a honeypot bundle: default data sharing, installer side effects, pinning a release, alert handling and full teardown. Everything touching the product is marked as not run.
- Look for defaults that send data elsewhere before first start, and recheck them after every update.
- Read an installer before running it, pin a release, read that release's docs, and know what it changes on the host.
- Decommissioning is part of the work: ordered removal of access, rules and data, then proof that it is gone.
- During an incident, contain without destroying evidence, then look wider for what else the source touched.
- Say what the product does not provide (here, notifications) instead of assuming it exists.

### Deception-and-Honeypots-Cloud-Sensor-Anatomy
Paper lesson on nine guardrails for an internet-facing honeypot, the provider policy, the true cost and why a spend alert is not a cap. Cites public data on what arrives.
- Read the provider's acceptable use terms first; silence is not permission, ask in writing.
- Know the difference between an alert and a hard limit, and enforce spending limits yourself in layers.
- Give every guardrail a reason and a concrete way to verify it.
- Isolate risky experiments in their own account so the failure lands where nothing else lives.
- Label arithmetic estimates and one-day or one-analyst data for what they are.

### Deception-and-Honeypots-Cloud-Cowrie-Weekend
Step by step build, lock down, expose, observe and destroy of a cloud honeypot, with teardown written first and cloud commands marked unrun. Includes lockout safety nets and proof that outbound traffic is blocked.
- Write teardown, kill switch layers, triggers and proof of removal before creating anything.
- Arm an automatic revert before applying a change that could lock you out, and keep the old session until a new one works.
- Prove a restriction with a test that should fail, and remember that existing connections can survive rule changes.
- Expose last, only after a final precondition checklist, and treat any change to a live exposed system as a rebuild.
- Predict outcomes (time to first event, exit codes) before running, then compare.

### Deception-and-Honeypots-Read-the-Sensor-Logs
Reads synthetic honeypot logs with jq and PowerShell, safely handling hostile and broken lines, reuses the detector, and lists how visitors recognize the imitation. Notes that silence is not safety.
- Expect broken, truncated and hostile records; a tool that stops at the first bad line gives silently partial answers.
- Escape untrusted fields when printing, since a terminal or other consumer may act on them.
- Exclude your own test traffic from measurements, and do not over-read a small sample.
- Check that configured details tell one consistent story and record the tells you cannot fix.
- Write the limit into the plan: no signal means nobody tripped it, not that nobody was there.

### Small-Example-Enterprise-Landscape
Says the project is a small teaching example and maps each question it answers to the product categories a large organization uses. Advises learning the questions rather than the tool names.
- Think in the question a tool answers, then compare products against it; do not mistake your stack for the field.
- Weigh the operating burden of running something, not only its features.
- Form your own view from primary docs before reading comparisons.
- Be explicit about what a small system cannot teach (scale, process, legacy, constraints).
- Principles such as default deny, least privilege and a written reason per rule carry across products.

### Logs-SIEM-and-Detection-Basics
Teaches reading, parsing, normalizing and correlating logs, then writing, breaking and tuning a failed-login rule and a baseline on invented data. Covers clock skew, duplicates and alert fatigue.
- Count with a loose pattern, then compare with the strict one; the variant you did not look at is how rules fail quietly.
- Every threshold trades false positives against misses; show the sweep, record why you chose the value and when to revisit it.
- Use two detectors that fail in different ways instead of perfecting one.
- Before trusting a timeline or count, check clock sync, time zones and duplicate sources, and remember what normalizing threw away.
- Review a proposed rule for window, grouping, severity, field matching, owner and review date. (The page's claims table also still mentions the older audit rule form in one row, a reminder to sweep all docs after a change.)

### Detection-and-Monitoring-Wazuh-and-the-Landscape
Introduces collect, store, detect and respond, explains Wazuh, and places commercial tools by what they watch, how they see it and who acts. States openly that nothing ships logs yet.
- State current blind spots next to the controls, and never describe planned work as present.
- Argue against your preferred choice: a monitoring agent adds root code, a secret and a network path.
- For each threat, name the exact event and place that would reveal it; if none exists it is undetectable as designed.
- Detection without a reader and a first action is only storage; also measure how long until a silent sensor is noticed.
- Logs may contain secrets, so choose what to collect on purpose.

## Batch lessons

1. **Plan for failure of every component, including the safeguard.** Ask what it reaches, how you would know, how you recover; decide fail open or closed; alert on silence. Slugs: Plan-for-Failure-Blast-Radius-and-Assuming-Breach, Rate-Limiting-at-Every-Layer, File-Integrity-and-Alerting-Tripwire-AIDE-Wazuh, The-DMZ-and-Hardening-a-Host-That-Faces-the-Internet, Detection-and-Monitoring-Wazuh-and-the-Landscape.
2. **Say exactly what was verified.** Label run, read, estimated, designed, built but off, not applied; keep a claims register; avoid flattering shorthand. Slugs: all pages with status banners, notably Attack-Surface-List-Shrink-Measure, Attack-Surface-Map-Layer-by-Layer, The-DMZ-and-Hardening-a-Host-That-Faces-the-Internet, Deception-and-Honeypots-Alerts-in-the-SIEM, Deception-and-Honeypots-T-Pot-at-Home.
3. **Prove the guard bites.** Negative cases, boundary tests, deliberate mutations, a test that should fail; a control without a failing check is "None". Slugs: Deception-and-Honeypots-Alerts-in-the-SIEM, Deception-and-Honeypots-Design-a-Honeynet, Attack-Surface-Map-Layer-by-Layer, Logs-SIEM-and-Detection-Basics, Deception-and-Honeypots-Cloud-Cowrie-Weekend, Rate-Limiting-at-Every-Layer.
4. **Predict, do, check, undo.** Write the expectation before running, then explain surprises (SYN cookies, the limiter skipped by an early return). Slugs: Rate-Limiting-at-Every-Layer, Deception-and-Honeypots-Honeyfiles-on-Your-Host, Logs-SIEM-and-Detection-Basics, Deception-and-Honeypots-Cloud-Cowrie-Weekend, Plan-for-Failure-Blast-Radius-and-Assuming-Breach.
5. **Untrusted input is data.** Parse, compare fields, bound size, escape on output, never trust client-written headers or names. Slugs: Deception-and-Honeypots-Plant-a-Canary, Deception-and-Honeypots-Honeyfiles-on-Your-Host, Deception-and-Honeypots-Alerts-in-the-SIEM, Deception-and-Honeypots-Read-the-Sensor-Logs, Rate-Limiting-at-Every-Layer.
6. **Every alert and control has an owner, a first action and a false positive cost.** Dry-run first, tune, remove noise. Slugs: File-Integrity-and-Alerting-Tripwire-AIDE-Wazuh, Rate-Limiting-at-Every-Layer, Logs-SIEM-and-Detection-Basics, Deception-and-Honeypots-What-Deception-Is, DMZ-Hardening-Checklist.
7. **Remove rather than hide, and list before you shrink.** Obscurity is not a control. Slugs: Attack-Surface-List-Shrink-Measure, Plan-for-Failure-Blast-Radius-and-Assuming-Breach, The-DMZ-and-Hardening-a-Host-That-Faces-the-Internet, Deception-and-Honeypots-Cloud-Sensor-Anatomy.
8. **Write the exit before the entry.** Teardown, kill switch, end date, spend limit, lockout revert, proof of removal. Slugs: Deception-and-Honeypots-Safety-and-Law, Deception-and-Honeypots-Cloud-Cowrie-Weekend, Deception-and-Honeypots-T-Pot-at-Home, Deception-and-Honeypots-Cloud-Sensor-Anatomy.
9. **State the cost and the residual risk of each choice.** Slugs: Plan-for-Failure-Blast-Radius-and-Assuming-Breach, Rate-Limiting-at-Every-Layer, File-Integrity-and-Alerting-Tripwire-AIDE-Wazuh, Small-Example-Enterprise-Landscape.
