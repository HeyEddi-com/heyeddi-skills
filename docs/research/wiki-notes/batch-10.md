# Batch 10 notes

### RAID-Levels-Parity-Rebuilds-and-Why-RAID-Is-Continuity-Not-a-Backup
Explains that RAID keeps a system running through drive failure but is not a backup, because deletion, corruption, ransomware and site loss hit every drive at once. It covers levels, parity, rebuild risk and the write hole, with a small drill and a clear list of what was and was not run.
- Name what a control does not protect against: list the failure events and mark which ones each safeguard actually answers, so "we have redundancy" is never read as "we can recover".
- Redundancy assumes independent failures. Ask what shared cause (same batch, box, login, power, bad update) would take out every copy together.
- An operation that finishes without error can still produce wrong data. Verify content, not exit status, and rehearse restore and recovery before the bad day, since recovery steps are where people destroy data.
- Predict the outcome, run it on a throwaway copy, compare, undo. A mismatch shows what you did not understand.
- Label every claim as read, observed, estimated or not run.

### Fork-Private-Stacks-and-the-Pipeline
Shows how to make a private copy of a public demo, separates demo values from ones to change or keep, and describes the gate chain from commit to apply.
- Copying code does not copy its protections. Branch protection, attached policies and external connections must be listed and recreated, then tested by trying the forbidden action.
- If a gate is unavailable (plan limit, missing permission), say so in writing and name what stands in its place instead of pretending it exists.
- Mark demo-grade choices explicitly with what production would change and why, so nobody copies compromises as best practice.
- For every pipeline stage ask what mistake only this stage can catch. A check that lives in someone's memory will be skipped.
- Find the expensive-to-reverse decisions early (address ranges, names) and treat them with more care than cheap ones. A pinned third-party reference is still code you have to read.

### Labs-Break-It-on-Purpose
Five exercises that deliberately weaken a safety property and ask which check will notice, including cases where a check fails for the wrong reason.
- A control is not proven until you have broken the thing it protects and watched it object. Every security control needs a test that fails when the control disappears.
- Read the error, not just the red. A failure for an accidental reason protects today and may not tomorrow.
- Treat skipped tests as "not checked", never as passed.
- Gates should fail closed: an unknown input is refused, not counted as zero.
- Test with near-miss values (a branch called "mainline", a null where false is assumed), because natural-looking conditions often have quiet bugs.

### Build-It-From-Zero-Accounts-to-Stage-1
An ordered build path with a checkpoint and "what you should see" at every step, ending with teardown and proof that billing stopped.
- Bound the downside before building: MFA, budget numbers and billing alerts come before the first token or resource.
- Write the expected result for each step in countable terms (exactly N resources) so surprises are visible.
- Verify from both sides: the thing works for who should reach it and fails for who should not.
- A green internal check proves consistency with your own model, not with the vendor's real price or behavior. Check the external fact too.
- Plan teardown and its failure cases as part of the build, and list what will survive it.

### Variables-Tfvars-and-Secrets
A decision table for where each configuration value belongs, why value files never hold secrets, and which names are immutable.
- Give every kind of value exactly one home, decided by an ordered set of questions.
- Ignore rules are a backstop, not the protection. The protection is never putting the secret there.
- Separate identity-bearing keys (changing them replaces resources) from free-to-edit labels, and enforce the separation with a test.
- A refactor of live configuration is accepted only when the plan shows no change.
- Keep example files honest with tests (every variable listed, nothing extra, no real values).

### Teardown-Checklist
Ordered destruction, the guard that must be temporarily relaxed, leftovers, read-only proof of zero resources and credential revocation.
- A success message from a destroy is a claim. Prove it with independent views, and check again later because data lags.
- When a safety guard blocks a legitimate action, open the narrowest reviewed exception and close it again afterwards.
- Order matters: destroy, prove, then revoke, so you do not strand yourself without the credential needed to finish.
- List what the automation never owned (hand-made objects, keys, accounts) and say why each stays.

### Self-Hosting-When-and-Why-with-SearXNG-as-the-Worked-Example
Weighs running a service yourself, shows who can see a search on each path, gives a ten-row checklist and says when not to host.
- Running something is an ongoing duty (patching, restore, monitoring, exposure). Decide "do not" if you cannot fill a row.
- Trace who can see data at each hop. A privacy tool usually moves trust rather than removing it.
- Make dangerous settings required with no default (bind address), because platform defaults may expose to everyone and bypass the firewall you rely on.
- Decide logging on purpose: keep health and error signals, do not write sensitive content.
- Say plainly when resource needs are unknown and how to measure them.

### Twingate-Service-Accounts-in-CAH
Researches what a vendor's machine identities are, which plans include them, where the code uses them and what the vendor leaves unanswered.
- Check plan and entitlement limits before designing around a feature, and record where vendor pages disagree or are silent instead of guessing.
- Answer "where do we use this?" by searching the code, and give the command so others can rerun it.
- A credential reaches everything its identity holds, so narrow by role and site, and keep keys out of tool state.
- Dormant code is not a working feature. State "merged, not applied, other half not built".
- Defaults that disagree between a console and an API (expiry) mean you should set the value explicitly.

### Zero-Trust-at-Home-Two-Connectors-and-Failover
Explains per-resource access with two outbound-only connectors, a failure table, firewall rules by role and honest limits.
- Write a table of what fails, what you see and what still works before relying on redundancy, and note what stays shared (power, router, identity provider).
- Test failover one side at a time, predict first, and keep a recovery path that does not depend on the thing being broken.
- Know what each control layer can actually see: a network firewall cannot enforce roles, it only caps the blast radius.
- Never update redundant members together, and have the rollback written before you need it.
- State which parts are automated and which are still manual.

### Why-Not-Private-Droplets-Yet
Answers why machines have public addresses: cost, with the same inbound exposure, plus the real trade-offs and the conditions for revisiting.
- When rejecting the textbook design, record the reason with numbers and what you give up.
- Distinguish a property you get for free (no route in) from a control you must keep correct (a firewall rule), and test the latter from outside.
- Name the triggers that would reopen the decision.
- State precisely what the guarantee is, including its exceptions.

### Why-I-Picked-These-Tools
An opinion page on tool choices with disclosures and what each tool does not do.
- Be explicit that a choice is preference or familiarity, and disclose bias.
- State a tool's gaps up front.
- Prefer structure that survives swapping any single product.

### From-Commit-to-Pipeline
Follows a change through nine stages, explains reusable pinned workflows, a single required gate, permissions and policy as code.
- Make one aggregate required check that treats skipped or cancelled jobs as failure.
- Share CI logic from one place and pin it to an exact commit, so behavior changes only through a reviewed line.
- Give each job the least permission, and read the caller's grants to know what a pipeline can do.
- A policy file that is not attached protects nothing. Distinguish written, tested and enforced.
- Put each question where the answer is cheapest, and read a plan for verb, count and match with the stated intent.

### Trace-One-Change-End-to-End
Traces a real firewall fix through every gate, then asks what would stop three worse variants of it.
- A pull request should state Why, Change, Testing and Not verified, so reviewers know what green does not prove.
- Review a change that edits a rule and its guarding test together with extra care.
- Predict which stacks should show no change. An unexpected diff is a finding.
- Success of plan or apply is not success of the fix. Reproduce the original symptom (repeatedly if intermittent) and recheck the security property.
- A gate that checks content may miss the effect (a one-line edit that replaces both machines). Ship such changes one unit at a time.

### Why-the-Clouds-Differ
Compares providers through four questions: boundary, internet path and its price, how rules target machines, and machine identity.
- Learn a new platform by asking a fixed set of portable questions rather than mapping names one to one.
- Do not carry a rule of thumb across platforms without rechecking it.
- An abstraction that hides two concepts behind one friendly word hides the thing that will bite.

### Provider-AWS-Account-Preparation
Protect, empty and watch a new account before creating anything.
- Set up containment, identity protection and alerts before the first resource.
- Know what happens when a free offer ends and what silently ends it.
- A budget notifies, it does not stop spending.
- Write down the spend limit and delete-by date before starting.

### Provider-AWS-The-Same-Four-Pieces
Maps the four building blocks to AWS, noting one object becomes several and what firewalls do not filter.
- Predict the resources from the existing code, then compare with a reference.
- Know the platform defaults and the blind spots of each control (metadata service).
- Grant no machine identity when none is needed.
- Say that mocked tests prove code shape, not platform behavior.

### Provider-AWS-Cost-Lesson
Prices a small stack, shows the NAT charge that would break the budget and how to prove zero.
- Show cost arithmetic line by line, including idle and by-the-hour items people forget.
- Say what the estimate leaves out.
- Check the shared total across everything, not each part alone.
- Refuse budget-breaking resource types automatically, since copied tutorials sneak them in.

### Provider-Azure-Account-Preparation
Boundaries, free credit, first identity, budgets and access before building on Azure.
- A new subscription is not isolation if it shares a directory. Verify what a boundary actually contains.
- Upgrading a plan can remove a safety limit. Recheck safeguards at plan transitions.
- If the safeguard cannot be created yet, create nothing yet.
- Mark unverified claims inline.

### Provider-Azure-The-Same-Four-Pieces
Shows that platform defaults differ (outbound access changing by API version, internal traffic allowed) and lists the resources needed.
- Set security-relevant and connectivity-relevant behavior explicitly. Defaults can change with an API or tool version without any diff in your code.
- When two official pages disagree, compare dates and say which you trust.
- "Closed from the internet" does not mean closed from neighbors. Test the second claim separately.
- A first-boot script can fail while the machine reports ready, so check the service itself.
- Where docs are silent, test rather than assume.

### Provider-Azure-Cost-Lesson
Prices the Azure stack with stated assumptions and admits the repository's cost gate does not cover Azure.
- State precisely what an existing guard covers and what only looks covered.
- Surface when a requirement (memory guidance) and a constraint (budget) cannot both be met.
- Record assumptions inside the arithmetic.

### Provider-GCP-Account-Preparation
Account setup without an organization, where guardrails must become habits, and no downloaded keys.
- When platform enforcement is unavailable, turn the guardrail into an explicit step with a checkpoint.
- Make checkpoints use a view that can actually show the thing (the keys tab, not the permissions page).
- Avoid long-lived key files; prefer short-lived identity.
- An alert nobody reads is worse than none.

### Provider-GCP-The-Same-Four-Pieces
Maps the pieces to GCP, including egress rules that cannot target tags and boot-script mechanisms that do not translate.
- Porting is redesign: check each assumption (rule targets, boot script format, how often it runs).
- Reason about both ends of a connection; a deny-all egress needs its own allow on the sender.
- Do not use broad default identities.
- Hold unreviewed work until someone with real platform experience has checked it.

### Provider-GCP-Cost-Lesson
Computes the break-even between public addresses and NAT and separates verified from working prices.
- Compute the break-even and name the unknown (your traffic) that decides it.
- Table which inputs are verified and carry that status into derived totals.
- Revisit the arithmetic when rates change.

### Enterprise-Networks-Campus-Branch-Datacenter-Cloud
Vocabulary of corporate network shapes, links, segmentation and shared services.
- Segment on purpose, and give every boundary rule an owner, review and test.
- Plan address space before systems need to join.
- Shared basics (DNS, time, certificates) are common hidden causes when everything looks broken.

### Enterprise-Infrastructure-Differences
Contrasts one-person practice with enterprise guardrails, inventory, state, recovery and vendors, saying why the small version is enough here.
- For each practice you skip, say why that is fine at this size and what event would end that.
- Code is intended inventory, not actual inventory. A clean plan cannot see resources made by hand.
- Put critical guardrails where the pipeline author cannot edit them.
- Split state and credentials by blast radius.

### Enterprise-Change-Management-for-Beginners
Change types, rollback, evidence and approval, then an honest account of what a one-person project has and lacks.
- A rollback is exact steps plus a trigger, and some changes cannot be undone, which raises the review bar.
- Pre-approve a narrow, machine-enforced change type rather than approving every instance.
- Record before acting, not after. Rubber-stamp review and "everything is emergency" are warning signs.
- Measure outcomes (change fail rate, recovery time), not approval counts.
- State missing controls plainly instead of implying equivalents.

### Enterprise-Identity-and-Secrets-at-Scale
Identity lifecycle, privilege, machine identity and secrets, and where the project's model breaks as it grows.
- Disabling one account is not full offboarding; issued sessions and independent keys survive.
- Every secret needs an owner, scope and expiry.
- Prefer short-lived exchanged credentials over stored ones.
- Judge a read-only token by what the values it reads can do.
- For each design piece, say how it scales and where it breaks.

### Working-in-a-Company-Tickets-Change-On-Call-and-Documentation
Templates and worked examples for tickets, change records, handovers, runbooks, post-mortems, access requests and on-call.
- Write so a stranger can act: expected, actual, exact error, impact, what was tried. Report impact and let priority follow.
- Each runbook step has run, expect, if not, undo, and a last-tested date. A handover includes "watch for" and "do not do".
- On an incident, restore service first, escalate early, record times as you go. Post-mortems look for system causes with owned, dated actions.
- Being able to do something is not permission to do it.
- A form check proves fields exist, not that they are true; ask how the control would be gamed and count the escape hatch (emergencies).

### Careers-Roles-and-What-to-Learn-Next
Maps roles and a skills ladder from using, reading, running, breaking, defending, watching, scaling to teaching.
- Build skill by doing: read the plan, run it, break it, fix it, then explain it to someone.
- Write the acceptance test before starting a practice project.
- A restore time you have timed is your real recovery time; a runbook someone else cannot follow is unfinished.

### How-This-Project-Is-Planned
Backlog, sizing, capacity limits, definitions of ready and done, and routing of work to people and agents.
- An item without a "done when" is a question, not a task.
- Done includes a test shown to fail without the change, updated docs, and for live systems a plan a human read.
- Risky changes get an adversarial review by someone other than the author.
- Limit work in flight to what review can absorb, and split oversized items before scheduling.
- Turn style and safety rules into tests with a reasoned allowlist, and lab scripts must use private temp folders and verify a pid before killing it.

### Project-Status
A generated snapshot of issues and pull requests, with classification rules, caveats and commands to reproduce every number.
- Generate status from the source of truth, timestamp it, and fail CI if the page and snapshot disagree.
- State the classification rules and their weaknesses (a reference is not proof of completion).
- Flag known data gaps at the top.

### Repository-Growth
A generated metrics page that explains how to read the numbers and the residual risk of the publishing job.
- Say what a metric does not measure.
- Do not trust mutable data you read back; verify continuity and fail rather than publish something inconsistent.
- When a permission cannot be narrowed, say so, name the real control and do not call script discipline access control.

### Screenshots-Policy
Rules for what may be pictured, redaction, metadata stripping, tests and a manual checklist.
- Avoid capturing sensitive data rather than hiding it afterwards.
- Use allowlists over blocklists for sanitizing.
- Automate what a test can check and give the rest an explicit human checklist that the author and reviewer both run.

### Settings-Reference
Generated table of every setting with defaults, validation, sensitivity and status.
- Generate reference docs from one machine-readable source and test it against the code.
- New features default off so merging changes nothing, and a test pins that.
- Roll out replacing changes one instance at a time with a health check between.
- Validate inputs strictly at the edge, especially anything rendered into boot scripts.
- Mark each setting's sensitivity and whether it exists or is only planned.

### Terraform-Reference
Explains each declaration in the modules and stacks and why it exists.
- Keep one source of truth so approved cost and deployed size cannot differ.
- Order dependencies explicitly when no reference implies them.
- Document each scanner exception next to the code with its reason.
- Write expected plan counts so reviewers can compare.

### Troubleshooting-Index
Lookup table from exact symptom to cause and where the fix is written, with a practice reproduction.
- Record real failures as symptom, likely cause, pointer.
- Read the exact message and identify which layer printed it.
- Fail loudly with a specific message when input is missing or ambiguous.
- Do not infer success from a summary line or diagnose by an indirect signal; use the explicit one.

## Batch lessons

1. Separate what was verified from what was not (read, run, estimated, never applied), and date external facts. Pages: RAID, Self-Hosting, Twingate-Service-Accounts, all Provider pages, Enterprise pages, Trace-One-Change, Working-in-a-Company.
2. Predict, then check: write the expected result (counts, which test, which message) before running, and treat the gap as the finding. Pages: RAID, Fork, Labs, Build-It, Trace-One-Change, Teardown, Troubleshooting-Index, Provider pages.
3. Prove controls by breaking them, and test the negative case. Pages: Labs, Trace-One-Change, Fork, Working-in-a-Company, Build-It, Azure-Four-Pieces, How-Planned.
4. Written is not enforced and success is not proof: unattached policies, mocked tests, green destroy and successful apply all need independent verification. Pages: From-Commit, Fork, Trace-One-Change, Teardown, Twingate-Service-Accounts, AWS-Four-Pieces, RAID, Azure-Cost.
5. Say what a safeguard does not cover and where the real boundary is. Pages: RAID, Why-Not-Private-Droplets, Cost lessons, Enterprise-Infrastructure, Zero-Trust, Repository-Growth, Working-in-a-Company.
6. Fail closed and be explicit rather than rely on defaults. Pages: Labs, Troubleshooting-Index, Azure-Four-Pieces, Self-Hosting, Settings-Reference, Variables, Terraform-Reference.
7. Plan for reversal and failure before acting: rollback with trigger, teardown order, restore test, one-at-a-time rollout, alerts first. Pages: Build-It, Teardown, Change-Management, Working-in-a-Company, Settings-Reference, Zero-Trust, RAID, account preparation pages.
8. Record decisions with reasons, trade-offs, demo-versus-production and revisit triggers. Pages: Fork, Why-Not-Private-Droplets, Why-I-Picked, Enterprise-Infrastructure, Identity-at-Scale, Change-Management.
9. One source of truth, generated docs and tests that hold documentation to the code. Pages: Settings-Reference, Project-Status, Variables, Terraform-Reference, How-Planned, Screenshots-Policy, Repository-Growth.
10. Least privilege and small blast radius: narrow credentials, no unneeded identity, scoped tokens, owners and expiry. Pages: Twingate-Service-Accounts, Zero-Trust, Identity-at-Scale, Four-Pieces pages, From-Commit, Teardown.
11. Cost is a design input checked before creation: line-by-line arithmetic, break-even, automated gate. Pages: Provider cost and account pages, Why-Not-Private-Droplets, Fork, Labs, Troubleshooting-Index.
