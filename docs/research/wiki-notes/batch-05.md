# Batch 05 notes

### WordPress-at-Scale-CDN-WAF-and-CI
Walks one server to a scaled web design (caches, CDN, WAF, load balancer, shared storage, tenant isolation, pipeline), with a local lab that reproduces the failures. It stresses that each layer is added for a named problem and brings a new one, and that the pipeline's permissions are the most dangerous thing in the design.

- Add a layer only when a specific problem shows up, and write down the new problem it creates (stale cache, replication lag, shared state) next to the one it solves.
- For any shared cache, treat "do not serve from it" and "do not store into it" as two separate rules, and keep a test that compares logged-in and anonymous responses after each deploy.
- Review a pipeline by what it can do, not what it is meant to do: untrusted code with secrets, unpinned actions, broad permissions, untrusted text in shell, one credential for every tenant.
- Test the recovery as well as the failure: a killed node came back at a new address and silently got no traffic until the balancer was fixed.
- Make deploys immutable releases with a pointer switch, build one artifact for staging and production, patch fleets in rings that stop on first failure, and give destroy order and cost per tier before building.

### Autoscaling-and-Elasticity-Scale-Out-Targets-Cooldowns-and-Cost-Caps
Explains autoscalers as a feedback loop (metric, target, min, max, policy), flapping, statelessness, health checks and billing risk. A short local simulation shows a scale-down window turning six size changes into two.

- Any automation that can spend money or create resources needs a hard maximum chosen from a budget, plus an alert when it sits at that maximum.
- In control loops, act fast on the way up and slowly on the way down, with tolerance, warmup and cooldown, and replay a fixed trace to see the behavior before running it live.
- Pick a signal that actually moves when you apply the remedy, or the loop never converges.
- A health check should exercise what a real request needs, but not so deeply that one slow dependency removes every copy at once.
- Say plainly when a system does not need the technique (a few low-traffic daemons), and keep only the cheap habits that would make it possible later.

### Threats-in-Plain-Words
Defines core security words with dated real cases, then teaches how to read a CVE record, what a severity score and an exploited-vulnerability list mean, and what compliance reports prove.

- Separate severity, likelihood and exposure: a score alone is not risk. Check whether it is being exploited, whether you run the affected version, and whether it is reachable.
- A name match from a list is only a pointer to where a human must read; "cannot tell" is a valid answer whose next step is to find out the version.
- Keep an inventory with versions and exposure, because you cannot patch or defend what you have not listed.
- Do not invent a middle mitigation (a firewall rule) unless a source says it works; follow the vendor advisory.
- Treat a certificate or audit as evidence about a stated scope and period, and ask for scope and exceptions.

### Security-Tools-Basics-Nmap-OpenVAS-Burp-Metasploit
Introduces scanning and testing tools from the defender's side, with a toy three-part system that is scanned, fixed in its build, and rescanned. Authorization and an isolated lab come first.

- Close a finding by changing the build and rerunning the exact same check from the same place, never by muting the tool or editing the ignore list.
- Before testing anything, prove where it listens and that you are authorized and in scope.
- Separate real fixes (segmentation, removing a debug page) from cosmetic ones (hiding a version banner).
- Every finding gets either a fix or a recorded decision (false positive, accepted, compensating control) with an owner and a review date.
- A clean scan only covers what the scanner could reach and had tests for; ask what it could not see.

### Memory-Forensics-Acquiring-RAM-and-Analyzing-It-with-Volatility-3
Shows how to capture a lab VM's memory from the hypervisor, build a matching symbol table and find a known process, file and listener. It is candid about smear, version drift and what was not run.

- Collect the most volatile evidence first; rebooting "to be safe" destroys what you need to diagnose.
- Observation changes the system, so record what you did, in what order, with which tool and version, and hash the result immediately.
- Do not trust a single view from inside a possibly broken system; compare two sources and prefer one from outside.
- Plant a known marker first, so you can tell a working analysis from an empty one.
- Build the debugging artifacts (symbols) at release time while they still exist, and pin tool versions.

### Email-Security-DNS-Gateways-and-API-Driven-Protection
Covers how mail travels, SPF, DKIM, DMARC, two models of mail security products, attack triage and why not to self-host mail, with a local evaluator lab.

- Roll out an enforcing control in stages: observe, find and fix legitimate users, soft enforce, then hard enforce, with reports read at each step.
- A control in front of a system is useless if the system still accepts direct traffic; lock the back door and test it by trying to bypass.
- Parsers that disagree are an attack surface (duplicate headers, stray carriage returns, repeated attributes); fail closed on ambiguous input and escape anything attacker-written before printing it.
- Before granting a third-party app standing access, read the permission list, restrict who can consent, and test how you would remove it.
- Learn a hard system by running it in a lab, but do not own in production what fails silently and depends on reputation you cannot control.

### Threat-Model-Exercise
Has the reader list assets, draw trust boundaries, fill a STRIDE table and work three what-if scenarios against the real repository, predicting before checking.

- Back every claim about a control with a file you opened; an empty "what stops it" cell is a finding, and a model made of beliefs is only a story.
- Trace where code actually runs relative to a gate: a human confirm after planning does not stop code that executed during planning.
- An allowlist or a script check that only guards honest code is not an isolation boundary; say what a compromised run could really reach.
- For a leaked secret, revoking the token is a half fix: rotate everything it could read and hunt for things the attacker may have created.
- Write down what the model does not cover, which controls live in vendor settings, and which risks are accepted.

### Threat-Dragon-Exercise
Draws the same pipeline as a data flow diagram with eight trust boundaries and per-element threats, and lists what was and was not verified about the tool.

- Label every arrow with the data that crosses it; "deploy" or "uses" hides the threat.
- For each boundary, name what holds it and where it can be verified; settings outside the repository cannot be proven by a diff.
- A model records beliefs and does not verify the system; a missing arrow produces no warning, so ask whose credential, which path, who writes.
- Keep diagrams and docs in step with tests (IDs, layout, no real identifiers), and check what is safe to commit.
- Mark claims as verified or not, with source and date.

### Threat-Frameworks-STRIDE-ATTACK-ATLAS
Compares design categories, an attacker technique catalog and an AI attack catalog on the same pipeline, including how AI agents with tools change the risk.

- Pick the framework by the question: design flaws, how it would be detected, or how an AI part can be abused.
- Naming a technique is not detecting it; for each threat say which log would show it and admit when none exists.
- A written rule to an agent is not a boundary; only what its credentials and machine cannot do counts, and secrets should not be in its environment.
- Judge an agent weakness by blast radius: the same prompt injection is minor without tools and serious with them.
- Pin versions of external reference data and test that cited IDs exist, since names and numbers move between releases.

### Disk-Forensics-with-Autopsy-and-The-Sleuth-Kit
Teaches imaging, hashing, listing and recovering deleted files with free tools, and writing a short finding with its limits.

- Hash first and work on a copy; say exactly what the hash proves and nothing more.
- Report what was observed, how, and the limit; do not turn "a file was deleted" into a claim about intent.
- Do not trust a silent empty result: a crash or empty listing may be the tool, so cross-check with a second method.
- Know that a distribution package may be old or a different product from the one the docs describe; check the installed version.
- Record which steps you actually ran and which come from documentation.

### Packet-Filters-Compared-iptables-nftables-ufw-pf
One firewall policy written four ways and tested with the same probe matrix in a throwaway network namespace, exposing differences such as an unfiltered IPv6 path.

- Write the expected answers as a small test matrix and rerun it after every change; test what should be blocked as well as allowed.
- Look for the path your rules do not cover (the second protocol, another interface, another tool rewriting rules).
- Apply configuration as one atomic, syntax-checked file kept in version control, knowing a valid but wrong rule still gets through.
- Before changing something you are connected through, keep a second way in or a timed rollback.
- When a result looks right, confirm the cause (a "blocked" result may come from a broken prerequisite or leftover limiter state, not your rule); keep personal tool preference apart from findings and fact-check it.

### IDS-and-IPS-Snort-and-Suricata
Explains detection versus prevention, sensor placement, rules and tuning, with offline exercises showing that some broken rules fail with no error at all. Ends with a threat model of the sensor.

- A monitor that is quiet looks like a healthy system: keep canary inputs that must trigger and run them after every change.
- Make partial load failures loud; a normal run exited 0 after dropping a bad rule.
- Know the expected answer from an independent tool before running the system under test.
- Every suppression or exception needs an owner, a reason, the narrowest scope and a review, because it is a permanent blind spot.
- Start new enforcement in report-only mode, decide fail-open or fail-closed on purpose, and treat auto-updated rules or feeds as a supply chain.

## Batch lessons

1. **Prove it works by making it fail.** Break the control on purpose, feed it a known-bad input, and check it fires; silence and exit 0 are not proof. (IDS-and-IPS-Snort-and-Suricata, Packet-Filters-Compared-iptables-nftables-ufw-pf, WordPress-at-Scale-CDN-WAF-and-CI, Email-Security-DNS-Gateways-and-API-Driven-Protection, Memory-Forensics-Acquiring-RAM-and-Analyzing-It-with-Volatility-3, Disk-Forensics-with-Autopsy-and-The-Sleuth-Kit)
2. **Predict first, then check.** Write the expected result before running, and treat the gap as the lesson. (Threat-Model-Exercise, Threat-Dragon-Exercise, Threat-Frameworks-STRIDE-ATTACK-ATLAS, Security-Tools-Basics-Nmap-OpenVAS-Burp-Metasploit, IDS-and-IPS-Snort-and-Suricata, Packet-Filters-Compared-iptables-nftables-ufw-pf, Autoscaling-and-Elasticity-Scale-Out-Targets-Cooldowns-and-Cost-Caps)
3. **Be honest about evidence.** Separate ran, read and estimated, with dates, versions and sources, and list what was not verified. (all 12 pages; strongest in Memory-Forensics-Acquiring-RAM-and-Analyzing-It-with-Volatility-3, Disk-Forensics-with-Autopsy-and-The-Sleuth-Kit, Threat-Dragon-Exercise, IDS-and-IPS-Snort-and-Suricata)
4. **State the limits and residual risk.** Say what the design, tool or model cannot see and what is accepted. (Threat-Model-Exercise, Threat-Dragon-Exercise, Threat-Frameworks-STRIDE-ATTACK-ATLAS, Email-Security-DNS-Gateways-and-API-Driven-Protection, Packet-Filters-Compared-iptables-nftables-ufw-pf, IDS-and-IPS-Snort-and-Suricata, Memory-Forensics-Acquiring-RAM-and-Analyzing-It-with-Volatility-3)
5. **Find the real boundary and the bypass.** Ask what gets around the control and what a compromised part could actually reach; written rules and in-script checks are not walls. (Threat-Model-Exercise, Threat-Frameworks-STRIDE-ATTACK-ATLAS, Email-Security-DNS-Gateways-and-API-Driven-Protection, WordPress-at-Scale-CDN-WAF-and-CI, Packet-Filters-Compared-iptables-nftables-ufw-pf, IDS-and-IPS-Snort-and-Suricata)
6. **Roll out risky changes in stages with a way back.** Observe before enforce, rings, rollback, atomic loads. (Email-Security-DNS-Gateways-and-API-Driven-Protection, IDS-and-IPS-Snort-and-Suricata, WordPress-at-Scale-CDN-WAF-and-CI, Packet-Filters-Compared-iptables-nftables-ufw-pf)
7. **Fix the cause and keep the record.** Change the build, retest the same way, and give every exception an owner, reason and review date. (Security-Tools-Basics-Nmap-OpenVAS-Burp-Metasploit, IDS-and-IPS-Snort-and-Suricata, Threats-in-Plain-Words, WordPress-at-Scale-CDN-WAF-and-CI)
8. **Cost, cap and teardown up front.** Price each piece, set a hard maximum, give build and destroy order, prove nothing is left, and say when not to build it. (WordPress-at-Scale-CDN-WAF-and-CI, Autoscaling-and-Elasticity-Scale-Out-Targets-Cooldowns-and-Cost-Caps, Email-Security-DNS-Gateways-and-API-Driven-Protection, Threat-Dragon-Exercise, IDS-and-IPS-Snort-and-Suricata)
