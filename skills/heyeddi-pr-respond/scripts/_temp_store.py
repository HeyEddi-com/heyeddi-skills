"""Ephemeral PR workflow paths outside the project tree.

HeyEddi PR respond must never write ``.heyeddi/docs/pr-*`` scratch files.
Comment caches live under the system temp directory only.
"""
from __future__ import annotations

import tempfile
from pathlib import Path


def pr_temp_dir(pr: int) -> Path:
    d = Path(tempfile.gettempdir()) / "heyeddi" / f"pr-{pr}" / "respond"
    d.mkdir(parents=True, exist_ok=True)
    return d


def comments_cache_path(pr: int) -> Path:
    return pr_temp_dir(pr) / "comments.json"


def inventory_cache_path(pr: int) -> Path:
    return pr_temp_dir(pr) / "inventory.json"
