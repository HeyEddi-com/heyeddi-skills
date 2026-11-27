"""Detect HeyEddi project stacks (Flutter, FastAPI, Firebase)."""
from __future__ import annotations

import json
import re
from pathlib import Path

BACKEND_DIR = "backend"
DEFAULT_API_PORT = 8090
DEFAULT_WEB_PORT = 8085


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def load_stack_config(root: Path) -> dict:
    cfg = load_json(root / ".heyeddi" / "stack.json")
    return cfg or {}


def frontend_kind(root: Path) -> str:
    cfg = load_stack_config(root)
    declared = cfg.get("frontend")
    if declared in ("flutter", "vue"):
        return declared
    if has_flutter(root):
        return "flutter"
    if has_vue(root):
        return "vue"
    return "unknown"


def has_flutter(root: Path) -> bool:
    pubspec = load_json(root / "pubspec.yaml")
    if pubspec and "flutter" in pubspec.get("dependencies", {}):
        return True
    return (root / "lib" / "main.dart").is_file() and (root / "pubspec.yaml").is_file()


SCAFFOLD_PACKAGE = "heyeddi_app"


def is_existing_app(root: Path) -> bool:
    """A pubspec the scaffold did not write: the demo app files do not belong in it."""
    pubspec = root / "pubspec.yaml"
    if not pubspec.is_file():
        return False
    match = re.search(r"(?m)^name:\s*(\S+)", pubspec.read_text(encoding="utf-8", errors="replace"))
    return not match or match.group(1) != SCAFFOLD_PACKAGE


def merge_stack(dest: Path, template: Path, *, dry_run: bool) -> bool:
    """Add missing keys from the template. Never replace a value the project set."""
    defaults = json.loads(template.read_text(encoding="utf-8"))
    current: dict = {}
    if dest.is_file():
        try:
            current = json.loads(dest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
    merged = {**defaults, **current}
    if merged == current:
        return False
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return True


def has_vue(root: Path) -> bool:
    pkg = load_json(root / "package.json")
    if pkg:
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "vue" in deps:
            return True
    return (root / "src").is_dir() and (root / "package.json").is_file()


def has_fastapi(root: Path) -> bool:
    for base in (root / BACKEND_DIR, root):
        pyproject = base / "pyproject.toml"
        if pyproject.is_file() and "fastapi" in pyproject.read_text().lower():
            return True
        if (base / "app" / "main.py").is_file():
            return True
    return (root / "openapi.json").is_file() and (root / BACKEND_DIR).is_dir()


def has_firebase(root: Path) -> bool:
    if (root / "firebase.json").is_file():
        return True
    if (root / "firestore.rules").is_file():
        return True
    cfg = load_stack_config(root)
    backends = cfg.get("backends") or []
    if isinstance(backends, list) and "firebase" in backends:
        return True
    return cfg.get("backend") == "firebase"


def fastapi_root(root: Path) -> Path:
    if (root / BACKEND_DIR / "pyproject.toml").is_file():
        return root / BACKEND_DIR
    if (root / "pyproject.toml").is_file() and "fastapi" in (root / "pyproject.toml").read_text().lower():
        return root
    return root / BACKEND_DIR


def parse_api_port(root: Path) -> int:
    cfg = load_stack_config(root)
    port = cfg.get("api_port")
    if port is not None:
        try:
            return int(port)
        except (TypeError, ValueError):
            pass
    return DEFAULT_API_PORT


def parse_web_port(root: Path) -> int:
    cfg = load_stack_config(root)
    port = cfg.get("web_port")
    if port is not None:
        try:
            return int(port)
        except (TypeError, ValueError):
            pass
    return DEFAULT_WEB_PORT


def infer_backends(root: Path) -> list[str]:
    cfg = load_stack_config(root)
    declared = cfg.get("backends") or cfg.get("backend")
    if isinstance(declared, str):
        declared = [declared]
    if isinstance(declared, list):
        return [b for b in declared if b in ("fastapi", "firebase")]

    backends: list[str] = []
    product = root / "PRODUCT.md"
    text = product.read_text().lower() if product.is_file() else ""
    if has_fastapi(root) or "fastapi" in text or (root / "openapi.json").is_file():
        backends.append("fastapi")
    if has_firebase(root) or "firebase" in text or "firestore" in text:
        backends.append("firebase")
    return backends


def detect(root: Path) -> dict:
    cfg = load_stack_config(root)
    frontend = frontend_kind(root)
    backends = infer_backends(root)
    return {
        "frontend": frontend,
        "flutter": frontend == "flutter" or has_flutter(root),
        "vue": frontend == "vue" or has_vue(root),
        "fastapi": "fastapi" in backends or has_fastapi(root),
        "firebase": "firebase" in backends or has_firebase(root),
        "backends": backends,
        "api_port": parse_api_port(root),
        "web_port": parse_web_port(root),
        "fastapi_root": str(fastapi_root(root)),
        "stack_config": str(root / ".heyeddi" / "stack.json") if cfg else None,
    }
