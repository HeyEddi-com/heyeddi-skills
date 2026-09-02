"""Suggest the next HeyEddi skill and user prompt after a pipeline task completes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _catalog import load_routing

ORCHESTRATOR_SCRIPT = (
    ".agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py"
)

# Default pipeline when skill-routing.json is absent or exhausted.
# `prompt` = what the user should paste in chat (@skill + sub-command + target).
DEFAULT_NEXT: dict[str, dict[str, str]] = {
    "heyeddi-intake": {
        "skill": "heyeddi-product",
        "prompt": "@heyeddi-product audit the product and write feature specs for each routed surface",
        "why": "Validate product.md and backlog before design or scaffold.",
    },
    "heyeddi-product": {
        "skill": "heyeddi-design",
        "prompt": "@heyeddi-design shape <route> from product.md personas and route intent",
        "why": "Turn product intent into a confirmed design brief before craft or handoff.",
    },
    "heyeddi-orchestrator": {
        "skill": "heyeddi-intake",
        "prompt": "@heyeddi-intake: describe the app or feature in plain language",
        "why": "No locked task yet: intake when product.md is thin or the goal is greenfield.",
    },
    "heyeddi-design": {
        "skill": "heyeddi-handoff",
        "prompt": "@heyeddi-handoff implement <route> from .heyeddi/designs/<feature>/",
        "why": "Brief or mockups ready: stack implementer builds Vue, then visual QA.",
    },
    "heyeddi-handoff": {
        "skill": "visual-auditor",
        "prompt": "@visual-auditor review and fix <route> against product.md and design.md",
        "why": "Visual QA after implementation: capture, contrast, fix, document.",
    },
    "design-handoff-flutter": {
        "skill": "visual-auditor",
        "prompt": "@visual-auditor review and fix <route> on Flutter web against product.md and design.md",
        "why": "Visual QA after Material handoff.",
    },
    "project-engineering": {
        "skill": "heyeddi-design",
        "prompt": "@heyeddi-design shape the first user-facing route now that the stack is scaffolded",
        "why": "Scaffold is up: design the first surface before more engineering.",
    },
    "flutter-engineering": {
        "skill": "heyeddi-design",
        "prompt": "@heyeddi-design shape the first Flutter route from product.md",
        "why": "Flutter scaffold is up: brief the first screen before handoff.",
    },
    "visual-auditor": {
        "skill": "pre-merge-gate",
        "prompt": "@pre-merge-gate run the merge readiness checklist",
        "why": "Full QA gate after visual fixes pass.",
    },
    "pre-merge-gate": {
        "skill": "heyeddi-pr-review",
        "prompt": "@heyeddi-pr-review review PR #<number> before merge",
        "why": "Submission review on the committed diff when a PR is open.",
    },
    "heyeddi-pr-review": {
        "skill": "heyeddi-pr-respond",
        "prompt": "@heyeddi-pr-respond address all review comments on PR #<number>",
        "why": "PR author: fix or decline each thread, then re-gate.",
    },
    "heyeddi-pr-respond": {
        "skill": "pre-merge-gate",
        "prompt": "@pre-merge-gate re-run gates after addressing review feedback",
        "why": "All threads responded and CI fixed: confirm merge readiness.",
    },
    "heyeddi-ci-config": {
        "skill": "heyeddi-ci-guide",
        "prompt": "@heyeddi-ci-guide summarize commands, authorize-merge rules, and feedback paths",
        "why": "Config is set: orient on CI commands and safety before respond/fails.",
    },
    "heyeddi-ci-guide": {
        "skill": "heyeddi-pr-respond",
        "prompt": "@heyeddi-pr-respond address review feedback on PR #<number> (human + HeyEddi CI)",
        "why": "Guide done: respond to all PR review findings.",
    },
    "heyeddi-ci-fails": {
        "skill": "heyeddi-pr-respond",
        "prompt": "@heyeddi-pr-respond address all review feedback on PR #<number>",
        "why": "CI failures fixed: respond to all PR review threads.",
    },
    "heyeddi-ci-runners": {
        "skill": "heyeddi-ci-guide",
        "prompt": "@heyeddi-ci-guide confirm runners are placeholder/fail-closed and list next CI skills",
        "why": "Pipeline YAML authored: restate fail-closed status and safety.",
    },
}

# Overrides when the finishing skill used a specific sub-command (e.g. design shape → craft).
MODE_NEXT: dict[str, dict[str, dict[str, str]]] = {
    "heyeddi-design": {
        "critique": {
            "skill": "visual-auditor",
            "prompt": "@visual-auditor review and fix <route> against product.md and design.md",
            "why": "Critique done: visual QA implements P0/P1 fixes from the report.",
        },
        "polish": {
            "skill": "visual-auditor",
            "prompt": "@visual-auditor re-check <route> after polish",
            "why": "Polish changed UI: confirm contrast and layout vs spec.",
        },
        "document": {
            "skill": "heyeddi-design",
            "prompt": "@heyeddi-design shape <route> for the next surface",
            "why": "Design system is documented: shape the next route.",
        },
    },
    "heyeddi-product": {
        "audit": {
            "skill": "heyeddi-design",
            "prompt": "@heyeddi-design shape <route> from the audit findings",
            "why": "Product audit is done: design the highest-priority route.",
        },
        "review": {
            "skill": "pre-merge-gate",
            "prompt": "@pre-merge-gate run the merge readiness checklist",
            "why": "Holistic PM review is complete: confirm gates before ship.",
        },
    },
    "heyeddi-orchestrator": {
        "sync": {
            "skill": "heyeddi-intake",
            "prompt": "@heyeddi-intake: continue product intake for this project",
            "why": "Workspace synced: intake if product context is still thin.",
        },
    },
}

DONE_NEXT: dict[str, str] = {
    "skill": "heyeddi-orchestrator",
    "prompt": "@heyeddi-orchestrator: what skill should handle: <describe next task>",
    "why": "Pipeline step complete: orchestrator picks the next @skill.",
}

def _frontend_stack(project_root: Path) -> str:
    stack_path = project_root / ".heyeddi" / "stack.json"
    if stack_path.is_file():
        try:
            data = json.loads(stack_path.read_text(encoding="utf-8"))
            return str(data.get("frontend") or "vue").lower()
        except (json.JSONDecodeError, OSError):
            pass
    if (project_root / "pubspec.yaml").is_file():
        return "flutter"
    return "vue"


def _implement_next(project_root: Path, route: str | None) -> dict[str, str]:
    frontend = _frontend_stack(project_root)
    route_token = route or "/<route>"
    if frontend == "flutter":
        return {
            "skill": "design-handoff-flutter",
            "prompt": f"@design-handoff-flutter implement {route_token} from .heyeddi/designs/<feature>/",
            "why": "Brief confirmed: Flutter implementer builds the screen, then visual QA.",
        }
    return {
        "skill": "heyeddi-handoff",
        "prompt": f"@heyeddi-handoff implement {route_token} from .heyeddi/designs/<feature>/",
        "why": "Brief confirmed: Vue implementer builds the screen, then visual QA.",
    }


def _feature_slug(route: str | None, feature: str | None = None) -> str:
    if feature:
        return feature
    if not route or route == "/":
        return "home"
    return route.strip("/").replace("/", "-")


def _substitute_placeholders(
    text: str,
    *,
    route: str | None,
    feature: str | None = None,
) -> str:
    slug = _feature_slug(route, feature)
    if route:
        text = text.replace("<route>", route)
    else:
        text = text.replace("<route>", "/<route>")
    text = text.replace("<feature>", slug)
    return text


def _prompt_for_route(route: dict[str, Any]) -> str:
    skill = str(route.get("skill") or "")
    route_path = route.get("route") or "/"
    feature = route.get("feature") or _feature_slug(route_path)
    mode = route.get("mode") or ""

    if skill == "heyeddi-design":
        sub = mode or "craft"
        return f"@heyeddi-design {sub} {route_path}: feature `{feature}`"
    if skill == "heyeddi-handoff":
        return (
            f"@heyeddi-handoff implement {route_path} from "
            f".heyeddi/designs/{feature}/"
        )
    if skill == "design-handoff-flutter":
        return (
            f"@design-handoff-flutter implement {route_path} from "
            f".heyeddi/designs/{feature}/"
        )
    if skill == "visual-auditor":
        return f"@visual-auditor review and fix {route_path}"
    if skill == "heyeddi-product":
        return f"@heyeddi-product holistic review for {route_path}"
    return f"@{skill}: work on `{feature}` at {route_path}"


def _entry(
    skill: str,
    prompt: str,
    *,
    why: str,
    source: str,
    route: str = "",
    feature: str = "",
) -> dict[str, str]:
    return {
        "skill": skill,
        "prompt": prompt,
        "why": why,
        "source": source,
        **({"route": route} if route else {}),
        **({"feature": feature} if feature else {}),
    }


def _route_entry(skill: str, route: dict[str, Any], *, why: str) -> dict[str, str]:
    return _entry(
        skill,
        _prompt_for_route(route),
        why=why,
        source="skill-routing.json",
        route=str(route.get("route") or ""),
        feature=str(route.get("feature") or ""),
    )


def _scaffold_entry(step: str, *, why: str) -> dict[str, str]:
    parts = step.split()
    skill = parts[0]
    tail = " ".join(parts[1:])
    if skill in {"project-engineering", "flutter-engineering"}:
        prompt = f"@{skill} scaffold the full stack for this project"
    elif tail.startswith("scaffold_stack"):
        prompt = f"@{skill.split('-')[0] if '-' in skill else skill} scaffold: run stack setup"
    else:
        prompt = f"@{skill} {tail}" if tail else f"@{skill}: read SKILL.md"
    return _entry(skill, prompt, why=why, source="skill-routing.json")


def _has_mockups(project_root: Path, route: str | None, feature: str | None) -> bool:
    designs = project_root / ".heyeddi" / "designs"
    if not designs.is_dir():
        return False
    slug = _feature_slug(route, feature)
    for candidate in (designs / slug, designs / (slug.replace("-", "_"))):
        if candidate.is_dir() and any(candidate.glob("*.png")):
            return True
    return any(designs.glob("**/*.png"))


def _next_from_routing(
    routing: dict[str, Any],
    current_skill: str,
    *,
    current_route: str | None,
) -> dict[str, str] | None:
    routes: list[dict[str, Any]] = list(routing.get("routes") or [])

    if current_skill == "heyeddi-intake":
        scaffold = routing.get("scaffold") or []
        if scaffold:
            return _scaffold_entry(
                str(scaffold[0]),
                why="First scaffold step from skill-routing.json after intake.",
            )
        if routes:
            first = routes[0]
            return _route_entry(
                str(first.get("skill") or ""),
                first,
                why="First routed surface after intake.",
            )

    if current_skill in {"project-engineering", "flutter-engineering"}:
        scaffold = routing.get("scaffold") or []
        if len(scaffold) > 1 and current_skill == str(scaffold[0]).split()[0]:
            return _scaffold_entry(
                str(scaffold[1]),
                why="Second scaffold step from skill-routing.json.",
            )
        if routes:
            first = routes[0]
            return _route_entry(
                str(first.get("skill") or ""),
                first,
                why="First design/handoff route after scaffold.",
            )

    index: int | None = None
    if current_route:
        for idx, route in enumerate(routes):
            if route.get("route") == current_route:
                index = idx
                break

    if index is None:
        for idx, route in enumerate(routes):
            route_skill = str(route.get("skill") or "")
            if route_skill == current_skill:
                index = idx
                break

    if index is not None and index + 1 < len(routes):
        nxt = routes[index + 1]
        prev = routes[index]
        return _route_entry(
            str(nxt.get("skill") or ""),
            nxt,
            why=f"Next route after {prev.get('route', '?')} in skill-routing.json.",
        )

    if index is not None and index + 1 >= len(routes):
        return dict(DEFAULT_NEXT.get("pre-merge-gate", DONE_NEXT))

    return None


def format_user_block(next_step: dict[str, str]) -> str:
    skill = next_step.get("skill", "")
    prompt = next_step.get("prompt", next_step.get("command", ""))
    why = next_step.get("why", "")
    lines = [
        "### Next step",
        f"**Skill:** `@{skill}`",
        f"**Prompt:** {prompt}",
        f"**Why:** {why}",
    ]
    route = next_step.get("route")
    if route:
        lines.insert(3, f"**Route:** `{route}`")
    return "\n".join(lines)


def suggest_next_skill(
    project_root: Path,
    *,
    current_skill: str | None = None,
    current_route: str | None = None,
    current_mode: str | None = None,
    hub_root: Path | None = None,
) -> dict[str, Any]:
    routing = load_routing(project_root)

    skill = (current_skill or "").strip()
    mode = (current_mode or "").strip().lower()
    next_step: dict[str, str] | None = None

    if mode and skill == "heyeddi-design" and mode in {"shape", "craft"}:
        next_step = _implement_next(project_root, current_route)
        next_step["source"] = "mode-chain"
    elif mode and skill in MODE_NEXT and mode in MODE_NEXT[skill]:
        next_step = dict(MODE_NEXT[skill][mode])
        next_step["source"] = "mode-chain"

    if next_step is None and routing and skill:
        next_step = _next_from_routing(
            routing,
            skill,
            current_route=current_route,
        )

    if next_step is None and skill == "heyeddi-design":
        next_step = _implement_next(project_root, current_route)
        next_step["source"] = "default-chain"

    if next_step is None and skill and skill in DEFAULT_NEXT:
        next_step = dict(DEFAULT_NEXT[skill])
        next_step["source"] = "default-chain"

    if next_step is None:
        next_step = dict(DONE_NEXT)
        next_step["source"] = "fallback"

    feature = next_step.get("feature") or None
    prompt = _substitute_placeholders(
        next_step.get("prompt", next_step.get("command", "")),
        route=current_route,
        feature=feature,
    )
    next_step["prompt"] = prompt
    next_step.pop("command", None)

    helper = (
        f"python {ORCHESTRATOR_SCRIPT} --current-skill {skill or 'heyeddi-orchestrator'} "
        f"--project-root ."
    )
    if current_route:
        helper += f' --route "{current_route}"'
    if mode:
        helper += f' --mode "{mode}"'

    return {
        "current_skill": skill or current_skill,
        "current_mode": mode or None,
        "routing_found": routing is not None,
        "next": next_step,
        "helper_command": helper,
        "user_block": format_user_block(next_step),
        "instruction": (
            "When the user's task for this skill is complete, end your final reply with user_block. "
            "The Prompt is what they paste in chat: @skill plus sub-command (shape, craft, sync, audit, etc.)."
        ),
    }
