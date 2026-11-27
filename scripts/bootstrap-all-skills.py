#!/usr/bin/env python3
"""Bootstrap all 11 HeyEddi skills with full triad structure under skills/."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TEMPLATE_CLI = REPO_ROOT / "templates" / "skill" / "scripts" / "_skill_cli.py"
REGISTER_TOOLS = REPO_ROOT / "scripts" / "cloud" / "register_tools.py"

PROJECT_ROOT_PARAM = {
    "type": "string",
    "description": "Workspace root path",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def copy_skill_cli(dest_scripts: Path) -> None:
    dest_scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_CLI, dest_scripts / "_skill_cli.py")


def manifest(skill: str, tools: list[dict]) -> str:
    return json.dumps(
        {"skill": skill, "version": "1.0.0", "tools": tools},
        indent=2,
    ) + "\n"


def skill_md(
    name: str,
    description: str,
    *,
    disable: bool = False,
    paths: list[str] | None = None,
    body: str,
) -> str:
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
    ]
    if disable:
        lines.append("disable-model-invocation: true")
    if paths:
        lines.append("paths:")
        for p in paths:
            lines.append(f"  - \"{p}\"")
    lines.extend(["---", "", body])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Skill definitions
# ---------------------------------------------------------------------------

SKILLS: dict[str, dict] = {}


def define_primevue_openprops_architect() -> None:
    name = "primevue-openprops-architect"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Enforces PrimeVue + OpenProps design system rules when editing Vue or CSS. "
                "Runs vue-tsc and stylelint when available. Use during any Vue SFC or stylesheet work.",
                paths=["**/*.vue", "**/*.css", "**/*.scss"],
                body=dedent("""
                    # PrimeVue + OpenProps Architect

                    ## When to use

                    - Editing `.vue` single-file components or project stylesheets
                    - Agent is about to add UI components, tokens, or layout
                    - Validating generated Vue against team design system

                    ## Instructions

                    1. Read `context/VOCABULARY.md` and `context/ANTI_PATTERNS.md` before writing UI code.
                    2. Reuse PrimeVue components from the project catalog — never invent props.
                    3. Use OpenProps CSS variables only (`var(--surface-1)`, `var(--font-sans)`).
                    4. After edits, run `python scripts/validate_vue.py --project-root <root>`.
                    5. Fix all reported issues before finishing.

                    ## Scripts

                    - `validate_vue.py` — runs `vue-tsc --noEmit` and stylelint if installed
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "validate_vue",
                        "description": "Run vue-tsc and stylelint against the project; return warnings as text.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/validate_vue.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — PrimeVue + OpenProps

                - Use OpenProps tokens: `var(--surface-1)`, `var(--surface-2)`, `var(--font-sans)`, `var(--size-fluid-3)`.
                - PrimeVue components in use: Button, DataTable, Dialog, InputText, Card, Panel, Toast.
                - Vue 3 `<script setup lang="ts">` with typed props and `defineEmits`.
                - Import shared wrappers from `@/components/ui/` before creating new primitives.
                - Spacing scale: OpenProps fluid sizes only — no arbitrary `px` padding.
                - Typography: `var(--font-size-2)` through `var(--font-size-5)` for hierarchy.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — PrimeVue + OpenProps

                - NEVER use inline `style=""` attributes or hardcoded hex colors (`#fff`, `#333`).
                - NEVER invent PrimeVue props — check component API before use.
                - NEVER duplicate Button/Input wrappers when a shared component exists.
                - NEVER use Tailwind utility classes if the project uses OpenProps.
                - NEVER add raw `<style>` blocks with magic numbers — use design tokens.
                - NEVER import PrimeVue components globally when the project uses on-demand registration.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — PrimeVue + OpenProps

                ## Good — token-based card

                ```vue
                <template>
                  <Card class="settings-card">
                    <template #title>Profile</template>
                    <p class="settings-card__hint">Update your display name.</p>
                  </Card>
                </template>

                <style scoped>
                .settings-card {
                  background: var(--surface-2);
                  padding: var(--size-fluid-3);
                }
                .settings-card__hint {
                  color: var(--text-2);
                  font-size: var(--font-size-2);
                }
                </style>
                ```

                ## Bad — hardcoded styles

                ```vue
                <template>
                  <div style="background: #fff; padding: 16px;">
                    <Button label="Save" color="blue" />
                  </div>
                </template>
                ```
            """),
            "scripts/validate_vue.py": dedent('''
                #!/usr/bin/env python3
                """Run vue-tsc and stylelint if available."""
                from __future__ import annotations

                import argparse
                import shutil
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root, run_command


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Validate Vue + CSS")
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    sections: list[str] = []

                    if shutil.which("npx"):
                        sections.append("## vue-tsc")
                        sections.append(
                            run_command(["npx", "vue-tsc", "--noEmit"], root)
                            if (root / "node_modules").is_dir()
                            else "[skip] node_modules not found — run npm install first"
                        )
                        if shutil.which("stylelint") or (root / "node_modules" / ".bin" / "stylelint").exists():
                            sections.append("## stylelint")
                            cmd = ["npx", "stylelint", "**/*.{css,vue,scss}"] if (root / "node_modules").is_dir() else ["stylelint", "**/*.{css,vue,scss}"]
                            sections.append(run_command(cmd, root))
                        else:
                            sections.append("## stylelint\n[skip] stylelint not installed")
                    else:
                        sections.append("[skip] npx not found — install Node.js to run vue-tsc/stylelint")

                    emit("\\n\\n".join(sections))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_verify_build() -> None:
    name = "verify-build"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Runs npm run build to catch Vite/Rollup failures before merge. "
                "Use when validating frontend changes or in CI pre-merge loops.",
                paths=["package.json", "**/*.vue", "**/*.ts"],
                body=dedent("""
                    # Verify Build

                    ## When to use

                    - Before opening or approving a PR with frontend changes
                    - After refactoring imports, routes, or Vite config
                    - When static generation or bundle errors are suspected

                    ## Instructions

                    1. Ensure dependencies are installed (`npm ci` or `npm install`).
                    2. Run `bash scripts/verify_build.sh --project-root <root>`.
                    3. If build fails, read the Rollup/Vite stack trace and fix imports or types.
                    4. Re-run until output shows success.

                    ## Scripts

                    - `verify_build.sh` — executes `npm run build` and returns combined output
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "verify_build",
                        "description": "Run npm run build and return stdout/stderr.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/verify_build.sh",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Build verification

                - Standard command: `npm run build` (Vite static build).
                - Success means zero exit code and no Rollup resolution errors.
                - Check `package.json` scripts for project-specific build targets.
                - Environment: Node 20+ recommended for Vite 5+ projects.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Build verification

                - NEVER merge when `verify_build` exits non-zero.
                - NEVER silence build warnings that indicate missing chunks or dynamic import failures.
                - NEVER assume dev-server success implies production build success.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Build verification

                ## Typical failure — unresolved import

                ```
                [exit 1]
                Could not resolve "./MissingComponent.vue" from src/views/Settings.vue
                ```

                Fix: correct the import path or add the missing file, then re-run verify_build.

                ## Success

                ```
                vite v5.4.0 building for production...
                ✓ built in 4.2s
                ```
            """),
            "scripts/verify_build.sh": dedent('''
                #!/usr/bin/env bash
                set -euo pipefail
                PROJECT_ROOT="."
                while [[ $# -gt 0 ]]; do
                  case "$1" in
                    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
                    *) echo "Unknown arg: $1" >&2; exit 1 ;;
                  esac
                done
                cd "$PROJECT_ROOT"
                if ! command -v npm >/dev/null 2>&1; then
                  echo "[error] npm not found — install Node.js"
                  exit 0
                fi
                if [[ ! -f package.json ]]; then
                  echo "[error] package.json not found in $PROJECT_ROOT"
                  exit 0
                fi
                npm run build 2>&1
            '''),
        }
    }


def define_visual_auditor() -> None:
    name = "visual-auditor"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Captures responsive screenshots via Playwright when available, or extracts a layout JSON tree as fallback. "
                "Use when checking mobile/desktop layout, spacing, or comparing UI to a reference image.",
                body=dedent("""
                    # Visual Auditor

                    ## When to use

                    - Designer or QA needs proof of responsive layout (375/768/1440)
                    - Comparing implemented route against reference screenshots
                    - Playwright unavailable → use layout tree fallback

                    ## Instructions

                    1. Start dev server or set `DEV_SERVER_URL` (default `http://localhost:5173`).
                    2. Run `python scripts/audit_ui.py --route /path --project-root <root>`.
                    3. If Playwright missing, run `python scripts/layout_tree.py` for dimension JSON.
                    4. Review artifacts under `.visual-audit/` or returned paths.

                    ## Env

                    - `DEV_SERVER_URL` — base URL for the SPA
                    - `ARTIFACT_BUCKET` — cloud: GCS upload target
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "capture_screenshots",
                        "description": "Capture responsive screenshots of a route at multiple viewport widths.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "route": {"type": "string", "description": "App route e.g. /settings"},
                                "project_root": PROJECT_ROOT_PARAM,
                                "widths": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "description": "Viewport widths (default 375,768,1440)",
                                },
                            },
                            "required": ["route", "project_root"],
                        },
                        "script": "scripts/audit_ui.py",
                        "readonly": True,
                    },
                    {
                        "name": "extract_layout",
                        "description": "Extract computed layout dimensions as JSON (no Playwright required).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "route": {"type": "string", "description": "App route e.g. /settings"},
                                "project_root": PROJECT_ROOT_PARAM,
                            },
                            "required": ["route", "project_root"],
                        },
                        "script": "scripts/layout_tree.py",
                        "readonly": True,
                    },
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Visual audit

                - Breakpoints: 375 (mobile), 768 (tablet), 1440 (desktop).
                - Visual hierarchy: clear heading scale, consistent section spacing, aligned form labels.
                - Density: comfortable touch targets (min 44px) on mobile widths.
                - Empty states must be visible at mobile — not hidden overflow.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Visual audit

                - NEVER approve UI based on desktop-only IDE preview.
                - NEVER ignore horizontal scroll at 375px width.
                - NEVER stack more than one primary CTA above the fold on mobile.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Visual audit

                ## Invoke screenshot capture

                ```bash
                python scripts/audit_ui.py --route /settings --project-root .
                ```

                ## Layout tree fallback output

                ```json
                {"route": "/settings", "elements": [{"tag": "main", "width": 375, "height": 812}]}
                ```
            """),
            "scripts/audit_ui.py": dedent('''
                #!/usr/bin/env python3
                """Capture responsive screenshots with Playwright (optional)."""
                from __future__ import annotations

                import argparse
                import json
                import os
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Visual audit screenshots")
                    parser.add_argument("--route", required=True)
                    parser.add_argument("--project-root", default=None)
                    parser.add_argument("--widths", default="375,768,1440")
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    widths = [int(w) for w in args.widths.split(",") if w.strip()]
                    base_url = os.environ.get("DEV_SERVER_URL", "http://localhost:5173")
                    out_dir = root / ".visual-audit"
                    out_dir.mkdir(parents=True, exist_ok=True)

                    try:
                        from playwright.sync_api import sync_playwright  # noqa: PLC0415
                    except ImportError:
                        emit(
                            "[skip] Playwright not installed.\\n"
                            "Install: pip install playwright && playwright install chromium\\n"
                            "Fallback: python scripts/layout_tree.py --route "
                            + args.route
                            + " --project-root "
                            + str(root)
                        )
                        return

                    artifacts: list[str] = []
                    url = base_url.rstrip("/") + args.route
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        for w in widths:
                            page = browser.new_page(viewport={"width": w, "height": 900})
                            try:
                                page.goto(url, wait_until="networkidle", timeout=15000)
                            except Exception as exc:
                                emit(f"[warn] navigation failed for {url}: {exc}")
                                browser.close()
                                return
                            slug = args.route.strip("/").replace("/", "_") or "home"
                            path = out_dir / f"{slug}_{w}px.png"
                            page.screenshot(path=str(path), full_page=True)
                            artifacts.append(str(path))
                            page.close()
                        browser.close()

                    emit(json.dumps({"route": args.route, "artifacts": artifacts}, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
            "scripts/layout_tree.py": dedent('''
                #!/usr/bin/env python3
                """Fallback layout extractor when Playwright or vision is unavailable."""
                from __future__ import annotations

                import argparse
                import json
                import os

                from _skill_cli import emit, resolve_project_root


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Layout tree fallback")
                    parser.add_argument("--route", required=True)
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    base_url = os.environ.get("DEV_SERVER_URL", "http://localhost:5173")

                    try:
                        from playwright.sync_api import sync_playwright  # noqa: PLC0415
                    except ImportError:
                        emit(
                            json.dumps(
                                {
                                    "route": args.route,
                                    "mode": "stub",
                                    "message": "Playwright not installed — returning placeholder layout tree",
                                    "elements": [
                                        {"tag": "body", "width": 375, "height": 800, "note": "install playwright for real data"}
                                    ],
                                },
                                indent=2,
                            )
                        )
                        return

                    url = base_url.rstrip("/") + args.route
                    tree: list[dict] = []
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page(viewport={"width": 375, "height": 900})
                        try:
                            page.goto(url, wait_until="networkidle", timeout=15000)
                            for sel in ["main", "header", "nav", "footer", "h1", "form"]:
                                loc = page.locator(sel).first
                                if loc.count():
                                    box = loc.bounding_box()
                                    if box:
                                        tree.append({"selector": sel, **{k: round(v) for k, v in box.items()}})
                        except Exception as exc:
                            emit(f"[warn] layout extraction failed: {exc}")
                        finally:
                            browser.close()

                    emit(json.dumps({"route": args.route, "project_root": str(root), "elements": tree}, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_design_handoff() -> None:
    name = "heyeddi-handoff"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Implements screens from designer screenshots and handoff notes. "
                "Loads DESIGN.md, maps regions to PrimeVue components, chains validation and visual audit. "
                "Use when Designer provides route, attachments, and notes — not for greenfield design.",
                body=dedent("""
                    # Design Handoff

                    ## When to use

                    - Designer attaches desktop/mobile screenshots for a route
                    - `designs/<feature>/` folder exists with reference images
                    - Implementing an approved mockup without Figma MCP

                    ## Instructions

                    1. Run `python scripts/load_handoff.py --route <route> --project-root <root>`.
                    2. Read `reference/screenshot-mode.md` for v1 workflow.
                    3. Load `DESIGN.md` and component catalog from project root.
                    4. Map screenshot regions → existing PrimeVue components.
                    5. Implement, then chain `@primevue-openprops-architect` → `@visual-auditor`.

                    ## Modes

                    - Screenshot (v1): `reference/screenshot-mode.md`
                    - Penpot (future): `reference/penpot-mode.md`
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "load_handoff",
                        "description": "Resolve screenshots and notes into a normalized handoff brief.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "route": {"type": "string", "description": "Target route e.g. /settings"},
                                "project_root": PROJECT_ROOT_PARAM,
                                "feature": {"type": "string", "description": "Feature folder under designs/"},
                            },
                            "required": ["route", "project_root"],
                        },
                        "script": "scripts/load_handoff.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Design handoff

                - Handoff brief: route, screenshots[], notes, component mapping hints.
                - `designs/<feature>/` — designer-provided PNG/SVG references.
                - `handoff.json` — optional structured brief alongside screenshots.
                - Reuse `SettingsSection`, `PageHeader`, and other catalog components first.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Design handoff

                - NEVER invent new components when catalog has a match.
                - NEVER skip mobile screenshot when desktop-only was provided — ask Designer.
                - NEVER implement without loading DESIGN.md tokens and spacing rules.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Design handoff

                ## Designer prompt

                ```
                @heyeddi-handoff
                Route: /settings
                Attachments: desktop.png, mobile.png
                Notes: reuse SettingsSection; empty state on mobile
                ```

                ## Brief output (abbreviated)

                ```json
                {"route": "/settings", "screenshots": ["designs/settings/desktop.png"], "notes": "..."}
                ```
            """),
            "reference/screenshot-mode.md": dedent("""
                # Screenshot mode (v1)

                1. Designer places PNGs in `designs/<feature>/` or attaches in chat.
                2. Agent runs `load_handoff.py` to build normalized brief.
                3. Agent reads DESIGN.md + PrimeVue catalog.
                4. Implement route; match spacing and hierarchy from screenshots.
                5. Chain validation (`primevue-openprops-architect`) and `visual-auditor` compare.
            """),
            "reference/penpot-mode.md": dedent("""
                # Penpot mode (stub — Phase 6)

                Future integration:

                - v2: Penpot PNG/SVG export in `designs/`
                - v3: Penpot REST API fetch
                - v4: Penpot MCP for live tokens and components

                Not available in v1. Use screenshot mode instead.
            """),
            "scripts/load_handoff.py": dedent('''
                #!/usr/bin/env python3
                """Resolve handoff inputs into a normalized brief."""
                from __future__ import annotations

                import argparse
                import json
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Load design handoff brief")
                    parser.add_argument("--route", required=True)
                    parser.add_argument("--project-root", default=None)
                    parser.add_argument("--feature", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    feature = args.feature or args.route.strip("/").replace("/", "-") or "home"
                    designs_dir = root / "designs" / feature
                    screenshots: list[str] = []
                    if designs_dir.is_dir():
                        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.svg"):
                            screenshots.extend(str(p) for p in designs_dir.glob(ext))

                    handoff_json = designs_dir / "handoff.json"
                    extra = {}
                    if handoff_json.is_file():
                        try:
                            extra = json.loads(handoff_json.read_text())
                        except json.JSONDecodeError as exc:
                            extra = {"parse_error": str(exc)}

                    design_md = root / "DESIGN.md"
                    product_md = root / "PRODUCT.md"
                    brief = {
                        "route": args.route,
                        "feature": feature,
                        "screenshots": screenshots,
                        "design_md": str(design_md) if design_md.is_file() else None,
                        "product_md": str(product_md) if product_md.is_file() else None,
                        "mode": "screenshot",
                        **extra,
                    }
                    if not screenshots:
                        brief["hint"] = f"No images in {designs_dir} — attach screenshots or add files there"
                    emit(json.dumps(brief, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_pre_merge_gate() -> None:
    name = "pre-merge-gate"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Runs pre-merge checks (tests, build, types, optional UI audit) and returns a markdown pass/fail report. "
                "Use when QA approves a PR or before merge to main.",
                body=dedent("""
                    # Pre-merge Gate

                    ## When to use

                    - QA wants a single green/red report before approving a PR
                    - Before merging frontend-heavy changes
                    - After addressing review feedback — confirm all gates pass

                    ## Instructions

                    1. Run `python scripts/pre_merge_gate.py --project-root <root>`.
                    2. Read the markdown report — each check shows PASS/FAIL/SKIP.
                    3. Fix failing checks and re-run until all required checks pass.

                    ## Checks

                    - npm test (if script exists)
                    - verify build
                    - vue-tsc (if available)
                    - Optional: duplicate UI scan stub
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "run_pre_merge_gate",
                        "description": "Orchestrate pre-merge checks and return markdown report.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/pre_merge_gate.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Pre-merge gate

                - Gate report: markdown table with check name, status, summary.
                - Required: build must pass for frontend PRs.
                - SKIP: tool or script not available — not a failure.
                - FAIL: blocking — must fix before merge.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Pre-merge gate

                - NEVER merge on FAIL status for build or test.
                - NEVER treat SKIP as PASS — investigate missing tooling in CI.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Pre-merge gate

                ## Sample report

                ```markdown
                # Pre-merge Gate Report

                | Check | Status | Summary |
                |-------|--------|---------|
                | build | PASS | built in 4.2s |
                | test | SKIP | no test script |
                ```
            """),
            "scripts/pre_merge_gate.py": dedent('''
                #!/usr/bin/env python3
                """Orchestrate pre-merge checks."""
                from __future__ import annotations

                import argparse
                import json
                import shutil
                import subprocess
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root, run_command


                def status_from_output(output: str) -> str:
                    if output.startswith("[skip]") or output.startswith("[error] command not found"):
                        return "SKIP"
                    if output.startswith("[exit") or "[error]" in output[:80]:
                        return "FAIL"
                    return "PASS"


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Pre-merge gate")
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    rows: list[tuple[str, str, str]] = []

                    pkg = root / "package.json"
                    if pkg.is_file():
                        data = json.loads(pkg.read_text())
                        scripts = data.get("scripts", {})
                        if "test" in scripts:
                            out = run_command(["npm", "test"], root, timeout=300)
                            rows.append(("test", status_from_output(out), out[:200]))
                        out = run_command(["npm", "run", "build"], root, timeout=600)
                        rows.append(("build", status_from_output(out), out[:200]))
                    else:
                        rows.append(("build", "SKIP", "no package.json"))

                    if shutil.which("npx") and (root / "node_modules").is_dir():
                        out = run_command(["npx", "vue-tsc", "--noEmit"], root)
                        rows.append(("vue-tsc", status_from_output(out), out[:200]))
                    else:
                        rows.append(("vue-tsc", "SKIP", "npx or node_modules missing"))

                    lines = ["# Pre-merge Gate Report", "", "| Check | Status | Summary |", "|-------|--------|---------|"]
                    for name, st, summary in rows:
                        summary = summary.replace("|", "\\|").replace("\\n", " ")
                        lines.append(f"| {name} | {st} | {summary[:120]} |")
                    fail_count = sum(1 for _, st, _ in rows if st == "FAIL")
                    lines.append("")
                    lines.append(f"**Overall:** {'BLOCKED' if fail_count else 'OK'} ({fail_count} failures)")
                    emit("\\n".join(lines))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_pr_review_responder() -> None:
    name = "heyeddi-pr-respond"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Fetches all PR comment types (inline, review, discussion) via gh api for team review workflow. "
                "Use when addressing PR review feedback with fix-vs-decline rules — stricter than built-in /babysit.",
                body=dedent("""
                    # PR Review Responder

                    ## When to use

                    - User asks to handle PR reviews or respond to review comments
                    - Need flat JSON of all comment types for tracking table
                    - Team rules: reply to every comment, fix-vs-decline matrix

                    ## Instructions

                    1. Run `python scripts/fetch_pr_comments.py --pr <number> --project-root <root>`.
                    2. Build tracking table — every comment gets a response.
                    3. Inline comments: reply in thread via `gh api .../comments/ID/replies`.
                    4. Post summary only after all individual replies.

                    ## Requires

                    - `gh` CLI authenticated (`GH_TOKEN` in cloud)
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "fetch_pr_comments",
                        "description": "Fetch inline, review, and discussion PR comments as flat JSON.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pr": {"type": "integer", "description": "Pull request number"},
                                "project_root": PROJECT_ROOT_PARAM,
                            },
                            "required": ["pr", "project_root"],
                        },
                        "script": "scripts/fetch_pr_comments.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — PR review

                - Inline comment: line-specific code feedback — reply via `/replies` endpoint.
                - Review comment: general review body from a submitted review.
                - Discussion comment: PR conversation thread.
                - Tracking table: Comment ID, type, author, summary, status (PENDING/RESPONDED).
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — PR review

                - NEVER leave a comment without a threaded reply.
                - NEVER post summary before all individual responses.
                - NEVER apply fixes for incorrect or out-of-scope comments without explanation.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — PR review

                ## Fetch comments

                ```bash
                python scripts/fetch_pr_comments.py --pr 42 --project-root .
                ```

                ## Response template (correct comment)

                ```
                ✅ Fixed - Added count_assets method for proper pagination
                ```
            """),
            "scripts/fetch_pr_comments.py": dedent('''
                #!/usr/bin/env python3
                """Fetch PR comments via gh api."""
                from __future__ import annotations

                import argparse
                import json
                import shutil

                from _skill_cli import emit, resolve_project_root, run_command


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Fetch PR comments")
                    parser.add_argument("--pr", type=int, required=True)
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)

                    if not shutil.which("gh"):
                        emit(json.dumps({
                            "error": "gh CLI not found",
                            "hint": "Install GitHub CLI and authenticate, or set GH_TOKEN for cloud agent",
                        }, indent=2))
                        return

                    repo_out = run_command(
                        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                        root,
                    )
                    if repo_out.startswith("[exit") or repo_out.startswith("[error]"):
                        emit(json.dumps({"error": "could not resolve repo", "detail": repo_out}, indent=2))
                        return
                    repo = repo_out.strip()
                    pr = args.pr

                    inline = run_command(
                        ["gh", "api", f"repos/{repo}/pulls/{pr}/comments"],
                        root,
                    )
                    discussion = run_command(
                        ["gh", "pr", "view", str(pr), "--json", "comments"],
                        root,
                    )
                    reviews = run_command(
                        ["gh", "pr", "view", str(pr), "--json", "reviews"],
                        root,
                    )

                    def try_parse(s: str):
                        try:
                            return json.loads(s)
                        except json.JSONDecodeError:
                            return s

                    emit(json.dumps({
                        "pr": pr,
                        "repo": repo,
                        "inline": try_parse(inline),
                        "discussion": try_parse(discussion),
                        "reviews": try_parse(reviews),
                    }, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_design_system_generalizer() -> None:
    name = "design-system-generalizer"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Scans token and component usage patterns from a golden reference page and diffs violations on other routes. "
                "Use when spreading a well-built page's patterns across the app in PR-sized chunks.",
                body=dedent("""
                    # Design System Generalizer

                    ## When to use

                    - One route is the "golden" reference (e.g. /settings)
                    - Other routes drift from tokens or component reuse
                    - Planning incremental migration PRs

                    ## Instructions

                    1. `python scripts/scan_patterns.py --route /golden --project-root <root>`
                    2. `python scripts/diff_violations.py --golden /golden --target /other --project-root <root>`
                    3. Propose small PRs — never whole-app rewrite in one shot.
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "scan_patterns",
                        "description": "Scan Vue files for OpenProps tokens and component imports on a route.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "route": {"type": "string", "description": "Golden route e.g. /settings"},
                                "project_root": PROJECT_ROOT_PARAM,
                            },
                            "required": ["route", "project_root"],
                        },
                        "script": "scripts/scan_patterns.py",
                        "readonly": True,
                    },
                    {
                        "name": "diff_violations",
                        "description": "Compare target route patterns against golden reference.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "golden": {"type": "string", "description": "Golden route"},
                                "target": {"type": "string", "description": "Route to check"},
                                "project_root": PROJECT_ROOT_PARAM,
                            },
                            "required": ["golden", "target", "project_root"],
                        },
                        "script": "scripts/diff_violations.py",
                        "readonly": True,
                    },
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Design system generalizer

                - Golden route: reference implementation with correct tokens and components.
                - Pattern: OpenProps var usage, PrimeVue import, shared wrapper usage.
                - Violation: hex color, missing token, forked component duplicate.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Generalizer

                - NEVER rewrite the entire app in one PR.
                - NEVER generalize without a signed-off golden page.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Generalizer

                ```bash
                python scripts/scan_patterns.py --route /settings --project-root .
                python scripts/diff_violations.py --golden /settings --target /billing --project-root .
                ```
            """),
            "scripts/scan_patterns.py": dedent('''
                #!/usr/bin/env python3
                """Scan token and component patterns (stub)."""
                from __future__ import annotations

                import argparse
                import json
                import re
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root

                TOKEN_RE = re.compile(r"var\\(--[a-z0-9-]+\\)")
                HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\\b")
                IMPORT_RE = re.compile(r"from ['\\"]([^'\\"]+)['\\"]")


                def vue_files_for_route(root: Path, route: str) -> list[Path]:
                    slug = route.strip("/").replace("/", "-") or "home"
                    candidates = list(root.glob(f"**/views/**/*{slug}*"))
                    candidates += list(root.glob(f"**/pages/**/*{slug}*"))
                    return [p for p in candidates if p.suffix == ".vue"][:20]


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Scan design patterns")
                    parser.add_argument("--route", required=True)
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    files = vue_files_for_route(root, args.route)
                    if not files:
                        emit(json.dumps({
                            "route": args.route,
                            "files": [],
                            "hint": "No matching Vue files — adjust glob or pass explicit paths in future",
                        }, indent=2))
                        return
                    report = {"route": args.route, "files": []}
                    for f in files:
                        text = f.read_text(errors="replace")
                        report["files"].append({
                            "path": str(f.relative_to(root)),
                            "openprops_tokens": sorted(set(TOKEN_RE.findall(text))),
                            "hex_colors": sorted(set(HEX_RE.findall(text))),
                            "imports": sorted(set(IMPORT_RE.findall(text)))[:30],
                        })
                    emit(json.dumps(report, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
            "scripts/diff_violations.py": dedent('''
                #!/usr/bin/env python3
                """Diff target route against golden patterns (stub)."""
                from __future__ import annotations

                import argparse
                import json
                import re
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root

                TOKEN_RE = re.compile(r"var\\(--[a-z0-9-]+\\)")
                HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\\b")


                def scan_file(path: Path) -> dict:
                    text = path.read_text(errors="replace")
                    return {
                        "tokens": set(TOKEN_RE.findall(text)),
                        "hex": set(HEX_RE.findall(text)),
                    }


                def vue_files(root: Path, route: str) -> list[Path]:
                    slug = route.strip("/").replace("/", "-") or "home"
                    return [p for p in root.glob(f"**/*{slug}*.vue")][:10]


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Diff violations vs golden")
                    parser.add_argument("--golden", required=True)
                    parser.add_argument("--target", required=True)
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    golden_tokens: set[str] = set()
                    target_hex: set[str] = set()
                    for f in vue_files(root, args.golden):
                        golden_tokens |= scan_file(f)["tokens"]
                    for f in vue_files(root, args.target):
                        target_hex |= scan_file(f)["hex"]
                    violations = []
                    if target_hex:
                        violations.append({"type": "hex_color", "values": sorted(target_hex)})
                    emit(json.dumps({
                        "golden": args.golden,
                        "target": args.target,
                        "golden_token_count": len(golden_tokens),
                        "violations": violations,
                    }, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_no_duplicate_ui() -> None:
    name = "no-duplicate-ui"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Scans Vue files for duplicate component names and similar template overlap. "
                "Use during PR review or when refactoring UI to enforce DRY architecture.",
                paths=["**/*.vue"],
                body=dedent("""
                    # No Duplicate UI

                    ## When to use

                    - PR adds a new Button/Card wrapper similar to existing ones
                    - Refactoring to consolidate forked components
                    - Pre-merge gate optional duplicate scan

                    ## Instructions

                    1. Run `python scripts/find_duplicate_ui.py --project-root <root>`.
                    2. Review pairs with high template similarity or matching filenames.
                    3. Consolidate into shared components under `@/components/ui/`.
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "find_duplicate_ui",
                        "description": "Find similar Vue filenames and template overlap.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/find_duplicate_ui.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — No duplicate UI

                - Shared primitives live in `@/components/ui/`.
                - Duplicate: same component name in two paths, or >60% template token overlap.
                - Fork: copy-paste of an existing SFC with minor renaming.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Duplicate UI

                - NEVER create `Button2.vue` when `Button.vue` exists.
                - NEVER copy entire SFCs — extract shared subcomponents instead.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Duplicate UI

                ```bash
                python scripts/find_duplicate_ui.py --project-root .
                ```

                Output lists filename pairs and overlap scores.
            """),
            "scripts/find_duplicate_ui.py": dedent('''
                #!/usr/bin/env python3
                """Find duplicate or similar Vue UI files."""
                from __future__ import annotations

                import argparse
                import json
                import re
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root

                TEMPLATE_RE = re.compile(r"<template>(.*?)</template>", re.DOTALL | re.IGNORECASE)


                def template_tokens(path: Path) -> set[str]:
                    m = TEMPLATE_RE.search(path.read_text(errors="replace"))
                    if not m:
                        return set()
                    return set(re.findall(r"[A-Za-z][A-Za-z0-9-]*", m.group(1)))


                def jaccard(a: set[str], b: set[str]) -> float:
                    if not a and not b:
                        return 0.0
                    return len(a & b) / len(a | b) if (a | b) else 0.0


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Find duplicate UI")
                    parser.add_argument("--project-root", default=None)
                    parser.add_argument("--min-score", type=float, default=0.55)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    vue_files = list(root.rglob("*.vue"))
                    if not vue_files:
                        emit(json.dumps({"duplicates": [], "hint": "no .vue files found"}, indent=2))
                        return
                    by_name: dict[str, list[str]] = {}
                    tokens: dict[str, set[str]] = {}
                    for f in vue_files:
                        if "node_modules" in f.parts:
                            continue
                        rel = str(f.relative_to(root))
                        by_name.setdefault(f.stem.lower(), []).append(rel)
                        tokens[rel] = template_tokens(f)
                    pairs: list[dict] = []
                    for stem, paths in by_name.items():
                        if len(paths) > 1:
                            pairs.append({"type": "same_filename", "stem": stem, "paths": paths})
                    paths_list = list(tokens.keys())
                    for i, a in enumerate(paths_list):
                        for b in paths_list[i + 1 :]:
                            score = jaccard(tokens[a], tokens[b])
                            if score >= args.min_score:
                                pairs.append({"type": "template_overlap", "a": a, "b": b, "score": round(score, 2)})
                    emit(json.dumps({"duplicate_count": len(pairs), "pairs": pairs[:50]}, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_backend_type_bridger() -> None:
    name = "backend-type-bridger"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Syncs FastAPI OpenAPI schema to TypeScript types and reads Firestore schema hints. "
                "Use when writing Vue composables against FastAPI or Firebase backends.",
                paths=["**/composables/**", "**/api/**", "openapi.json"],
                body=dedent("""
                    # Backend Type Bridger

                    ## When to use

                    - Frontend agent needs accurate API payload shapes
                    - `openapi.json` or FastAPI server available locally
                    - Firestore rules or schema file exists for Firebase projects

                    ## Instructions

                    1. FastAPI: `python scripts/sync_openapi.py --project-root <root>`
                    2. Firebase: `python scripts/fetch_firestore_schema.py --project-root <root>`
                    3. Import generated types in composables — never guess field names.
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "sync_openapi",
                        "description": "Fetch openapi.json and summarize or emit types path.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_root": PROJECT_ROOT_PARAM,
                                "url": {"type": "string", "description": "OpenAPI URL (optional)"},
                            },
                            "required": ["project_root"],
                        },
                        "script": "scripts/sync_openapi.py",
                        "readonly": True,
                    },
                    {
                        "name": "fetch_firestore_schema",
                        "description": "Read Firestore rules or schema file for TS type hints.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/fetch_firestore_schema.py",
                        "readonly": True,
                    },
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Backend type bridger

                - `openapi.json` — FastAPI exported schema at project root or `/openapi.json`.
                - `types/api.ts` — generated or hand-maintained frontend types target.
                - `firestore.rules` — security rules hinting collection structure.
                - `firebase.json` — signals Firebase project layout.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Type bridger

                - NEVER guess API response fields without syncing OpenAPI.
                - NEVER use `any` for API payloads when types can be generated.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Type bridger

                ```bash
                python scripts/sync_openapi.py --project-root . --url http://localhost:8090/openapi.json
                python scripts/fetch_firestore_schema.py --project-root .
                ```
            """),
            "scripts/sync_openapi.py": dedent('''
                #!/usr/bin/env python3
                """Sync OpenAPI schema to types summary."""
                from __future__ import annotations

                import argparse
                import json
                import urllib.error
                import urllib.request
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Sync OpenAPI")
                    parser.add_argument("--project-root", default=None)
                    parser.add_argument("--url", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    local = root / "openapi.json"
                    spec = None
                    source = None

                    if local.is_file():
                        spec = json.loads(local.read_text())
                        source = str(local)
                    elif args.url:
                        try:
                            with urllib.request.urlopen(args.url, timeout=10) as resp:
                                spec = json.loads(resp.read().decode())
                            source = args.url
                        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                            emit(json.dumps({"error": str(exc), "hint": "Start FastAPI or place openapi.json in project root"}, indent=2))
                            return
                    else:
                        emit(json.dumps({
                            "error": "no openapi source",
                            "hint": "Add openapi.json to project root or pass --url http://localhost:8090/openapi.json",
                        }, indent=2))
                        return

                    paths = list(spec.get("paths", {}).keys())[:30]
                    schemas = list(spec.get("components", {}).get("schemas", {}).keys())[:30]
                    out_types = root / "src" / "types" / "api.ts"
                    emit(json.dumps({
                        "source": source,
                        "path_count": len(spec.get("paths", {})),
                        "sample_paths": paths,
                        "sample_schemas": schemas,
                        "suggested_types_file": str(out_types),
                        "hint": "Use openapi-typescript or datamodel-codegen for full generation",
                    }, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
            "scripts/fetch_firestore_schema.py": dedent('''
                #!/usr/bin/env python3
                """Read Firestore rules / schema hints."""
                from __future__ import annotations

                import argparse
                import json
                import re
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root

                COLLECTION_RE = re.compile(r"match\\s+/([a-zA-Z0-9_/-]+)")


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Fetch Firestore schema hints")
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    rules = root / "firestore.rules"
                    schema = root / "firestore.schema.json"
                    firebase_json = root / "firebase.json"
                    result = {"collections": [], "files_found": []}

                    if rules.is_file():
                        result["files_found"].append(str(rules))
                        text = rules.read_text()
                        result["collections"] = sorted(set(COLLECTION_RE.findall(text)))
                    if schema.is_file():
                        result["files_found"].append(str(schema))
                        try:
                            result["schema"] = json.loads(schema.read_text())
                        except json.JSONDecodeError as exc:
                            result["schema_error"] = str(exc)
                    if firebase_json.is_file():
                        result["files_found"].append(str(firebase_json))
                        result["firebase_project"] = True

                    if not result["files_found"]:
                        result["hint"] = "No firestore.rules or firestore.schema.json — add Firebase config to project root"
                    emit(json.dumps(result, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_composable_patterns() -> None:
    name = "composable-patterns"
    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Provides FastAPI JWT and Firebase client composable patterns for consistent auth and data layers. "
                "Context-first skill — use when writing or reviewing Vue composables for API access.",
                paths=["**/composables/**", "**/use*.ts"],
                body=dedent("""
                    # Composable Patterns

                    ## When to use

                    - Writing `useAuth`, `useApi`, or Firestore data composables
                    - Choosing between FastAPI JWT vs Firebase client patterns
                    - Reviewing composable error handling and token refresh

                    ## Instructions

                    1. Read `context/fastapi-jwt.md` for REST + JWT projects.
                    2. Read `context/firebase-client.md` for Firebase/Firestore projects.
                    3. Optional: `python scripts/validate_composable.py --path src/composables/useX.ts`

                    ## Notes

                    - Prefer context docs over improvising interceptors or security rules.
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "validate_composable",
                        "description": "Stub validator for composable file conventions.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Composable file path"},
                                "project_root": PROJECT_ROOT_PARAM,
                            },
                            "required": ["path", "project_root"],
                        },
                        "script": "scripts/validate_composable.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — Composables

                - Composable: `use*` function returning reactive state + actions.
                - FastAPI JWT: Bearer token in Authorization header, refresh via `/auth/refresh`.
                - Firebase: `onAuthStateChanged`, rules-aware reads, no server secrets in client.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — Composables

                - NEVER store refresh tokens in localStorage without team approval.
                - NEVER bypass Firestore security rules with admin SDK in frontend.
                - NEVER mix Firebase and JWT auth patterns in one composable.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — Composables

                See `fastapi-jwt.md` and `firebase-client.md` for full patterns.
            """),
            "context/fastapi-jwt.md": dedent("""
                # FastAPI JWT composable pattern

                ```ts
                // useApi.ts — attach Bearer token, handle 401 refresh
                export function useApi() {
                  const auth = useAuthStore();
                  async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
                    const res = await fetch(`/api${path}`, {
                      ...init,
                      headers: {
                        Authorization: `Bearer ${auth.accessToken}`,
                        "Content-Type": "application/json",
                        ...init?.headers,
                      },
                    });
                    if (res.status === 401) {
                      await auth.refresh();
                      return fetchApi(path, init);
                    }
                    if (!res.ok) throw new Error(await res.text());
                    return res.json();
                  }
                  return { fetchApi };
                }
                ```
            """),
            "context/firebase-client.md": dedent("""
                # Firebase client composable pattern

                ```ts
                // useFirestoreCollection.ts — rules-aware reads
                import { collection, onSnapshot, query, where } from "firebase/firestore";
                import { useFirebase } from "./useFirebase";

                export function useFirestoreCollection<T>(name: string, ownerId: string) {
                  const { db, user } = useFirebase();
                  const items = ref<T[]>([]);
                  watchEffect((onCleanup) => {
                    if (!user.value) return;
                    const q = query(collection(db, name), where("ownerId", "==", ownerId));
                    const unsub = onSnapshot(q, (snap) => {
                      items.value = snap.docs.map((d) => ({ id: d.id, ...d.data() }) as T);
                    });
                    onCleanup(unsub);
                  });
                  return { items };
                }
                ```
            """),
            "scripts/validate_composable.py": dedent('''
                #!/usr/bin/env python3
                """Stub composable validator."""
                from __future__ import annotations

                import argparse
                import json
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Validate composable stub")
                    parser.add_argument("--path", required=True)
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    target = (root / args.path).resolve()
                    if not target.is_file():
                        emit(json.dumps({"status": "SKIP", "reason": f"file not found: {target}"}, indent=2))
                        return
                    text = target.read_text(errors="replace")
                    checks = {
                        "exports_use_function": "export function use" in text or "export const use" in text,
                        "no_admin_sdk": "firebase-admin" not in text,
                        "has_error_handling": "catch" in text or "throw" in text,
                    }
                    emit(json.dumps({"path": str(target.relative_to(root)), "checks": checks}, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def define_heyeddi_design() -> None:
    name = "heyeddi-design"
    skill_src = SKILLS_DIR / name
    if skill_src.is_dir() and (skill_src / "SKILL.md").is_file():
        files: dict[str, str] = {}
        for path in sorted(skill_src.rglob("*")):
            if not path.is_file() or path.name == "_skill_cli.py":
                continue
            rel = path.relative_to(skill_src).as_posix()
            files[rel] = path.read_text()
        SKILLS[name] = {"files": files}
        return

    SKILLS[name] = {
        "files": {
            "SKILL.md": skill_md(
                name,
                "Designs new screens within OpenProps, PrimeVue, and DESIGN.md constraints. "
                "Sub-commands: craft (new screen), shape (IA/layout), polish (refine). "
                "Replaces impeccable for HeyEddi stack — explicit invocation only.",
                body=dedent("""
                    # HeyEddi Design

                    ## When to use

                    - `@heyeddi-design craft` — new screen from brief
                    - `@heyeddi-design shape` — information architecture / layout exploration
                    - `@heyeddi-design polish` — refine existing screen
                    - Visual proof: delegate to `@visual-auditor`

                    ## Instructions

                    1. Run `python scripts/load_context.py --project-root <root>`.
                    2. Read `reference/craft.md`, `shape.md`, or `polish.md` for the sub-command.
                    3. Follow DESIGN.md tokens and PrimeVue catalog.
                    4. Validate with `primevue-openprops-architect` after implementation.
                """),
            ),
            "manifest.json": manifest(
                name,
                [
                    {
                        "name": "load_design_context",
                        "description": "Load PRODUCT.md and DESIGN.md for design sessions.",
                        "parameters": {
                            "type": "object",
                            "properties": {"project_root": PROJECT_ROOT_PARAM},
                            "required": ["project_root"],
                        },
                        "script": "scripts/load_context.py",
                        "readonly": True,
                    }
                ],
            ),
            "context/VOCABULARY.md": dedent("""
                # Vocabulary — HeyEddi design

                - Craft: net-new screen from product brief within design system.
                - Shape: wireframe-level IA before pixel polish.
                - Polish: tighten spacing, hierarchy, microcopy on existing UI.
                - DESIGN.md: team tokens, component catalog, layout rules.
            """),
            "context/ANTI_PATTERNS.md": dedent("""
                # Anti-patterns — HeyEddi design

                - NEVER design outside OpenProps + PrimeVue without documenting exception.
                - NEVER skip DESIGN.md when crafting new screens.
                - NEVER use impeccable — this skill replaces it for HeyEddi stack.
            """),
            "context/EXAMPLES.md": dedent("""
                # Examples — HeyEddi design

                ```
                @heyeddi-design craft
                Brief: Settings page with profile form and danger zone
                ```

                ```
                @heyeddi-design polish
                Route: /settings — tighten mobile spacing
                ```
            """),
            "reference/craft.md": dedent("""
                # Craft — new screen

                1. Load context (`load_context.py`) — PRODUCT.md + DESIGN.md.
                2. Clarify user goal, primary action, empty/error states.
                3. Pick layout pattern from DESIGN.md (list-detail, form page, dashboard).
                4. Map UI to PrimeVue components + OpenProps tokens only.
                5. Implement Vue SFCs; run validate_vue.
                6. Run visual-auditor at 375/768/1440.
            """),
            "reference/shape.md": dedent("""
                # Shape — IA and layout

                1. Outline sections as markdown hierarchy (H1 → sections → CTAs).
                2. Propose mobile-first stack order before desktop columns.
                3. Identify reusable blocks from component catalog.
                4. Get Designer approval on structure before craft/polish.
            """),
            "reference/polish.md": dedent("""
                # Polish — refine existing screen

                1. Load route in visual-auditor screenshots.
                2. Compare against VISUAL_HIERARCHY expectations.
                3. Adjust token usage, spacing scale, heading levels.
                4. Improve microcopy clarity — no lorem ipsum in production paths.
                5. Re-validate and re-audit.
            """),
            "scripts/load_context.py": dedent('''
                #!/usr/bin/env python3
                """Load PRODUCT.md and DESIGN.md for design sessions."""
                from __future__ import annotations

                import argparse
                import json
                from pathlib import Path

                from _skill_cli import emit, resolve_project_root


                def read_md(path: Path, max_chars: int = 8000) -> str | None:
                    if not path.is_file():
                        return None
                    text = path.read_text(errors="replace")
                    return text[:max_chars] + ("…" if len(text) > max_chars else "")


                def main() -> None:
                    parser = argparse.ArgumentParser(description="Load design context")
                    parser.add_argument("--project-root", default=None)
                    args = parser.parse_args()
                    root = resolve_project_root(args.project_root)
                    design = root / "DESIGN.md"
                    product = root / "PRODUCT.md"
                    emit(json.dumps({
                        "project_root": str(root),
                        "design_md": read_md(design),
                        "product_md": read_md(product),
                        "design_exists": design.is_file(),
                        "product_exists": product.is_file(),
                        "hint": None if design.is_file() else "Add DESIGN.md to project root for full craft workflow",
                    }, indent=2))


                if __name__ == "__main__":
                    main()
            '''),
        }
    }


def register_all_skills() -> None:
    define_primevue_openprops_architect()
    define_verify_build()
    define_visual_auditor()
    define_design_handoff()
    define_pre_merge_gate()
    define_pr_review_responder()
    define_design_system_generalizer()
    define_no_duplicate_ui()
    define_backend_type_bridger()
    define_composable_patterns()
    define_heyeddi_design()


def bootstrap() -> list[str]:
    if not TEMPLATE_CLI.is_file():
        raise SystemExit(f"Missing template CLI: {TEMPLATE_CLI}")

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    for name, spec in SKILLS.items():
        skill_dir = SKILLS_DIR / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        copy_skill_cli(skill_dir / "scripts")

        for rel_path, content in spec["files"].items():
            dest = skill_dir / rel_path
            write(dest, content)
            if rel_path.endswith(".py") or rel_path.endswith(".sh"):
                dest.chmod(0o755)

        created.append(name)
        print(f"  ✓ {name}")

    gitkeep = SKILLS_DIR / ".gitkeep"
    if created and gitkeep.is_file():
        gitkeep.unlink()
        print("  ✓ removed .gitkeep")

    return created


def main() -> None:
    print("Bootstrapping HeyEddi skills...")
    register_all_skills()
    created = bootstrap()
    print(f"\nCreated {len(created)} skills under {SKILLS_DIR}")

    if REGISTER_TOOLS.is_file():
        result = subprocess.run(
            [sys.executable, str(REGISTER_TOOLS), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            tools = json.loads(result.stdout)
            print(f"register_tools.py: {len(tools)} tools across {len(created)} skills")
            by_skill: dict[str, int] = {}
            for t in tools:
                by_skill[t["skill"]] = by_skill.get(t["skill"], 0) + 1
            for skill in created:
                print(f"  - {skill}: {by_skill.get(skill, 0)} tools")
        else:
            print(result.stderr or result.stdout, file=sys.stderr)


if __name__ == "__main__":
    main()
