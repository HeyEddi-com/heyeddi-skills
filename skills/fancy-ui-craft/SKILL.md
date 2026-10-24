---
name: fancy-ui-craft
description: "Depth for a few Vue 3 surfaces: cursor spotlight, frosted glass, one TresJS accent, and a local dotLottie state. Use on a hero, a featured card, or an empty state. Do not apply it to tables, forms, or every card. No React, no Tailwind."
version: 1.0.0
product-version: 3.8.0
author: HeyEddi-com
---

# Fancy UI craft

Depth is for the one surface that should feel considered. Tables, settings forms, and lists stay flat and use PrimeVue Aura plus `@aura-design-tokens`.

## When to use

- A hero, a featured metric, or a single promotional card needs a spotlight or glass.
- An empty, loading, or success state needs a short animation.
- A hero needs one 3D accent.

## Packages

Install only the piece you use.

```bash
npm install @vueuse/core
npm install @tresjs/core three
npm install @lottiefiles/dotlottie-vue
```

## Spotlight

`useMouseInElement` from `@vueuse/core`. The glow color is `var(--app-spotlight)` from `@aura-design-tokens`. Do not put a hex in the component.

```vue
<script setup>
import { ref } from 'vue';
import { useMouseInElement } from '@vueuse/core';

const cardRef = ref(null);
const { elementX, elementY, isOutside } = useMouseInElement(cardRef);
</script>

<template>
  <div
    ref="cardRef"
    class="spotlight-card"
    :style="{
      '--mouse-x': `${elementX}px`,
      '--mouse-y': `${elementY}px`,
      '--spotlight-opacity': isOutside ? '0' : '1'
    }"
  >
    <div class="spotlight-overlay" />
    <div class="card-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.spotlight-card {
  position: relative;
  background: var(--app-surface-card);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  overflow: hidden;
  padding: 24px;
}
.spotlight-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: var(--spotlight-opacity);
  background: radial-gradient(
    600px circle at var(--mouse-x) var(--mouse-y),
    var(--app-spotlight),
    transparent 70%
  );
}
.card-content {
  position: relative;
  z-index: 1;
}
</style>
```

## Glass

Use the glass tokens. One panel per view, not a stack of blurs.

```css
.glass-panel {
  background: var(--app-glass);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--app-glass-border);
  box-shadow: inset 0 1px 0 0 var(--app-glass-rim);
  border-radius: 16px;
}
```

## 3D accent

`@tresjs/core` is one object on a hero or a key metric, at most. Give the canvas a fixed height. Stop the rotation when `prefers-reduced-motion: reduce` matches. Color the material from the primary token, not a new hex.

## Lottie

`@lottiefiles/dotlottie-vue` plays a file that lives in the repo (`src/assets/...lottie`). Use it for success, loading, or empty. Do not point `src` at a third-party host. Do not loop a decorative animation on a page the user sits on. A loading state may loop until the data arrives.

## Next

`@visual-verification` screenshots the page. If the spotlight, glass, or 3D makes text fail contrast or crowds the task, remove the effect.
