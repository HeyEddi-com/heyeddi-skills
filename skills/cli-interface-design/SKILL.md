---
name: cli-interface-design
description: "Designs readable interactive CLIs with @clack/prompts, consola, and picocolors. After writing the script, run it and inspect ANSI stdout for alignment. Does not render HTML, Canvas, or a browser screenshot."
version: 1.0.1
product-version: 3.10.0
author: HeyEddi-com
---

# CLI Interface Design

Readable, interactive command-line interfaces, project generators, and background monitors. No HTML and no Canvas.

Do not load Quasar, PrimeVue, or `@vueuse/motion` for a terminal task. If the same product also has a GUI, that GUI is a separate `@vue-design-system` route.

## When the agent activates this skill

- Writing CLI setup scripts, provisioning tools, or dev utilities.
- Presenting background task execution, health checks, or deployment logs.
- Generating interactive terminal prompts (selections, confirmations, text inputs).

## How the agent sees a CLI

Do not open a browser and do not call `@visual-verification`. Run the command in the terminal, capture the ANSI and Unicode stdout, and check character-cell alignment in that text: column edges, box borders, and label spacing. Fix the script and run it again before calling the CLI done.

## Installation

```bash
npm install @clack/prompts consola picocolors
```

## Pattern A: interactive configuration flow

```js
// cli/interactive-flow.js
import { intro, outro, text, select, isCancel, cancel } from '@clack/prompts';
import pc from 'picocolors';
import { pathToFileURL } from 'node:url';

const DEFAULTS = { appName: 'core-runtime', platform: 'desktop' };

function ensure(value) {
  if (isCancel(value)) { cancel('Operation aborted.'); process.exit(0); }
  return value;
}

export async function runConfigWizard(argv = process.argv.slice(2)) {
  intro(pc.bgMagenta(pc.black(' APPLICATION ARCHITECT ')));

  // Never wait for keys without a terminal: CI, scripts, and agents take the defaults.
  const interactive = process.stdin.isTTY && !argv.includes('--yes');
  let { appName, platform } = DEFAULTS;

  if (interactive) {
    appName = ensure(await text({
      message: 'What is the package name?',
      placeholder: DEFAULTS.appName,
      validate: (value) => (!value ? 'Name cannot be empty' : undefined)
    }));
    platform = ensure(await select({
      message: 'Target build ecosystem:',
      options: [
        { value: 'desktop', label: 'Tauri Desktop', hint: 'Quasar Frame + PrimeVue Data' },
        { value: 'mobile', label: 'Capacitor Mobile', hint: 'Quasar Layout + Touch Gestures' },
        { value: 'cloud', label: 'Web SPA / PWA', hint: 'Aura Design Preset' }
      ]
    }));
  }

  outro(pc.green(`Target [${pc.bold(appName)}] configured for [${platform}].`));
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  await runConfigWizard();
}
```

Use `confirm` for destructive confirmations. Always handle `isCancel` before continuing. A destructive step never defaults to yes: without a terminal it needs an explicit flag.

## Pattern B: real-time status and hierarchical logs

```js
// cli/status-logger.js
import { consola } from 'consola';
import pc from 'picocolors';

export function logSystemState(metrics) {
  consola.box({
    title: pc.cyan(' ENGINE STATUS '),
    message: `Active Workers: ${pc.green(metrics.workers)}\nMemory Usage:   ${pc.yellow(metrics.memory)}\nProtocol:       ${metrics.protocol}`
  });

  consola.start('Synchronizing state caches across projects...');
  // After task completion:
  consola.success('Distributed caches synchronized successfully.');
}
```

## Instructions

1. Stay inside the 16-color ANSI palette that `picocolors` provides. Do not emit raw hex or 256-color sequences.
2. One question per step. Validate empty required text. Exit 0 on cancel.
3. Status uses `consola.start`, `consola.success`, `consola.error`, and `consola.box`. Do not print unstructured `console.log` banners for the same job.
4. Do not render a fake terminal inside a Vue page unless the user asked for a GUI that displays logs. Log text in a GUI still comes from the product's data components (`@primevue-aura`), not from embedding clack.
5. Every prompt has a flag or a default, so the script also runs without a terminal. Before finishing, run that path under a time limit (`timeout 60 node cli/interactive-flow.js --yes < /dev/null`) and read stdout. A wizard that was never executed is not done.
6. Put logic in plain functions and unit test them first, per `@heyeddi` `reference/testing.md`.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill cli-interface-design --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
