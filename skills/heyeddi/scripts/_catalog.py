"""Discover HeyEddi skills and suggest matches for a user prompt."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

DEFAULT_HUB_MARKERS = ("skills-registry.json",)

TRIGGER_FILE_CANDIDATES = (
    "reference/triggers.md",
    "reference/triggers.txt",
    "triggers.txt",
)

STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "use",
        "when",
        "with",
        "you",
        "your",
        "not",
        "all",
        "can",
        "will",
        "into",
        "via",
        "how",
        "what",
        "which",
        "who",
        "where",
        "about",
        "before",
        "after",
        "than",
        "then",
        "them",
        "they",
        "our",
        "we",
        "was",
        "were",
        "been",
        "being",
        "does",
        "did",
        "doing",
        "should",
        "would",
        "could",
        "may",
        "might",
        "must",
        "need",
        "needs",
        "using",
        "used",
        "also",
        "any",
        "each",
        "other",
        "such",
        "only",
        "just",
        "more",
        "most",
        "some",
        "like",
        "over",
        "under",
        "between",
        "through",
        "during",
        "without",
        "within",
        "while",
        "skill",
        "skills",
        "agent",
        "cursor",
        "heyeddi",
    }
)

INDEX_VERSION = 1
GENERATOR = "heyeddi@3.0.2"


def skills_index_json(project_root: Path) -> Path:
    return project_root / ".heyeddi" / "skills-index.json"


def skills_index_md(project_root: Path) -> Path:
    return project_root / ".heyeddi" / "skills-index.md"


def load_skills_index(project_root: Path) -> dict[str, Any] | None:
    path = skills_index_json(project_root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(data.get("skills"), list):
        return None
    return data


def render_skills_index_md(catalog: dict[str, Any]) -> str:
    generated = catalog.get("generated_at", "unknown")
    lines = [
        "# Skills index",
        "",
        f"**Generated:** {generated} · **Maintained by:** `@heyeddi`",
        "",
        "Cached catalog: read this instead of every `SKILL.md` at session start. "
        "Refresh after installing skills: `write_skills_index --project-root .`",
        "",
        f"**Installed:** {catalog.get('installed_count', 0)} / {catalog.get('skill_count', 0)} skills",
        "",
        "| Skill | Invoke | Installed | Description |",
        "|-------|--------|-----------|-------------|",
    ]
    for entry in catalog.get("skills", []):
        name = entry.get("name", "?")
        invoke = entry.get("invoke_as", f"@{name}")
        installed = "yes" if entry.get("installed") else "no"
        desc = (entry.get("description") or "").replace("|", "\\|")
        if len(desc) > 120:
            desc = f"{desc[:117]}..."
        lines.append(f"| {name} | {invoke} | {installed} | {desc} |")
    lines.extend(
        [
            "",
            "## Quick use",
            "",
            "1. `suggest_skills --user-prompt \"...\"`: rank skills for the task",
            "2. Read **one** chosen skill's `SKILL.md` (path in JSON index)",
            "3. Follow `docs/intake/skill-routing.json` when present",
            "",
        ]
    )
    return "\n".join(lines)


def write_skills_index(project_root: Path, hub_root: Path | None = None) -> dict[str, Any]:
    catalog = build_catalog(project_root, hub_root)
    catalog["index_version"] = INDEX_VERSION
    catalog["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalog["generator"] = GENERATOR
    catalog["installed_count"] = sum(1 for entry in catalog["skills"] if entry.get("installed"))

    heyeddi = project_root / ".heyeddi"
    heyeddi.mkdir(parents=True, exist_ok=True)

    json_path = skills_index_json(project_root)
    md_path = skills_index_md(project_root)
    json_path.write_text(json.dumps(catalog, indent=2) + "\n")
    md_path.write_text(render_skills_index_md(catalog))

    return {
        "ok": True,
        "written": [str(json_path.relative_to(project_root)), str(md_path.relative_to(project_root))],
        "generated_at": catalog["generated_at"],
        "skill_count": catalog["skill_count"],
        "installed_count": catalog["installed_count"],
    }


def get_catalog(
    project_root: Path,
    hub_root: Path | None = None,
    *,
    refresh: bool = False,
    write_if_missing: bool = True,
) -> dict[str, Any]:
    """Prefer `.heyeddi/skills-index.json`; scan filesystem when missing or refresh."""
    if not refresh:
        cached = load_skills_index(project_root)
        if cached:
            cached = dict(cached)
            cached["loaded_from"] = str(skills_index_json(project_root).relative_to(project_root))
            return cached

    catalog = build_catalog(project_root, hub_root)
    if write_if_missing or refresh:
        write_info = write_skills_index(project_root, hub_root)
        reloaded = load_skills_index(project_root)
        if reloaded:
            catalog = dict(reloaded)
        catalog["loaded_from"] = "scan+write"
        catalog["write"] = write_info
    else:
        catalog["loaded_from"] = "scan"
    return catalog


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(errors="replace")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            fields[key.strip()] = val.strip()
    return fields


def find_hub_root(start: Path | None = None) -> Path | None:
    """Locate hub root from cwd / start only: no env, no home directory."""
    for candidate in (start, Path.cwd()) if start else (Path.cwd(),):
        if candidate is None:
            continue
        for directory in (candidate, *candidate.parents):
            if (directory / "skills-registry.json").is_file():
                return directory
            if all((directory / marker).exists() for marker in DEFAULT_HUB_MARKERS):
                return directory
    return None


def skill_search_roots(project_root: Path, hub_root: Path | None) -> list[Path]:
    """Install-tree roots only: never user-home or env-controlled paths."""
    roots: list[Path] = []
    if hub_root:
        roots.append(hub_root / "skills")
    agents = project_root / ".agents" / "skills"
    if agents.is_dir():
        roots.append(agents)
    cursor_project = project_root / ".cursor" / "skills"
    if cursor_project.is_dir():
        roots.append(cursor_project)
    return roots


def read_registry(hub_root: Path | None) -> list[dict[str, str]]:
    if not hub_root:
        return []
    registry_path = hub_root / "skills-registry.json"
    if not registry_path.is_file():
        return []
    data = json.loads(registry_path.read_text())
    return list(data.get("skills", []))


def resolve_skill_md(name: str, search_roots: list[Path]) -> Path | None:
    for root in search_roots:
        candidate = root / name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if len(token) > 2 and token not in STOP_WORDS}


def name_tokens(skill_name: str) -> set[str]:
    parts = re.split(r"[-_]+", skill_name.lower())
    return {part for part in parts if len(part) > 2 and part not in STOP_WORDS}


def extract_phrases(text: str) -> list[str]:
    """Two- and three-word phrases from description for substring matching."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    phrases: list[str] = []
    for size in (3, 2):
        for index in range(len(words) - size + 1):
            chunk = words[index : index + size]
            if any(len(word) <= 2 for word in chunk):
                continue
            if all(word in STOP_WORDS for word in chunk):
                continue
            phrases.append(" ".join(chunk))
    return phrases


def load_skill_triggers(skill_dir: Path | None) -> list[tuple[str, bool]]:
    """Return (pattern, is_regex) from optional per-skill trigger files."""
    if skill_dir is None or not skill_dir.is_dir():
        return []
    for rel in TRIGGER_FILE_CANDIDATES:
        path = skill_dir / rel
        if not path.is_file():
            continue
        patterns: list[tuple[str, bool]] = []
        for raw_line in path.read_text(errors="replace").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            line = re.sub(r"^[-*]\s+", "", line).strip()
            if not line:
                continue
            if line.startswith("regex:"):
                patterns.append((line[6:].strip(), True))
            elif line.startswith("/") and line.endswith("/") and len(line) > 2:
                patterns.append((line[1:-1], True))
            else:
                patterns.append((line, False))
        return patterns
    return []


def score_entry(entry: dict[str, Any], prompt: str) -> tuple[int, list[str]]:
    """Score one catalog entry against a prompt: no hardcoded skill map."""
    prompt_lower = prompt.lower()
    prompt_tokens = tokenize(prompt)
    score = 0
    reasons: list[str] = []

    description = entry.get("scoring_text") or entry.get("description") or ""
    desc_tokens = tokenize(description)
    overlap = prompt_tokens & desc_tokens
    if overlap:
        score += len(overlap) * 3
        for token in sorted(overlap)[:4]:
            reasons.append(f"description: {token}")

    for phrase in extract_phrases(description):
        if phrase in prompt_lower:
            score += 4
            reasons.append(f"description phrase: {phrase}")

    for token in name_tokens(entry["name"]):
        if token in prompt_tokens:
            score += 5
            reasons.append(f"name: {token}")

    skill_dir = entry.get("skill_dir")
    skill_dir_path = Path(skill_dir) if skill_dir else None
    cached_triggers = entry.get("triggers")
    if cached_triggers:
        trigger_items = [(item["pattern"], item.get("regex", False)) for item in cached_triggers]
    else:
        trigger_items = load_skill_triggers(skill_dir_path)
    for pattern, is_regex in trigger_items:
        if is_regex:
            try:
                matched = re.search(pattern, prompt_lower, re.IGNORECASE) is not None
            except re.error:
                matched = False
        else:
            matched = pattern.lower() in prompt_lower
        if matched:
            score += 6
            label = pattern if len(pattern) <= 40 else f"{pattern[:37]}..."
            reasons.append(f"trigger: {label}")

    return score, reasons


def build_catalog(project_root: Path, hub_root: Path | None = None) -> dict[str, Any]:
    hub = hub_root or find_hub_root(project_root)
    registry = read_registry(hub)
    search_roots = skill_search_roots(project_root, hub)
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()

    def append_entry(
        name: str,
        registry_description: str,
        skill_md: Path | None,
        *,
        source: str | None = None,
    ) -> None:
        frontmatter = parse_frontmatter(skill_md) if skill_md else {}
        fm_desc = frontmatter.get("description", "")
        registry_desc = registry_description or ""
        scoring_text = " ".join(part for part in (registry_desc, fm_desc) if part).strip()
        trigger_list = load_skill_triggers(skill_md.parent if skill_md else None)
        item: dict[str, Any] = {
            "name": name,
            "description": fm_desc or registry_desc,
            "scoring_text": scoring_text,
            "version": frontmatter.get("version", ""),
            "installed": skill_md is not None,
            "skill_md": str(skill_md) if skill_md else None,
            "skill_dir": str(skill_md.parent) if skill_md else None,
            "invoke_as": f"@{name}",
            "has_triggers_file": bool(trigger_list),
            "triggers": [{"pattern": pattern, "regex": is_regex} for pattern, is_regex in trigger_list],
        }
        if source:
            item["source"] = source
        entries.append(item)

    for item in registry:
        name = item.get("name", "")
        if not name or name in seen:
            continue
        seen.add(name)
        skill_md = resolve_skill_md(name, search_roots)
        append_entry(name, item.get("description", ""), skill_md)

    for root in search_roots:
        if not root.is_dir():
            continue
        for skill_dir in sorted(root.iterdir()):
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
                continue
            name = skill_dir.name
            if name in seen:
                continue
            seen.add(name)
            skill_md = skill_dir / "SKILL.md"
            append_entry(name, "", skill_md, source="local-only")

    entries.sort(key=lambda entry: entry["name"])
    return {
        "hub_root": str(hub) if hub else None,
        "project_root": str(project_root),
        "skill_count": len(entries),
        "skills": entries,
    }


def load_routing(project_root: Path) -> dict[str, Any] | None:
    path = project_root / ".heyeddi" / "docs" / "intake" / "skill-routing.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def product_md_exists(project_root: Path) -> bool:
    for rel in (".heyeddi/product.md", ".heyeddi/PRODUCT.md", "PRODUCT.md"):
        if (project_root / rel).is_file():
            return True
    return False


def suggest_skills(
    project_root: Path,
    user_prompt: str,
    *,
    hub_root: Path | None = None,
    limit: int = 8,
    refresh_index: bool = False,
) -> dict[str, Any]:
    catalog = get_catalog(project_root, hub_root, refresh=refresh_index)
    routing = load_routing(project_root)
    suggestions: list[dict[str, Any]] = []

    if routing:
        for route in routing.get("routes", []):
            skill = route.get("skill")
            if not skill:
                continue
            suggestions.append(
                {
                    "skill": skill,
                    "score": 100,
                    "reason": f"skill-routing.json route {route.get('route', '?')}",
                    "route": route.get("route"),
                    "feature": route.get("feature"),
                    "source": "skill-routing.json",
                }
            )
        for scaffold_skill in routing.get("scaffold", []):
            name = scaffold_skill.split()[0] if isinstance(scaffold_skill, str) else ""
            if name:
                suggestions.append(
                    {
                        "skill": name,
                        "score": 90,
                        "reason": "skill-routing.json scaffold step",
                        "source": "skill-routing.json",
                    }
                )

    for entry in catalog["skills"]:
        if not entry.get("installed"):
            continue
        score, reasons = score_entry(entry, user_prompt)
        if score <= 0:
            continue
        suggestions.append(
            {
                "skill": entry["name"],
                "score": score,
                "reason": "; ".join(reasons[:4]),
                "source": "description-match",
            }
        )

    merged: dict[str, dict[str, Any]] = {}
    for item in suggestions:
        skill = item["skill"]
        existing = merged.get(skill)
        if existing is None or item["score"] > existing["score"]:
            merged[skill] = item

    ranked = sorted(merged.values(), key=lambda item: (-item["score"], item["skill"]))[:limit]

    workflow: list[str] = []
    if routing:
        workflow.append("Follow .heyeddi/docs/intake/skill-routing.json route order.")
    elif not product_md_exists(project_root) and ranked:
        top = ranked[0]
        workflow.append(
            f"No product.md yet: top match @{top['skill']} ({top['reason']}). "
            "Confirm intake/product doc skill before implementation."
        )
    elif ranked:
        workflow.append(f"Read @{ranked[0]['skill']} SKILL.md, then invoke tools.")
    else:
        workflow.append("Run load_catalog and pick a skill whose description fits the task.")

    return {
        "prompt_char_count": len(user_prompt.strip()),
        "routing_found": routing is not None,
        "product_md_found": product_md_exists(project_root),
        "catalog_skill_count": catalog["skill_count"],
        "catalog_source": catalog.get("loaded_from", "scan"),
        "skills_index": str(skills_index_json(project_root).relative_to(project_root)),
        "scoring": "description tokens + name tokens + cached triggers (no hardcoded map)",
        "suggestions": ranked,
        "recommended_workflow": workflow,
        "note": (
            "Read `.heyeddi/skills-index.md` for the full catalog without opening every SKILL.md. "
            "Refresh index after skill installs. Read one chosen SKILL.md before invoking tools. "
            "Caller prompt text is not echoed (prompt-injection boundary)."
        ),
    }
