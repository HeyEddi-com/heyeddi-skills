"""Paths for cross-pillar workflow sync under `.heyeddi/docs/workflow/`."""
from __future__ import annotations

from pathlib import Path

PILLARS = ("product", "ux", "design")
VALID_PILLARS = frozenset(PILLARS)


def workflow_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs" / "workflow"


def opinions_dir(root: Path) -> Path:
    return workflow_dir(root) / "opinions"


def opinion_path(root: Path, pillar: str) -> Path:
    return opinions_dir(root) / f"{pillar}.md"


def sync_log_path(root: Path) -> Path:
    return workflow_dir(root) / "sync-log.md"


def active_context_path(root: Path) -> Path:
    return workflow_dir(root) / "active-context.json"


def readme_path(root: Path) -> Path:
    return workflow_dir(root) / "README.md"
