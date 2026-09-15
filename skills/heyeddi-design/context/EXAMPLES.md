
# Examples: HeyEddi design

## Vague brief (no sub-command)

```
I want an enterprise view for our admin app
```

Agent runs **discover** → asks about users, density, nav, data → **shape** pipeline.

## Full shape flow

```
@heyeddi-design shape
Feature: enterprise-settings
Brief: B2B admin settings: org profile, members, billing, danger zone
```

Produces `designs/enterprise-settings/research.md`, wireframes, `brief.md`: waits for confirmation.

## Build after confirmation

```
@heyeddi-design craft enterprise-settings
Route: /settings
```

## Greenfield project

```
@heyeddi-design init
```

Then `document` → `shape` → `craft`.

## Critique (auto next step)

```
@heyeddi-design critique the login page
```

Or plain language: *"this login screen looks terrible: what's wrong?"*

Writes `.heyeddi/docs/login-critique.md` with ambition gate, then **Stay → implement** or **Escalate → shape** (unless user said report-only).

## Better design (usually redesign)

```
@heyeddi-design
Make the dashboard a better design — not just polish
```

Or: *"redesign the settings page"* / *"make it better"*

Runs critique ambition gate → typically **shape** (new Design signature) → craft → implement. Not spacing-only.

## Critique then polish (local)

```
@heyeddi-design polish /login
```

Runs **critique** first if needed; polish-path only if gate says Stay.

## Polish only (local)

```
@heyeddi-design polish
Route: /settings: tighten mobile spacing
```

## Wrong skill (has mockups)

```
@heyeddi-handoff
Route: /settings
Attachments: desktop.png, mobile.png
```
