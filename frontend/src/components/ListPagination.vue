<template>
  <div class="d-flex align-center justify-space-between flex-wrap ga-3 mt-4" aria-label="Paginación del listado">
    <span class="text-body-small text-subtle" role="status">{{ start }}–{{ Math.min(page * pageSize, total) }} de {{ total }}</span>
    <v-select v-model="pageSize" :items="[10, 25, 50]" label="Por página" density="compact" hide-details class="list-page-size" />
    <v-pagination v-model="page" :length="Math.max(1, Math.ceil(total / pageSize))" :total-visible="3" density="compact" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ total: { type: Number, required: true } })
const page = defineModel('page', { type: Number, required: true })
const pageSize = defineModel('pageSize', { type: Number, required: true })
const start = computed(() => props.total ? (page.value - 1) * pageSize.value + 1 : 0)
</script>

<style scoped>
.list-page-size { flex: 0 0 125px; }
</style>
