# Batch 04 notes

### Enterprise-Identity-SSO-SAML-OIDC
A beginner walkthrough of directories, identity providers, SAML, OAuth, OIDC, SCIM, roles, MFA and the joiner-mover-leaver cycle. It stresses exactly what an application must check in a signed assertion or token, and includes local fake-data labs and a claims register.

- Treat a signed token as untrusted until every check passes (signature, issuer, audience, time window, request binding), and let the application, not the token header, decide which algorithm is accepted.
- Do not write security-critical parsing or signature code yourself; use a maintained library, and know which checks it only performs when configured.
- Key records on a stable identifier, not on something that changes or gets reused such as an email address.
- Removing access means more than disabling the account: think about live sessions, tokens that still carry old groups, local accounts and machine keys, and give every non-human identity an owner and an end date.
- When picking a control, name what it does not stop (phishing-resistant sign-in does not protect a stolen session), and alert on privilege changes, not only on sign-ins.

### Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV
Explains the protocols inside a security key, PIN and backup habits, a published side-channel flaw in one vendor's firmware, and the trade between updatable and frozen firmware. Software-only exercises show what a software token cannot enforce.

- Do not conclude more than the evidence shows: a tool refusing to export a key is not proof the key cannot be extracted; look for the property that actually guarantees it.
- A model of a system (software token, mock) reproduces the interface but not the protection, so find out which guarantees the stand-in lacks.
- Weigh design choices by how they fail (scales and hides versus loud, local and slow) and state the cost of the side you pick.
- Plan the recovery path before the lockout (second key, tested recovery codes, a list of where each is registered); the weakest recovery method sets the real strength.
- Read an advisory for its preconditions, affected versions and what it does not break, then decide against your own threat model.

### Data-Formats-JSON-YAML-HCL
Covers JSON, YAML, HCL and friends, their classic traps (type guessing, duplicate keys, indentation that parses but changes meaning), safe loading and conversion. Exercises make each failure happen.

- Valid is not correct: check shape and types with a schema or a small checker, not only syntax.
- The dangerous mistake is the one that does not error (a block shifted to another level, a second duplicate key winning); inspect the parsed structure, and do not ignore whitespace when reviewing YAML.
- Load strictly: safe loader, refuse duplicates and aliases in sensitive files, cap size and depth, and treat outside files as data, never instructions.
- Keep one source of truth that every consumer reads, so two things cannot drift apart.
- Parsers disagree on edge cases, so validate locally with the same tool CI uses.

### OpenTofu-From-Zero
A hands-on introduction to init, plan, apply, destroy, plan symbols, state, count versus for_each, modules and mock tests. The centerpiece is a loop that builds, previews the destroy, destroys and proves the state is empty.

- "It said it succeeded" is a claim; verify with an independent count or listing, and have scripts stop when the check fails.
- Preview destructive actions and read every affected item, not just the summary totals, because a replacement hides a delete.
- Give things stable identities (keys, not positions) when the set can change.
- Hiding a value on screen is not protecting it; ask where it is actually stored.
- A narrowed run (targeting one piece) is incomplete evidence; test that guard rails fire by feeding them bad input.

### Plans-State-Drift-and-Recovery
Teaches plan review, the discard rule, state, locking, drift, safe record changes (moved, import, removed) and four reproducible disasters with recoveries. Ends with a break-and-recover drill.

- Review a plan against the intent: every touched item must be explainable by the change, every delete needs a named reason, and when unsure, discard (re-running is cheap, a wrong apply is not).
- Apply exactly what was reviewed (saved plan), and refuse stale approvals.
- During recovery, diagnose first, restore the source of truth, re-read what is really wrong, and only then change anything; take a deliberate backup before risky work.
- For unexplained drift, do not auto-revert or auto-accept; find out who and why, then make code and reality agree.
- Know what each safeguard and detector does not cover (a delete guard vanishes with its block; a clean plan says nothing about unmanaged objects).

### Ansible-Configuration-Management-Versus-Provisioning
Contrasts creating resources with keeping machines configured, and covers inventory, modules, idempotence, check mode, roles, vault and pull mode. Includes honest limits and a run-twice lab.

- Write operations that describe the end state and prove idempotence by running twice; a second run that still changes things signals a bug or two rules fighting.
- A dry run is a prediction with blind spots; know when it is trustworthy and still roll out in small batches.
- Removing the declaration does not remove the effect; cleanup has to be explicit.
- Whatever holds keys to everything is the most valuable target; protect it, and read third-party automation before running it with your privileges.
- Correction only happens when something runs, so do not claim "cannot drift".

### Native-IaC-vs-Open-Standards-CloudFormation-ARM-Bicep-and-OpenTofu
Compares vendor infrastructure tools with open ones, lays out lock-in as a list of things to rewrite, and notes that a portable tool does not make portable code. It also says when native is the better pick.

- Make trade-offs concrete: list what would have to be redone to leave, instead of repeating a slogan.
- State a recommendation and then honestly list the cases where the other option wins.
- Separate what transfers (method, review habits) from what does not (resource definitions).
- Treat a single-vendor dependency's end of life as a real risk when choosing.
- When two sources disagree, report both rather than picking one silently; a lint pass is not a security review.

### Spacelift-From-Zero
A hosted-runner lesson: stacks, proposed versus tracked runs, confirmation, secrets, policies, dependencies, and destroy-before-delete teardown with a checklist. The console path was written from documentation and not run.

- Grant integrations the narrowest access that works (one repository, not all).
- Tear down in dependency order, destroy resources before deleting the thing that tracks them, and tick each checklist box after looking, not from memory.
- Untrusted code (a pull request) must never run next to secrets; understand why a check is red before treating it as noise.
- A green preview does not prove the apply will work.
- Layer controls and know how each can be bypassed (direct push, console settings, detached policy); the checker should not be the same party as the changer.

### Build-and-Destroy-Stack-Per-Service
How to split infrastructure into one stack per service, pass values between stacks, order build and destroy, tag, budget and prove nothing is left. A local five-stack lab shows the wrong-order failure and an untagged leftover.

- Split along ownership, change rate and blast radius, and state the cost of splitting; do not split everything.
- Share identifiers, never secrets, across boundaries, and keep the published interface small and pinned by a test.
- A checker must be seen to fail; it must fail closed (an unreadable result is not zero) and use two independent views.
- A tag search only proves tagged things are gone; inventory everything and explain each line.
- Write teardown and compute a hard worst-case budget (including forgetting) before creating anything; alerts are not caps.

### Environments-and-Promotion-Dev-Staging-Production
Explains local, staging and production, why each needs its own state, secrets, project and cost ceiling, how changes are promoted from one trunk, and what mocks cannot prove. It is candid that staging is only planned.

- Environments are separate only if a mistake in one cannot reach another; a variable named "environment" separates nothing.
- Say plainly what is built, planned and not designed; do not let a design doc read as reality.
- Know what each test level can prove: mocks check your logic, only the real service reveals limits, permissions and name clashes.
- Every extra deploy branch is another path to secrets that needs the same protection; prefer one trunk with differences in configuration unless there is a real need.
- A test that checks what is requested does not prove what is permitted; verify access boundaries by trying the forbidden thing.

### LAMP-and-LEMP-From-Zero
Builds Apache and Nginx stacks side by side, covers PHP and database support, a runtime advisory, trust boundaries, cost, and a STRIDE model. It labels precisely what was run and what was only read.

- Trace one request and mark each trust boundary; expose only what must be public.
- Do not over-read measurements: say what was measured, what confounds it, and change one variable to isolate a cause.
- Protections can silently stop working after a migration or config change, so test on the system you actually run that the forbidden thing is still refused.
- Know every version you run, including the runtime under the application, and whether it still gets fixes.
- Make comparisons and external claims traceable ("this source says, as of this date; this part is unknown"), and install the firewall before the machine.

### WordPress-and-PHP-Security-WAF-and-Static-Sites
Covers where the risk sits (runtime, application, plugins), a critical PHP advisory, memory safety, hardening, WAF tuning, static sites and a threat model. Sources and unread items are listed.

- Locate a flaw in the right layer, because that decides who fixes it and how; the cheapest hardening is removing code you do not use.
- Defense layers (WAF, hiding versions, disabled functions) reduce damage but never replace the patch; take advice from the specific advisory, which can contradict general habits.
- Introduce blocking controls in detect-only mode, fix false positives with the narrowest exception, then re-run both the legitimate case and the attack probe to confirm.
- Verify a hardening change took effect (before and after) and test that features still work.
- Removing a component moves risk (to the build chain and repository access) rather than deleting it; say where it moved and what residual risk remains.

### Static-vs-Dynamic-Sites-Hugo-and-WordPress-and-Recon
How to tell a static site from WordPress from outside, what each leaks, with a loopback stand-in lab, plus a short opinion section on careers. The author is explicit that the stand-ins are not the real products.

- One signal is evidence, not proof; state a conclusion as "very likely" with the independent signs that agree.
- Hiding a symptom does not fix the flaw.
- Be explicit about what a stand-in does and does not demonstrate.
- Test only what you own or have written permission to test, and check what a tool actually sends.
- Public work with clear write-ups is a good way to show how you think (the author's opinion).

## Batch lessons

1. **Prove it, do not trust the success message.** Independent checks, parsed output, before and after comparisons, empty-state counts. Pages: OpenTofu-From-Zero, Build-and-Destroy-Stack-Per-Service, Spacelift-From-Zero, Data-Formats-JSON-YAML-HCL, WordPress-and-PHP-Security-WAF-and-Static-Sites, Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV.
2. **Break it on purpose, and make sure the check can fail.** Predict, do, check, undo; feed guard rails bad input; checkers fail closed. Pages: Enterprise-Identity-SSO-SAML-OIDC, Data-Formats-JSON-YAML-HCL, OpenTofu-From-Zero, Plans-State-Drift-and-Recovery, Ansible-Configuration-Management-Versus-Provisioning, Build-and-Destroy-Stack-Per-Service, LAMP-and-LEMP-From-Zero.
3. **Silent failures are the worst ones.** Valid but wrong files, index shifts, ignored per-folder rules, duplicate keys, stale access, forgotten resources. Pages: Data-Formats-JSON-YAML-HCL, Plans-State-Drift-and-Recovery, LAMP-and-LEMP-From-Zero, Build-and-Destroy-Stack-Per-Service, Enterprise-Identity-SSO-SAML-OIDC.
4. **Label what was verified.** Run, read, estimated, not verified, planned, not designed, with dates and a claims register. Pages: all 13 (strongest in Environments-and-Promotion-Dev-Staging-Production, WordPress-and-PHP-Security-WAF-and-Static-Sites, Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV).
5. **Say what a control or tool does not do.** Mocks, check mode, delete guards, WAFs, tags, alerts, sensitive flags, lint passes. Pages: Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV, Plans-State-Drift-and-Recovery, Ansible-Configuration-Management-Versus-Provisioning, Environments-and-Promotion-Dev-Staging-Production, Build-and-Destroy-Stack-Per-Service, WordPress-and-PHP-Security-WAF-and-Static-Sites, Static-vs-Dynamic-Sites-Hugo-and-WordPress-and-Recon.
6. **Preview and review destructive changes; apply exactly what was approved; when unsure, stop.** Pages: OpenTofu-From-Zero, Plans-State-Drift-and-Recovery, Ansible-Configuration-Management-Versus-Provisioning, Spacelift-From-Zero.
7. **Plan the way back first.** Teardown, recovery, backups and second keys are written before building. Pages: Spacelift-From-Zero, Build-and-Destroy-Stack-Per-Service, Plans-State-Drift-and-Recovery, Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV, LAMP-and-LEMP-From-Zero.
8. **Limit blast radius and privilege.** Separate stacks, secrets, users and tokens; protect whatever holds the keys; state files and runners are as sensitive as production. Pages: Enterprise-Identity-SSO-SAML-OIDC, Ansible-Configuration-Management-Versus-Provisioning, Spacelift-From-Zero, Build-and-Destroy-Stack-Per-Service, Environments-and-Promotion-Dev-Staging-Production, LAMP-and-LEMP-From-Zero, WordPress-and-PHP-Security-WAF-and-Static-Sites.
9. **Present decisions as trade-offs with residual risk and costs**, including when the other choice is right. Pages: Native-IaC-vs-Open-Standards-CloudFormation-ARM-Bicep-and-OpenTofu, Hardware-Security-Keys-YubiKey-Nitrokey-Smart-Cards-and-PIV, Build-and-Destroy-Stack-Per-Service, Environments-and-Promotion-Dev-Staging-Production, WordPress-and-PHP-Security-WAF-and-Static-Sites, Static-vs-Dynamic-Sites-Hugo-and-WordPress-and-Recon.
10. **Think as the attacker and the reviewer before calling it done.** Build, break, detect, evade, defend, with named trust boundaries. Pages: Enterprise-Identity-SSO-SAML-OIDC, Ansible-Configuration-Management-Versus-Provisioning, Spacelift-From-Zero, LAMP-and-LEMP-From-Zero, WordPress-and-PHP-Security-WAF-and-Static-Sites.
