# Batch 09 notes

### Running-Monero-Properly-Hardware-Wallet-Qubes-and-Whonix-Offline-Wallet-and-PiNodeXMR
A design for running a Monero wallet with a hardware signer, a wallet VM with no network, a separate node VM routed over Tor, and an always-on node. It is written from documents only and marks which parts are documented, which are the author's own combination, and which are unverified.

- When a design is assembled from several documents, tabulate each part as documented, combined by me, or not verified, so nobody mistakes a plausible composition for a tested one.
- Check source code when docs are silent or disagree: the file-signing path that seemed available turned out to be refused for hardware keys.
- Protect separate assets separately and say which control covers which (a hardware key stops theft but does not stop a compromised host reading history).
- For each trust boundary, write what crosses it, what an attacker needs to defeat it and what they then gain, including the direction in which less trusted data gets parsed by a more trusted component.
- Treat a hobby project's defaults and manual as claims to audit (shared default passwords, advice to port-forward an unencrypted admin interface), then write the hardening yourself: nothing exposed, patching with an owner, a tested rebuild.

### Radio-Off-Grid-Communication-LoRa-Meshtastic-Reticulum-Ham-and-SIGINT
A survey of communication paths that survive internet and power outages, with capacity arithmetic, licensing and interception law, and an honest statement that the project has no radio fallback at all.

- For every fallback ask what it depends on that the failure takes away (power, uplink, carrier, identity service).
- Compute capacity before choosing a channel: a short script showed a status text fits easily while a log stream would fill most of the link.
- Validate your own model against published reference values (the computed bit rates are checked against the vendor table) and state what the model ignores.
- Label every performance figure by origin (vendor figure, design goal, theoretical, measured).
- Know the legal and rule constraints before the technical ones, and say "I do not know" where the text does not answer.

### Hardware-Security-Modules-What-They-Are-and-Building-Your-Own-with-pico2hsm
Explains what an HSM protects (copying a key) and what it does not (misuse of a connected, unlocked device), then reads a hobby HSM firmware project's own claims and limits, with an untested build exercise.

- State a control's guarantee together with its non-guarantee: custody of a key is a different question from who may use it.
- Plan for the loss of anything non-exportable before relying on it; hardware protection is not a backup.
- When a README's marketing and its security file disagree, trust the one that lists limits.
- Check what a development or debug configuration silently removes, and never let a public dev key reach real use. Treat irreversible steps (one-time fuses) as their own gate.
- Rehearse the flow in software first, with a negative check (tampered input must fail), and keep an explicit list of what to verify once the real hardware arrives.

### The-CIA-Triad-Confidentiality-Integrity-Availability
Defines confidentiality, integrity and availability, maps generic failures and trade-offs onto them, and audits the repository's controls by property, writing "None" where nothing exists.

- Inventory controls in a table with the property served, the implementing file and a status (built, written but off, none).
- A control that is written but not applied or not attached protects nothing; never count it.
- Ask which property was hit first and what follows, because the response differs (revoke, fail over, restore).
- An integrity reference must be recorded before the change and stored where the same writer cannot alter it.
- Integrity covers mistakes by authorized people, not only attackers; design review and checks for that.

### GRC-Governance-Risk-and-Compliance-in-Plain-Terms-Laws-Frameworks-and-Attestations
Separates laws, standards, frameworks and attestations, describes the policy to risk to control to evidence loop, and shows why a certificate is a dated, scoped snapshot.

- Make evidence a by-product of normal work (merge records, CI runs) instead of collecting it before an audit.
- Test a control three ways: is it designed right, is it in place, did it run every time.
- Evidence must exist for the whole population, not only the items you remember.
- When relying on someone's report, read scope, dates, exceptions, exclusions and what you are expected to do yourself.
- Record decisions to accept risk with an owner and review date, and never edit a record to look better; say "I do not have that".

### US-Privacy-Law-No-General-Right-the-Patchwork-Data-Brokers-Social-Security-Numbers-and-License-Plate-Readers
A dated survey of US privacy law, data brokers, Social Security number misuse and license plate readers, with facts kept apart from a clearly labelled opinion section.

- Do not use an identifier as an authenticator; choose secrets that are separate, rotatable and revocable.
- An identifier introduced for one narrow purpose drifts into many; design and review reuse of keys and IDs deliberately.
- Collect and keep less: most stored scans in the audited case concerned nobody of interest, and long retention plus wide sharing with no audit was the harm.
- Verify actual sharing and defaults in the running system; owners discovered afterwards that they shared more widely than they knew, and a vendor's own pages disagreed on retention.
- Keep established, contested and not-established statements apart, and set opinion beside the evidence that supports or limits it.

### Privacy-Law-Around-the-World-GDPR-PIPEDA-POPIA-and-PIPL-Compared-With-the-United-States
Compares four privacy laws on scope, rights, breach clocks, transfers and penalties, and turns them into engineering duties and a worked incident exercise.

- Translate obligations into system capabilities: find a person's data across systems, verify the requester, export, delete, and keep a processor list.
- Maintain a living data map (what, why, where, who receives, how long) before you need it for a request, breach or transfer.
- Decide in advance who declares "aware", who records the time, and which templates and contacts are used; a clock starts early.
- Vendors are part of your clock: contracts should say how fast and through whom they notify.
- Log only what detection needs, keep it for a defined time, and keep personal data separate from the evidence about it.

### Cross-Tenant-Data-Governance-Retention-and-DLP
Moves sensitive data between two accounts with narrow roles, a verified and purged monthly job with a manual fallback, and a toy content scanner to show false-positive tuning.

- A copy of data needs an owner, purpose and end date written before the first byte moves.
- Choose transfer direction and permissions so the credential that crosses the boundary can do the least (write-only, one prefix, no wildcard).
- Verify guarantees in vendor docs: an expiry rule has no completion-time promise, so it is only a backstop; a deadline needs an explicit job that checks the result and alerts.
- Design the failure path: do not delete after a failed verify, fail loudly, alert on silence and overdue items, offer dry run, and keep a practiced manual runbook with force as a human decision.
- Every exception (allowlist entry, forced override) is attack surface and needs an owner and a reason; automate the checkable steps and keep judgment with people.

### Business-Continuity-and-Disaster-Recovery-BCP-and-DR
Separates keeping work going from restoring systems, sets recovery targets in dependency order, studies public postmortems and writes a candid recovery plan for the project's single-copy control plane.

- Recovery order follows the dependency graph; a system cannot promise to return before what it needs, and the secret store, code host, state and access path come first.
- Look for loops where the recovery tool depends on the thing that failed (including provider control planes and the plan stored inside the outage).
- Label targets as proposals until timed, and write "None" for missing procedures instead of inventing one.
- Run discussion-only tabletops where only what is written counts, and limit them to a few findings with owner and date.
- Deletion and bad bulk operations are disasters too: soft delete, accept only unambiguous identifiers, alert on destructive actions that look like normal workflow, and test recovery at the scale it would be needed. Auto-updating agents are other people changing your production.

### Backups-Recovery-and-Patching
Teaches backup versus snapshot and replica, recovery targets, a timed restore verified against a manifest, patch layers, and how to read a vulnerability record.

- Count restores, not backups: restore into a fresh place, compare with a record made earlier, and time it.
- Alert when a backup or restore test fails or does not run; a log nobody reads is silence.
- Know which tool patches which layer; OS auto-updates do not reach container images, extra repositories or app dependencies.
- Prioritize vulnerabilities by whether you run it, whether it is reachable, whether it is being exploited and how much the machine matters, not by severity score alone.
- Give destructive tooling a guard (the lab script refuses to delete anything without its marker file) and keep backup credentials unable to delete.

### Backups-Deep-Dive-3-2-1-1-0-Immutability-and-Restore-Testing
Extends the backup rules with immutable copies, zero restore errors, key custody, backing up the backup system, retention and what the project does not protect.

- Redundancy is not backup: anything that faithfully replicates mistakes only keeps you running.
- Count independent failure domains and credentials, not copies; one account that can delete all copies means one copy.
- Say what each protection does not stop (immutability keeps bad data and secrets readable; versioning can be deleted by the same key).
- Hold keys separate but reachable, with two holders, and prove it by restoring on an empty machine using only the written recovery kit.
- Set retention longer than the time to notice a problem, and back up the backup system itself (config, scripts, schedule, runbook, tool).

## Batch lessons

1. **State what was run and what was only read.** Every page opens with what was executed, not run and not read, and keeps claims tagged with source and date. Shown by: Monero, Radio, HSM, CIA, GRC, US privacy, world privacy, Cross-tenant, BCP/DR, Backups, Backups deep dive.
2. **Record gaps as findings.** Write "None", "written but off" or "not verified" instead of implying coverage. Shown by: CIA, Radio, BCP/DR, Backups deep dive, GRC, Monero.
3. **Pair every control with what it does not do.** Shown by: HSM, Backups deep dive, Backups, Monero, Cross-tenant, CIA, GRC, Radio.
4. **A thing is not proven until exercised against an independent expectation.** Restore and compare with an earlier manifest, include a case that must fail, and time it. Shown by: Backups, Backups deep dive, BCP/DR, CIA, HSM, Cross-tenant, Radio.
5. **Silence is a failure.** Alert on missing runs, failed jobs and overdue items, and check the result, not the exit code. Shown by: Backups, Backups deep dive, Cross-tenant, BCP/DR.
6. **Limit what one credential, account or boundary can reach.** Least privilege, add-only credentials, separate failure domains, trust direction. Shown by: Cross-tenant, Backups, Backups deep dive, Monero, HSM, CIA.
7. **Map dependencies and loops before a failure.** Shown by: BCP/DR, Radio, Backups deep dive, Monero.
8. **Read the guarantee in the primary source, not the product name or badge.** Lifecycle timing, vendor backup limits, certificate scope, marketing versus security notes, source code over guides. Shown by: Cross-tenant, Backups, Backups deep dive, GRC, HSM, Monero, US privacy.
9. **Data is a liability with an owner, purpose and end date.** Minimize, map, retain deliberately, be able to delete. Shown by: Cross-tenant, world privacy, US privacy, Backups deep dive.
10. **Put numbers and clocks on promises, and label estimates.** Recovery targets, breach deadlines, airtime capacity, dependency-ordered targets, small scripts that check a plan for contradictions. Shown by: BCP/DR, Backups, world privacy, Radio.
