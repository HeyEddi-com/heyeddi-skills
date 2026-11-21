"""Cost gate: estimate_change_cost detectors, budget gate, validation inputs, plan smell."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENG_SCRIPTS = ROOT / "skills" / "engineering-excellence" / "scripts"
sys.path.insert(0, str(ENG_SCRIPTS))

from _cost_rules import cron_runs_per_month  # noqa: E402
from check_engineering_plan import check_engineering_plan  # noqa: E402
from estimate_change_cost import estimate_change_cost, parse_diff  # noqa: E402


def _diff(path: str, added: list[str] = (), removed: list[str] = ()) -> str:
    body = "".join(f"-{x}\n" for x in removed) + "".join(f"+{x}\n" for x in added)
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n{body}"


def _init(project: Path, budget: dict | None = None) -> None:
    proc = subprocess.run(
        [sys.executable, str(ENG_SCRIPTS / "init_engineering_docs.py"), "--project-root", str(project)],
        cwd=str(ENG_SCRIPTS), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    if budget is not None:
        path = project / ".heyeddi" / "docs" / "engineering" / "budget.json"
        data = json.loads(path.read_text())
        data.update(budget)
        path.write_text(json.dumps(data))


def _drivers(result: dict) -> list[str]:
    return [f["driver"] for f in result["findings"]]


def test_init_scaffolds_budget(tmp_path: Path) -> None:
    _init(tmp_path)
    data = json.loads((tmp_path / ".heyeddi/docs/engineering/budget.json").read_text())
    assert data["change_error_monthly"] == 200
    assert "llm_calls_per_month" in data["assumptions"]


def test_parse_diff_ignores_headers_and_handles_deleted_files() -> None:
    text = _diff("infra/main.tf", added=['resource "google_compute_router_nat" "nat" {'])
    text += "diff --git a/old.tf b/old.tf\n--- a/old.tf\n+++ /dev/null\n@@ -1 +0,0 @@\n-gone\n"
    files = parse_diff(text)
    assert files["infra/main.tf"]["added"] == ['resource "google_compute_router_nat" "nat" {']
    assert files["old.tf"]["removed"] == ["gone"]


def test_terraform_resource_priced_and_removal_saves(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("infra/main.tf", added=['resource "google_sql_database_instance" "db" {'])
    diff += _diff("infra/old.tf", removed=['resource "google_compute_router_nat" "nat" {'])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    lows = sorted(f["low"] for f in result["findings"])
    assert lows == [-32, 10]
    assert result["total_monthly_high"] == 250 - 60
    assert (tmp_path / result["report"]).is_file()


def test_min_instances_is_always_on_cost(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("infra/run.tf", added=["    min_instance_count = 2"], removed=["    min_instance_count = 0"])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    finding = next(f for f in result["findings"] if f["driver"] == "always-on")
    assert finding["low"] == 14 and finding["high"] == 130
    assert "min instances 0" in finding["cheaper"]


def test_llm_model_swap_shows_saving(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("app/ai.py", added=['MODEL = "claude-haiku-5-5"'], removed=['MODEL = "claude-opus-5-5"'])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    by_msg = {f["message"].split(":")[0]: f for f in result["findings"]}
    # 10k calls * (2000 * $4 + 500 * $20) / 1M = $180 for Opus; Haiku is $4.50
    assert by_msg["stops calling claude-opus-5-5"]["high"] == -180
    assert by_msg["calls claude-haiku-5-5"]["high"] == 4.5
    assert result["total_monthly_high"] < 0


def test_unknown_model_flagged_without_price(tmp_path: Path) -> None:
    _init(tmp_path)
    result = estimate_change_cost(tmp_path, diff_text=_diff("app/ai.ts", added=['model: "gpt-9-mini"']))
    assert result["unknown_count"] == 1


def test_docs_and_tests_do_not_count(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("README.md", added=["Use claude-opus-5-5 with min_instances = 3"])
    diff += _diff("tests/test_ai.py", added=['MODEL = "claude-opus-5-5"'])
    assert estimate_change_cost(tmp_path, diff_text=diff)["findings"] == []


def test_fixtures_tests_and_regex_source_do_not_count(tmp_path: Path) -> None:
    """Regression: the gate flagged its own tests and detector regex on first dogfood run."""
    _init(tmp_path)
    diff = _diff("tests/test_cost.py", added=["    min_instance_count = 2", "    - cron: '*/10 * * * *'"])
    diff += _diff("fixtures/app/infra/main.tf", added=['resource "google_container_cluster" "c" {'])
    diff += _diff("scripts/rules.py", added=['CPU = re.compile(r"(--no-cpu-throttling)")'])
    assert estimate_change_cost(tmp_path, diff_text=diff)["findings"] == []


@pytest.mark.parametrize(
    "expr,runs",
    [("*/5 * * * *", 12 * 24 * 30), ("0 3 * * *", 30), ("0 9 * * 1-5", 5 * 30 / 7), ("bad", None)],
)
def test_cron_runs_per_month(expr: str, runs: float | None) -> None:
    assert cron_runs_per_month(expr) == runs


def test_ci_schedule_and_macos_runner(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff(".github/workflows/nightly.yml", added=["    - cron: '*/10 * * * *'", "    runs-on: macos-latest"])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    assert set(_drivers(result)) == {"schedule", "ci"}
    sched = next(f for f in result["findings"] if f["driver"] == "schedule")
    assert sched["severity"] == "warn"  # 4,320 runs/month


def test_fast_polling_in_frontend(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("src/views/Dash.vue", added=["  setInterval(refresh, 2000)", "  setInterval(slow, 60000)"])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    assert len(result["findings"]) == 1
    assert result["findings"][0]["driver"] == "polling"


def test_over_budget_fails_then_approval_records_adr(tmp_path: Path) -> None:
    _init(tmp_path, {"change_error_monthly": 100})
    diff = _diff("infra/gke.tf", added=['resource "google_container_cluster" "main" {'])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    assert result["ok"] is False
    approved = estimate_change_cost(tmp_path, diff_text=diff, approved="Need GKE for GPU jobs")
    assert approved["ok"] is True
    decisions = (tmp_path / ".heyeddi/docs/engineering/decisions.md").read_text()
    assert "Cost approved over budget" in decisions and "GPU jobs" in decisions


def test_monthly_limit_uses_current_spend(tmp_path: Path) -> None:
    _init(tmp_path, {"monthly_limit": 100, "current_monthly": 90, "change_error_monthly": None})
    diff = _diff("infra/nat.tf", added=['resource "google_compute_router_nat" "nat" {'])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    assert result["ok"] is False
    assert any("monthly_limit" in b["message"] for b in result["budget_findings"])


def test_missing_budget_warns_but_passes(tmp_path: Path) -> None:
    result = estimate_change_cost(tmp_path, diff_text="")
    assert result["ok"] is True
    assert any("No budget.json" in b["message"] for b in result["budget_findings"])


def test_terraform_plan_replaces_diff_guess(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("infra/main.tf", added=['resource "google_sql_database_instance" "db" {'])
    plan = {"resource_changes": [
        {"address": "google_redis_instance.cache", "type": "google_redis_instance", "change": {"actions": ["create"]}},
        {"address": "google_compute_address.old", "type": "google_compute_address", "change": {"actions": ["delete"]}},
        {"address": "google_storage_bucket.b", "type": "google_storage_bucket", "change": {"actions": ["no-op"]}},
    ]}
    result = estimate_change_cost(tmp_path, diff_text=diff, terraform_plan=plan)
    assert _drivers(result) == ["terraform-plan", "terraform-plan"]
    assert result["total_monthly_high"] == 250 - 8


def test_infracost_overrides_terraform(tmp_path: Path) -> None:
    _init(tmp_path)
    diff = _diff("infra/main.tf", added=['resource "google_sql_database_instance" "db" {', "  min_instance_count = 1"])
    diff += _diff("app/ai.py", added=['MODEL = "claude-sonnet-5-5"'])
    result = estimate_change_cost(tmp_path, diff_text=diff, infracost={"diffTotalMonthlyCost": "42.5"})
    assert sorted(_drivers(result)) == ["infracost", "llm"]
    assert "infracost" in result["sources"]


def test_cli_check_reads_git_diff(tmp_path: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    _init(tmp_path, {"change_error_monthly": 50})

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
    git("checkout", "-q", "-b", "feat")
    (tmp_path / "infra").mkdir()
    (tmp_path / "infra" / "db.tf").write_text('resource "google_sql_database_instance" "db" {\n}\n')
    proc = subprocess.run(
        [sys.executable, str(ENG_SCRIPTS / "estimate_change_cost.py"), "--project-root", str(tmp_path), "--check"],
        cwd=str(ENG_SCRIPTS), capture_output=True, text=True,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["base"] == "main"
    assert payload["findings"][0]["file"] == "infra/db.tf"


def test_plan_gate_warns_on_cost_driver_without_estimate(tmp_path: Path) -> None:
    _init(tmp_path)
    bare = check_engineering_plan(tmp_path, "Add Cloud SQL and set min instances to 1.", "plan.md")
    assert bare["ok"] is True
    assert any(f["principle"] == "Budget" for f in bare["findings"])
    costed = check_engineering_plan(
        tmp_path, "Add Cloud SQL (~$10/month, budget ok; rejected AlloyDB).", "plan.md"
    )
    assert not any(f["principle"] == "Budget" for f in costed["findings"])


PRE_MERGE = ROOT / "skills" / "pre-merge-gate" / "scripts" / "pre_merge_gate.py"
QUIET = ["--skip-backend", "--skip-duplicate-ui", "--skip-prose-audit", "--skip-visual-audit",
         "--skip-setup-audit", "--skip-engineering-audit"]


def _pre_merge(project: Path, *extra: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(PRE_MERGE), "--project-root", str(project), *QUIET, *extra],
        cwd=str(PRE_MERGE.parent), capture_output=True, text=True,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def test_pre_merge_runs_cost_estimate(tmp_path: Path) -> None:
    _init(tmp_path)
    _code, out = _pre_merge(tmp_path)
    assert "| cost-estimate | PASS |" in out


def test_pre_merge_cost_skip_blocked_under_signoff(tmp_path: Path) -> None:
    _init(tmp_path)
    code, out = _pre_merge(tmp_path, "--skip-cost-estimate", "--signoff", "--no-pr", "--skip-git-clean")
    assert "| cost-estimate | FAIL |" in out
    assert "--skip-cost-estimate" in out
    assert code != 0


# --- Firestore reads: usage-based cost that Terraform never shows ---

def _fs(tmp_path: Path, path: str, added: list[str], removed: list[str] = ()) -> dict:
    _init(tmp_path)
    return estimate_change_cost(tmp_path, diff_text=_diff(path, added=added, removed=list(removed)))


def test_polled_unbounded_query_blows_the_reads_limit(tmp_path: Path) -> None:
    """The incident shape: a collection read on a timer, no limit(), few clients."""
    result = _fs(tmp_path, "src/composables/useEvents.ts", [
        "setInterval(async () => {",
        "  const snap = await getDocs(collection(db, 'events'))",
        "}, 5000)",
    ])
    assert result["firestore_reads_per_day"] > 100_000_000
    assert result["ok"] is False
    assert any("firestore_reads_per_day_limit" in b["message"] for b in result["budget_findings"])
    assert any("polled every 5000 ms" in f["message"] for f in result["findings"])


def test_unbounded_listener_priced_and_limit_fixes_it(tmp_path: Path) -> None:
    loose = _fs(tmp_path, "src/views/Feed.vue", ["onSnapshot(collection(db, 'posts'), (s) => {})"])
    assert loose["firestore_reads_per_day"] == 200 * 1000 + 50 * 5000
    assert "no limit" in loose["findings"][0]["message"]
    assert "limit()" in loose["findings"][0]["cheaper"]

    tight = _fs(tmp_path, "src/views/Feed.vue", ["onSnapshot(query(collection(db, 'posts'), limit(20)), (s) => {})"])
    assert tight["firestore_reads_per_day"] == 200 * 20 + 50 * 5000
    assert "no limit" not in tight["findings"][0]["message"]


def test_single_doc_listener_is_cheap(tmp_path: Path) -> None:
    result = _fs(tmp_path, "src/views/Me.vue", ["onSnapshot(doc(db, 'users', uid), (s) => {})"])
    assert result["firestore_reads_per_day"] == 200 * 1 + 50 * 5000


def test_read_inside_loop_multiplies(tmp_path: Path) -> None:
    result = _fs(tmp_path, "src/services/orders.ts", [
        "for (const id of ids) {",
        "  const snap = await getDoc(doc(db, 'orders', id))",
        "}",
    ])
    assert result["firestore_reads_per_day"] == 200 * 20
    assert "inside a loop" in result["findings"][0]["message"]


def test_fixing_a_query_shows_the_saving(tmp_path: Path) -> None:
    result = _fs(
        tmp_path, "src/views/Feed.vue",
        added=["const snap = await getDocs(query(collection(db, 'posts'), limit(25)))"],
        removed=["const snap = await getDocs(collection(db, 'posts'))"],
    )
    assert result["firestore_reads_per_day"] == 200 * 25 - 200 * 1000
    assert result["total_monthly_high"] < 0


def test_python_and_dart_reads_detected(tmp_path: Path) -> None:
    py = _fs(tmp_path, "backend/app/jobs.py", ["docs = db.collection('events').stream()"])
    assert py["firestore_reads_per_day"] == 200 * 1000
    dart = _fs(tmp_path, "lib/feed.dart", ["FirebaseFirestore.instance.collection('posts').snapshots().listen((s) {});"])
    assert dart["firestore_reads_per_day"] > 0


def test_limit_declared_before_the_read_counts(tmp_path: Path) -> None:
    result = _fs(tmp_path, "src/services/feed.ts", [
        "const q = query(collection(db, 'posts'), limit(25))",
        "const snap = await getDocs(q)",
    ])
    assert result["firestore_reads_per_day"] == 200 * 25
    assert "no limit" not in result["findings"][0]["message"]


def test_getdoc_is_never_labelled_no_limit(tmp_path: Path) -> None:
    result = _fs(tmp_path, "src/services/user.ts", ["const snap = await getDoc(ref)"])
    assert result["findings"], result
    assert "no limit" not in result["findings"][0]["message"]


def test_unrelated_get_calls_are_not_firestore(tmp_path: Path) -> None:
    result = _fs(tmp_path, "src/util/cache.ts", ["const hit = cache.get()", "const v = map.get()"])
    assert result["findings"] == []


def test_firestore_trigger_that_writes_is_flagged(tmp_path: Path) -> None:
    result = _fs(tmp_path, "functions/src/index.ts", [
        "export const onChange = onDocumentWritten('items/{id}', async (event) => {",
        "  await event.data.after.ref.update({ touched: true })",
        "})",
    ])
    assert any("retrigger" in f["message"] for f in result["findings"])


def test_usage_cost_without_billing_alert_warns_until_terraform_has_one(tmp_path: Path) -> None:
    diff = _diff("src/views/Feed.vue", added=["onSnapshot(query(collection(db, 'posts'), limit(20)), cb)"])
    _init(tmp_path, {"firestore_reads_per_day_limit": None, "change_warn_monthly": None})
    before = estimate_change_cost(tmp_path, diff_text=diff)
    assert any("google_billing_budget" in b["message"] for b in before["budget_findings"])
    (tmp_path / "infra").mkdir()
    (tmp_path / "infra" / "billing.tf").write_text('resource "google_billing_budget" "b" {}\n')
    after = estimate_change_cost(tmp_path, diff_text=diff)
    assert not any("google_billing_budget" in b["message"] for b in after["budget_findings"])


def test_multiline_set_interval_counts_as_polling(tmp_path: Path) -> None:
    """Regression: only one-line setInterval(fn, ms) was recognized."""
    _init(tmp_path)
    diff = _diff("src/views/Dash.vue", added=["setInterval(async () => {", "  await refresh()", "}, 2000)"])
    result = estimate_change_cost(tmp_path, diff_text=diff)
    assert [f["driver"] for f in result["findings"]] == ["polling"]


def test_commented_out_cost_is_ignored(tmp_path: Path) -> None:
    """Regression: the gate priced an example call inside the detector's own docstring."""
    _init(tmp_path)
    diff = _diff("src/views/Old.vue", added=["// onSnapshot(collection(db, 'posts'), cb)", "# min_instances = 5"])
    diff += _diff("infra/old.tf", added=['# resource "google_container_cluster" "c" {'])
    assert estimate_change_cost(tmp_path, diff_text=diff)["findings"] == []
