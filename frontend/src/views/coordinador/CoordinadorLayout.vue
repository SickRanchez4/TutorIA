<template>
  <v-app class="coord-shell">
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      color="surface"
      class="border-e coord-drawer"
      width="260"
      rail-width="76"
    >
      <div class="d-flex align-center pa-4 coord-drawer-head" :class="rail ? 'justify-center' : 'justify-space-between'">
        <div class="d-flex align-center ga-2" style="min-width: 0">
          <div class="brand-mark">
            <v-icon icon="mdi-brain" color="primary" size="20"></v-icon>
          </div>
          <div v-if="!rail" class="text-truncate">
            <p class="text-caption text-medium-emphasis mb-0 text-truncate d-flex align-center ga-2">
              <span class="status-dot"></span>
              {{ authStore.user?.institucion?.nombre || 'Institución' }}
            </p>
          </div>
        </div>
        <v-btn v-if="!rail" icon="mdi-chevron-left" variant="text" size="small" density="comfortable" class="coord-icon-btn" @click="rail = true"></v-btn>
      </div>

      <v-divider class="border-opacity-50"></v-divider>

      <v-list nav class="pa-2" density="comfortable">
        <v-list-item
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          rounded="lg"
          class="mb-1 nav-item"
          :prepend-icon="item.icon"
          :title="rail ? undefined : item.label"
        >
          <v-tooltip v-if="rail" activator="parent" location="end">{{ item.label }}</v-tooltip>
        </v-list-item>
      </v-list>

      <template #append>
        <div v-if="rail" class="d-flex justify-center pa-2">
          <v-btn icon="mdi-chevron-right" variant="text" size="small" class="coord-icon-btn" @click="rail = false"></v-btn>
        </div>
        <v-divider class="border-opacity-50"></v-divider>
        <div class="pa-3">
          <div class="d-flex align-center ga-2 coord-user-block" :class="rail ? 'justify-center' : ''">
            <v-avatar color="primary" variant="tonal" size="36">
              <span class="text-caption font-weight-bold">{{ initials }}</span>
            </v-avatar>
            <div v-if="!rail" class="flex-grow-1 text-truncate">
              <p class="text-body-2 font-weight-medium mb-0 text-truncate">{{ userName }}</p>
              <p class="text-caption coord-head-sub mb-0">Coordinador</p>
            </div>
            <v-btn v-if="!rail" icon="mdi-logout" variant="text" size="small" color="error" class="coord-icon-btn" @click="logout"></v-btn>
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar color="surface" elevation="0" class="border-b coord-topbar" height="68">
      <v-app-bar-title class="text-body-1 font-weight-bold">
        {{ currentLabel }}
      </v-app-bar-title>
      <v-spacer></v-spacer>
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
      <v-container fluid class="py-6 px-6" style="max-width: 1400px;">
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
import { useAuthStore } from '../../stores/auth'
import { useCoordinadorToast } from './useCoordinadorToast'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { toast, toastError } = useCoordinadorToast()

const drawer = ref(true)
const rail = ref(false)

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
const initials = computed(() => (userName.value || '?').trim().slice(0, 2).toUpperCase())
</script>

<style scoped>
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 197, 118, 0.14);
  border: 1px solid rgba(124, 197, 118, 0.28);
  box-shadow: 0 0 20px rgba(124, 197, 118, 0.22);
  flex-shrink: 0;
}

.coord-shell {
  background:
    radial-gradient(circle at 8% 6%, rgba(124, 197, 118, 0.16), rgba(124, 197, 118, 0) 32%),
    radial-gradient(circle at 90% 10%, rgba(124, 197, 118, 0.08), rgba(124, 197, 118, 0) 28%),
    linear-gradient(140deg, #1c1d22 0%, #22242a 55%, #2b2d34 100%);
}

.coord-drawer {
  border-right: 1px solid rgba(124, 197, 118, 0.2);
  backdrop-filter: blur(12px);
  background: linear-gradient(180deg, rgba(36, 37, 43, 0.96), rgba(45, 47, 55, 0.96));
}

.coord-drawer-head {
  border-bottom: 1px solid rgba(124, 197, 118, 0.12);
}

.coord-head-sub {
  opacity: 0.72;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7cc576;
  box-shadow: 0 0 0 rgba(124, 197, 118, 0.6);
  animation: status-pulse 1.8s ease-out infinite;
}

.coord-user-block {
  border: 1px solid rgba(124, 197, 118, 0.16);
  border-radius: 14px;
  padding: 8px;
  background: rgba(124, 197, 118, 0.06);
}

.coord-icon-btn {
  border-radius: 10px;
}

.coord-topbar {
  border-bottom: 1px solid rgba(124, 197, 118, 0.16);
  backdrop-filter: blur(10px);
  background: rgba(40, 42, 49, 0.86);
}

.coord-main {
  position: relative;
}

.coord-user-chip {
  color: #0f0f11;
  font-weight: 700;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.28);
}

.nav-item :deep(.v-list-item-title) {
  font-size: 0.875rem;
  font-weight: 600;
}

.nav-item {
  border: 1px solid transparent;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.nav-item:hover {
  transform: translateY(-2px);
  border-color: rgba(124, 197, 118, 0.2);
  box-shadow: 0 0 14px rgba(124, 197, 118, 0.15);
}

.nav-item.v-list-item--active {
  background: rgba(124, 197, 118, 0.12);
  border-color: rgba(124, 197, 118, 0.34);
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.2);
  color: rgb(var(--v-theme-primary));
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

@keyframes status-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(124, 197, 118, 0.55);
  }
  70% {
    box-shadow: 0 0 0 9px rgba(124, 197, 118, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(124, 197, 118, 0);
  }
}
</style>

