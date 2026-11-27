
#!/usr/bin/env python3
"""Run vue-tsc and stylelint if available."""
from __future__ import annotations

import argparse
import shutil
import sys

from _skill_cli import emit, fail, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Vue + CSS")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    if not (root / "package.json").is_file():
        emit("[skip] no package.json: nothing to validate")
        return
    if not shutil.which("npx"):
        fail("npx not found: install Node.js, then rerun")
    if not (root / "node_modules").is_dir():
        fail("node_modules not found: run npm install, then rerun")

    sections: list[str] = []
    failed = False

    def run(title: str, cmd: list[str]) -> None:
        nonlocal failed
        output = run_command(cmd, root)
        failed = failed or output.startswith(("[exit", "[error]"))
        sections.append(f"## {title}\n\n{output}")

    tsconfig = root / "tsconfig.json"
    if tsconfig.is_file():
        if not (root / "node_modules" / ".bin" / "vue-tsc").exists():
            fail("vue-tsc not installed: run npm install -D vue-tsc typescript, then rerun")
        # A solution-style tsconfig (files: [] plus references) checks nothing without -b.
        solution = '"references"' in tsconfig.read_text(encoding="utf-8", errors="replace")
        run("vue-tsc", ["npx", "vue-tsc", "-b" if solution else "--noEmit"])
    else:
        sections.append("## vue-tsc\n[skip] no tsconfig.json")

    if (root / "node_modules" / ".bin" / "stylelint").exists():
        run("stylelint", ["npx", "stylelint", "**/*.{css,vue,scss}"])
    else:
        sections.append("## stylelint\n[skip] stylelint not installed")

    emit("\n\n".join(sections))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
