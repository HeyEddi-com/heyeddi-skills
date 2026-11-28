# Batch 03 notes

### How-a-Web-Request-Works
Walks one HTTPS request through DNS, TCP, TLS and HTTP, then explains certificate chains and has the reader build a private CA, break it with an expired certificate and a wrong name, and see what each failure looks like.
- Debug by layer: first decide which step failed (name, connection, handshake, application), because each has its own error text and its own fix.
- Never switch off a check to get green (for example skipping certificate verification). Fix the name, the date or the trust anchor, since a disabled check leaves no trace that anything was wrong.
- Grant trust as narrowly as the purpose: pass a test CA to one command, constrain what it may sign and make it short-lived, instead of adding it to the system trust store.
- When building a failure to learn from, leave exactly one fault in place so the error you see is the one you meant to study.
- Monitor expiry with a check that fails by exit code and a warning window longer than the renewal window, and automate renewal so it is routine.

### DNS-Cloudflare-and-Hosting-Your-Own-Website
Explains domain ownership, records, TTL, delegation, proxying, TLS modes and origin lockdown, with a local DNS lab and a never-run hosting walkthrough. Treats DNS as a trust boundary.
- Order changes by dependency in both directions: create the firewall before the server and publish records last; on teardown remove the DNS record before the server it points to.
- Plan around caches: lower the TTL a full old TTL before a change, and do not "fix" a correct record because a cache still shows the old one.
- Test the negative case that proves the control: the key test is that a direct request to the origin fails, not that the site loads.
- Make scripts that build security rules fail closed: if a fetched list is empty or implausibly short, stop before applying anything.
- Keep intended state as code or a file and diff live state against it, so a stray or malicious record shows as drift even on names nobody watches.

### Subnets-NAT-and-Firewalls-By-Hand
Teaches subnet arithmetic, routing, NAT and firewalls by doing them in network namespaces, then runs a break and fix loop on a default-deny rule set.
- Separate a side effect from a control: NAT happens to drop some traffic but is not policy. Ask which rule actually enforces the property you rely on.
- Review a rule set as default first, then each exception, then who can use it, and question every wide rule (who needs it, what happens if misused).
- Use the same verification command before and after a change, from a vantage point that should be denied, so the only variable is the change.
- Read failure symptoms precisely: refused, timeout and unreachable point to different causes. Know what an instrument cannot tell you (a counter shows hits, not who sent them).
- Predict the result before running, and compute by hand before trusting a library; library definitions (such as "is private") may not match the rule you meant.

### Behind-a-CDN-Real-Client-IPs-and-OSI-Basics
Shows why a server behind a proxy sees only the proxy's address, how forwarded headers can be forged, and the rule for trusting them, with a lab that reproduces the self-block and the spoof. Argues an IP address is a weak identifier.
- Believe client-supplied data only when it arrives from a party you have explicitly listed; the working happy path is exactly why "trust everything" survives testing.
- Read the default of every tool you enable; some trust all sources unless told otherwise.
- Act at the layer that can see the thing you want to block, and check what each variable or rule now refers to after a change (an allow list may silently start testing the visitor instead of the peer).
- Treat external lists as data you refresh: validate, diff, alert on change, keep the old file if the fetch fails, and syntax test before reload.
- Do not make one weak signal decide identity; combine it with account, session and behavior signals, and log both the claimed and the observed source so lies are detectable.

### IPv6-Adoption-and-Handling-It-Safely
Explains IPv6 basics, adoption reasons labeled documented or opinion, why the project keeps it off, a guard test that enforces that, and a checklist for turning it on, with a lab showing the one-family firewall hole.
- A control must cover every path to the same thing; check the second protocol, interface or door, because a rule written for one says nothing about the other.
- Turn a deliberate "off" decision into an automated test that fails if it drifts, and write down what the test cannot see.
- Treat enabling a capability as one coordinated change with a written checklist (firewall, DNS, limits, logs, monitoring, rollback order, cost), publishing last.
- Do not block a whole protocol class without knowing what it carries; an over-tight rule can break the system in a way that looks unrelated.
- Label each claim as documented or opinion, and record a stakeholder's choice in their words beside what the sources say, without declaring it a mistake.

### APIs-and-Tokens-From-Zero
Introduces HTTP, status codes, JSON, credential types, JWTs, scopes, expiry and leak response with read-only exercises.
- Explore an unfamiliar system with read-only calls first, and read the object back after a write; a success code is only the server's claim.
- Read the exact error class: unknown identity and not allowed are different problems. When a permission is missing, add that one, do not widen to everything.
- Give each program its own narrow, expiring credential so actions are attributable and revocation hits only one thing.
- On a leak, revoke before cleaning up, then rotate, check the audit log, and record which check would have caught it.
- Keep secrets out of places that are recorded by default (command arguments, URLs, history, logs).

### Hashing-Encryption-and-Keys
Distinguishes encoding, hashing, encryption and signing, covers password storage, key custody and hardware keys, and has the reader break each primitive on purpose.
- Name the property you need (secrecy, integrity, authenticity) before choosing a tool; plain encryption can accept tampered data with no error.
- Use reviewed libraries and their defaults; do not invent constructions.
- After "it is encrypted", keep asking: where is the key, who else holds it, in transit or at rest, is it authenticated.
- A check is only as good as where its reference came from: a hash or public key delivered beside the thing it verifies proves little.
- Run the tool and trust the output over the document, and mark clearly what was run, what was read and what is a guess.

### Secrets-From-Day-One
Sets out a habit order for secrets (password manager, secrets manager, env file rules, scanning, rotation, leak drill), with a scanner, a history cleanup drill and a log-reading exercise.
- Assume anything pasted somewhere shared has been copied; the cure is revocation, and history rewriting is later tidiness that cannot reach other clones.
- Prove a fix: present the old secret to the real service and read the refusal, with caches disabled, then hunt for copies.
- Isolate by asset: one config and one short-lived read-only token each, and judge a read-only token by what it can read.
- Layer safety nets and state what each misses; measure the tool yourself (the author counted detection rates and found a documented default differed from the binary).
- Name the residual risks and open design questions in writing, assign an owner to every expiry date, and have a tested recovery and outage plan for each new dependency.

### Password-Managers-and-Passkeys-What-Each-Protects-and-Where-They-Fail
Explains vault design, what a provider breach exposes, hosted versus self-hosted versus offline, passkeys and TOTP, recovery, and a build, corrupt and restore exercise.
- Evaluate a design by asking what an attacker holding each artifact gets and still needs, not by brand or slogan.
- A backup or recovery path counts only after you have restored from it, and it must not depend on the thing it recovers.
- Choosing to self-host moves duties to you; compare options by what each makes you responsible for.
- State the limit of a protection (a compromised device defeats the vault) rather than implying it covers everything.
- Treat vendor claims as claims: quote them as read, with date, and disclose conflicts of interest such as affiliate links.

### Disk-and-File-Encryption-VeraCrypt-TrueCrypt-History-BitLocker-FileVault-and-LUKS
Covers what encryption at rest protects (powered off, not running), platform disk encryption, VeraCrypt features and limits, a sourced TrueCrypt timeline, and a VM exercise.
- State the exact condition under which a control holds; "encrypted" says nothing about a running, unlocked machine.
- Verify actual state, not the feature label: a tool can be "on" yet unprotected.
- Prefer the simpler option unless the case clearly needs the advanced one; a feature that fails through ordinary habits is worse than none.
- Understand what an operation really changes (a password change rewrites the header only, so old copies still open with the old password).
- Report your own failed runs and harness mistakes, say what the environment distorts (use ratios, not seconds), and leave unresolved source conflicts unresolved instead of picking one.

## Batch lessons

1. **Break it on purpose and see the failure.** Build the control, introduce the fault, observe the exact symptom, fix, and rerun the same check. (How-a-Web-Request-Works, DNS-Cloudflare, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, Hashing-Encryption-and-Keys, Secrets-From-Day-One, Password-Managers, Disk-Encryption)
2. **Predict, do, check, undo.** Write the expected result first and plan the cleanup before creating anything, including teardown and cost before any cloud resource. (How-a-Web-Request-Works, DNS-Cloudflare, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, APIs-and-Tokens, Secrets-From-Day-One, Disk-Encryption)
3. **Be honest about evidence.** Mark what was run, what was only read, what is a guess, with dates and a claims register. (all ten pages)
4. **Verify the denied path and the real state, not the happy path or the label.** (DNS-Cloudflare, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, Secrets-From-Day-One, Disk-Encryption, APIs-and-Tokens)
5. **Know what each control does not protect, and name the residual risk.** (How-a-Web-Request-Works, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, Hashing-Encryption-and-Keys, Secrets-From-Day-One, Password-Managers, Disk-Encryption)
6. **Default deny and fail closed.** Unmatched traffic is dropped, a bad fetch changes nothing, a failed secret pull never falls back to a literal. (DNS-Cloudflare, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, Secrets-From-Day-One)
7. **Narrow and short-lived trust.** Scope by source, purpose and time; one identity per asset. (How-a-Web-Request-Works, Subnets-NAT-Firewalls, Behind-a-CDN, APIs-and-Tokens, Secrets-From-Day-One, Hashing-Encryption-and-Keys)
8. **Cover every path and check defaults.** Second protocol family, direct-to-origin door, tool defaults that trust everyone, old clones and old headers. (DNS-Cloudflare, Behind-a-CDN, IPv6, Secrets-From-Day-One, Disk-Encryption)
9. **Order matters in changes and incidents.** Build and destroy in dependency order; revoke before cleaning up; publish exposure last. (DNS-Cloudflare, IPv6, APIs-and-Tokens, Secrets-From-Day-One, Hashing-Encryption-and-Keys)
10. **Review as an adversary.** Take the reviewer, scanner or responder seat on your own work and say only what the evidence supports. (DNS-Cloudflare, Subnets-NAT-Firewalls, Behind-a-CDN, IPv6, Secrets-From-Day-One, Disk-Encryption)
