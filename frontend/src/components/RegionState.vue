<template>
  <div class="empty-state" :role="error ? 'alert' : 'status'" :aria-busy="loading">
    <v-progress-circular v-if="loading" indeterminate size="24" color="primary" />
    <p>{{ loading ? 'Cargando...' : error || message }}</p>
    <v-btn v-if="error" color="primary" @click="emit('retry')">Reintentar</v-btn>
  </div>
</template>

<script setup>
defineProps({ loading: Boolean, error: { type: String, default: '' }, message: { type: String, default: 'No hay registros.' } })
const emit = defineEmits(['retry'])
</script>
