<template>
  <div class="panel-title">
    <p class="panel-title__heading mb-0">Panel <span>{{ role }}</span></p>
    <p v-if="subtitle" class="panel-title__subtitle text-caption text-medium-emphasis mb-0">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  role: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<style scoped>
.panel-title { min-width: 0; }
.panel-title__heading {
  color: #f4f8f4;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.3;
  white-space: normal;
}
.panel-title__heading span { color: #9be692; }
.panel-title__subtitle { white-space: normal; overflow-wrap: anywhere; line-height: 1.3; }
@media (max-width: 599px) {
  .panel-title__heading { font-size: 0.88rem; }
  .panel-title__subtitle { font-size: 0.65rem !important; }
}
</style>