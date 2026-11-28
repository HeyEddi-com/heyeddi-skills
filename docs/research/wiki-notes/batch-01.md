# Batch 01 notes

### Glossary
A very large alphabetical-ish term list (cloud, security, privacy, crypto, law, ops), each with a plain definition, often a limit of the thing, and a link to the page that explains it.
- Define a term by what it does and also what it does not do (snapshot is not backup, encoding is not secrecy, RAID is not backup, NAT is not a firewall).
- Separate claims from proof: a backup is only proven by a timed restore, a connectivity test button only proves one connection worked, a checksum or signature only proves what it covers.
- Keep paired ideas distinct so decisions stay clean (authentication vs authorization, severity vs priority, identifier vs authenticator, RPO vs RTO).
- Mark unverified or unrun statements inside reference material, with dates for facts that change.

### Reading-Order
Numbered reading paths by audience, with time estimates, prerequisites, checkpoints and an upfront statement of which parts are built, drafted or never applied; a test keeps the navigation consistent.
- State status honestly at the top of docs: built and tested, written but not applied, planned.
- Give each step a checkpoint that is something the reader can do or explain, not just "read it".
- Explain how estimates were computed, and do not invent a number where there is no basis.
- Enforce documentation structure with a test so new pages cannot be orphaned and links cannot rot.

### Start-Here-If-You-Are-New
Onboarding page that maps homelab ideas to cloud terms, states the assumed starting level, and lays out a primer path; ends with advice not to lean on AI as a crutch.
- State the assumed prior knowledge explicitly and point people elsewhere if they lack it.
- Teach new concepts by mapping them to ones the reader already has, then name where the analogy differs.
- Know that deleting the code is not deleting the resource; verify teardown, and set a billing alert before creating anything.
- Learn the thing yourself first, then direct the AI; AI amplifies both strengths and weaknesses.

### Home
Front page: what the project is, which path fits which reader, current build status and cost per stage, and how the wiki is published.
- Keep one place that shows current state per stage, including cost and what is not applied.
- Route readers by role and goal instead of one linear manual.
- Keep docs in the same repo and review pipeline as code, and publish from there only.

### Contents
Generated index of every page with purpose, audience and status markers, plus a "when would I need this" line for side pages.
- Generate indexes from a manifest and fail CI when the page drifts from it.
- Label every document with its maturity (draft, steps not run, unbuilt).
- Describe a doc by the problem or confusion that would send someone to it.

### Why-This-Exists
Opinion page on why the author teaches this for free, how long it took to learn, tool choice, disclosures, and the build, break, detect, evade, defend loop.
- Understand how a system is built before trying to break it; then switch sides repeatedly and question your own design.
- Say what you know from doing versus from reading, and mark estimates.
- Disclose conflicts of interest where a recommendation appears.
- Compare tools fairly, including where the alternative is the simpler choice, and why you chose anyway.
- Admit thin areas (here, hands-on evasion) instead of implying full coverage.

### Give-Feedback-and-Open-an-Issue
How to report problems: what to include, what never to paste, and private reporting for security issues.
- A useful report has location, environment, expected result, actual result and exact error text.
- Assume anything posted publicly is permanent; if a secret leaks, revoke first and edit second.
- Treat reader confusion as a defect in the page.
- Say what you did not verify (example commands not run).

### What-Is-the-Cloud
Primer on VMs, object storage and functions, public addresses, billing for existence, APIs and tokens, and shared responsibility.
- Invert home defaults: close things before the resource exists.
- Design machines to hold nothing irreplaceable so recovery is destroy and rebuild.
- Treat a write-capable token as the most valuable asset.
- Know which half of shared responsibility is yours; most failures happen there.
- Some limits (size not offered in a region) are only found by asking the real API or trying.

### Networking-Basics-for-This-Project
Addresses, CIDR, ports, firewalls, inbound vs outbound, VPCs, DNS, NTP and SSH, as needed for this design.
- Reduce what listens; an attacker can only talk to a listening program.
- Reason about both directions of every connection; replies are free, new connections need a rule on each side.
- Allow narrow outbound ports with a reason for each, not "allow all".
- Choose address ranges that will not collide with networks you may connect later.
- Pair a concept with a safe experiment, and only probe systems you own.

### Identity-Secrets-and-Zero-Trust-Basics
Authentication vs authorization, secret types, how secrets leak, secrets managers, least privilege, MFA and zero trust.
- Ask "who are you" and "what may you do" separately for every design.
- List the concrete leak routes and map each control to one of them.
- Scope every token to the smallest job; a permission error from a narrow token is the right kind of failure.
- Grant access based on identity and policy, never on network location.
- Rotate first, then remove from history; deleting a committed secret does not unleak it.

### What-Is-Infrastructure-as-Code
Describing infrastructure in files, with providers, resources, plan, apply, state, drift, modules and where the tool should run.
- Read the plan (the proposed diff against reality) before applying, and watch for surprise destroys.
- Treat unexpected drift as an alarm, and make reruns idempotent.
- State holds secrets and identity of resources; decide who can read it and lock it.
- Split by blast radius so a mistake in one layer cannot touch another.
- Reject bad input at the edge with validation, and test security properties with fake providers.

### Git-GitHub-and-Pull-Requests
Commits, branches, pull requests, CI, action pinning, branch protection and wiki contributions.
- Put every change, including your own and docs, through one reviewed gate that records why.
- Keep the thing that checks separate from the thing that changes; CI holds no credentials.
- Pin third-party code and downloads by hash.
- Automated checks stop honest mistakes only; the real boundary is who can push. Say so.

### Containers-and-Docker-Basics
Containers vs VMs, images, Compose, state, and what must change to move home-lab daemons to the cloud.
- Ask where state lives before anything else, so the host can be disposable.
- List the assumptions the old environment satisfied silently (disk, long life, local config, log files) before migrating.
- Make health checks measure real work done recently, not process existence.
- Know that control of the container daemon is control of the host.
- Add a second layer even when the first covers it (bind to private address behind a cloud firewall).

### How-Money-Works-in-the-Cloud
How cloud bills grow and defenses ordered by how early they act: alert, written ceiling, approval before creation, CI cost gate, single source for sizes, easy destroy.
- Decide and record the budget before building; approve cost before the resource exists.
- When two things must match (priced size and built size), make them one value.
- Turn limits into failing checks, and make raising a limit a visible reviewed diff.
- Order defenses by how early they catch the mistake and keep a late backstop.
- Count complexity and your own time as costs; date vendor prices and free-tier claims.

### Enterprise-Engineering-Habits
Names the habits behind the project (review, separation of duties, least privilege, default deny, threat model, stage gates, runbooks, blameless post-mortems, verify and record, boring tools) with a small-scale version of each.
- Prefer rules that fail closed (allow lists) because forgetting then breaks something instead of exposing it.
- Grow in small stages that each have a design, cost, approval, verification and teardown.
- Write the rebuild and rotation steps while calm, then test the document.
- "It should work" and "I watched it work on this date" are different; write which one you mean.
- Choose boring, open, replaceable tools and know the exit cost.

### Architecture-Overview
Data plane vs control plane, components with the reason for each, three key paths, naming and repository layout.
- Separate how users reach the system from how the system gets changed.
- For every component write what it does and why this one.
- Explain the few paths that matter (a change, a session, a secret) instead of every edge.
- Use predictable naming and parameterize region so growth is instantiation, not copy-paste.
- Say what is left out of the diagrams because it is not applied.

### Why-ZTNA-Not-a-VPN
A comparison of per-resource zero trust access with remote-access VPNs, by threat, with real incidents, a standards mapping and an honest section on where VPNs are fine.
- Compare designs threat by threat, including rows where the alternative wins (availability).
- Prefer removing an attack surface (no listener) over hardening it.
- Back claims with dated incidents and primary sources.
- Argue against your own choice: name the new trust you take on, the failure mode and the recovery path.
- Critique the model, not a straw man (a well-configured WireGuard is credited).

### Twingate
How access is wired: components, two connectors, narrow resources, access groups as code, token risk, telemetry settings and verification.
- If the only way in runs through one component, run two and stagger their reboots and updates.
- Guard against configuration that produces something unreachable (refuse an empty admin list).
- Keep a table of settings with whether each was verified from vendor docs.
- Roll out disruptive changes one instance at a time and check access before doing the next.
- Check what a command proves; a health check that says the service runs does not say it is connected.

### DigitalOcean-Network-and-Firewalls
Tag-based layered firewalls, protection attached at creation, tag rules instead of addresses, both directions inside the private network.
- Leave no window of exposure: protection exists before the resource, with explicit ordering dependencies.
- Reference stable identities (tags) rather than things that change on rebuild (addresses).
- Suppress a scanner finding only with a written reason, and name the weakest rule.
- Record dated vendor behavior, since platform semantics change.
- Include an outside verification that shows the property actually holds.

### Droplet-Hardening
First-boot hardening, staggered updates, optional host firewall and metadata lock, external port scan, and a list of what is not done.
- Do not rely on one control; the host should hold if the network rule is wrong.
- Ship risky changes behind a default-off flag, apply to one instance, verify, then the rest, with a written rollback.
- Validate config before restarting the service that could lock you out, and add a self-check that undoes a bad ruleset.
- State exactly what each test does not prove, and separate "reasoned" from "tested on a real machine".
- Skip measures that only obscure (moving a port); think through interactions such as another service flushing your rules.

### OpenTofu-Stacks-and-Modules
Why layered stacks and modules, conventions, mocked tests and a provider upgrade note.
- Split state by blast radius, change rate, credentials needed and reviewable plan size.
- Pass only the values a consumer needs rather than giving it access to everything upstream.
- Pin the list of exposed outputs in a test so adding one is deliberate.
- Look up shared existing things instead of taking ownership of them.
- Before a dependency upgrade, state what the first plan should show and what means stop.

### Spacelift
How runs and approvals work, why pull request plans get no credentials, push and plan policies, allowlist design and where the real trust boundary is.
- Never give secrets to code from an unreviewed branch in a public repo.
- Do not mistake an in-branch script check for a security control; name the actual boundary.
- Make exceptions narrow (scoped by stack, resource, port, source), reviewed in code, and deny anything unknown.
- Turn conventions (no deleting core pieces, no auto-apply) into enforced rules.
- Report precisely what is written, what is tested with fixtures, and what is not yet attached or live.

### Doppler-and-Secrets
Where each secret lives, a fail-closed fetch script, residual places secrets still land, and rotation.
- Fail closed: fetch only in allowed run types, by name, with a verified tool, and mask output.
- Least privilege by convention is not isolation; say what malicious code could still read.
- List every other place a secret ends up (state, boot data) with its mitigation.
- Write rotation steps that include a verification and revoking the old value.
- Test the negative cases (wrong branch, bad checksum get nothing) and verify masking in a real log.

### CI-Tests-and-Cost-Gate
One gate job, shared pinned workflows, least-privilege CI, a cost gate, repository-wide rule tests and an identifier leak check.
- Have one required aggregate check that treats skipped or cancelled as failure.
- Use allowlists for paid resource types so anything new is refused until reviewed.
- Document what each guardrail cannot see and what backstops it.
- A leak checker must not echo what it found, and must fail if it scanned nothing.
- Write cross-cutting invariants as repo tests (docs match settings, no IPv6, secrets separated); fix reusable CI in the shared library.

### Threat-Model
Assets, trust boundaries, fourteen numbered threats with controls and residual risk, accepted risks and what would change the model.
- For each threat write the control and what is still left over.
- Collect accepted risks in one list with the reason, so an oversight is distinguishable from a choice.
- Scope the model to the actual system and say what is out of scope.
- State which future changes will invalidate the model and what must be added first.
- Do not count a mitigation until it is actually attached or enabled.

### Lessons-Learned
Ten build failures with symptom, real cause, fix and general lesson (installer false success, two-sided firewall rules, existing resources, platform plan limits, new account limits, a check that could only fail).
- Check the end state, not the exit code; avoid piping installers into a shell.
- When a first fix fails, trace the whole path from both ends, and mark a cause as unproven if it is only the leading guess.
- Verify a feature exists on your plan and a size or permission exists on your account before designing around it; label fallbacks as fallbacks.
- A check that cannot pass trains people to ignore red; remove it or make it passable.
- Test the mitigation both ways: what must be blocked and what must still happen.

### Roadmap
Staged plan with sprint status, per-phase cost ceilings with arithmetic, and each stage's built, open and not-planned items.
- Show cost arithmetic and remaining headroom, and have each phase carry its limit, reason and decision date.
- Distinguish merged, mock-tested, applied and verified; do not claim what you cannot check.
- Ship dependent work flag-off with tests while apply stays gated on a person.
- Write "not planned" and "rejected for now" with the numbers and the trigger that would reopen it.
- Design today so the likely later move is cheap (portable handlers, state off host) without building it yet.

## Batch lessons

1. **Be exact about status and proof.** Separate planned, written, mock-tested, applied and verified; date external facts; mark guesses. Seen in: Reading-Order, Contents, Home, Why-This-Exists, Droplet-Hardening, Spacelift, Twingate, Roadmap, Lessons-Learned, Enterprise-Engineering-Habits, Give-Feedback-and-Open-an-Issue.
2. **State what a check or control does not prove, and name the residual risk.** Seen in: Glossary, Droplet-Hardening, CI-Tests-and-Cost-Gate, Doppler-and-Secrets, Spacelift, Threat-Model, Git-GitHub-and-Pull-Requests, Why-ZTNA-Not-a-VPN, Twingate.
3. **Verify the real end state, from outside where possible.** Exit 0, "installed" or "masked" are not evidence. Seen in: Lessons-Learned, Enterprise-Engineering-Habits, Droplet-Hardening, DigitalOcean-Network-and-Firewalls, Twingate, Doppler-and-Secrets.
4. **Turn rules into automated gates** (allowlists, repo-wide invariant tests, policy as code, generated docs), with deliberate reviewed exceptions. Seen in: CI-Tests-and-Cost-Gate, Spacelift, How-Money-Works-in-the-Cloud, Contents, Reading-Order, OpenTofu-Stacks-and-Modules, Droplet-Hardening.
5. **Default deny and fail closed, with protection in place before the thing exists.** Seen in: Enterprise-Engineering-Habits, DigitalOcean-Network-and-Firewalls, Networking-Basics-for-This-Project, Doppler-and-Secrets, Spacelift, What-Is-the-Cloud.
6. **Least privilege and small blast radius**, including splitting state, tokens and who checks vs who changes. Seen in: Identity-Secrets-and-Zero-Trust-Basics, Git-GitHub-and-Pull-Requests, OpenTofu-Stacks-and-Modules, Doppler-and-Secrets, Spacelift, CI-Tests-and-Cost-Gate, What-Is-Infrastructure-as-Code.
7. **Roll out in small reversible steps**: stages, default-off flags, one instance first, written rollback, read the plan for surprise destroys. Seen in: Droplet-Hardening, Twingate, Roadmap, Enterprise-Engineering-Habits, What-Is-Infrastructure-as-Code, OpenTofu-Stacks-and-Modules.
8. **Treat cost as a design input** with a written ceiling, arithmetic and approval before creation. Seen in: How-Money-Works-in-the-Cloud, CI-Tests-and-Cost-Gate, Roadmap, Home.
9. **Record why, including rejected options, failures and exit conditions**, without blame. Seen in: Lessons-Learned, Why-ZTNA-Not-a-VPN, Roadmap, Threat-Model, Architecture-Overview, Enterprise-Engineering-Habits.
10. **Check assumptions against the real platform early** (plan features, account limits, hidden assumptions of the old environment). Seen in: Lessons-Learned, What-Is-the-Cloud, Containers-and-Docker-Basics, Spacelift.
11. **Make machines disposable and rebuild the recovery path.** Seen in: What-Is-the-Cloud, Containers-and-Docker-Basics, What-Is-Infrastructure-as-Code, How-Money-Works-in-the-Cloud.
