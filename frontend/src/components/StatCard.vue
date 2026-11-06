<template>
  <v-card class="stat-card surface-card h-100" rounded="xl">
    <v-card-text class="d-flex align-start justify-space-between ga-3 pa-5">
      <div class="min-w-0">
        <p class="stat-card__label mb-1">{{ label }}</p>
        <p class="text-headline-small font-weight-black mb-1">{{ value }}</p>
        <slot name="caption">
          <p v-if="caption" class="stat-card__caption mb-0">{{ caption }}</p>
        </slot>
      </div>
      <div class="icon-tile" aria-hidden="true">
        <v-icon :icon="icon" size="21"></v-icon>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: String, required: true },
  caption: { type: String, default: '' },
})
</script>

<style scoped>
.stat-card {
  min-height: 120px;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
}

.stat-card:hover {
  border-color: var(--tutoria-border-strong) !important;
  transform: translateY(-2px);
}

.stat-card__label {
  color: var(--tutoria-text-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

.stat-card__caption {
  color: var(--tutoria-text-muted);
  font-size: 0.72rem;
}
</style>
