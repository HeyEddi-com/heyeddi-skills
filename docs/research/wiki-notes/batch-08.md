# Batch 08 notes

### How-Tor-Works-in-Depth-Circuits-Relays-Directory-Authorities-and-Onion-Services
Explains Tor circuits, relay roles, directory authorities, guards, bridges and onion services, then lists documented weaknesses with dates. It states the adversary and the design non-goals up front, and marks what was read, what was inferred and what was never run.

- Start from the stated adversary and non-goals of a system. Say what it does not defend against before saying what it does.
- For each component, write what it can learn and what it cannot. A "who knows what" table is a fast way to review a design for separation of knowledge.
- Learn why a number or rule exists (three hops, long-lived guards). An intuitive "more random is safer" can be wrong: repeated low-probability exposure becomes near certain over many tries.
- Treat shared dependencies (the relay list, the shipped authority list, the signed download) as part of the security claim, and avoid per-user variation that makes someone stand out.
- Separate bugs that can be patched from limits built into the design, and note that no documented attack is not proof of safety.

### How-I2P-Works-Tunnels-Garlic-Routing-and-the-Network-Database
Covers I2P's one-way tunnels, bundled messages, distributed network database and peer profiling, then its documented weaknesses and an honest comparison with Tor. It flags where the project's own pages are stale, contradict each other or read like advocacy.

- When two official documents disagree, say so, decline to guess, and treat it as a sign that the docs are not maintained together.
- Date every document and figure you lean on. A 2010 threat model or an old "accurate for version X" label changes how much weight it carries.
- Separate a project's claims about itself (and about competitors) from checked facts. Use the mechanics it describes and discount its verdicts.
- Never trust self-reported attributes from untrusted peers (claimed bandwidth); grade on what you observe, and notice that performance-based selection makes choices predictable.
- Compare tools by first asking which question each answers. "It depends" is only useful when you name what it depends on.

### The-Browsing-Setups-Compared-Tor-Browser-Brave-Whonix-Tails-and-Qubes-with-Whonix
Compares five ways of running Tor against nine fixed threats, drawing each one's trust boundary and cost. It argues that fit to the threat matters more than the number of layers.

- Compare options with a matrix: fix the list of threats first, score every option against the same rows, and mark which cells are vendor claims or your own guess.
- Draw the trusted computing base for each option. Isolation does not remove trust, it moves it (every app must behave becomes the hypervisor must be sound).
- Prefer making a failure impossible by structure (the work machine has no route out) over relying on every program being configured correctly.
- Every added layer must be installed, patched and used correctly. Pick the smallest design that covers the stated adversary.
- Choose a tool for what its makers built it for, not for what it signals about you. Label opinion as opinion.

### OPSEC-for-Tor-and-I2P-That-Holds-Up-Identities-Layers-Metadata-and-Habits
Splits identity into device, network, account and behavior layers and shows that anonymity networks only help with one. It gives rules with reasons, documented failure cases, a test for security theater and two audience-specific checklists.

- When something leaks, ask which layer it leaked on and whether the control you own even operates there.
- Test any proposed rule with three questions: which named adversary does it stop, on which layer, and what does it cost or newly break.
- A plan too hard to follow daily will be skipped. Write separate short checklists for different risk levels instead of one maximal list.
- State the limit of a cleanup tool (a metadata cleaner cannot find everything) and lower the risk at the source, for example by using simpler formats.
- Read incidents for the pattern, not the people, and remember public cases are a biased sample that says nothing about how often a practice works.

### Hands-On-Whonix-and-Qubes-OS-Gateway-Split-Compartments-Disposables-and-Policy-Prompts
A lab guide to building the gateway/workstation split and Qubes compartments, with each step written as predict, do, check, undo and marked run or not run. It covers fail-closed behavior, signature checks, first-match policy rules and the blast radius of a compromised compartment.

- Structure procedures as predict, do, check, undo. Writing the expected result first makes surprises visible, and an undo step keeps experiments safe.
- Design to fail closed, then prove it by removing the dependency and confirming nothing gets through.
- Test the negative case of every check (tampered file, missing key), and say what a pass does not prove: a good signature shows who signed, not that the content is harmless.
- Practice on stand-ins and throwaway clones, keeping a clean master you never use.
- Map what crosses each boundary and what decides it; default deny, and be careful with data flowing from less trusted to more trusted components.

### The-Darknet-Landscape-Markets-OPSEC-Clearnet-and-Layering-Tor-I2P-and-VPN
Uses documented public cases to show how darknet markets work and fail, and what operator mistakes teach about operational security. It argues for threat modeling before tools and shows the case for and against each way of layering Tor, I2P and a VPN.

- Order of work: threat model, then the smallest set of measures, then habits, then write down the accepted risk.
- Strong tools on one layer do not protect weak habits on another. Spend effort where the real route to failure is.
- Read an official or vendor number for exactly what it counts and who is announcing it; show conflicting figures side by side.
- Trust should come from a channel you already verified (the service's own HTTPS page), not from copied lists that go stale or get poisoned.
- A system that holds other people's money or logs everything creates its own target and temptation. Minimize what you hold.

### Lab-Publish-a-Web-Server-as-a-Tor-Onion-Service-and-an-I2P-Site-Time-Boxed-and-Defensive
A time-boxed lab that puts a static page behind an onion service and an I2P tunnel, audits the origin for exposure mistakes with a script, and tears it down. An optional default-off infrastructure flag is tested with mocked providers and never applied.

- Check what packages do by default (listening on every interface, default sites, extra listeners) and bind explicitly; then verify from outside, not only from the same host.
- Behind a proxy or tunnel everyone looks local, so never grant access based on a loopback source address.
- Ship risky features behind a default-off flag, test both states, and prove the off state renders byte for byte as before.
- Turn mistakes into a small read-only audit script tested against a deliberately broken and a clean fixture, and say a clean run only proves those checks found nothing.
- Plan the exit before you start: time box, tear-down order, key custody, and secrets generated where they live so they never enter code, plan or state.

### Blockchain-Fundamentals-Hashes-Blocks-Nodes-Consensus-and-Forks
Explains hashes, blocks, Merkle trees, nodes, consensus and forks, checking a real block snapshot by recomputing the hashes. It also says what a blockchain is not and what "decentralized" does not promise.

- Verify what you quote when it is cheap: recompute the hash or the sum instead of copying it, and say what that check still does not show.
- An implementation detail (a database lock limit) can silently become part of the contract that other versions depend on. Watch for accidental rules during upgrades.
- Treat marketing words (immutable, decentralized, trustless) as questions: in what respect, enforced by whom, to what degree.
- Finality and confirmation counts are risk settings that depend on the stakes, not fixed laws. Rules of thumb should be traced to a source.
- Report a discrepancy you found in a source and do not depend on it; also ask whether the technology is needed at all.

### How-Bitcoin-Works-Keys-UTXOs-Mining-and-Why-It-Is-Pseudonymous-and-Traceable
Explains keys, the unspent output model, mining and node types, then how public ledger analysis links addresses and what it can and cannot prove. It ends with a synthetic clustering exercise with an answer key.

- Keep "what the data shows" apart from "what I infer from it". A two-column can say / cannot say table is a good form for reports and debugging conclusions.
- Heuristics have assumptions, false positive rates and known breaking cases. State them, and remember one wrong link can merge huge parts of a graph.
- Pseudonymous data becomes identifying once any outside source joins it. Reused identifiers and permanent records make that join retroactive.
- Teach and test with synthetic data whose expected results are worked out and checked by code.
- Preserve evidence (ids, times, time zone) before anything is changed or deleted.

### How-Monero-Works-Compared-with-Bitcoin-and-Ethereum-DeFi-Mixers-Swaps-and-Ransomware
Describes Monero's privacy mechanisms, compares it with Bitcoin and Ethereum using dated live reads, and covers DeFi failures, mixers, atomic swaps and ransomware duties. Old research results and unconfirmed claims are kept apart from current facts.

- Classify failures by what failed (code, keys, input data) and ask which control would have narrowed each one. A system is only as sound as the external data it reads.
- In any multi-step protocol across systems, design every stall path: who acts, what is refunded, and timeouts with enough margin for delays. Write the scenarios as a table and test them.
- Granting access or approval can be standing and irreversible (view key, token allowance). Know the scope and duration before granting.
- Privacy or safety properties hold inside one boundary; check metadata, endpoints and edges where the data enters and leaves.
- Do not carry old research numbers into the present, and report "I found nothing about X" as a gap in your reading, not as proof there is nothing.

### Wallets-and-Key-Custody-Hot-and-Cold-Hardware-Wallets-Recovery-Shamir-and-Multisig
Covers wallet types, what hardware devices do and do not protect, recovery phrases, secret splitting, multisignature and company custody controls, with a no-funds restore drill. It discloses an affiliate link and narrows a vendor-related claim to exactly what sources support.

- A backup is only real after a restore from it has been performed and compared, including deliberately wrong inputs to see how they fail (a wrong passphrase may fail silently).
- Compare a non-secret fingerprint or derived value to verify a secret, never the secret itself.
- For every control, name where the rule is enforced, who can change it, and how it fails (rubber-stamp approvals, logs insiders can edit, several keys in one drawer).
- Say "reduced" and not "prevented" when a defense only shrinks a threat; list what it does not cover.
- Disclose conflicts of interest, and restate a disputed claim as "supported by what I read" and "not supported by what I read".

### Paper-Wallets-Generators-and-Offline-Key-Generation-Tails-Electrum-and-Monero
Explains why single-key paper wallets fell out of favor, where sources disagree, how to judge a key generator and how to do offline generation as an ordered procedure. The only thing run was a signature check on a throwaway key, and the assembled procedure is labeled untested.

- Removing one risk does not remove others: an air-gapped machine does not fix weak randomness, and two tools agreeing does not prove either is right.
- Judge a dependency or tool with explicit checks (readable source, verified download, reviewed internals, maintenance status), recording the limit of each check.
- Rehearse the whole recovery and use path with a tiny stake on a test network before trusting it, because the step you never exercised is the one that fails.
- Record the context needed to recover later (software, format, version, date) alongside the backup.
- When a procedure is assembled from several documents, say so and call it untested until someone runs it end to end; when sources disagree, show both and say what you take from it.

## Batch lessons

1. **Name the adversary and the non-goals before choosing a defense.** Threat model first, smallest set of measures, written accepted risk. Slugs: How-Tor-Works, The-Browsing-Setups-Compared, OPSEC-for-Tor-and-I2P, The-Darknet-Landscape, Lab-Publish-a-Web-Server, Wallets-and-Key-Custody, Paper-Wallets.
2. **Label how you know each thing.** Run, read, inferred, general knowledge or not read, with dates, a claims register and a plain "not verified" section. All 12 pages: How-Tor-Works, How-I2P-Works, The-Browsing-Setups-Compared, OPSEC-for-Tor-and-I2P, Hands-On-Whonix-and-Qubes, The-Darknet-Landscape, Lab-Publish-a-Web-Server, Blockchain-Fundamentals, How-Bitcoin-Works, How-Monero-Works, Wallets-and-Key-Custody, Paper-Wallets.
3. **Say what a result does not prove.** A good signature, a clean audit run, a cleaned file, a matching address or a cluster each have a stated limit. Slugs: Hands-On-Whonix-and-Qubes, Lab-Publish-a-Web-Server, OPSEC-for-Tor-and-I2P, Blockchain-Fundamentals, How-Bitcoin-Works, Paper-Wallets.
4. **Map trust boundaries.** For each part: what it knows, what it must be trusted for, what crosses, who decides. Slugs: How-Tor-Works, The-Browsing-Setups-Compared, Hands-On-Whonix-and-Qubes, How-Monero-Works, Wallets-and-Key-Custody, Blockchain-Fundamentals.
5. **Complexity is a cost.** Each layer adds a party, a setting and a failure mode. Slugs: The-Browsing-Setups-Compared, OPSEC-for-Tor-and-I2P, The-Darknet-Landscape, Wallets-and-Key-Custody, How-Tor-Works.
6. **The weak point is usually the edge (defaults, endpoints, habits, people), not the core algorithm.** Slugs: How-Tor-Works, OPSEC-for-Tor-and-I2P, The-Darknet-Landscape, Lab-Publish-a-Web-Server, Wallets-and-Key-Custody.
7. **Prove behavior with negative and failure cases, and design the stall and fail-closed paths.** Slugs: Hands-On-Whonix-and-Qubes, Lab-Publish-a-Web-Server, How-Monero-Works, Wallets-and-Key-Custody, Paper-Wallets.
8. **Rehearse safely with an exit.** Throwaway data and clones, undo and tear-down steps, restore tests before real stakes. Slugs: Hands-On-Whonix-and-Qubes, Lab-Publish-a-Web-Server, Wallets-and-Key-Custody, Paper-Wallets, How-Bitcoin-Works.
9. **Handle sources critically.** Date them, separate self-interested claims from evidence, show disagreements, do not resolve what you cannot. Slugs: How-I2P-Works, The-Darknet-Landscape, Blockchain-Fundamentals, How-Monero-Works, Wallets-and-Key-Custody, Paper-Wallets.
10. **Make documentation claims testable.** Repository tests recompute tables, answer keys and transcripts printed in the lesson. Slugs: Hands-On-Whonix-and-Qubes, Lab-Publish-a-Web-Server, Blockchain-Fundamentals, How-Bitcoin-Works, How-Monero-Works, Wallets-and-Key-Custody.
