"""Cost-driver detectors for estimate_change_cost.py.

Each detector reads one changed file (added and removed lines) and returns findings:
{driver, severity, file, message, low, high, confidence, cheaper}. `low`/`high` are
monthly USD deltas (negative = saving) or None when the cost depends on unknown usage.
"""
from __future__ import annotations

import re

from _cost_firestore import firestore_usage
from _cost_common import (  # noqa: E402
    CODE_EXT, CONFIG_EXT, SECONDS_PER_MONTH, _finding, _is_code, _skip, poll_intervals_ms,
)

TF_RESOURCE = re.compile(r'^\s*resource\s+"(\w+)"\s+"([\w-]+)"')
MIN_INSTANCES = re.compile(
    r"(?:min_instance_count|min_instances|minInstances|minScale[\"']?|--min-instances)"
    r"\s*[:= ]\s*[\"']?(\d+)"
)
CPU_ALWAYS = re.compile(
    r"(cpu_idle\s*=\s*false|cpu-throttling[\"']?\s*:\s*[\"']?false|--no-cpu-throttling)"
)
CLAUDE_MODEL = re.compile(r"\bclaude-(fable|mythos|opus|sonnet|haiku)-\d+(?:-\d+)?\b")
OTHER_MODEL = re.compile(r"\b(gpt-[\w.]+(?:-[\w.]+)*|gemini-[\w.]+(?:-[\w.]+)*)\b")
CRON = re.compile(r"(?:schedule|cron)\s*[:=]\s*[\"']([^\"']+)[\"']")
RUNS_ON = re.compile(r"runs-on\s*:\s*(.+)")



def terraform_resources(path: str, added: list[str], removed: list[str], rates: dict, _a: dict) -> list[dict]:
    if not path.endswith(".tf") or _skip(path):
        return []
    table = rates.get("terraform_resources", {})
    out: list[dict] = []
    for lines, sign, verb in ((added, 1, "adds"), (removed, -1, "removes")):
        for line in lines:
            m = TF_RESOURCE.match(line)
            if not m:
                continue
            rtype, name = m.groups()
            row = table.get(rtype)
            if row is None:
                if rtype.startswith(("google_", "aws_", "azurerm_")):
                    out.append(_finding("terraform", path, f"{verb} {rtype}.{name}: no rate on file",
                                        severity="info"))
                continue
            out.append(_finding(
                "terraform", path, f"{verb} {rtype}.{name}",
                low=sign * row["low"], high=sign * row["high"], confidence="medium",
                cheaper=row.get("cheaper", "") if sign > 0 else "",
                severity="warn" if sign > 0 and row["high"] >= 10 else "info",
            ))
    return out


def _sum_ints(pattern: re.Pattern, lines: list[str]) -> int:
    return sum(int(m.group(1)) for line in lines for m in [pattern.search(line)] if m)


def always_on_compute(path: str, added: list[str], removed: list[str], rates: dict, _a: dict) -> list[dict]:
    if _skip(path) or not path.endswith(CONFIG_EXT + CODE_EXT):
        return []
    out: list[dict] = []
    delta = _sum_ints(MIN_INSTANCES, added) - _sum_ints(MIN_INSTANCES, removed)
    if delta:
        row = rates["cloud_run_min_instance"]
        out.append(_finding(
            "always-on", path, f"min instances change by {delta:+d}: billed while idle",
            low=delta * row["low"], high=delta * row["high"], confidence="medium",
            cheaper=row["cheaper"] if delta > 0 else "", severity="warn" if delta > 0 else "info",
        ))
    cpu = sum(bool(CPU_ALWAYS.search(x)) for x in added) - sum(bool(CPU_ALWAYS.search(x)) for x in removed)
    if cpu and path.endswith(CONFIG_EXT):
        row = rates["cpu_always_allocated"]
        out.append(_finding(
            "always-on", path, "CPU always allocated" if cpu > 0 else "CPU always-allocated removed",
            low=cpu * row["low"], high=cpu * row["high"], confidence="low",
            cheaper=row["cheaper"] if cpu > 0 else "", severity="warn" if cpu > 0 else "info",
        ))
    return out


def _model_rate(model: str, rates: dict) -> dict | None:
    exact = rates.get("llm_per_mtok", {}).get(model)
    if exact:
        return exact
    m = CLAUDE_MODEL.search(model)
    return rates.get("llm_family_fallback", {}).get(m.group(1)) if m else None


def _models(lines: list[str]) -> set[str]:
    found: set[str] = set()
    for line in lines:
        found.update(m.group(0) for m in CLAUDE_MODEL.finditer(line))
        found.update(m.group(1) for m in OTHER_MODEL.finditer(line))
    return found


def llm_calls(path: str, added: list[str], removed: list[str], rates: dict, a: dict) -> list[dict]:
    if _skip(path) or not path.endswith(CODE_EXT + CONFIG_EXT):
        return []
    new, old = _models(added), _models(removed)
    calls, tin, tout = a["llm_calls_per_month"], a["llm_input_tokens"], a["llm_output_tokens"]
    out: list[dict] = []
    for models, sign, verb in ((new - old, 1, "calls"), (old - new, -1, "stops calling")):
        for model in sorted(models):
            rate = _model_rate(model, rates)
            if rate is None:
                out.append(_finding("llm", path, f"{verb} {model}: add its rate under rates.llm_per_mtok",
                                    severity="warn" if sign > 0 else "info"))
                continue
            per_call = (tin * rate["input"] + tout * rate["output"]) / 1e6
            monthly = sign * calls * per_call
            out.append(_finding(
                "llm", path,
                f"{verb} {model}: ${per_call * 1000:.2f} per 1k calls at {tin}/{tout} tokens, "
                f"{calls:,} calls/month assumed",
                low=monthly * 0.5, high=monthly, confidence="low",
                cheaper=rates.get("llm_cheaper", "") if sign > 0 else "",
                severity="warn" if sign > 0 else "info",
            ))
    return out


def _field_count(field: str, size: int) -> float:
    total = 0.0
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step_s = part.split("/", 1)
            step = max(int(step_s), 1) if step_s.isdigit() else 1
        if part in ("*", "?"):
            span = size
        elif "-" in part:
            lo, hi = part.split("-", 1)
            span = int(hi) - int(lo) + 1 if lo.isdigit() and hi.isdigit() else size
        else:
            span = 1
        total += max(span // step, 1) if step > 1 else span
    return total


def cron_runs_per_month(expr: str) -> float | None:
    fields = expr.split()
    if len(fields) != 5:
        return None
    minute, hour, dom, _month, dow = fields
    per_day = _field_count(minute, 60) * _field_count(hour, 24)
    if dow not in ("*", "?"):
        days = _field_count(dow, 7) * 30 / 7
    elif dom not in ("*", "?"):
        days = _field_count(dom, 30)
    else:
        days = 30
    return per_day * days


def schedules(path: str, added: list[str], _r: list[str], rates: dict, a: dict) -> list[dict]:
    if _skip(path) or not path.endswith(CONFIG_EXT + CODE_EXT):
        return []
    out: list[dict] = []
    is_ci = path.startswith(".github/workflows/")
    for line in added:
        m = CRON.search(line)
        runs = cron_runs_per_month(m.group(1)) if m else None
        if runs is None:
            continue
        if is_ci:
            cost = runs * a["ci_minutes_per_run"] * rates["ci_runner_per_minute"]["linux"]
            low, high, conf = cost, cost, "medium"
        else:
            low, high, conf = None, None, "low"
        out.append(_finding(
            "schedule", path, f"schedule '{m.group(1)}' runs about {runs:,.0f} times/month",
            low=low, high=high, confidence=conf,
            cheaper="run less often, or trigger on events instead of a timer",
            severity="warn" if runs > 1000 else "info",
        ))
    return out


def ci_runners(path: str, added: list[str], _r: list[str], rates: dict, a: dict) -> list[dict]:
    if not path.startswith(".github/workflows/") or _skip(path):
        return []
    out: list[dict] = []
    per_min = rates["ci_runner_per_minute"]
    for line in added:
        m = RUNS_ON.search(line)
        if not m:
            continue
        label = m.group(1).strip().strip("'\"").lower()
        if "macos" in label:
            kind = "macos"
        elif re.search(r"large|xl|cores|-(8|16|32|64)", label):
            kind = "large"
        else:
            continue
        monthly = a["ci_runs_per_month"] * a["ci_minutes_per_run"] * per_min[kind]
        out.append(_finding(
            "ci", path, f"job on {kind} runner '{label}'",
            low=monthly * 0.5, high=monthly, confidence="low",
            cheaper="ubuntu-latest unless the job needs the bigger or macOS runner",
        ))
    return out


def polling(path: str, added: list[str], _r: list[str], rates: dict, a: dict) -> list[dict]:
    if not _is_code(path):
        return []
    out: list[dict] = []
    for ms in poll_intervals_ms("\n".join(added)):
        if ms <= 0 or ms >= 30000:
            continue
        requests = a["concurrent_clients"] * SECONDS_PER_MONTH * 1000 / ms
        cost = requests / 1e6 * rates["requests_per_million"]
        out.append(_finding(
            "polling", path,
            f"polls every {ms} ms: about {requests:,.0f} requests/month at "
            f"{a['concurrent_clients']} open clients (request fee only)",
            low=cost, high=cost * 3, confidence="low",
            cheaper="longer interval, pause when the tab is hidden, or push with SSE / websockets",
            severity="warn" if ms < 10000 else "info",
        ))
    return out


DETECTORS = (terraform_resources, always_on_compute, llm_calls, schedules, ci_runners, polling, firestore_usage)


COMMENT_LINE = ("#", "//", "/*", "*", "<!--")


def _code_lines(lines: list[str]) -> list[str]:
    return [x for x in lines if not x.lstrip().startswith(COMMENT_LINE)]


def detect(path: str, added: list[str], removed: list[str], rates: dict, assumptions: dict) -> list[dict]:
    added, removed = _code_lines(added), _code_lines(removed)
    findings: list[dict] = []
    for detector in DETECTORS:
        findings.extend(detector(path, added, removed, rates, assumptions))
    return findings
