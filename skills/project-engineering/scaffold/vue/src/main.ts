import { createApp } from "vue";
// Quasar core CSS loads first, PrimeVue Aura second, motion third.
import { Quasar, Dialog, Notify, BottomSheet, Morph } from "quasar";
import "@quasar/extras/material-icons/material-icons.css";
import "quasar/src/css/index.sass";
import PrimeVue from "primevue/config";
import { definePreset } from "@primeuix/themes";
import Aura from "@primevue/themes/aura";
import "primeicons/primeicons.css";
import { MotionPlugin } from "@vueuse/motion";
import App from "./App.vue";
import router from "./router";
import "./styles/tokens.css";

const HeyEddiAura = definePreset(Aura, {
  semantic: {
    primary: {
      50: "{indigo.50}",
      100: "{indigo.100}",
      200: "{indigo.200}",
      300: "{indigo.300}",
      400: "{indigo.400}",
      500: "{indigo.500}",
      600: "{indigo.600}",
      700: "{indigo.700}",
      800: "{indigo.800}",
      900: "{indigo.900}",
      950: "{indigo.950}",
    },
  },
});

// Dark mode is the .dark-mode class, shared by PrimeVue and tokens.css.
// It follows the system setting until the app adds its own switch.
const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
const applyScheme = () => document.documentElement.classList.toggle("dark-mode", systemDark.matches);
applyScheme();
systemDark.addEventListener("change", applyScheme);

const app = createApp(App);
app.use(Quasar, { plugins: { Dialog, Notify, BottomSheet }, directives: { Morph } });
app.use(PrimeVue, {
  theme: {
    preset: HeyEddiAura,
    options: {
      prefix: "p",
      darkModeSelector: ".dark-mode",
      cssLayer: false,
    },
  },
});
app.use(MotionPlugin);
app.use(router);
app.mount("#app");
