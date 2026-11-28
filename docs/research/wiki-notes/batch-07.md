# Notes: batch 07

### Wazuh-SIEM-and-Data-Pipelines
Follows one log line from a host to an alert (agent, decoder, rules, index, dashboard) and shows with two toy scripts how the pipeline fails with no error: unparsed lines, a threshold one event short, a wrong clock. Draft rules are openly marked as never loaded into a real server.
- A pipeline that parses nothing looks the same as one with nothing to report. Count what you could not process and alert on that ratio; exit code 0 is not health.
- For each stage of a data flow, name the one signal that says it stopped. A stage with no such signal is a blind spot, and the "gone quiet" alert comes before the "attack" alert.
- Test rules at the exact boundary (four must stay silent, five must fire) and against negative and drifted input, not only the happy case.
- Keep "no alert" and "never arrived" as separate debugging questions with separate evidence. Compare counts at source and destination.
- Say what a toy or simulation does not prove (different regex dialect, different time source), so passing it is not mistaken for passing the real system.

### Detecting-and-Managing-Tor-I2P-and-VPN-on-a-Network-the-Defenders-View
What a network defender can and cannot see of Tor, I2P and VPNs, with list-matching shapes for several tools, a scored synthetic exercise and a policy and incident-response view.
- A match is a lead, not proof. Check list freshness, port, direction and list type; identify the host rather than the person; write "the log shows" and nothing more.
- Measure a detection against known ground truth and report false positives and misses separately. Each added check removes one kind of false positive and none removes the misses.
- External data ages. Record its version and last-seen date and treat a stale list as a source of wrong answers.
- Choose the vantage point deliberately and state what each cannot see, so coverage is not overstated.
- Blocking is a decision about people. Start by watching, write down the trade-off, who approved it and when it is reviewed, and allow-list your own systems before any alert goes live.

### Cloud-Telemetry-What-and-Why
Defines log, metric, trace and alert, separates team functions from tools, and argues that shipping telemetry off a host is a security decision with its own costs.
- Collecting data and having someone find out are different things. An alert needs a rule, a recipient and an action.
- Evidence kept only on the machine that can be compromised lasts only as long as that machine.
- Every new visibility path is a new route and a new exposure. List its costs (root code, secrets, memory, bandwidth, silence) and accept each on purpose.
- Label estimates as estimates and measure on one host before rolling out.
- Know what "normal" looks like before alerting on "abnormal".

### Multiple-Sites-and-Identity
How one codebase serves many sites through settings, why an immutable resource name must be separate from a changeable telemetry name, and what breaks at two sites (collisions, cardinality, cost gate blind spots).
- Never let one value serve both as infrastructure identity and as display label. State for each setting whether it can change on a live system and what a change would destroy.
- Adding another instance should be new data, not new code. A code change means something hard-coded belongs in a setting, and the existing deployment's plan should stay unchanged.
- Think about growth in label or key cardinality up front and restrict free-form values with validation.
- Ask what each guardrail cannot see (a cost gate that checks directories, not deployed instances; undeclared stacks) and write the manual control that covers it.
- "Not documented" is not "no limit". Check the real limit before applying and do not assume a number.

### Telemetry-Crosses-the-Trust-Boundary
Designs metric pull and log push across a cloud to home boundary with one-port resources, a default-deny firewall, a short-lived bootstrap secret and an explicit list of residual risks.
- Limiting host and port is not read-only access. Ask what the whole service on that port allows (methods, admin and write endpoints) and prefer no inbound path at all.
- Prove a boundary with negative tests that must fail, plus one positive test showing needed traffic still works; record date, tester and rule version and rerun after changes.
- Secrets leak through state, user data, metadata, backups and disks. List every holder and how long, even with a secret manager.
- For each new threat write position, control and residual risk, and what happens if the control fails.
- Say which kind of proof a test gives: mocked plan, static source check, or real run.

### Reading-a-Dashboard-as-an-Operator
How dashboards hide failures through averages, sums and empty panels, and why an expected-target inventory is needed to detect a silent site.
- For every panel or check ask what it would look like if the answer were bad. If bad looks like good, it can lie.
- Absence cannot be detected from the data alone. Compare what is there with a list of what should be there, written down earlier.
- Do not average or sum away the single failing member; show per instance or worst case.
- Test alert rules with fixtures for each failure shape, including the surprising ones (series present but all failing).
- Write the limitation of the fix too: the inventory is only as current as its last generation, and removing an item silences it.

### Grafana-Basics-From-a-Blank-Page
Walks from data source to panel, alert and contact point, stressing a read-only database account, secrets from a store, what a connection test proves, and config kept as files.
- Make the account's own permissions the limit, because the UI does not validate queries. Network narrowness is not permission.
- Know what a green check proves. A passing connection test says nothing about privileges, TLS strictness or whether real queries work.
- Decide on purpose what "no data" and "error" mean for an alert; a wrong default reports that all is well.
- A panel earns its place only if it changes a decision (page, wait, roll back); otherwise delete it or make it an alert.
- Keep dashboards and rules as reviewed files and block hand edits that would be silently lost; encrypted is not the same as encrypted to the right server.

### Grafana-Dashboards
Describes three shipped dashboards, their variables and panels, and gives a long, precise list of what was and was not verified against synthetic data.
- State verification level per artifact: structure checked, rendered with fake data, never run against the real system.
- Say what a passing test proves and what it does not, especially when the test uses your own evaluator and your own assumed field names (the fixture follows the same assumptions as the code).
- Build test data so the filter under test has to do the work (otherwise another filter can hide a broken one), and check that removing the clause makes the test fail.
- Detect "answers but exports almost nothing", not only up or down.
- Keep environment details (addresses, data source ids) out of shared artifacts and enforce that with a test.

### Lab-Demo-Monitoring-Stack
A free synthetic multi-site monitoring lab where the learner can silence a site on command and watch the alert and dashboard react.
- Build a cheap local model with a switch that injects the failure, so detection is watched working before it is needed.
- Predict the result before running, then compare. The gap is the lesson.
- Reuse the real shipped artifacts in the lab instead of copies, so the lab tests what you would deploy.
- Break the rule on purpose and confirm a specific test fails; tests can also reveal behavior the design text missed.
- Pin versions, bind to localhost, generate passwords at run time and give a teardown.

### Build-Your-Own-Mini-SOC
Staged, budget-bound plan for a small cloud monitoring and security stack, with cost tables, honest limits of alert forwarding and a measurement list.
- Deliver in stages that each stand alone, starting with the free one that teaches the most.
- Put the cost arithmetic beside each option, say which combinations do not fit the ceiling, and name what is metered and outside the gate.
- Write down the losses of a design (raw events do not forward, duplicates, dropped UDP) and reproduce them deliberately.
- Turn each guess into a named measurement with a method.
- Plan teardown (keys, services, backups, billing check) as part of the build.

### DFIR-Toolkits-and-Live-Triage-SIFT-Velociraptor-KAPE-and-the-Incident-Response-Workflow
Surveys forensic tools, contrasts live triage with dead-box imaging, lays out an incident workflow and gives a triage script exercise, with a list of what failed when run.
- Looking changes the system. Collect most volatile first, write down every command, and decide where evidence goes before collecting.
- Containment is a judgment between preserving evidence and stopping harm; decide who may make it during preparation.
- A tool's output is a lead until you know what it read. An empty-input hash means "could not read", not "clean".
- Check licenses and maintenance on the owner's page; free is not open source, and old copies carry old holes.
- Report what failed in your own run (missing command, unexpected volume, permission gaps) instead of presenting a clean story.

### Stage-2-Home-Side-Runbook
Operator runbook for the home side: VLAN, default-deny firewall, recorded negative tests, headless client, target file, inventory alerts and rollback.
- Order the work so the boundary and its recorded tests come before anything starts sending.
- Define "done" as evidence you hold (filled test table, loaded config, passing fixtures), not as steps performed.
- Pre-fill results as "not run yet" so unverified rows cannot pass for verified.
- Check that the control you think is blocking is the one blocking (read the deny log).
- Use two layers and say what each cannot do; include rollback steps and keep real values out of the repository.

### Open-Firmware-and-Trustworthy-Hardware-coreboot-Heads-Nitrokey-and-Vendors-That-Ship-the-Intel-ME-Disabled
Explains firmware, TPM, Secure Boot and measured boot, then reads four vendors' claims about disabling the management engine word by word.
- Read claims precisely. "Disabled" may mean absent, neutralized, soft or flag disabled; ask the method, the models, whether it is a default, and who can undo it.
- For each security mechanism write what it does not prove (detects versus prevents; signed is not trustworthy; measured is not reviewed).
- When a claim cannot be verified, leave it out or mark it, and separate vendor statements from observations.
- Verify state on the actual machine with read-only checks, and parse raw values correctly instead of trusting a label.
- Spend effort according to the threat model; ordinary hygiene often beats exotic hardware, and avoid irreversible actions without a recovery path.

### Digital-Forensics-Foundations-Evidence-Handling-Chain-of-Custody-and-Order-of-Volatility
Basics of evidence handling: order of volatility, bit-for-bit imaging, hash checks and chain of custody, with a small hash and tamper exercise.
- Preserve before you fix. Rebooting or wiping to recover can destroy the answer to "what happened".
- Never work on the original; verify the copy (hash source, hash copy, re-hash source).
- Know exactly what a check proves: a matching hash shows identity at that moment, not that the source was untouched or the conclusion right.
- A checksum stored where the same party can edit both protects nothing.
- Record who, what, when, tool version and errors; deviating from a procedure is acceptable only if documented.

### Network-Log-and-Timeline-Forensics-Packet-Captures-Logs-and-Plaso
Treats captures and logs as evidence, ranks log sources by trust, shows time zone and clock skew errors, builds a timeline and writes a four-line finding.
- Separate observed, inferred and not shown. An address is not a person.
- Name the clock and zone behind every timestamp, convert to UTC, keep the original line, and measure skew with an event two sources both saw.
- A gap says writing stopped, not why. Ask other sources what happened during it.
- Rank sources by who could have altered them; ship logs off the box.
- Absence at one observation point is not absence elsewhere. A copy's timestamps describe the copy.

### Cryptography-Fundamentals-Symmetric-Asymmetric-Hashing-Certificates-and-Keys
What encryption does and does not give, how key exchange, MACs, signatures and certificates work, where the project uses each or nothing, key custody, current standards and runnable experiments.
- Ask of any "it's encrypted": against whom, in which state, and who holds the key. Encryption is not integrity, authenticity or availability.
- Use well-reviewed libraries at their defaults; never roll your own, reuse a nonce, use a password as a key or disable certificate verification.
- Trust the exit status, not the output a tool printed before its check finished.
- Audit your own system in a table with file evidence, and write "None" where a control is missing instead of leaving it blank.
- Make demo output deterministic (stable labels instead of version-dependent text), and plan key custody, rotation, recovery tests and an algorithm inventory.

### Privacy-Security-and-Anonymity-Three-Different-Things-and-Why-There-Is-No-Silver-Bullet
Separates who can see in, who can get in and who can tell it is you, scores six tools against the three and shows that behavior identifies people whatever the network path.
- Name the adversary and the asset before choosing a tool; the same tool is strong against one and useless against another.
- Split a fuzzy requirement into distinct questions and make a matrix of what each solution covers; no single row is full.
- Collect and hand out less; data never given cannot leak or be correlated.
- Small harmless facts combine into identification, so judge data in combination.
- Weigh likelihood separately from capability, and accept how much effort is worth it; revisit when things change.

### Privacy-vs-Security-Blinds-and-Locks-Physical-Security-and-Monero
Blinds versus locks: where privacy and security overlap and pull apart, with a cryptocurrency example, privacy law principles, physical controls and a desk audit.
- A system can be fully secure and not private, or the reverse; review both.
- Security controls such as logs and cameras create personal data. Limit what they hold, how long and who reads it.
- A product's headline feature does not remove the user's other duties (key custody, trusted servers, device and software integrity).
- Physical access, disposal and people are part of the system; excluding them should be an explicit choice.
- Physical or technical barriers only delay; pair them with detection and response, and test only what you own or have written permission for.

### Tor-I2P-and-the-Darknet-Without-the-Myths
Calm explanation of Tor, I2P, privacy operating systems and a node example, including a careful test of the claim that government funding implies a backdoor.
- Take a popular claim apart: say which premise is true, then test the step to the conclusion separately.
- Mark evidence quality per statement (project's own claim, secondary source, allegation, personal statement) and admit that a negative cannot be proven.
- Pick a tool for the situation and say when it is the wrong one.
- Record documented failures with dates to see where systems really break (often the surrounding software, not the core design).
- Ask for a source you can open before believing a frightening claim.

### How-a-VPN-Works-Tunnels-What-It-Hides-What-It-Does-Not-and-What-an-Audit-Proves
What a VPN does to a packet, who sees what, leaks and fail-open behavior, and how to read audit reports and "no logs" claims, with two local exercises.
- Draw the data path and list per party what it can see; a protection often only moves trust to someone else.
- Ask what happens when the control drops. Check for fail-open and bypass paths (IPv6, DNS, routes injected by others).
- Read an audit or review for date, scope, what was excluded and what it actually tested; do not carry its verdict beyond that.
- State the threat model and what is out of scope before describing the mechanism.
- Verify behavior yourself with a baseline first, then the protected case, and model the idea cheaply when the real system is not available.

## Batch lessons

1. **Silence is not health.** Design so that missing data, a dead collector or an unparsed input is visible; compare against an expected list and decide what "no data" means. Slugs: Wazuh-SIEM-and-Data-Pipelines, Cloud-Telemetry-What-and-Why, Multiple-Sites-and-Identity, Reading-a-Dashboard-as-an-Operator, Grafana-Basics-From-a-Blank-Page, Grafana-Dashboards, Lab-Demo-Monitoring-Stack, Network-Log-and-Timeline-Forensics-Packet-Captures-Logs-and-Plaso.
2. **Say exactly what was verified.** Separate run, read, estimated and unverified; mark it per claim; record what failed. Slugs: all 20, most strongly Grafana-Dashboards, Wazuh-SIEM-and-Data-Pipelines, Open-Firmware-and-Trustworthy-Hardware-coreboot-Heads-Nitrokey-and-Vendors-That-Ship-the-Intel-ME-Disabled, DFIR-Toolkits-and-Live-Triage-SIFT-Velociraptor-KAPE-and-the-Incident-Response-Workflow, How-a-VPN-Works-Tunnels-What-It-Hides-What-It-Does-Not-and-What-an-Audit-Proves.
3. **Know what a passing check proves and what it does not** (test, hash, connection test, audit, certificate, mocked suite). Slugs: Grafana-Basics-From-a-Blank-Page, Grafana-Dashboards, Telemetry-Crosses-the-Trust-Boundary, Digital-Forensics-Foundations-Evidence-Handling-Chain-of-Custody-and-Order-of-Volatility, Cryptography-Fundamentals-Symmetric-Asymmetric-Hashing-Certificates-and-Keys, How-a-VPN-Works-Tunnels-What-It-Hides-What-It-Does-Not-and-What-an-Audit-Proves, Open-Firmware-and-Trustworthy-Hardware-coreboot-Heads-Nitrokey-and-Vendors-That-Ship-the-Intel-ME-Disabled.
4. **Prove the guard bites.** Write negative and boundary tests, inject the failure, remove the clause and watch the test fail, include one positive control. Slugs: Wazuh-SIEM-and-Data-Pipelines, Telemetry-Crosses-the-Trust-Boundary, Reading-a-Dashboard-as-an-Operator, Grafana-Dashboards, Lab-Demo-Monitoring-Stack, Stage-2-Home-Side-Runbook, Cryptography-Fundamentals-Symmetric-Asymmetric-Hashing-Certificates-and-Keys, Detecting-and-Managing-Tor-I2P-and-VPN-on-a-Network-the-Defenders-View.
5. **Predict, then run, then compare, then undo.** Slugs: Wazuh-SIEM-and-Data-Pipelines, Cloud-Telemetry-What-and-Why, Multiple-Sites-and-Identity, Reading-a-Dashboard-as-an-Operator, Lab-Demo-Monitoring-Stack, Grafana-Basics-From-a-Blank-Page, Cryptography-Fundamentals-Symmetric-Asymmetric-Hashing-Certificates-and-Keys, How-a-VPN-Works-Tunnels-What-It-Hides-What-It-Does-Not-and-What-an-Audit-Proves.
6. **Threat model and limits first.** Name adversary, asset, what is out of scope and what the control cannot do; a control often moves trust rather than removing it. Slugs: Detecting-and-Managing-Tor-I2P-and-VPN-on-a-Network-the-Defenders-View, Telemetry-Crosses-the-Trust-Boundary, Privacy-Security-and-Anonymity-Three-Different-Things-and-Why-There-Is-No-Silver-Bullet, Privacy-vs-Security-Blinds-and-Locks-Physical-Security-and-Monero, Tor-I2P-and-the-Darknet-Without-the-Myths, How-a-VPN-Works-Tunnels-What-It-Hides-What-It-Does-Not-and-What-an-Audit-Proves.
7. **Least privilege and least data.** Narrow access, read-only accounts, one key per purpose, secrets away from files, collect and keep less. Slugs: Telemetry-Crosses-the-Trust-Boundary, Grafana-Basics-From-a-Blank-Page, Stage-2-Home-Side-Runbook, Cryptography-Fundamentals-Symmetric-Asymmetric-Hashing-Certificates-and-Keys, Privacy-vs-Security-Blinds-and-Locks-Physical-Security-and-Monero, Privacy-Security-and-Anonymity-Three-Different-Things-and-Why-There-Is-No-Silver-Bullet.
8. **Observation is not inference.** A match, log line or hash is a lead; separate seen, inferred and not shown. Slugs: Detecting-and-Managing-Tor-I2P-and-VPN-on-a-Network-the-Defenders-View, DFIR-Toolkits-and-Live-Triage-SIFT-Velociraptor-KAPE-and-the-Incident-Response-Workflow, Digital-Forensics-Foundations-Evidence-Handling-Chain-of-Custody-and-Order-of-Volatility, Network-Log-and-Timeline-Forensics-Packet-Captures-Logs-and-Plaso.
9. **Count the cost and plan the exit.** State money, memory and exposure, measure estimates, and write teardown or rollback. Slugs: Cloud-Telemetry-What-and-Why, Multiple-Sites-and-Identity, Build-Your-Own-Mini-SOC, Lab-Demo-Monitoring-Stack, Stage-2-Home-Side-Runbook, Wazuh-SIEM-and-Data-Pipelines.
