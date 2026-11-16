<template>
  <v-alert v-if="result" :type="result.issues.length ? 'warning' : 'success'" variant="tonal" title="Resultado de importación" class="mb-4" role="status">
    <p class="mb-1">{{ result.created }} registros nuevos · {{ result.enrolled }} inscripciones · {{ result.issues.length }} omisiones.</p>
    <details v-if="result.issues.length">
      <summary>Ver motivos de las omisiones</summary>
      <ol><li v-for="(reason, index) in result.issues" :key="index">{{ reason }}</li></ol>
    </details>
  </v-alert>
</template>

<script setup>
defineProps({ result: { type: Object, default: null } })
</script>
