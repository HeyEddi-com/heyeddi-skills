# Examples

```css
.invoice-card {
  background: var(--app-surface-card);
  color: var(--app-text-main);
  border: 1px solid var(--app-border);
}

.invoice-card small {
  color: var(--app-text-muted);
}
```

The page background stays on `body` via `--app-bg`. Do not set it again on `<q-page>` with a hex value.
