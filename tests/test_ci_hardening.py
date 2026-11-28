"""The audit flags unpinned actions, open token permissions, and unsafe shell in CI."""
from __future__ import annotations

from pathlib import Path

from _skill_loader import load_skill_script

ROOT = Path(__file__).resolve().parents[1]
audit = load_skill_script("engineering-excellence", "audit_engineering")
SHA = "a" * 40


def _findings(tmp_path: Path, text: str, rel: str = ".github/workflows/ci.yml") -> list[str]:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return [f["message"] for f in audit.scan_ci(tmp_path)]


def test_hardened_workflow_is_clean(tmp_path: Path) -> None:
    text = f"""permissions: {{}}
jobs:
  a:
    steps:
      - uses: actions/checkout@{SHA} # v4
      - uses: ./.github/actions/local
      - run: |
          set -euo pipefail
          cat x | wc -l
      - run: test -f a || test -f b
"""
    assert _findings(tmp_path, text) == []


def test_tag_pinned_action_and_missing_permissions(tmp_path: Path) -> None:
    messages = _findings(tmp_path, "jobs:\n  a:\n    steps:\n      - uses: actions/checkout@v4\n")
    assert any("actions/checkout@v4" in m for m in messages)
    assert any("permissions" in m for m in messages)


def test_download_piped_into_shell(tmp_path: Path) -> None:
    messages = _findings(tmp_path, "curl -fsSL https://example.com/i.sh | sudo bash\n", "scripts/install.sh")
    assert any("piped into a shell" in m for m in messages)


def test_pipe_without_pipefail(tmp_path: Path) -> None:
    for step in ("      - run: make test | tee log\n", "      - run: |\n          make test | tee log\n"):
        messages = _findings(tmp_path, "permissions: {}\njobs:\n  a:\n    steps:\n" + step)
        assert any("pipefail" in m for m in messages), step


def test_this_repository_passes() -> None:
    assert audit.scan_ci(ROOT) == []
