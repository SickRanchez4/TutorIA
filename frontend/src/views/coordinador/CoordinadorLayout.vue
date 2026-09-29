<template>
  <v-app class="coord-shell">
    <RoleSidebar
      v-model="drawer"
      role="Coordinador"
      :user-name="userName"
      :items="navItems"
      permanent-on-desktop
      @logout="logout"
    />

    <v-app-bar color="surface" elevation="0" class="border-b coord-topbar" height="68">
      <v-app-bar-nav-icon v-if="!mdAndUp" aria-label="Abrir navegación" @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title class="coord-toolbar-title">
        <PanelTitle role="Coordinador" />
      </v-app-bar-title>
      <v-chip variant="flat" color="primary" size="small" class="mr-2 coord-user-chip" prepend-icon="mdi-account-circle-outline">
        {{ userName }}
      </v-chip>
    </v-app-bar>

    <v-snackbar
      :model-value="!!toast"
      :color="toastError ? 'error' : 'success'"
      location="top right"
      timeout="3500"
    >
      {{ toast }}
    </v-snackbar>

    <v-main class="coord-main">
      <v-container fluid class="coord-container py-4 py-md-6 px-3 px-sm-4 px-md-6" style="max-width: 1400px;">
        <router-view v-slot="{ Component }">
          <transition name="coord-page" mode="out-in" appear>
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '../../stores/auth'
import { coordinadorToast } from '../../composables/useToast'
import RoleSidebar from '../../components/RoleSidebar.vue'
import PanelTitle from '../../components/PanelTitle.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { mdAndUp } = useDisplay()
const { message: toast, isError: toastError } = coordinadorToast

const drawer = ref(mdAndUp.value)

const navItems = [
  { to: '/coordinador/cursos', label: 'Cursos', icon: 'mdi-book-open-variant-outline' },
  { to: '/coordinador/cuentas', label: 'Cuentas', icon: 'mdi-account-group-outline' },
  { to: '/coordinador/institucion', label: 'Institucion', icon: 'mdi-domain' },
  { to: '/coordinador/analytics', label: 'Analytics', icon: 'mdi-chart-line' },
  { to: '/coordinador/perfil', label: 'Perfil', icon: 'mdi-account-circle' },
]

const currentLabel = computed(() => navItems.find((i) => route.path.startsWith(i.to))?.label || 'Panel Coordinador')

function logout() {
  authStore.logout()
  router.push('/login')
}
const userName = computed(() => authStore.user?.full_name || authStore.user?.name || authStore.user?.email)
</script>

<style scoped>
.coord-shell {
  background:
    radial-gradient(circle at 8% 6%, rgba(124, 197, 118, 0.16), rgba(124, 197, 118, 0) 32%),
    radial-gradient(circle at 90% 10%, rgba(124, 197, 118, 0.08), rgba(124, 197, 118, 0) 28%),
    linear-gradient(140deg, #1c1d22 0%, #22242a 55%, #2b2d34 100%);
}

.coord-topbar {
  border-bottom: 1px solid rgba(124, 197, 118, 0.16);
  backdrop-filter: blur(10px);
  background: rgba(40, 42, 49, 0.86);
}

.coord-toolbar-title { flex: 1 1 0; min-width: 0; }

.coord-main {
  position: relative;
}

.coord-user-chip {
  color: #0f0f11;
  font-weight: 700;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.28);
}

.coord-page-enter-active,
.coord-page-leave-active {
  transition: opacity 0.26s ease, transform 0.26s ease;
}

.coord-page-enter-from,
.coord-page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 959px) {
  .coord-topbar {
    padding-inline: 4px;
  }

  .coord-user-chip {
    max-width: min(220px, 42vw);
  }

  .coord-user-chip :deep(.v-chip__content) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

@media (max-width: 599px) {
  .coord-container {
    padding-inline: 12px !important;
  }

  .coord-user-chip {
    width: 34px;
    min-width: 34px;
    max-width: 34px;
    padding-inline: 0 !important;
  }

  .coord-user-chip :deep(.v-chip__content) { display: none; }
  .coord-user-chip :deep(.v-chip__prepend) { margin-inline: auto; }
}

@media (prefers-reduced-motion: reduce) {
  .coord-page-enter-active,
  .coord-page-leave-active {
    animation: none !important;
    transition: none !important;
  }
}
</style>

