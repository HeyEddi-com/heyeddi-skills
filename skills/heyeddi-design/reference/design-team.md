# Design team

`@taste-penpot` chooses the look in one pass and writes tokens.

`@heyeddi-design` records personas, the route job, and those tokens in `.heyeddi/design.md`, then hands implementation to `@heyeddi-handoff` or `@design-handoff-flutter`.

`@heyeddi` calls them in that order.

This skill does not run a second aesthetic search. If taste tokens are missing, load `@taste-penpot` and use its result. PrimeVue and OpenProps map those tokens onto the stack. They do not replace them.

Penpot is optional. `.heyeddi/stack.json` `design.penpot`: `auto` (default), `on`, or `off`. `design.taste` stays `on`.
