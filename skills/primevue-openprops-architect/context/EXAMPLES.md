
# Examples: PrimeVue + project tokens

## Good: token-based card

```vue
<template>
  <Card class="settings-card">
    <template #title>Profile</template>
    <template #content>
      <p class="settings-card__hint">Update your display name.</p>
    </template>
  </Card>
</template>

<style scoped>
.settings-card {
  background: var(--app-surface-card);
  padding: 1rem;
}
.settings-card__hint {
  color: var(--app-text-muted);
  font-size: 0.875rem;
}
</style>
```

## Bad: hardcoded styles

```vue
<template>
  <div style="background: #fff; padding: 16px;">
    <Button label="Save" color="blue" />
  </div>
</template>
```
