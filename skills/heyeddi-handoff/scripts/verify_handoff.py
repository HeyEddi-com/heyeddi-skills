#!/usr/bin/env python3
"""Verify implementation matches mockup-brief Implementation spec."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _heyeddi_paths import designs_dir
from _skill_cli import emit, fail, resolve_project_root

BRIEF_FILENAME = "mockup-brief.md"

# Extra checks for the app-shell and settings layouts. Each runs only when the spec names its files or tokens.
SHELL_CHECKS: list[tuple[str, list[str], list[str]]] = [
    (
        "Sidebar width token",
        ["src/styles/tokens.css"],
        [r"--sidebar-width"],
    ),
    (
        "Sidebar flex column + user pinned",
        ["src/components/layout/AppSidebar.vue"],
        [r"flex-direction:\s*column", r"margin-top:\s*auto"],
    ),
    (
        "Nav active brand pill",
        ["src/components/layout/AppSidebar.vue"],
        [r"brand-subtle", r"nav-link--active|active"],
    ),
    (
        "App shell layout",
        ["src/components/layout/AppShell.vue"],
        [r"AppSidebar", r"app-shell"],
    ),
    (
        "Top bar height token",
        ["src/styles/tokens.css", "src/components/layout/AppTopBar.vue"],
        [r"--topbar-height"],
    ),
]

ROUTE_CHECKS: list[tuple[str, list[str], list[str]]] = [
    (
        "Settings cards use Card",
        ["src/views/SettingsView.vue"],
        [r"Card", r"settings__cards|settings__card"],
    ),
    (
        "Settings Card body uses #content slot",
        ["src/views/SettingsView.vue"],
        [r"<template\s+#content>", r"Card"],
    ),
    (
        "Card stack gap",
        ["src/views/SettingsView.vue"],
        [r"gap:\s*var\(--size-"],
    ),
    (
        "Save CTA outside cards",
        ["src/views/SettingsView.vue"],
        [r"Save changes", r"settings__save"],
    ),
    (
        "Content max-width",
        ["src/styles/tokens.css", "src/views/SettingsView.vue"],
        [r"--content-max-width|max-width"],
    ),
]

CARD_BLOCK = re.compile(r"<Card\b[^>]*>([\s\S]*?)</Card>", re.IGNORECASE)
TEMPLATE_SLOT = re.compile(r"<template\s+#([\w-]+)>[\s\S]*?</template>", re.IGNORECASE)
BODY_ELEMENT = re.compile(
    r"<\s*(div|label|InputText|ToggleSwitch|Button|span|p|form|section|DataTable|Column|Tag)\b",
    re.IGNORECASE,
)


def find_primevue_card_slot_issues(text: str, *, source: str = "unknown") -> list[dict]:
    """Fail when Card has loose body elements outside named slots (PrimeVue drops them)."""
    issues: list[dict] = []
    for index, match in enumerate(CARD_BLOCK.finditer(text), start=1):
        body = match.group(1)
        slots = {slot.lower() for slot in TEMPLATE_SLOT.findall(body)}
        remainder = TEMPLATE_SLOT.sub("", body).strip()
        if BODY_ELEMENT.search(remainder) and "content" not in slots:
            preview = remainder.split("\n", 1)[0].strip()[:80]
            issues.append(
                {
                    "source": source,
                    "card_index": index,
                    "message": (
                        "PrimeVue Card has body elements outside <template #content> "
                        f"(found: {preview!r})"
                    ),
                }
            )
    return issues


def verify_primevue_card_slots(root: Path) -> dict:
    """Scan Vue sources for Card slot misuse."""
    all_issues: list[dict] = []
    for path in sorted((root / "src").rglob("*.vue")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "<Card" not in text:
            continue
        rel = str(path.relative_to(root))
        all_issues.extend(find_primevue_card_slot_issues(text, source=rel))
    return {"ok": not all_issues, "issues": all_issues}


def feature_dir(root: Path, route: str, feature: str | None) -> tuple[str, Path]:
    feat = feature or route.strip("/").replace("/", "-") or "home"
    return feat, designs_dir(root) / feat


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _resolve_targets(root: Path, target: str) -> list[Path]:
    paths: list[Path] = []
    for part in re.split(r"[,;]", target):
        part = part.strip().strip("`")
        if not part:
            continue
        if "/" in part or part.endswith((".vue", ".css", ".ts")):
            paths.append(root / part)
        else:
            # Component name → search layout folder
            for hit in (root / "src").rglob(f"{part}*"):
                if hit.suffix in {".vue", ".css"}:
                    paths.append(hit)
    return paths


def _requirement_patterns(requirement: str) -> list[str]:
    patterns: list[str] = []
    for token in re.findall(r"--[\w-]+", requirement):
        patterns.append(re.escape(token))
    for css in re.findall(
        r"(margin-top:\s*auto|flex:\s*1|brand-subtle|justify-content:\s*flex-end|gap:\s*var\(--size-)",
        requirement,
        re.I,
    ):
        patterns.append(re.escape(css).replace(r"\ ", r"\s*"))
    if "padding" in requirement.lower() and "card" in requirement.lower():
        patterns.append(r"p-card-body|\.p-card")
    if not patterns:
        # Loose: any significant word from requirement
        words = [w for w in re.findall(r"[a-z][\w-]*", requirement.lower()) if len(w) > 4]
        if words:
            patterns.append(re.escape(words[0]))
    return patterns


def _file_matches(path: Path, patterns: list[str]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return all(re.search(p, text, re.I) for p in patterns)


def _run_named_checks(
    root: Path,
    checks: list[tuple[str, list[str], list[str]]],
) -> list[dict]:
    results: list[dict] = []
    for name, rel_paths, patterns in checks:
        files = [root / p for p in rel_paths]
        ok = any(_file_matches(f, patterns) for f in files if f.is_file())
        results.append(
            {
                "name": name,
                "ok": ok,
                "files": [str(f) for f in files if f.is_file()],
                "patterns": patterns,
            }
        )
    return results


def _named_in_spec(
    checks: list[tuple[str, list[str], list[str]]], spec_text: str
) -> list[tuple[str, list[str], list[str]]]:
    """Keep checks whose component or token the Implementation spec mentions."""
    selected = []
    for check in checks:
        names = [Path(p).stem for p in check[1] if p.endswith(".vue")]
        names += [pattern for pattern in check[2] if pattern.startswith("--") and "|" not in pattern]
        if any(name in spec_text for name in names):
            selected.append(check)
    return selected


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
        paths = _resolve_targets(root, target)
        if not paths:
            paths = list((root / "src").rglob("*.vue"))[:3]
        ok = bool(patterns) and any(_file_matches(p, patterns) for p in paths)
        results.append(
            {
                "name": name,
                "ok": ok,
                "requirement": requirement,
                "target": target,
                "patterns": patterns,
            }
        )
    return results


def verify_handoff(
    root: Path,
    feature_path: Path,
    *,
    phase: str = "full",
) -> dict:
    bp = feature_path / BRIEF_FILENAME
    brief_text = bp.read_text() if bp.is_file() else ""
    spec_text = _extract_section(brief_text, "Implementation spec")

    checks: list[dict] = [{"name": "Implementation spec present", "ok": bool(spec_text)}]
    if spec_text:
        checks.extend(_run_spec_table(root, spec_text))

    if phase in ("shell", "full"):
        checks.extend(_run_named_checks(root, _named_in_spec(SHELL_CHECKS, spec_text)))
    if phase == "full":
        checks.extend(_run_named_checks(root, _named_in_spec(ROUTE_CHECKS, spec_text)))

    card_slot = verify_primevue_card_slots(root)
    checks.append(
        {
            "name": "PrimeVue Card #content slots",
            "ok": card_slot["ok"],
            "issues": card_slot.get("issues") or [],
        }
    )

    failed = [c for c in checks if not c.get("ok")]
    return {
        "ok": not failed,
        "phase": phase,
        "has_implementation_spec": bool(spec_text),
        "checks": checks,
        "failed": [c["name"] for c in failed],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify handoff implementation vs brief spec")
    parser.add_argument("--route", required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--feature", default=None)
    parser.add_argument("--phase", choices=("shell", "full"), default="full")
    parser.add_argument("--check", action="store_true", help="Exit 1 if verification fails")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    feat, fdir = feature_dir(root, args.route, args.feature)
    result = verify_handoff(root, fdir, phase=args.phase)
    result["route"] = args.route
    result["feature"] = feat
    emit(json.dumps(result, indent=2))

    if args.check and not result.get("ok"):
        failed_names = result.get("failed") or ["unknown"]
        extra = ""
        for check in result.get("checks") or []:
            if check.get("name") == "PrimeVue Card #content slots" and check.get("issues"):
                details = "; ".join(
                    f"{row['source']}: {row['message']}" for row in check["issues"][:3]
                )
                extra = f" ({details})"
                break
        fail(
            "Handoff verification failed: "
            + ", ".join(failed_names)
            + extra
            + ". See reference/primevue-card-slots.md and mockup-brief Implementation spec."
        )


if __name__ == "__main__":
    main()
