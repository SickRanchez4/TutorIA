<template>
  <v-card class="page-header surface-card" rounded="xl">
    <v-card-text class="page-header__body">
      <div class="page-header__copy">
        <slot name="before" />
        <p v-if="overline" class="eyebrow mb-1">{{ overline }}</p>
        <slot name="title">
          <h1 class="text-headline-small font-weight-black mb-1">{{ title }}</h1>
        </slot>
        <p v-if="subtitle" class="text-subtle mb-0">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="page-header__actions">
        <slot name="actions" />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  overline: { type: String, default: '' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>

<style scoped>
.page-header {
  overflow: hidden;
}

.page-header::before {
  position: absolute;
  top: 0;
  left: 10%;
  width: 80%;
  height: 1px;
  content: '';
  background: linear-gradient(90deg, transparent, rgba(171, 238, 163, 0.7), transparent);
  pointer-events: none;
}

.page-header__body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px !important;
}

.page-header__copy {
  min-width: 0;
}

.page-header__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

@media (max-width: 599px) {
  .page-header__body {
    align-items: stretch;
    padding: 16px !important;
  }

  .page-header__actions,
  .page-header__actions :deep(.v-btn) {
    width: 100%;
  }
}
</style>
