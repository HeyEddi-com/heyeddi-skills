#!/usr/bin/env python3
"""Sync local OpenAPI schema to Dart model stubs under lib/models/.

Security: reads only a local file under the project root. Never fetches remote
URLs (avoids SSRF / third-party content in agent context). Agents must place
``openapi.json`` on disk first (scaffold, export, or curl to a file).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _skill_cli import emit, resolve_project_root


def resolve_openapi_path(root: Path, relative: str) -> Path | None:
    """Return an openapi file path if it exists and stays under project root."""
    if "://" in relative:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


RESERVED = frozenset(
    "assert break case catch class const continue default do else enum extends false final finally "
    "for if in is new null rethrow return super switch this throw true try var void while with".split()
)


def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


def field_name(name: str) -> str:
    out = re.sub(r"[^a-zA-Z0-9_$]", "_", name)
    if not out or out[0].isdigit() or out[0] == "_":
        out = f"f{out}" if out.startswith("_") else f"f_{out}"
    return f"{out}_" if out in RESERVED else out


def is_class(schema: dict) -> bool:
    if any(key in schema for key in ("$ref", "enum", "anyOf", "oneOf", "allOf")):
        return False
    if "properties" in schema:
        return True
    return schema.get("type") == "object" and not isinstance(schema.get("additionalProperties"), dict)


def dart_type(schema: dict, schemas: dict, seen: frozenset[str] = frozenset()) -> str:
    """Dart type (without `?`) for one OpenAPI schema. Enums map to their value type."""
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        target = schemas.get(name)
        if target is None or name in seen:
            return "dynamic"
        return safe_name(name) if is_class(target) else dart_type(target, schemas, seen | {name})
    for key in ("anyOf", "oneOf", "allOf"):
        if key in schema:
            parts = [part for part in schema[key] if part.get("type") != "null"]
            return dart_type(parts[0], schemas, seen) if len(parts) == 1 else "dynamic"
    kind = schema.get("type")
    if isinstance(kind, list):
        kinds = [one for one in kind if one != "null"]
        kind = kinds[0] if len(kinds) == 1 else None
    if kind is None and schema.get("enum") and all(isinstance(v, str) for v in schema["enum"]):
        kind = "string"
    if kind == "string":
        return "DateTime" if schema.get("format") == "date-time" else "String"
    if kind == "array":
        return f"List<{dart_type(schema.get('items', {}), schemas, seen)}>"
    if kind == "object" or "properties" in schema:
        return "Map<String, dynamic>"
    return {"integer": "int", "number": "double", "boolean": "bool"}.get(kind, "dynamic")


def convert(kind: str, source: str) -> str:
    """Expression that turns a non-null JSON value into `kind`."""
    if kind == "dynamic":
        return source
    if kind == "int":
        return f"({source} as num).toInt()"
    if kind == "double":
        return f"({source} as num).toDouble()"
    if kind == "DateTime":
        return f"DateTime.parse({source} as String)"
    if kind.startswith("List<"):
        item = kind[5:-1]
        if item == "dynamic":
            return f"{source} as List<dynamic>"
        return f"({source} as List<dynamic>).map((e) => {convert(item, 'e')}).toList()"
    if kind in ("String", "bool", "Map<String, dynamic>"):
        return f"{source} as {kind}"
    return f"{kind}.fromJson({source} as Map<String, dynamic>)"


def from_json(kind: str, key: str) -> str:
    escaped = key.replace("\\", "\\\\").replace("'", "\\'").replace("$", "\\$")
    source = f"json['{escaped}']"
    if kind == "dynamic":
        return source
    if kind in ("String", "bool", "Map<String, dynamic>", "List<dynamic>"):
        return f"{source} as {kind}?"
    if kind in ("int", "double"):
        return f"({source} as num?)?.to{'Int' if kind == 'int' else 'Double'}()"
    return f"{source} != null ? {convert(kind, source)} : null"


def render_class(name: str, schema: dict, schemas: dict) -> str:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    factory = f"  factory {name}.fromJson(Map<String, dynamic> json) {{"
    if not props:
        return "\n".join(
            [f"class {name} {{", f"  const {name}();", "", factory, f"    return const {name}();", "  }", "}"]
        )
    fields = [(key, field_name(key), dart_type(meta, schemas)) for key, meta in props.items()]
    lines = [f"class {name} {{", f"  const {name}({{"]
    for key, field, _ in fields:
        lines.append(f"    {'required ' if key in required else ''}this.{field},")
    lines += ["  });", ""]
    for _, field, kind in fields:
        lines.append(f"  final {kind}{'' if kind == 'dynamic' else '?'} {field};")
    lines += ["", factory, f"    return {name}("]
    for key, field, kind in fields:
        lines.append(f"      {field}: {from_json(kind, key)},")
    lines += ["    );", "  }", "}"]
    return "\n".join(lines)


def fail_json(payload: dict) -> None:
    emit(json.dumps(payload, indent=2))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync local openapi.json to Dart models (no network fetch)"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--openapi",
        default="openapi.json",
        help="Path relative to project root (default: openapi.json)",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    openapi_path = resolve_openapi_path(root, args.openapi)
    if openapi_path is None:
        fail_json(
            {
                "error": "no local openapi file",
                "hint": (
                    "Place OpenAPI JSON at openapi.json (or pass --openapi <relpath>). "
                    "Do not fetch URLs inside this skill: export from FastAPI or: "
                    "curl -fsS http://127.0.0.1:8090/openapi.json -o openapi.json"
                ),
            }
        )

    try:
        spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail_json({"error": f"invalid openapi JSON: {exc}", "source": str(openapi_path)})

    schemas = spec.get("components", {}).get("schemas", {})
    out_dir = root / "lib" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "api_models.dart"

    parts = [
        "// Generated from OpenAPI. Do not edit: put refinements in another file.",
        f"// Source: {openapi_path.name}",
        "",
    ]
    written: list[str] = []
    for name, schema in schemas.items():
        safe = re.sub(r"[^a-zA-Z0-9_]", "", name)
        if not safe:
            continue
        if is_class(schema):
            parts.append(render_class(safe, schema, schemas))
            parts.append("")
            written.append(safe)

    out_file.write_text("\n".join(parts))

    emit(
        json.dumps(
            {
                "source": str(openapi_path.relative_to(root)),
                "schema_count": len(schemas),
                "written": str(out_file.relative_to(root)),
                "interfaces": written,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
