#!/usr/bin/env python3
"""Audit codebase for KISS, YAGNI, DRY, SOLID signals; write `.heyeddi/docs/` report."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from _heyeddi_paths import engineering_docs_dir, product_md, skill_docs_dir
from _skill_cli import emit, fail, resolve_project_root

MAX_FILE_LINES = 400
ERROR_FILE_LINES = 800
ABSTRACTION_HINTS = re.compile(
    r"(Factory|Manager|Orchestrator|Abstract|Base[A-Z]\w+Service)",
    re.MULTILINE,
)
ROUTER_HEAVY = re.compile(
    r"(async def|def)\s+\w+.*:\n(?:.*\n){8,}?(?=async def|def|@|$)",
    re.MULTILINE,
)


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def _scan_src(root: Path) -> list[dict]:
    findings: list[dict] = []
    src = root / "src"
    if not src.is_dir():
        return findings

    vue_files = list(src.rglob("*.vue"))
    ts_files = list(src.rglob("*.ts"))
    py_backend = list((root / "backend" / "app").rglob("*.py")) if (root / "backend").is_dir() else []

    for path in vue_files + ts_files + py_backend:
        rel = str(path.relative_to(root))
        lines = _line_count(path)
        if lines > ERROR_FILE_LINES:
            findings.append(
                {
                    "principle": "KISS",
                    "severity": "error",
                    "file": rel,
                    "message": f"File has {lines} lines (>{ERROR_FILE_LINES}): split before merge",
                }
            )
        elif lines > MAX_FILE_LINES:
            findings.append(
                {
                    "principle": "KISS",
                    "severity": "warn",
                    "file": rel,
                    "message": f"File has {lines} lines (>{MAX_FILE_LINES}): consider splitting",
                }
            )
        text = path.read_text(encoding="utf-8", errors="replace")
        if ABSTRACTION_HINTS.search(text) and "test" not in rel.lower():
            findings.append(
                {
                    "principle": "YAGNI",
                    "severity": "info",
                    "file": rel,
                    "message": "Abstraction naming detected: confirm it serves multiple call sites",
                }
            )

    router = root / "src" / "router" / "index.ts"
    if router.is_file():
        rtext = router.read_text(encoding="utf-8", errors="replace")
        if len(rtext.splitlines()) > 80:
            findings.append(
                {
                    "principle": "SOLID",
                    "severity": "warn",
                    "file": str(router.relative_to(root)),
                    "message": "Router file is large: keep routes thin; move logic to views/composables",
                }
            )

    backend_routers = list((root / "backend" / "app" / "routers").glob("*.py")) if (root / "backend").is_dir() else []
    for path in backend_routers:
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in ROUTER_HEAVY.finditer(text):
            body = match.group(0)
            if "return " in body and body.count("\n") > 12:
                findings.append(
                    {
                        "principle": "SOLID",
                        "severity": "warn",
                        "file": str(path.relative_to(root)),
                        "message": "Fat route handler: prefer service layer",
                    }
                )
                break

    views = list((src / "views").glob("*.vue")) if (src / "views").is_dir() else []
    tests = list((root / "tests").rglob("*.spec.ts")) + list((root / "tests").rglob("*.spec.js"))
    test_text = "\n".join(t.read_text(errors="replace") for t in tests if t.is_file())
    for view in views:
        name = view.stem
        if name not in test_text and "placeholder" not in view.read_text(errors="replace").lower():
            findings.append(
                {
                    "principle": "Testable",
                    "severity": "info",
                    "file": str(view.relative_to(root)),
                    "message": f"No unit test reference for {name}: add smoke spec",
                }
            )

    return findings


def _check_docs(root: Path) -> list[dict]:
    issues: list[dict] = []
    eng = engineering_docs_dir(root)
    required = ("architecture.md", "reuse-catalog.md", "decisions.md")
    for name in required:
        path = eng / name
        if not path.is_file():
            issues.append(
                {
                    "principle": "Documentation",
                    "severity": "error",
                    "file": f".heyeddi/docs/engineering/{name}",
                    "message": "Missing: run init_engineering_docs.py",
                }
            )
        elif path.stat().st_size < 100:
            issues.append(
                {
                    "principle": "Documentation",
                    "severity": "warn",
                    "file": str(path.relative_to(root)),
                    "message": "Stub: expand engineering notes",
                }
            )
    return issues


def _write_report(root: Path, findings: list[dict]) -> Path:
    skill_docs_dir(root).mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    report = skill_docs_dir(root) / f"engineering-audit-{today}.md"
    lines = [
        f"# Engineering audit: {today}",
        "",
        "Principles: **KISS**, **YAGNI**, **DRY**, **SOLID**, **Testable**.",
        "",
        f"**Findings:** {len(findings)}",
        "",
        "| Principle | Severity | File | Note |",
        "|-----------|----------|------|------|",
    ]
    for row in findings:
        lines.append(
            f"| {row['principle']} | {row['severity']} | `{row['file']}` | {row['message']} |"
        )
    lines.extend(
        [
            "",
            "## Next steps",
            "",
            "1. Update `.heyeddi/docs/engineering/architecture.md` if modules changed",
            "2. Add reuse entries before creating new wrappers",
            "3. `append_decision.py` for non-obvious trade-offs",
            "",
        ]
    )
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def audit_engineering(root: Path) -> dict:
    findings = _scan_src(root) + _check_docs(root)
    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]
    report = _write_report(root, findings)
    return {
        "ok": not errors,
        "finding_count": len(findings),
        "warn_count": len(warns),
        "report": str(report.relative_to(root)),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineering excellence audit")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--check", action="store_true", help="Exit 1 on error-severity findings")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any warn+ finding")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    result = audit_engineering(root)
    emit(json.dumps(result, indent=2))

    if args.check and not result.get("ok"):
        fail("Engineering audit failed: see report")
    if args.strict and result.get("warn_count", 0) > 0:
        fail(f"Engineering audit: {result['warn_count']} warning(s): see {result['report']}")


if __name__ == "__main__":
    main()
