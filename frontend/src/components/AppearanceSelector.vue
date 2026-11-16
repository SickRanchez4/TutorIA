<template>
  <v-menu v-if="compact" :close-on-content-click="true">
    <template #activator="{ props }">
      <v-btn v-bind="props" icon="mdi-theme-light-dark" aria-label="Cambiar apariencia" variant="text" />
    </template>
    <v-list role="listbox" aria-label="Apariencia">
      <v-list-item
        v-for="option in options"
        :key="option.value"
        :title="option.title"
        role="option"
        :aria-selected="modelValue === option.value"
        :active="modelValue === option.value"
        @click="emit('update:modelValue', option.value)"
      />
    </v-list>
  </v-menu>
  <v-select
    v-else
    :model-value="modelValue"
    :items="options"
    label="Apariencia"
    density="compact"
    hide-details
    prepend-inner-icon="mdi-theme-light-dark"
    class="appearance-selector"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>

<script setup>
defineProps({
  modelValue: { type: String, required: true },
  compact: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
const options = [
  { title: 'Claro', value: 'light' },
  { title: 'Oscuro', value: 'dark' },
  { title: 'Sistema', value: 'system' },
]
</script>

<style scoped>
.appearance-selector { width: 100%; min-width: 0; }
</style>
