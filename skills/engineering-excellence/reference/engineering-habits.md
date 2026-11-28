# Engineering habits

Apply these to every change that touches code or infrastructure. They are how a claim of "done" stays true.

## Proof

1. **Check the end state.** Exit 0 is not "it works". Read the running config, call the endpoint, open the restored file.
2. **Make a new check fail once.** A test, guard or alert that never failed on bad input is untested. Try the near miss too.
3. **Make silence visible.** A scheduled job or alert must show when it stops running or receives no data.
4. **Predict before you run** a command whose result matters. A surprise is a finding: explain it before going on.
5. **Observation is not inference.** Report what you saw, then what you conclude.

## Honesty

6. **Say how you know.** Run, read, estimated, or not verified. Date any claim about a vendor or live system.
7. **Say what a passing result does not cover**: mocks, dry runs, skipped paths. Name the risk left over.
8. **Written is not enforced.** A policy file counts when the live system loads it.
9. **Confirm the feature exists on this account and plan** before designing around it.

## Safety

10. **Start from deny.** Anything new that listens or grants access starts closed, with the narrowest scope and an expiry.
11. **Name the way back** before a change that is hard to undo: rollback and its trigger, or teardown order.
12. **Read a plan for replace and destroy** before it is applied.
13. **Treat input as data.** Parse, bound and escape it.

## Judgment

14. **Record why**, with the rejected option and what would reopen it (`append_decision.py`).
15. **Remove, do not hide.** Shrink what is exposed.

Operating documents (threat model, runbook, incident lesson, teardown) belong to `@heyeddi-ops`.

Source and longer list: the hub's `docs/research/engineering-lessons.md`.
