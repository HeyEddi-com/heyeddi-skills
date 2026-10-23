---
name: cli-interface-design
description: "Designs readable interactive CLIs with @clack/prompts, consola, and picocolors. After writing the script, run it and inspect ANSI stdout for alignment. Does not render HTML, Canvas, or a browser screenshot."
version: 1.0.0
product-version: 3.6.0
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
import { intro, outro, text, select, confirm, isCancel, cancel } from '@clack/prompts';
import pc from 'picocolors';

export async function runConfigWizard() {
  intro(pc.bgMagenta(pc.black(' APPLICATION ARCHITECT ')));

  const appName = await text({
    message: 'What is the package name?',
    placeholder: 'core-runtime',
    validate: (value) => (!value ? 'Name cannot be empty' : undefined)
  });
  if (isCancel(appName)) { cancel('Operation aborted.'); process.exit(0); }

  const platform = await select({
    message: 'Target build ecosystem:',
    options: [
      { value: 'desktop', label: 'Tauri Desktop', hint: 'Quasar Frame + PrimeVue Data' },
      { value: 'mobile', label: 'Capacitor Mobile', hint: 'Quasar Layout + Touch Gestures' },
      { value: 'cloud', label: 'Web SPA / PWA', hint: 'Aura Design Preset' }
    ]
  });
  if (isCancel(platform)) { cancel('Operation aborted.'); process.exit(0); }

  outro(pc.green(`Target [${pc.bold(appName)}] configured for [${platform}].`));
}
```

`confirm` is part of the import surface. Use it for destructive confirmations. Always handle `isCancel` before continuing.

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
5. Run the script and read stdout before finishing. A wizard that was never executed is not done.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill cli-interface-design --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
