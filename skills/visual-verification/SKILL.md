---
name: visual-verification
description: "Visual self-correction for Vue UI through the Playwright MCP. After a layout or dashboard change, screenshot the Vite dev server and fix overlap, wrap, padding, and unstyled type before done. Uses browser_navigate, browser_resize, and browser_take_screenshot. Not Puppeteer. Not a substitute for @visual-auditor's recorded review."
version: 1.0.0
product-version: 3.6.0
author: HeyEddi-com
---

# Visual Verification Loop

`@primevue/mcp` and `@quasar/mcp` understand component code. They do not render pixels. This skill uses the **Playwright MCP** (`@playwright/mcp`) so the agent can see the live Vite page and fix what it sees.

Do not use Puppeteer or `@modelcontextprotocol/server-puppeteer`.

`@visual-auditor` still records the done review (contrast report, widths, fix log). Run this loop first, while the dev server is hot, and correct the code before that review.

## When the agent activates this skill

- After any major UI component, layout change, or dashboard view.
- After `@motion-physics` on a GUI surface.
- When checking a mobile drawer against the desktop layout.
- When contrast, overlap, or an unwanted scrollbar is in question.

Do not use this skill for a CLI. Terminal alignment is `@cli-interface-design` (run the script, read stdout).

## Feedback cycle

```
1. Agent writes Vue code to file
2. Vite dev server (localhost:5173) hot-reloads
3. browser_navigate, then browser_resize, then browser_take_screenshot
4. Agent inspects the rendered image
5. Agent fixes the flaw in code
```

Repeat until the screenshot has no overlap, broken wrap, misaligned padding, or raw unstyled type. Then stop. Do not declare the GUI task complete on an unread screenshot.

## MCP server

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

## Commands

The dev server must already be running at `http://localhost:5173`.

1. Navigate. Hash routes stay on `#/…`. History routes use the path with no hash.

```
browser_navigate
  url: http://localhost:5173/#/dashboard
```

2. Resize, then screenshot. Repeat for both viewports. `browser_take_screenshot` does not take width and height. `browser_resize` does.

| Surface | width | height | filename |
|---------|-------|--------|----------|
| Desktop | 1440 | 900 | `.heyeddi/docs/visual-verification/dashboard-desktop.png` |
| Mobile (iPhone 14) | 390 | 844 | `.heyeddi/docs/visual-verification/dashboard-mobile.png` |

```
browser_resize
  width: 1440
  height: 900

browser_take_screenshot
  filename: .heyeddi/docs/visual-verification/dashboard-desktop.png
  scale: css
  fullPage: true
```

Then the same pair at 390×844 with `dashboard-mobile.png`.

3. Read the saved PNG. Look for overlap, broken flex wrap, padding that does not match the token scale, unstyled fonts, and horizontal scroll that the layout did not intend.

4. Edit the Vue or CSS. Wait for HMR. Screenshot again. One fix round is the default. A second round only if the first screenshot still shows a defect.

`browser_snapshot` is the accessibility tree. Use it to find a control. Use `browser_take_screenshot` when the question is visual.

## Instructions

1. Confirm `http://localhost:5173` responds. If it does not, start the Vite server the project already uses, then navigate.
2. Capture desktop and mobile before calling the screen done.
3. Fix code. Do not answer with a list of flaws and leave them.
4. `@visual-auditor` runs after this loop when the pipeline asks for a recorded review. Do not skip that gate by treating this screenshot as the audit file.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill visual-verification --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
