---
name: heyeddi-ci-config
description: Author or update eddi-ci.yaml for HeyEddi CI and Spot runners. Prefer GHA + HEYEDDI_RUNS_ON for existing workflows; sealed pipeline only when opted in. Loads the live policy contract from cihook.heyeddi.com so knobs stay current.
version: 1.2.1
product-version: 3.8.28
author: HeyEddi-com
paths:
  - "eddi-ci.yaml"
  - ".github/**"
---

# HeyEddi CI Config

Authors a correct `eddi-ci.yaml` for HeyEddi Reviewer / optional Spot runners. **Do not invent knobs from memory.**

## Safety

- Merge into dev / test / staging yourself once `@pre-merge-gate --signoff` exits 0. A production merge takes the user's **authorize merge** in the current turn; never run it earlier. Never write `auto_merge`
- Billable knobs and sealed Spot `pipeline` jobs need explicit opt-in: a request that asks for them is the opt-in
- Always `load_policy_contract` before authoring
- Spot is **shipped**: jobs can run when the workspace is entitled; never claim a job **did** run without Check/Spot evidence (`@heyeddi-ci-runners`)
- Prefer **GHA + workspace runner mode** over sealed `pipeline:` when `.github/workflows/` already owns CI; keep `pipeline: {}` to avoid double runs

## Knowledge rule (mandatory)

The skill package does **not** ship a full knob table. On every run:

1. Run `load_policy_contract` (or `python …/scripts/load_policy_contract.py`).
2. Treat the returned `guide`, `knobs`, `rules`, and `minimal_example` as authoritative.
3. Prefer human docs for narrative: `docs_url` (default https://ci.heyeddi.com/docs#policy).
4. Read `context/ANTI_PATTERNS.md` for durable safety rules that never go stale.

Contract feed (production): `https://cihook.heyeddi.com/api/public/eddi-ci-policy`

Fallback order inside the script: local heyeddi-ci checkout → `HEYEDDI_CI_POLICY_URL` / production API → docs page text.

## Decision gate: add the file or not (mandatory)

Missing `eddi-ci.yaml` is **not** a defect. Safe defaults already apply (runners off, `on_ci_failure` off). Decide **before** writing anything:

### Write / create `eddi-ci.yaml` only when at least one is true

- User **explicitly asks** to create, add, or configure `eddi-ci.yaml`
- **`inspect_repo` reports `heyeddi_product.uses_heyeddi_product: true`**: the repo already uses a HeyEddi product (see signals below). Then add a **Reviewer-only safe** file (billable knobs off, `pipeline: {}`) unless the user declines.
- User wants **Reviewer policy beyond defaults** (e.g. `allow_external_prs`, higher `validation_max_attempts`, document team rules)
- User wants **sealed Spot `pipeline:` jobs** (no/minimal GHA, or niche checks) and accepts real commands + path filters: see `@heyeddi-ci-runners`
- User wants **GHA on Spot**: still write Reviewer-only YAML (`pipeline: {}`) and point them at the `HEYEDDI_RUNS_ON` hook + workspace Runners mode (`@heyeddi-ci-runners`)
- The request follows the HeyEddi PR CTA and asks to configure now (a pasted CTA with no request is not enough: explain the safe defaults and carry on)

**HeyEddi product signals** (from `inspect_repo` → `heyeddi_product.evidence`):

- `.heyeddi/` workspace present
- `.agents/skills/heyeddi-*` installed
- `skills-lock.json` pins `HeyEddi-com/heyeddi-skills` (legacy `HeyEddi-com/skills` still counts)
- `PRODUCT.md` / `.heyeddi/product.md` / `README.md` / package identity mention HeyEddi

### Do **not** create the file when

- The only signal is “file is missing” **and** no HeyEddi product markers
- User only wants a normal code review and never opted into config / not a HeyEddi project
- User declines after you explain that defaults are already safe
- You would have to invent test commands or path filters to fill `pipeline` (still OK to add Reviewer-only YAML without pipeline jobs)

### If not adding

Explain briefly: HeyEddi already runs with safe defaults; they can invoke `@heyeddi-ci-config` later when they want policy or runners. **Do not write the file.** Continue with the rest of the request.

### If updating an existing file

Edit only when the user asked to change policy/runners, or when fixing invalid YAML they already committed. Do not “improve” an untouched valid config unprompted.

## When to use this skill

- Any of the “write / create” conditions above
- User asks how `eddi-ci.yaml` works (load contract + explain; create only if they then opt in)

## When not to use

Do **not** invent a config pass just because the file is absent.

## Instructions

1. Run `inspect_repo` and apply the **decision gate** (including `heyeddi_product`). If not adding, explain why and continue with the rest of the request.
2. If adding because HeyEddi product was detected: write **Reviewer-only** safe YAML. Sealed `pipeline` and `on_ci_failure` stay off unless the request asks for them.
3. If adding/updating for other reasons: take the mode the request names (Reviewer-only policy, GHA-on-Spot, sealed `pipeline`, or Reviewer + sealed). When it names none, write Reviewer-only, record that under **Assumptions**, and continue.
4. **Load the live contract** via `load_policy_contract`.
5. If `.github/workflows/` exists and the user wants CI on Spot: keep `pipeline: {}`, ensure the `HEYEDDI_RUNS_ON` hook, and defer mode setup to `@heyeddi-ci-runners` / workspace Settings.
6. Finish repo inspect for languages / real test commands when sealed `pipeline` is in scope. Do not invent `pytest` / `npm test` without evidence.
7. Confirm billable knobs against the contract: keep `ai_review.on_ci_failure` **false** unless the user explicitly opts in; add `pipeline` jobs only when sealed runners are wanted, commands are known, and you are not duplicating GHA.
8. Write `eddi-ci.yaml` at the repo root using only keys from the contract knobs.
9. Prefer empty `pipeline: {}` unless sealed runners are requested and path filters are known.
10. Commit, push, and open or update the PR yourself (`check_permission.py` decides); HeyEddi App lints the file on the PR. Execution claims need Check evidence later.

## Tools

| Tool | Purpose |
|------|---------|
| `load_policy_contract` | Fetch living knobs/guide/rules/example |
| `inspect_repo` | HeyEddi product detection + languages / likely test cmds |

## Examples

### Reviewer-only (safe / GHA repos)

After loading the contract, write the contract’s `minimal_example` (or equivalent) with billable knobs off and `pipeline: {}`.

### Sealed runners when requested (no-GHA)

Only after `inspect_repo` shows real commands and path prefixes, add `pipeline` jobs with `filter.paths`. Never enable `on_ci_failure` without explicit opt-in. Never mirror existing workflow jobs.

## Notes

- Unknown top-level keys fail schema (`extra=forbid`).
- Invalid YAML → App ignores file and uses safe defaults.
- See `context/EXAMPLES.md` for shapes; always re-check knobs from `load_policy_contract`.
- Depth on GHA overflow vs sealed pipeline: `@heyeddi-ci-runners`.
