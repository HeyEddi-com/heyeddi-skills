"""Ephemeral PR workflow paths outside the project tree.

HeyEddi CI respond must never write ``.heyeddi/docs/pr-*-ci-*`` (or any
``pr-*-ci-*`` file under the project root). Comment caches live under the
system temp directory only.
"""
from __future__ import annotations

import tempfile
from pathlib import Path


def pr_temp_dir(pr: int) -> Path:
    d = Path(tempfile.gettempdir()) / "heyeddi" / f"pr-{pr}" / "ci"
    d.mkdir(parents=True, exist_ok=True)
    return d


def comments_cache_path(pr: int) -> Path:
    return pr_temp_dir(pr) / "comments.json"
