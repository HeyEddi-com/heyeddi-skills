"""CI evidence lives in the system temp directory, never in the project tree."""
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path


def ci_temp_dir(root: Path, pr: int) -> Path:
    repo = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:10]
    directory = Path(tempfile.gettempdir()) / "heyeddi" / f"pr-{pr}" / f"ci-fails-{repo}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory
