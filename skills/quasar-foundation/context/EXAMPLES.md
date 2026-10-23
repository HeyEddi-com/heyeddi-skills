# Examples

Settings shell:

```vue
<q-layout view="lHh Lpr lFf">
  <q-header elevated>
    <q-toolbar>
      <q-toolbar-title>Settings</q-toolbar-title>
    </q-toolbar>
  </q-header>
  <q-drawer v-model="left" show-if-above bordered>
    <!-- route links -->
  </q-drawer>
  <q-page-container>
    <q-page padding>
      <!-- PrimeVue data goes here, not Quasar form kits -->
    </q-page>
  </q-page-container>
</q-layout>
```
