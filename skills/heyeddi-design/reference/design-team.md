# Design team

`@taste-penpot` is the general design skill. It chooses the look in one pass and writes tokens. Penpot is an optional designer visual (API MCP), not a second design skill.

`@heyeddi-design` records personas, the route job, and those tokens in `.heyeddi/design.md`, then hands implementation to `@heyeddi-handoff` or `@design-handoff-flutter`.

`@heyeddi` calls them in that order.

This skill does not run a second aesthetic search. If taste tokens are missing, load `@taste-penpot` and use its result. `@vue-design-system` maps those tokens onto Vue 3: Quasar shells, PrimeVue Aura data, spring motion, and the Aura token bridge. They do not replace the look.

Penpot is the designer visual and demo surface. `.heyeddi/stack.json` `design.penpot`: `auto` (default), `on`, or `off`. `design.taste` stays `on`. Connection is the Penpot API MCP (`penpot-api`), not the plugin MCP.
