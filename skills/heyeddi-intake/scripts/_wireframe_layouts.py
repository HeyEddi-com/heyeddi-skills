"""Product-specific wireframe scaffolds: layout varies by route purpose, not one PNG template."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PageContext:
    product_name: str
    route: str
    feature: str
    purpose: str
    view: str = "View"
    primary_persona: str = ""
    success_feeling: str = ""


def _slug_title(feature: str) -> str:
    return feature.replace("-", " ").title()


def _classify(purpose: str, route: str) -> str:
    p = purpose.lower()
    r = route.lower()
    if r in ("/", "") or "marketing" in p or "homepage" in p or "hero" in p:
        return "marketing"
    if "login" in r or "sign-in" in p or "sign in" in p:
        return "login"
    if "dashboard" in r or "roster" in p or "table" in p or "team" in p:
        return "dashboard"
    if "settings" in r or "profile" in p or "notification" in p:
        return "settings"
    return "generic"


def _regions_table(rows: list[tuple[str, str, str, str]]) -> str:
    lines = [
        "## Regions (required)",
        "| Region | Desktop | Mobile | Suggested component |",
        "|--------|---------|--------|---------------------|",
    ]
    for region, desktop, mobile, component in rows:
        lines.append(f"| {region} | {desktop} | {mobile} | {component} |")
    return "\n".join(lines) + "\n"


def wireframe_marketing(ctx: PageContext) -> str:
    title = _slug_title(ctx.feature)
    return f"""# Wireframe: {title} ({ctx.product_name})

Fidelity: wireframe (layout only). Colors from `.heyeddi/design.md`.
Route: `{ctx.route}` · Purpose: {ctx.purpose}

## Desktop (ASCII)

```
+------------------------------------------------------------------+
| {ctx.product_name:<20}                    [Features] [Pricing] [Sign in] |
+------------------------------------------------------------------+
|                                                                  |
|     {ctx.product_name}: headline from product voice              |
|     Subhead: {ctx.success_feeling or 'clear value for primary persona'} |
|                                                                  |
|     [ Primary CTA → /login ]    [ Secondary learn more ]         |
|                                                                  |
|     +----------------+  +----------------+  +----------------+   |
|     | Feature block  |  | Feature block  |  | Feature block  |   |
|     | (3 bullets)    |  |                |  |                |   |
|     +----------------+  +----------------+  +----------------+   |
|                                                                  |
+------------------------------------------------------------------+
```

## Mobile

```
[{ctx.product_name}]
Headline (2 lines max)
Subhead
[ Primary CTA full width ]
[ Feature ][ Feature ]
[ Feature ]
```

{_regions_table([
    ("Top nav", "Logo left, links right", "Logo + menu", "Marketing header"),
    ("Hero", "Centered copy + dual CTA", "Stacked", "Hero section"),
    ("Feature grid", "3 columns", "1 column stack", "Card grid"),
])}
"""


def wireframe_login(ctx: PageContext) -> str:
    title = _slug_title(ctx.feature)
    return f"""# Wireframe: {title} ({ctx.product_name})

Fidelity: wireframe (layout only). Colors from `.heyeddi/design.md`.
Route: `{ctx.route}` · Purpose: {ctx.purpose}

## Desktop (ASCII)

```
+------------------------------------------------------------------+
| {ctx.product_name:<20}                              [Back to home] |
+------------------------------------------------------------------+
|                    +---------------------------+                 |
|                    | Sign in to {ctx.product_name:<16}|                 |
|                    | Email [....................] |                 |
|                    | Password [................] |                 |
|                    | [ ] Remember me              |                 |
|                    | [ Sign in: primary ]       |                 |
|                    | Forgot password?             |                 |
|                    +---------------------------+                 |
+------------------------------------------------------------------+
```

## Mobile

```
[{ctx.product_name}]
Sign in
Email [...............]
Password [...........]
[ Sign in full width ]
```

{_regions_table([
    ("Brand strip", "Product name", "Compact header", "Top bar"),
    ("Auth card", "Centered ~400px", "Full width inset", "Card / Panel"),
    ("Form", "Email + password + CTA", "Same fields stacked", "InputText + Button"),
])}
"""


def wireframe_dashboard(ctx: PageContext) -> str:
    title = _slug_title(ctx.feature)
    persona = ctx.primary_persona or "team lead"
    return f"""# Wireframe: {title} ({ctx.product_name})

Fidelity: wireframe (layout only). Colors from `.heyeddi/design.md`.
Route: `{ctx.route}` · Purpose: {ctx.purpose}

**Layout note:** This page is **not** a generic KPI stat grid unless product.md says so.
Derive columns and rows from `{ctx.purpose}`.

## Desktop (ASCII)

```
+--sidebar--+-- main --------------------------------------------+
| {ctx.product_name:<10}| Topbar [ search........ ] [+ Invite] [avatar]|
| Nav        | {title}: {ctx.success_feeling or 'status at a glance'} |
| - Dash *   | +--------------------------------------------------+ |
| - Settings | | Team roster (DataTable: NOT default stat cards) | |
|            | | Name      | Role    | Status   | Last active    | |
|            | | Alex      | Lead    | Active   | Today          | |
|            | | Jordan    | IC      | Away     | Yesterday      | |
|            | +--------------------------------------------------+ |
| [user]     | [ Refresh ]  [ Filter ▾ ]                            |
+------------+------------------------------------------------------+
```

## Mobile

```
[≡] {ctx.product_name}  [A]
{title}
[ search................ ]
+----------------------------+
| Name | Status | Role      |
| Alex | Active | Lead      |
| Jordan | Away | IC        |
+----------------------------+
[ Refresh ]
```

{_regions_table([
    ("Sidebar", "Nav + active route", "Drawer / hidden", "AppSidebar"),
    ("Toolbar", "Search + actions", "Stacked", "Toolbar row"),
    ("Data surface", "Table from API purpose", "Scrollable table", "DataTable"),
    ("Empty state", "Copy for {persona}", "Same", "EmptyState panel"),
])}
"""


def wireframe_settings(ctx: PageContext) -> str:
    title = _slug_title(ctx.feature)
    return f"""# Wireframe: {title} ({ctx.product_name})

Fidelity: wireframe (layout only). Colors from `.heyeddi/design.md`.
Route: `{ctx.route}` · Purpose: {ctx.purpose}

## Desktop (ASCII)

```
+--sidebar--+-- main ----------------------------------+
| {ctx.product_name:<10}| {title}                          |
| Nav        | Subtitle: {ctx.success_feeling or 'profile & prefs'} |
| - Dash     | +---------------- Profile --------------+ |
| - Sett *   | | Display name [................]      | |
|            | | Email        [................]      | |
|            | +--------------------------------------+ |
|            | +------------- Notifications --------+ |
|            | | Email alerts          [toggle on]  | |
|            | +--------------------------------------+ |
| [user]     |              [ Save changes ]         |
+------------+----------------------------------------+
```

## Mobile

```
[≡] {ctx.product_name}
{title}
+-- Profile card ----------+
| Display name [.........] |
| Email [................] |
+--------------------------+
+-- Notifications --------+
| Email alerts    [toggle]|
+--------------------------+
[ Save changes: full width ]
```

{_regions_table([
    ("Sidebar", "Nav + user chip", "Top bar + menu", "AppSidebar"),
    ("Profile card", "Fields from purpose", "Stacked inputs", "Card #content"),
    ("Notifications", "Toggle rows", "Same", "Card + ToggleSwitch"),
    ("Save CTA", "Outside cards, right", "Full width bottom", "Button"),
])}
"""


def wireframe_generic(ctx: PageContext) -> str:
    title = _slug_title(ctx.feature)
    safe_purpose = re.sub(r"\s+", " ", ctx.purpose.strip()) or "Page content from product.md"
    return f"""# Wireframe: {title} ({ctx.product_name})

Fidelity: wireframe (layout only). Colors from `.heyeddi/design.md`.
Route: `{ctx.route}` · Purpose: {ctx.purpose}

**Agent:** Replace the placeholder regions below with layout that matches this route's purpose.
Do not reuse the settings-page template unless this route is actually settings.

## Desktop (ASCII)

```
+--sidebar--+-- main ----------------------------------+
| {ctx.product_name:<10}| {title}                          |
| Nav        | {safe_purpose[:48]}...                    |
|            | +--------------------------------------+ |
|            | | Primary content region               | |
|            | | (derive from product.md pages)       | |
|            | +--------------------------------------+ |
|            | [ Primary action ]  [ Secondary ]       |
+------------+----------------------------------------+
```

## Mobile

```
[≡] {ctx.product_name}
{title}
+-- main content ----------+
| (stack blocks per purpose)|
+--------------------------+
[ Primary action ]
```

{_regions_table([
    ("Chrome", "App shell", "Top bar", "Layout from scaffold"),
    ("Main", "Purpose-driven blocks", "Stacked", "Cards / table / form"),
    ("Actions", "CTA from route intent", "Full width", "Button"),
])}
"""


def build_wireframe(ctx: PageContext) -> str:
    kind = _classify(ctx.purpose, ctx.route)
    builders = {
        "marketing": wireframe_marketing,
        "login": wireframe_login,
        "dashboard": wireframe_dashboard,
        "settings": wireframe_settings,
        "generic": wireframe_generic,
    }
    return builders[kind](ctx)


def page_context_from_product(
    data: dict,
    *,
    feature: str,
    route: str | None,
) -> PageContext:
    product_name = data.get("product_name") or "Product"
    pages = [p for p in (data.get("pages") or []) if isinstance(p, dict)]
    route_intent = {r["route"]: r for r in (data.get("route_intent") or []) if isinstance(r, dict) and r.get("route")}

    page = None
    if route:
        page = next((p for p in pages if p.get("route") == route), None)
    if page is None:
        page = next((p for p in pages if feature_slug_from_route(p.get("route", "")) == feature), None)
    if page is None and pages:
        page = pages[0]

    resolved_route = route or (page.get("route") if page else f"/{feature}")
    purpose = (page.get("purpose") if page else "") or f"Layout for {feature}"
    view = (page.get("view") if page else "") or "View"
    intent = route_intent.get(resolved_route, {})
    return PageContext(
        product_name=product_name,
        route=resolved_route,
        feature=feature,
        purpose=purpose,
        view=view,
        primary_persona=intent.get("primary_persona", ""),
        success_feeling=intent.get("success_feeling", ""),
    )


def feature_slug_from_route(route: str) -> str:
    return route.strip("/").replace("/", "-") or "home"
