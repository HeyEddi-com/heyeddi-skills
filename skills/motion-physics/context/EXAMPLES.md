# Examples

```vue
<script setup>
import { MotionPresets } from '@/design/motion-presets';
</script>

<template>
  <button v-motion="MotionPresets.microFeedback" type="button">
    Save invoice
  </button>
</template>
```

A list uses `:initial` and `:enter` from `MotionPresets.staggerItem(index)`.
