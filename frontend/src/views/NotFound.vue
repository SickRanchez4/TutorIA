<template>
  <v-app>
    <AppBackdrop />
    <v-main>
      <v-container class="position-relative">
        <v-card class="surface-card pa-6">
          <h1 class="text-headline-small">Página no disponible</h1>
          <p class="my-4">La dirección no existe o ya no está disponible.</p>
          <v-btn color="primary" variant="flat" :to="auth.isAuthenticated ? auth.dashboardRoute : '/login'">Volver a mi inicio</v-btn>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import AppBackdrop from '../components/AppBackdrop.vue'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
document.title = 'Página no disponible · TutorIA'
</script>
