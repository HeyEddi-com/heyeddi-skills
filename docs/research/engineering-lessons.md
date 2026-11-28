# How to be a better engineer: lessons from 176 pages

Date: 2026-11-27. Source: the [Clouds-Against-Humanity wiki](https://github.com/ChiefGyk3D/Clouds-Against-Humanity/wiki) (Apache-2.0, by ChiefGyk3D). Page by page notes are in [wiki-notes](wiki-notes/).

These are the habits that came back across the ten reading batches, in our own words. The vendor and topic facts are left out.

## Proof

1. **Check the end state.** "It exited 0" and "it works" are different claims. Look at the running config, the listening port, the restored file.
2. **Make the guard fail on purpose.** A check that has never failed is untested. Feed it the bad input, then the near miss.
3. **Silence is not health.** A job that stopped running looks the same as a job with nothing to report. Alert on missing runs and missing data.
4. **Predict, run, compare, undo.** Write the expected result first. The gap is what you learn.
5. **Separate what you saw from what you concluded.** A log line or a matching hash is a lead.

## Honesty

6. **Say how you know.** Run, read, estimated, or not verified, with the date for anything that can change.
7. **Say what a control does not do.** Mocked tests, a clean audit, a delete guard: each has a hole. Name it and the risk you accept.
8. **Written is not enforced.** A policy in the repository does nothing until it is attached to the live system.
9. **Read the guarantee at the source.** A feature name or a badge is not the promise. Check that your plan or account has it before designing on it.

## Safety

10. **Start from no.** Default deny, fail closed, protection in place before the thing exists.
11. **Keep reach small.** One narrow, short-lived credential per thing. What checks is not what changes.
12. **Plan the way back first.** Rollback and its trigger, teardown order, a restore you have timed, a second key.
13. **Change one thing at a time.** Observe before enforcing. Read the plan for replace and destroy.
14. **Input is data.** Parse it, bound it, escape it. Never trust a name or header the client wrote.

## Judgment

15. **Name the adversary and the non-goals** before choosing a defense.
16. **Cost is a design input.** Ceiling, arithmetic and cap before anything is created.
17. **Record why,** with the rejected options and what would reopen the decision.
18. **Complexity costs.** Each layer adds a party to trust, a setting and a failure.
19. **Remove, do not hide.** List what is exposed, then shrink it.
20. **Keep one source of truth.** Generate documents from it, or test them against the code.
