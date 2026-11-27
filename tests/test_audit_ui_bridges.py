"""OpenAPI bridges must emit types that match the schema and compile."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parent.parent / "skills"
NULL = {"type": "null"}


def _ref(name: str) -> dict:
    return {"$ref": f"#/components/schemas/{name}"}


SCHEMAS = {
    "Role": {"type": "string", "enum": ["admin", "member"]},
    "Org": {"type": "object", "required": ["id"], "properties": {"id": {"type": "integer"}}},
    "Empty": {"type": "object"},
    "User": {
        "type": "object",
        "required": ["id", "role", "org"],
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "nick": {"anyOf": [{"type": "string"}, NULL]},
            "role": _ref("Role"),
            "org": _ref("Org"),
            "boss": {"anyOf": [_ref("User"), NULL]},
            "tags": {"type": "array", "items": {"type": "string"}},
            "orgs": {"type": "array", "items": _ref("Org")},
            "joined": {"type": "string", "format": "date-time"},
            "x-trace": {"type": "string"},
        },
    },
    **{f"Filler{i}": {"type": "object", "properties": {"n": {"type": "number"}}} for i in range(45)},
}


def _run(skill: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SKILLS / skill / "scripts" / "sync_openapi.py"), "--project-root", str(root)],
        capture_output=True,
        text=True,
    )


def _project(root: Path) -> Path:
    spec = {"openapi": "3.1.0", "paths": {}, "components": {"schemas": SCHEMAS}}
    (root / "openapi.json").write_text(json.dumps(spec))
    return root


def test_typescript_types_follow_the_schema(tmp_path: Path) -> None:
    proc = _run("backend-type-bridger", _project(tmp_path))
    assert proc.returncode == 0, proc.stderr
    out = (tmp_path / "src" / "types" / "api.ts").read_text()
    assert "nick?: string | null;" in out
    assert 'export type Role = "admin" | "member";' in out
    assert "role: Role;" in out
    assert "boss?: User | null;" in out
    assert "orgs?: Org[];" in out
    assert '"x-trace"?: string;' in out
    assert "export interface Filler44 " in out


def test_dart_models_follow_the_schema(tmp_path: Path) -> None:
    proc = _run("dart-type-bridger", _project(tmp_path))
    assert proc.returncode == 0, proc.stderr
    out = (tmp_path / "lib" / "models" / "api_models.dart").read_text()
    assert "const Empty();" in out
    assert "({\n  });" not in out
    assert "final String? nick;" in out
    assert "final String? role;" in out
    assert "final Org? org;" in out
    assert "Org.fromJson(json['org'] as Map<String, dynamic>)" in out
    assert "final User? boss;" in out
    assert "final List<Org>? orgs;" in out
    assert "final List<String>? tags;" in out
    assert "final String? x_trace;" in out
    assert "x_trace: json['x-trace'] as String?," in out
    assert "class Filler44 " in out


@pytest.mark.parametrize("skill", ["backend-type-bridger", "dart-type-bridger"])
@pytest.mark.parametrize("content", [None, "{not json"])
def test_missing_or_invalid_openapi_fails(tmp_path: Path, skill: str, content: str | None) -> None:
    if content is not None:
        (tmp_path / "openapi.json").write_text(content)
    proc = _run(skill, tmp_path)
    assert proc.returncode != 0
    assert "error" in proc.stdout
