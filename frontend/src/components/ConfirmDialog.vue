<template>
  <v-dialog :model-value="confirmation.open" max-width="520" aria-labelledby="confirmation-title" @update:model-value="open => open || resolveConfirmation(false)">
    <v-card class="surface-card" rounded="xl">
      <v-card-title id="confirmation-title" class="text-wrap">{{ confirmation.title }}</v-card-title>
      <v-card-text>{{ confirmation.message }}</v-card-text>
      <v-card-actions class="flex-wrap">
        <v-btn autofocus variant="text" @click="resolveConfirmation(false)">Permanecer / Cancelar</v-btn>
        <v-spacer />
        <v-btn :color="confirmation.destructive ? 'error' : 'primary'" variant="flat" @click="resolveConfirmation(true)">{{ confirmation.confirmText }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { confirmation, resolveConfirmation } from '../composables/useConfirm'
</script>
