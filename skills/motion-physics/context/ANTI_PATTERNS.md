# Anti-patterns

- `transition: all 0.3s ease-in-out` on cards, dialogs, or buttons.
- Stagger delays above 40ms per item, or a total delay above 200ms.
- Infinite pulse, float, or spin on decorative elements.
- One-off stiffness numbers copied into a component instead of `MotionPresets`.
- Animating Quasar drawer width or PrimeVue virtual scroller offset.
