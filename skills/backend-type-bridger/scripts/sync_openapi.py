#!/usr/bin/env python3
"""Sync local OpenAPI schema to TypeScript types under src/types/api.ts.

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
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    # Refuse URL-shaped arguments that somehow landed in --openapi
    if "://" in relative:
        return None
    return candidate


def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


def property_key(name: str) -> str:
    return name if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name) else json.dumps(name)


def union(parts: list[str], joiner: str = " | ") -> str:
    return joiner.join(dict.fromkeys(parts)) or "unknown"


def ts_type(schema: dict) -> str:
    """TypeScript type for one OpenAPI 3.0 or 3.1 schema."""
    if "$ref" in schema:
        base = safe_name(schema["$ref"].rsplit("/", 1)[-1])
    elif "const" in schema:
        base = json.dumps(schema["const"])
    elif "enum" in schema:
        base = union([json.dumps(value) for value in schema["enum"]])
    elif "anyOf" in schema or "oneOf" in schema:
        base = union([ts_type(part) for part in schema.get("anyOf") or schema.get("oneOf")])
    elif "allOf" in schema:
        base = union([ts_type(part) for part in schema["allOf"]], " & ")
    else:
        kind = schema.get("type")
        if isinstance(kind, list):
            base = union([ts_type({**schema, "type": one}) for one in kind])
        elif kind == "array":
            item = ts_type(schema.get("items", {}))
            base = f"({item})[]" if " " in item else f"{item}[]"
        elif kind == "object" or "properties" in schema:
            extra = schema.get("additionalProperties")
            if "properties" in schema:
                base = "{ " + " ".join(render_fields(schema)) + " }"
            elif isinstance(extra, dict):
                base = f"Record<string, {ts_type(extra)}>"
            else:
                base = "Record<string, unknown>"
        else:
            base = {
                "string": "string",
                "integer": "number",
                "number": "number",
                "boolean": "boolean",
                "null": "null",
            }.get(kind, "unknown")
    if schema.get("nullable") and base != "null":
        base = f"{base} | null"
    return base


def render_fields(schema: dict) -> list[str]:
    required = set(schema.get("required", []))
    return [
        f"{property_key(name)}{'' if name in required else '?'}: {ts_type(meta)};"
        for name, meta in schema.get("properties", {}).items()
    ]


def render_declaration(name: str, schema: dict) -> str:
    composed = any(key in schema for key in ("$ref", "enum", "const", "anyOf", "oneOf", "allOf"))
    plain_object = "properties" in schema or (
        schema.get("type") == "object" and not isinstance(schema.get("additionalProperties"), dict)
    )
    if plain_object and not composed and not schema.get("nullable"):
        lines = [f"export interface {name} {{", *(f"  {line}" for line in render_fields(schema)), "}"]
        return "\n".join(lines)
    return f"export type {name} = {ts_type(schema)};"


def fail_json(payload: dict) -> None:
    emit(json.dumps(payload, indent=2))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync local openapi.json to TypeScript types (no network fetch)"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--openapi",
        default="openapi.json",
        help="Path relative to project root (default: openapi.json)",
    )
    parser.add_argument("--output", default="src/types/api.ts")
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
    out_file = root / args.output
    out_file.parent.mkdir(parents=True, exist_ok=True)

    parts = [
        "/** Generated from OpenAPI. Do not edit: put refinements in another file. */",
        f"// Source: {openapi_path.name}",
        "",
    ]
    written: list[str] = []
    for name, schema in schemas.items():
        safe = safe_name(name)
        if not safe:
            continue
        parts.append(render_declaration(safe, schema))
        parts.append("")
        written.append(safe)

    content = "\n".join(parts).rstrip() + "\n"
    out_file.write_text(content)

    # Emit summary only: never dump raw OpenAPI into agent context
    emit(
        json.dumps(
            {
                "source": str(openapi_path.relative_to(root)),
                "schema_count": len(schemas),
                "path_count": len(spec.get("paths", {})),
                "written": str(out_file.relative_to(root)),
                "interfaces": written,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
