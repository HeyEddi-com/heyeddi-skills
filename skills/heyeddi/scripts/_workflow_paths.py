"""Paths for cross-pillar workflow sync under `.heyeddi/docs/workflow/`."""
from __future__ import annotations

import re
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


_ENTRY = re.compile(r"^### (\S+): `([^`]+)` \((\w+)\)$", re.M)
_REQUESTS = re.compile(r"^\*\*Requests:\*\*(.*)$", re.M)


def open_requests(root: Path, route: str) -> list[dict]:
    """Sibling requests on `route` that no entry from that sibling has answered yet."""
    entries: list[tuple[str, str, list[str]]] = []
    for pillar in PILLARS:
        path = opinion_path(root, pillar)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        found = list(_ENTRY.finditer(text))
        for i, match in enumerate(found):
            if match.group(2) != route:
                continue
            body = text[match.end() : found[i + 1].start() if i + 1 < len(found) else len(text)]
            line = _REQUESTS.search(body)
            entries.append((match.group(1), pillar, re.findall(r"`@(\w+)`", line.group(1)) if line else []))
    open_: list[dict] = []
    for when, pillar, wanted in entries:
        waiting = [w for w in wanted if not any(p == w and at >= when for at, p, _ in entries)]
        if waiting:
            open_.append({"from": pillar, "at": when, "waiting_for": waiting})
    return open_
