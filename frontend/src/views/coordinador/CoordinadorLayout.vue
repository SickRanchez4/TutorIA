<template>
  <RoleLayout role="Coordinador" :items="NAV_ITEMS" :toast="coordinadorToast">
    <router-view v-slot="{ Component }">
      <transition name="coord-page" mode="out-in" appear>
        <component :is="Component" />
      </transition>
    </router-view>
  </RoleLayout>
</template>

<script setup>
import RoleLayout from '../../components/RoleLayout.vue'
import { coordinadorToast } from '../../composables/useToast'

const NAV_ITEMS = [
  { to: '/coordinador/cursos', label: 'Cursos', icon: 'mdi-book-open-variant-outline' },
  { to: '/coordinador/cuentas', label: 'Cuentas', icon: 'mdi-account-group-outline' },
  { to: '/coordinador/institucion', label: 'Institución', icon: 'mdi-domain' },
  { to: '/coordinador/analytics', label: 'Analíticas', icon: 'mdi-chart-line' },
  { to: '/coordinador/perfil', label: 'Perfil', icon: 'mdi-account-circle' },
]
</script>

<style scoped>
.coord-page-enter-active,
.coord-page-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.coord-page-enter-from,
.coord-page-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
