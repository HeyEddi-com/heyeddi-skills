#!/usr/bin/env python3
"""Cost gate: estimate the monthly run cost of a change and check it against the budget.

Reads the branch diff (or --diff-file), finds cost drivers, prices them from
reference/cost-rates.json (overridable in budget.json), and writes
.heyeddi/docs/cost-estimate-<date>.md. Never calls a cloud or pricing API: pass a
`terraform show -json` plan or an `infracost diff --format json` file to validate.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from _cost_rules import detect
from _heyeddi_paths import engineering_docs_dir, skill_docs_dir
from _skill_cli import emit, fail, resolve_project_root

RATES_FILE = Path(__file__).resolve().parents[1] / "reference" / "cost-rates.json"
BASE_CANDIDATES = ("origin/main", "main", "origin/master", "master")
MAX_UNTRACKED_LINES = 2000

DEFAULT_BUDGET = {
    "currency": "USD",
    "change_warn_monthly": 25,
    "change_error_monthly": 200,
    "monthly_limit": None,
    "current_monthly": None,
    "firestore_reads_per_day_limit": 1_000_000,
    "assumptions": {
        "llm_calls_per_month": 10000,
        "llm_input_tokens": 2000,
        "llm_output_tokens": 500,
        "ci_runs_per_month": 200,
        "ci_minutes_per_run": 5,
        "concurrent_clients": 50,
        "firestore_sessions_per_day": 200,
        "firestore_docs_per_query": 1000,
        "firestore_doc_changes_per_day": 5000,
        "firestore_loop_iterations": 20,
        "firestore_reads_per_day_warn": 100_000,
    },
    "rates": {},
}


def budget_path(root: Path) -> Path:
    return engineering_docs_dir(root) / "budget.json"


def load_budget(root: Path) -> tuple[dict, bool]:
    budget = json.loads(json.dumps(DEFAULT_BUDGET))
    path = budget_path(root)
    if not path.is_file():
        return budget, False
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in data.items():
        if isinstance(value, dict) and isinstance(budget.get(key), dict):
            budget[key].update(value)
        else:
            budget[key] = value
    return budget, True


def load_rates(overrides: dict) -> dict:
    rates = json.loads(RATES_FILE.read_text(encoding="utf-8"))
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(rates.get(key), dict):
            rates[key].update(value)
        else:
            rates[key] = value
    return rates


def _git(root: Path, *args: str) -> str | None:
    git = shutil.which("git")
    if git is None:
        return None
    proc = subprocess.run([git, *args], cwd=root, capture_output=True, text=True, shell=False)
    return proc.stdout if proc.returncode == 0 else None


def git_diff(root: Path, base: str | None) -> tuple[str, str | None]:
    """Diff of the working tree against the merge base, plus untracked files as added."""
    if _git(root, "rev-parse", "--is-inside-work-tree") is None:
        return "", None
    candidates = (base,) if base else BASE_CANDIDATES
    ref = next((c for c in candidates if _git(root, "rev-parse", "--verify", "--quiet", c)), None)
    if ref is None:
        return "", None
    merge_base = (_git(root, "merge-base", "HEAD", ref) or ref).strip()
    diff = _git(root, "diff", "--unified=0", "--no-color", merge_base) or ""
    for rel in (_git(root, "ls-files", "--others", "--exclude-standard") or "").splitlines():
        try:
            lines = (root / rel).read_text(encoding="utf-8").splitlines()[:MAX_UNTRACKED_LINES]
        except (OSError, UnicodeDecodeError):
            continue
        diff += f"diff --git a/{rel} b/{rel}\n+++ b/{rel}\n@@ -0,0 +1 @@\n"
        diff += "".join(f"+{line}\n" for line in lines)
    return diff, ref


def parse_diff(text: str) -> dict[str, dict[str, list[str]]]:
    files: dict[str, dict[str, list[str]]] = {}
    current: dict[str, list[str]] | None = None
    old_path = None
    in_hunk = False
    for line in text.splitlines():
        if line.startswith("diff --git "):
            current, in_hunk, old_path = None, False, None
        elif not in_hunk and line.startswith("--- "):
            old_path = line[6:] if line.startswith("--- a/") else None
        elif not in_hunk and line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else old_path
            current = files.setdefault(path, {"added": [], "removed": []}) if path else None
        elif line.startswith("@@"):
            in_hunk = current is not None
        elif in_hunk and current is not None:
            if line.startswith("+"):
                current["added"].append(line[1:])
            elif line.startswith("-"):
                current["removed"].append(line[1:])
    return files


def terraform_plan_findings(plan: dict, rates: dict) -> list[dict]:
    table = rates.get("terraform_resources", {})
    out: list[dict] = []
    for rc in plan.get("resource_changes", []):
        actions = rc.get("change", {}).get("actions", [])
        sign = 1 if actions == ["create"] else -1 if actions == ["delete"] else 0
        row = table.get(rc.get("type", ""))
        if not sign or row is None:
            continue
        out.append({
            "driver": "terraform-plan", "severity": "warn" if sign > 0 else "info",
            "file": rc.get("address", rc.get("type")),
            "message": f"plan {actions[0]}s {rc.get('address')}",
            "low": sign * row["low"], "high": sign * row["high"],
            "confidence": "medium", "cheaper": row.get("cheaper", "") if sign > 0 else "",
        })
    return out


def infracost_finding(data: dict) -> dict | None:
    raw = data.get("diffTotalMonthlyCost")
    if raw in (None, ""):
        return None
    value = float(raw)
    return {
        "driver": "infracost", "severity": "warn" if value > 0 else "info", "file": "infracost",
        "message": f"Infracost diff: {value:+.2f} USD/month for the Terraform in this change",
        "low": value, "high": value, "confidence": "high", "cheaper": "",
    }


USAGE_DRIVERS = ("firestore", "llm", "polling")


def has_billing_alert(root: Path) -> bool:
    skip = {"node_modules", ".terraform", ".git", ".venv"}
    for tf in root.rglob("*.tf"):
        if skip.intersection(tf.parts):
            continue
        try:
            if "google_billing_budget" in tf.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            continue
    return False


def budget_gate(total_high: float, budget: dict, has_budget: bool, *, reads_per_day: int = 0,
                usage_driven: bool = False, billing_alert: bool = True) -> list[dict]:
    out: list[dict] = []
    read_limit = budget.get("firestore_reads_per_day_limit")
    if read_limit is not None and reads_per_day > read_limit:
        out.append({"severity": "error", "message": (
            f"Change may add about {reads_per_day:,} Firestore reads/day, over "
            f"firestore_reads_per_day_limit {read_limit:,}. Bound the queries before shipping.")})
    if usage_driven and not billing_alert and not budget.get("billing_alert_acknowledged"):
        out.append({"severity": "warn", "message": (
            "Usage-based cost (Firestore, model calls) cannot be fully estimated from code, and no "
            "google_billing_budget exists in this repo. Add budget alerts in Terraform (plan locally; "
            "the pipeline applies them), or set billing_alert_acknowledged in budget.json.")})
    if not has_budget:
        out.append({"severity": "warn", "message": "No budget.json: defaults used. Run init_engineering_docs.py and set limits."})
    warn_at, error_at = budget["change_warn_monthly"], budget["change_error_monthly"]
    if error_at is not None and total_high > error_at:
        out.append({"severity": "error", "message": f"Change may add up to ${total_high:,.2f}/month, over change_error_monthly ${error_at:,.2f}"})
    elif warn_at is not None and total_high > warn_at:
        out.append({"severity": "warn", "message": f"Change may add up to ${total_high:,.2f}/month, over change_warn_monthly ${warn_at:,.2f}"})
    limit, current = budget.get("monthly_limit"), budget.get("current_monthly")
    if limit is not None and current is not None and current + total_high > limit:
        out.append({"severity": "error", "message": f"Projected ${current + total_high:,.2f}/month passes monthly_limit ${limit:,.2f}"})
    return out


def record_approval(root: Path, reason: str, total_high: float) -> str | None:
    decisions = engineering_docs_dir(root) / "decisions.md"
    if not decisions.is_file():
        return None
    block = (
        f"\n### {date.today().isoformat()}: Cost approved over budget\n\n"
        f"**Context:** Cost gate estimated up to ${total_high:,.2f}/month for this change.\n\n"
        f"**Decision:** Approved by the user: {reason}\n\n"
        "**Consequences:** Check real spend after a month; adjust budget.json or roll back.\n"
    )
    decisions.write_text(decisions.read_text(encoding="utf-8").rstrip() + "\n" + block, encoding="utf-8")
    return str(decisions.relative_to(root))


def _money(value) -> str:
    return "unknown" if value is None else f"{value:+,.2f}"


def write_report(root: Path, result: dict) -> Path:
    skill_docs_dir(root).mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    path = skill_docs_dir(root) / f"cost-estimate-{today}.md"
    lines = [
        f"# Cost estimate: {today}",
        "",
        f"Base: `{result['base'] or 'none'}`. Sources: {', '.join(result['sources']) or 'none'}.",
        "",
        f"**Monthly change:** ${result['total_monthly_low']:,.2f} to ${result['total_monthly_high']:,.2f} "
        f"(USD, estimate). Firestore reads: about {result['firestore_reads_per_day']:,}/day. "
        f"Drivers with unknown cost: {result['unknown_count']}.",
        "",
        "| Driver | File | Change | Low $/mo | High $/mo | Confidence | Cheaper option |",
        "|--------|------|--------|----------|-----------|------------|----------------|",
    ]
    for f in result["findings"]:
        lines.append(
            f"| {f['driver']} | `{f['file']}` | {f['message']} | {_money(f['low'])} | "
            f"{_money(f['high'])} | {f['confidence']} | {f['cheaper']} |"
        )
    lines += ["", "## Budget", ""]
    lines += [f"- **{b['severity']}**: {b['message']}" for b in result["budget_findings"]] or ["- Within budget."]
    lines += ["", "## Assumptions", ""]
    lines += [f"- `{k}`: {v}" for k, v in result["assumptions"].items()]
    lines += [
        "",
        "Rates are rough list prices. Check the provider pricing page before a real decision.",
        "Validate infra with `terraform show -json plan.out` or an Infracost diff JSON.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def estimate_change_cost(
    root: Path,
    *,
    diff_text: str | None = None,
    base: str | None = None,
    terraform_plan: dict | None = None,
    infracost: dict | None = None,
    approved: str | None = None,
) -> dict:
    budget, has_budget = load_budget(root)
    rates = load_rates(budget.get("rates", {}))
    assumptions = budget["assumptions"]
    sources: list[str] = []
    if diff_text is None:
        diff_text, base = git_diff(root, base)
    if diff_text:
        sources.append("diff")

    findings: list[dict] = []
    for path, change in parse_diff(diff_text).items():
        findings.extend(detect(path, change["added"], change["removed"], rates, assumptions))

    infra_override = infracost_finding(infracost) if infracost else None
    if terraform_plan is not None or infra_override is not None:
        findings = [f for f in findings if f["driver"] != "terraform"]
    if terraform_plan is not None and infra_override is None:
        findings.extend(terraform_plan_findings(terraform_plan, rates))
        sources.append("terraform-plan")
    if infra_override is not None:
        findings = [f for f in findings if not f["file"].endswith(".tf")]
        findings.append(infra_override)
        sources.append("infracost")

    total_low = round(sum(f["low"] or 0 for f in findings), 2)
    total_high = round(sum(f["high"] or 0 for f in findings), 2)
    budget_findings = budget_gate(
        total_high, budget, has_budget,
        reads_per_day=sum(f.get("reads_per_day", 0) for f in findings),
        usage_driven=any(f["driver"] in USAGE_DRIVERS and (f["high"] or 0) > 0 for f in findings),
        billing_alert=has_billing_alert(root),
    )
    errors = [b for b in budget_findings if b["severity"] == "error"]
    approval_path = None
    if errors and approved:
        approval_path = record_approval(root, approved, total_high)
        if approval_path:
            for b in errors:
                b["severity"] = "warn"
                b["message"] += " (approved, ADR recorded)"
            errors = []

    result = {
        "ok": not errors,
        "base": base,
        "sources": sources,
        "total_monthly_low": total_low,
        "total_monthly_high": total_high,
        "unknown_count": sum(1 for f in findings if f["high"] is None),
        "firestore_reads_per_day": sum(f.get("reads_per_day", 0) for f in findings),
        "findings": findings,
        "budget_findings": budget_findings,
        "assumptions": assumptions,
        "approval_recorded": approval_path,
        "summary_warning": summary_warning(errors, total_low, total_high, findings),
    }
    result["report"] = str(write_report(root, result).relative_to(root))
    return result


def summary_warning(errors: list[dict], low: float, high: float, findings: list[dict]) -> str | None:
    """First line of the agent's final summary when the change is over budget. Never a stop."""
    if not errors:
        return None
    top = sorted(findings, key=lambda f: f["high"] or 0, reverse=True)[:3]
    drivers = "; ".join(
        f"{f['driver']} in {f['file']}" + (f" (cheaper: {f['cheaper']})" if f.get("cheaper") else "") for f in top
    ) or "see report"
    reasons = "; ".join(b["message"] for b in errors)
    return (
        f"Cost: over budget, ${low:,.0f} to ${high:,.0f}/month added. {reasons}. Top drivers: {drivers}. "
        "The change stays on the branch; pick the cheaper option from the report, or approve it at merge "
        "(estimate_change_cost --approved \"<reason>\")."
    )


def _read_json(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        fail(f"File not found: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate the monthly run cost of a change")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--base", default=None, help="Git ref to diff against (default origin/main, main)")
    parser.add_argument("--diff-file", default=None, help="Unified diff to read instead of git")
    parser.add_argument("--terraform-plan-json", default=None, help="Output of terraform show -json plan.out")
    parser.add_argument("--infracost-json", default=None, help="Output of infracost diff --format json")
    parser.add_argument("--approved", default=None, help="User's reason for going over budget; writes an ADR")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the change is over budget. Merge gate only (pre-merge-gate); during work run without it.",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    diff_text = None
    if args.diff_file:
        path = Path(args.diff_file)
        if not path.is_file():
            fail(f"Diff file not found: {args.diff_file}")
        diff_text = path.read_text(encoding="utf-8", errors="replace")

    result = estimate_change_cost(
        root,
        diff_text=diff_text,
        base=args.base,
        terraform_plan=_read_json(args.terraform_plan_json),
        infracost=_read_json(args.infracost_json),
        approved=args.approved,
    )
    emit(json.dumps(result, indent=2))
    if args.check and not result["ok"]:
        fail(
            "Cost gate failed: over budget. This blocks the merge, not the work: keep the change on the branch, "
            "lead the final summary with summary_warning, and rerun with --approved when the user accepts the cost."
        )


if __name__ == "__main__":
    main()
