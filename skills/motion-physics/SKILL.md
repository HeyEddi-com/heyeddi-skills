---
name: motion-physics
description: "Spring micro-interactions for Vue 3 using @vueuse/motion. Use when introducing cards, dialogs, lists, hover, or press feedback. Forbids linear spatial easing, long staggers, and looping motion unless a loading state was requested."
version: 1.0.0
product-version: 3.6.0
author: HeyEddi-com
---

# Spring Motion

Replaces generic fade and slide effects with spring physics from `@vueuse/motion`.

Do not invent transition coordinates. Use the three presets below. Shell and data components stay in `@quasar-foundation` and `@primevue-aura`.

## When the agent activates this skill

- Introducing cards, modals, or list items to the DOM.
- Card hover states, focus depth, and button tap compressions.
- Staggering sequential data lists or dashboard panels.

## Installation

```bash
npm install @vueuse/motion
```

Register `MotionPlugin` after PrimeVue in `src/main.js`. The bootstrap block is in `@primevue-aura`.

## Physics profiles

```js
// src/design/motion-presets.js
export const MotionPresets = {
  // Snappy feedback for clicks, toggles, and icon buttons
  microFeedback: {
    hovered: { scale: 1.02, transition: { type: 'spring', stiffness: 400, damping: 25 } },
    tapped: { scale: 0.97, transition: { type: 'spring', stiffness: 500, damping: 30 } }
  },

  // Structural panel / dialog entry
  modalEnter: {
    initial: { opacity: 0, scale: 0.95, y: 15 },
    enter: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { type: 'spring', stiffness: 280, damping: 22 }
    }
  },

  // Stagger helper for lists / tables
  staggerItem: (index) => ({
    initial: { opacity: 0, y: 12 },
    enter: {
      opacity: 1,
      y: 0,
      transition: {
        delay: Math.min(index * 35, 200), // Cap max delay to prevent slowness
        type: 'spring',
        stiffness: 320,
        damping: 24
      }
    }
  })
};
```

When a moment matches a preset, use the preset. The directive defaults apply only when none of the three presets fit:

- Interactive elements: `{ type: 'spring', stiffness: 350, damping: 25 }`
- Dialogs and overlays: `{ type: 'spring', stiffness: 280, damping: 22 }` (same as `modalEnter`)

## Anti-AI-slop motion rules

- No linear transitions: never use `ease-in-out` or `linear` timing for spatial movements (`x`, `y`, `scale`). Always use spring damping.
- Cap animation delays: never set list stagger delays greater than 40ms per item or total delay exceeding 200ms. `staggerItem` uses 35ms and caps at 200ms.
- No continuous looping: avoid looping pulses, infinite rotations, or floating animations on UI elements unless explicitly requested for an active loading state.
- Provide a `prefers-reduced-motion` path: skip spatial springs and use an instant opacity change.

## Instructions

1. Import `MotionPresets` from `src/design/motion-presets.js`. Do not copy the numbers into a component as one-off values.
2. Bind `v-motion` to the preset that matches the moment.
3. Do not animate layout properties that PrimeVue or Quasar already own (drawer width, virtual scroller position) unless the user asked for that motion.
4. Loading indicators may loop. Everything else plays once.

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill motion-physics --project-root .
   ```

2. Include the script's **`### Next step`** block in your **final** reply.
