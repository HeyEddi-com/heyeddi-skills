---
name: layout-morph
description: "Shared-element morphs in Vue 3 with Quasar v-morph. Use when a card, row, or chip expands into its detail view in the same screen. GSAP Flip is only the fallback when the two states are not in one view. No React, no Tailwind."
version: 1.0.0
product-version: 3.8.0
author: HeyEddi-com
---

# Layout morph

A small surface grows into its detail without a hard cut. Quasar `v-morph` owns that move. Springs for hover, press, and dialog entry stay in `@motion-physics`.

## When to use

- A card, list row, or chip and its expanded panel are both in the same view.
- The user asked for a shared-element or layout transition.

Do not morph every route change. Do not morph a data table into itself.

## Setup

`Morph` is registered with Quasar in the bootstrap owned by `@primevue-aura`:

```js
import { Quasar, Dialog, Notify, Morph } from 'quasar';

app.use(Quasar, { plugins: { Dialog, Notify, Morph } });
```

No extra package. Quasar already ships `v-morph`.

## Pattern

Both states share one group name. Colors come from `@aura-design-tokens`.

```vue
<script setup>
import { ref } from 'vue';

const morphGroup = ref('card');

function toggleView() {
  morphGroup.value = morphGroup.value === 'card' ? 'expanded' : 'card';
}
</script>

<template>
  <div>
    <div
      v-morph:card:step-group="morphGroup"
      class="compact-card"
      @click="toggleView"
    >
      <div class="card-title">Performance metrics</div>
    </div>

    <div v-morph:expanded:step-group="morphGroup" class="expanded-panel">
      <h3>Performance metrics</h3>
      <button type="button" @click="toggleView">Close</button>
    </div>
  </div>
</template>

<style scoped>
.compact-card,
.expanded-panel {
  background: var(--app-surface-card);
  border: 1px solid var(--app-border);
  color: var(--app-text-main);
}
.compact-card {
  width: 280px;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
}
.expanded-panel {
  width: min(600px, 100%);
  padding: 24px;
  border-radius: 16px;
}
</style>
```

## GSAP Flip

Use `gsap` Flip only when the compact state and the expanded state cannot live in the same component, such as a list on one route and a detail page on another. Install `gsap` only in that case. Prefer a route transition or `@motion-physics` `modalEnter` when a morph would be decorative.

## Reduced motion

When `prefers-reduced-motion: reduce` matches, swap the group without the morph. Show the expanded panel immediately.

## Next

After the morph exists, `@fancy-ui-craft` only if this surface also needs depth. Otherwise `@visual-verification`.
