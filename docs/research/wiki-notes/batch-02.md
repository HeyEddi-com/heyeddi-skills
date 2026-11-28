# Batch 02 notes

### Git-From-Zero
A first walkthrough of git and GitHub (account, 2FA, fork, clone, branch, commit, push, PR) by GUI or command line, plus recovery from five common mistakes. Each command comes with the output you should expect.

- Give every step an expected result, so the reader can tell success from silent failure.
- Run a read-only check (status) before any fix, and offer an abort or rescue path before a destructive one.
- Before a destructive command, preserve the work first (new branch), state the exact precondition that makes it safe, and warn what it discards.
- Name the target explicitly when a default could send work somewhere public or shared (PR base repository).
- Practice in a throwaway copy, and remember it may still be public.

### Terminal-and-Your-First-Script
Shell basics (paths, pipes, PATH, exit codes, quoting) and a read-only checkup script with strict mode, linting and version control. It stresses how scripts hide failures.

- Read the gate's exit code, not its text. Pipes, `|| true`, `if` and `set +e` can swallow a failure, and every suppression needs a written reason.
- Exit 0 does not prove the thing works, and a check that silently does not run is worse than one that fails.
- Know the holes in your safety net: strict mode misses empty variables, so guard destructive paths explicitly and list what will be deleted first.
- Keep checking separate from changing. Report-only and dry-run come before any delete.
- Break your own script on purpose to see that the detection works, and make CI linters actually fail the build (some only print findings by default).

### Linux-for-Enterprise-Beginners
Distribution families, packages, services, permissions, SSH, firewalls, mandatory access control, logs and lifecycle dates, with a container lab.

- Identify what you are on (OS, version) before applying advice, since copied snippets are family-specific.
- Switching off a protection is a diagnosis step, not a fix. Read the denial and fix the one thing.
- Treat end-of-support dates as security dates: each machine needs a release, a date and an owner for the move.
- Validate config before restarting a service that could lock you out, and allow your own access before enabling a firewall.
- State how far each source can be trusted (vendor, aggregator, estimate) and which one wins on conflict.

### First-Hour-on-a-New-System-Updates-and-Baseline
Argues for a fixed order on any new machine: update and automate updates, take a baseline, harden, then install workloads. Covers staggering, rollback, what OS updates miss and the update channel as attack surface.

- Order matters: record a known-good "before" so later changes can be seen and attributed.
- Never change all redundant instances at once. Use canary, rings and soak time, and respect dependency order.
- "Installed" is not "on", and "package updated" is not "process restarted". Verify the effective state.
- For any automation, list what it does not cover (containers, third-party repos, source builds, firmware).
- Weigh both risks in writing (update breaks it vs flaw stays open); the answer to breakage is snapshot, pin with owner and expiry, tested rollback and post-change monitoring. Pin important rules with a test so docs and code cannot drift apart.

### Patch-Management-and-Automatic-Security-Updates
How unattended upgrades work, where results are logged, which conditions deserve alerts, reboot policy, testing, rollback and limits.

- Alert on absence, not only events: a job that stops running produces no error, so check the age of the last success from outside the host.
- Verify the merged effective configuration. A second config file appended to a list instead of replacing it, found only by measuring.
- Test the alert path end to end, route by urgency so people do not mute it, and ask who notices if the notifier stops.
- Judge success by whether the service came back, not by the tool's "done" message.
- Say plainly what was run, what was only read, what was estimated, and which fixtures were invented.

### Red-and-Blue-Yin-and-Yang-and-Your-Lab-OS
Attack and defense as one discipline, written authorization before testing, seeing one finding inside a whole system, and building an isolated lab.

- Think from both sides: design defenses from attacker steps, and know what traces your own actions leave.
- Rate a finding in system context (patching, segmentation, identity, logging, backup, rollout), not in isolation.
- Write scope, authorization and stop conditions before acting on anything.
- Verify isolation with a concrete check after every change, and say what the check does not prove.
- Quote what a source says and separately mark what it does not say or what is your own judgment.

### Virtual-Machines-Hypervisors-Desktop-and-Datacenter-Options
Hypervisor types, desktop and server options, a dated account of VMware licensing changes, networking modes, snapshots, sizing and a first VM.

- Do not argue labels. Decide on cost, supported hosts and guests, and maintenance.
- Vendor terms change, so date the facts and re-check before relying on an old tutorial. Dependence on a vendor license is a migration risk.
- Pick the most restrictive connectivity that still does the job, per use case.
- A snapshot is not a backup, and it must be taken before the risky step.
- Verify downloads, and know the limit of the check (checksum from the same page as the file). Report exactly what a partial test proved (options parse, not that it boots).

### Device-Firmware-Security-Intel-ME-AMD-PSP-MINIX-and-Kernel-Design
What the management processors in PCs are, kernel design tradeoffs, and a careful separation of documented vulnerabilities from the backdoor claim, with read-only inspection.

- Separate evidence, claims and inference. Say what you looked for and did not find.
- Argue risk from capability and inspectability; you do not need to prove intent.
- A good guarantee has a stated scope and assumptions (a proof is not "secure" in general).
- An architecture pattern does not make a system safe by itself, and presence of a feature does not show it is enabled.
- Do not attempt irreversible changes without a recovery plan and spare hardware, and expect lost features.

### Virtual-Machines-Containers-and-Cloud-Service-Models
VM vs container isolation, why images do not patch themselves, service models and shared responsibility, zones, sizes, rebuild checklist and container hardening.

- For every layer, name who patches it. Patching the host does nothing for images.
- Start least privileged (non-root, read-only, no capabilities, limits, loopback only) and add back only what is proven necessary.
- Redundancy counts only with replicated state, health-aware routing and a tested failover; shared dependencies fail together.
- Be able to rebuild a lost machine from things stored elsewhere, including a restore you have tried.
- Read the cost and the teardown before creating a resource, then prove it is gone.

### Kubernetes-for-Beginners-What-It-Adds-Over-Docker-and-Compose
What Kubernetes adds (desired-state reconciliation across hosts), what managed offerings leave to you, and why one Compose host is right for this project for now.

- Choose the simpler tool with explicit conditions, and write down the triggers that would make you switch.
- Build now so the later move is cheap (config from environment, state off the host) without adopting the big system early.
- Change the declared source, not the running thing.
- Defaults can be weaker than the name suggests (a "Secret" is not encrypted by default).
- Count total cost: money, concepts to learn, upgrades and attack surface.

### Choosing-a-Container-Engine-Docker-Podman-Kubernetes-Portainer-Cockpit
Compares Docker and Podman (daemon, rootless, compose, systemd, GPU) and the exposure of two web management tools, with the maintainer's stated preference.

- Compare tools at the right layer, and decide from real constraints (privilege, compatibility, boot behavior, hardware, host count).
- Label personal preference as experience rather than benchmark, and say when you would choose the other.
- A convenience group, socket mount or admin UI can equal root. Trace who really holds control.
- "Compatible" or "supported" has limits: read which configurations are actually covered.
- Removing a component also removes what it did for you (restarts), so find the replacement.

### Self-Hosting-AI-Ollama-FrankenLLM-vLLM-and-the-GPU-Stack-PyTorch-CUDA-ROCm-and-Intel
Running models yourself: memory estimation, servers, the GPU software layers, vendor support limits, the lack of API authentication and rules for using AI assistants. Marked as unrun.

- Estimate capacity with a shown formula, then measure; the calculation is only a lead. When docs disagree on a default, read the running value and set it explicitly.
- Treat AI-supplied flags, versions and packages as leads: check the docs or `--help`, keep verified and inferred lists, never paste secrets, read scripts before running, change one thing at a time and ask what success and failure look like.
- Check what actually listens and who can reach it. A partial API key or loopback assumption is not protection, and you should name defects in your own documented layout.
- Check whether a dependency is maintained (archived or retired projects still appear in guides).
- Downloaded models and data are untrusted input; judge quality on your own task set, not vendor benchmarks.

### Windows-Active-Directory-and-macOS-in-the-Enterprise
Domains, Group Policy, Kerberos and NTLM, cloud identity, event logs, Mac device management and directory defense, with read-only exercises and a disposable lab.

- Learn a new environment by mapping its equivalents to what you know, using read-only commands first.
- Protect the control point: tier powerful accounts, avoid shared admin passwords and standing privilege.
- Detect both ways: periodic comparison with an approved list and live events, and know each method's blind spot (additions only).
- Ship logs off the machine, and for each alert name a benign false positive and the first responder action.
- Before relying on a preview flag such as a dry run, confirm that the specific command supports it. Hidden dependencies (DNS) can look like a different failure.

### Cron-Systemd-Timers-and-Init-Scripts-vs-Systemd
Cron syntax and limits, systemd timers, a translation table, which distributions ship cron, init design tradeoffs and a ordered troubleshooting checklist.

- Verify schedules and unit files with checking tools before they are due; similar names can mean different things (weekly).
- A scheduled job needs answers for environment, output, missed runs, overlap and dependencies.
- Troubleshoot in a fixed order from most likely cause: is it installed, enabled, triggered, then failing.
- Narrow a sweeping claim ("Linux dropped cron") to what the data shows, per system and date.
- State your preference with its reason and give the critics' case fairly; do not assume the platform has the tool.

## Batch lessons

1. Verify the effective state, not the intent or the success message (merged config, listening address, service back up, exit code, loaded size): Terminal-and-Your-First-Script, First-Hour-on-a-New-System-Updates-and-Baseline, Patch-Management-and-Automatic-Security-Updates, Self-Hosting-AI, Virtual-Machines-Containers-and-Cloud-Service-Models, Cron-Systemd-Timers.
2. Label confidence honestly: run, read, estimated, not verified, with dates and sources; never inflate a partial test: most pages carry some form; strongest in Patch-Management, Virtual-Machines-Hypervisors, Device-Firmware-Security, Self-Hosting-AI, Cron-Systemd-Timers, Linux-for-Enterprise-Beginners.
3. Silent failure and absence are the dangerous cases: swallowed exit codes, jobs that stop running, notify-only tools, missed runs: Terminal-and-Your-First-Script, Patch-Management, First-Hour, Cron-Systemd-Timers.
4. Make destructive or risky steps reversible: look first, snapshot or back up, state the undo and teardown, try the rollback once: Git-From-Zero, Terminal, First-Hour, Patch-Management, Virtual-Machines-Hypervisors, Virtual-Machines-Containers, Windows-Active-Directory, Cron-Systemd-Timers, Device-Firmware-Security.
5. Predict, do, check, undo, and break it on purpose to prove detection works: Terminal, Linux-for-Enterprise-Beginners, First-Hour, Patch-Management, Red-and-Blue, Kubernetes, Choosing-a-Container-Engine, Windows-Active-Directory, Cron-Systemd-Timers.
6. Default to least privilege and narrowest exposure, and know what grants root or reach: Linux, Red-and-Blue, Virtual-Machines-Hypervisors, Virtual-Machines-Containers, Choosing-a-Container-Engine, Self-Hosting-AI, Windows-Active-Directory.
7. State what a tool or protection does not cover, and who owns each remaining layer: First-Hour, Patch-Management, Virtual-Machines-Containers, Kubernetes, Self-Hosting-AI, Device-Firmware-Security.
8. Choose from real constraints and total cost, pick the simplest that fits, record switch triggers: Kubernetes, Choosing-a-Container-Engine, Virtual-Machines-Hypervisors, Self-Hosting-AI, Cron-Systemd-Timers.
9. Do not change everything at once: canary, stagger, one change then check: First-Hour, Patch-Management, Self-Hosting-AI.
10. Separate fact from opinion and claim, and present the counter case: Device-Firmware-Security, Red-and-Blue, Choosing-a-Container-Engine, Cron-Systemd-Timers.
