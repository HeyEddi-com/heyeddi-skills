# Examples

Invoice table inside a Quasar page:

```vue
<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
</script>

<template>
  <DataTable :value="invoices" dataKey="id" paginator :rows="20">
    <Column field="number" header="Invoice" sortable />
    <Column field="status" header="Status">
      <template #body="{ data }">
        <Tag :value="data.status" />
      </template>
    </Column>
  </DataTable>
</template>
```
