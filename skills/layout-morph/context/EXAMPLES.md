# Examples: Layout morph

A metrics card and its detail panel are both in `MetricsCard.vue`. Use one `v-morph` group. Do not navigate to a new route for that open.

A list lives on `/reports` and the detail is `/reports/:id`. Do not force `v-morph` across those routes. Use the route transition, or GSAP Flip only if the user asked for a shared element across the navigation.
