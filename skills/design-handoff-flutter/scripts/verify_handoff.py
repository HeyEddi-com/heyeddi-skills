#!/usr/bin/env python3
"""Verify Flutter implementation matches mockup-brief Implementation spec."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _heyeddi_paths import designs_dir
from _skill_cli import emit, fail, resolve_project_root

BRIEF_FILENAME = "mockup-brief.md"

SHELL_CHECKS: list[tuple[str, list[str], list[str]]] = [
    ("App shell widget", ["lib/widgets/app_shell.dart"], [r"class AppShell", r"NavigationDrawer|Drawer"]),
    ("Material theme", ["lib/theme/app_theme.dart"], [r"ThemeData", r"useMaterial3:\s*true"]),
    ("GoRouter routes", ["lib/router/app_router.dart"], [r"GoRoute", r"path:"]),
]

DEFAULT_ROUTE_CHECKS: list[tuple[str, list[str], list[str]]] = []


def feature_dir(root: Path, route: str, feature: str | None) -> tuple[str, Path]:
    feat = feature or route.strip("/").replace("/", "-") or "home"
    return feat, designs_dir(root) / feat


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _resolve_dart_targets(root: Path, target: str) -> list[Path]:
    paths: list[Path] = []
    for part in re.split(r"[,;]", target):
        part = part.strip().strip("`")
        if not part:
            continue
        if part.endswith(".dart") or "/" in part:
            paths.append(root / part)
        else:
            for hit in (root / "lib").rglob(f"*{part}*"):
                if hit.suffix == ".dart":
                    paths.append(hit)
    return paths


def _requirement_patterns(requirement: str) -> list[str]:
    patterns: list[str] = []
    for token in re.findall(r"--[\w-]+", requirement):
        patterns.append(re.escape(token))
    for css in re.findall(
        r"(margin-top:\s*auto|flex:\s*1|EdgeInsets|Card\(|NavigationDrawer|useMaterial3)",
        requirement,
        re.I,
    ):
        patterns.append(re.escape(css).replace(r"\ ", r"\s*"))
    if not patterns:
        words = [w for w in re.findall(r"[a-z][\w-]*", requirement.lower()) if len(w) > 4]
        if words:
            patterns.append(re.escape(words[0]))
    return patterns


def _file_matches(path: Path, patterns: list[str]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return all(re.search(p, text, re.I) for p in patterns)


def _run_named_checks(root: Path, checks: list[tuple[str, list[str], list[str]]]) -> list[dict]:
    results: list[dict] = []
    for name, rel_paths, patterns in checks:
        files = [root / p for p in rel_paths] if rel_paths else list((root / "lib").rglob("*.dart"))[:12]
        ok = any(_file_matches(f, patterns) for f in files if f.is_file())
        results.append({"check": name, "ok": ok, "files": [str(f) for f in files if f.is_file()]})
    return results


def _run_spec_table(root: Path, spec_text: str) -> list[dict]:
    results: list[dict] = []
    for line in spec_text.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 3 or cells[0].lower() in ("component / region", "component", "region"):
            continue
        name, requirement, target = cells[0], cells[1], cells[2]
        patterns = _requirement_patterns(requirement)
        paths = _resolve_dart_targets(root, target)
        if not paths:
            slug = target.replace(".dart", "").replace("lib/", "")
            paths = list((root / "lib").rglob(f"*{slug}*"))
        ok = bool(patterns) and any(_file_matches(p, patterns) for p in paths)
        results.append(
            {
                "check": name,
                "ok": ok,
                "requirement": requirement,
                "target": target,
                "patterns": patterns,
            }
        )
    return results


def route_screen_checks(root: Path, route: str, brief_text: str = "") -> list[tuple[str, list[str], list[str]]]:
    slug = route.strip("/").replace("/", "-") or "home"
    screen_name = "".join(part.capitalize() for part in slug.split("-")) + "Screen"
    rel = f"lib/screens/{slug}_screen.dart"
    alt = f"lib/screens/{screen_name.lower()}.dart"
    paths = [rel]
    if not (root / rel).is_file() and (root / alt).is_file():
        paths = [alt]
    checks = [(f"{route} screen exists", paths, [r"class \w+Screen"])]
    if re.search(r"\bCard\b", brief_text):
        checks.append((f"{route} uses Card", paths, [r"Card\("]))
        checks.append((f"{route} card padding", paths, [r"EdgeInsets"]))
    return checks


def verify_handoff(root: Path, feature_path: Path, route: str, *, phase: str = "full") -> dict:
    brief_path = feature_path / BRIEF_FILENAME
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.is_file() else ""
    spec_text = _extract_section(brief_text, "Implementation spec")

    checks: list[dict] = []
    if spec_text:
        checks.extend(_run_spec_table(root, spec_text))

    if phase in ("shell", "full"):
        checks.extend(_run_named_checks(root, SHELL_CHECKS))
    if phase == "full":
        checks.extend(_run_named_checks(root, route_screen_checks(root, route, brief_text)))

    failed = [c for c in checks if not c.get("ok")]
    return {
        "ok": len(checks) > 0 and not failed,
        "phase": phase,
        "has_implementation_spec": bool(spec_text),
        "checks": checks,
        "failed": [c.get("check") or c.get("name") for c in failed],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--feature", default=None)
    parser.add_argument("--phase", choices=["shell", "full"], default="full")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    feat, fdir = feature_dir(root, args.route, args.feature)
    result = verify_handoff(root, fdir, args.route, phase=args.phase)
    result["route"] = args.route
    result["feature"] = feat
    result["frontend"] = "flutter"
    result["mockup_brief"] = str(fdir / BRIEF_FILENAME) if (fdir / BRIEF_FILENAME).is_file() else None
    emit(json.dumps(result, indent=2))
    if args.check and not result.get("ok"):
        fail(f"{len(result.get('failed') or [])} check(s) failed: see checks[]")


if __name__ == "__main__":
    main()
