<template>
  <v-app class="role-layout">
    <AppBackdrop />

    <RoleSidebar
      v-model="drawer"
      :role="role"
      :icon="icon"
      :user-name="authStore.displayName"
      :items="items"
      :active="active"
      permanent-on-desktop
      @select="emit('select', $event)"
      @logout="logout"
    />

    <v-app-bar elevation="0" height="64" class="role-layout__bar">
      <v-app-bar-nav-icon v-if="!mdAndUp" aria-label="Abrir navegación" @click="drawer = true"></v-app-bar-nav-icon>
      <div class="role-layout__title">
        <div v-if="!mdAndUp" class="role-layout__mark" aria-hidden="true">
          <v-icon :icon="icon" size="19"></v-icon>
        </div>
        <PanelTitle :role="role" :subtitle="sectionLabel" />
      </div>
      <v-chip variant="tonal" color="primary" class="role-layout__user mr-3" prepend-icon="mdi-account-circle-outline">
        {{ authStore.displayName }}
      </v-chip>
    </v-app-bar>

    <v-snackbar
      :model-value="!!toast.state.message"
      :color="toast.state.isError ? 'error' : 'success'"
      location="top right"
      :timeout="-1"
      @update:model-value="(open) => open || toast.clear()"
    >
      {{ toast.state.message }}
    </v-snackbar>

    <v-main :class="['role-layout__main', { 'role-layout__main--fill': fill }]">
      <div v-if="fill" class="role-layout__fill">
        <slot />
      </div>
      <v-container v-else fluid class="role-layout__container">
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '../stores/auth'
import AppBackdrop from './AppBackdrop.vue'
import RoleSidebar from './RoleSidebar.vue'
import PanelTitle from './PanelTitle.vue'

/**
 * Dashboard chrome shared by every role: backdrop, navigation, top bar,
 * toast and main area. Items use `value` (in-page sections, reported through
 * `select`) or `to` (router links).
 */
const props = defineProps({
  role: { type: String, required: true },
  icon: { type: String, default: 'mdi-brain' },
  items: { type: Array, required: true },
  active: { type: String, default: '' },
  toast: { type: Object, required: true },
  /** Main area takes exactly the viewport height (no page scroll) on large screens. */
  fill: { type: Boolean, default: false },
})
const emit = defineEmits(['select'])

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { mdAndUp } = useDisplay()
const drawer = ref(mdAndUp.value)

const sectionLabel = computed(() => {
  const item = props.items.find((i) => (i.to ? route.path.startsWith(i.to) : i.value === props.active))
  return item?.label || ''
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.role-layout {
  background: transparent !important;
}

.role-layout__bar {
  border-bottom: 1px solid rgba(var(--tutoria-green-rgb), 0.16) !important;
  background: rgba(22, 26, 30, 0.82) !important;
  backdrop-filter: blur(14px) saturate(1.1);
}

.role-layout__title {
  display: flex;
  flex: 1 1 0;
  min-width: 0;
  align-items: center;
  gap: 12px;
  margin-inline: 16px 8px;
}

.role-layout__mark {
  display: grid;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid rgba(155, 226, 153, 0.42);
  border-radius: 11px;
  color: #b6f2aa;
  background: linear-gradient(145deg, rgba(var(--tutoria-green-rgb), 0.22), rgba(var(--tutoria-green-rgb), 0.05));
}

.role-layout__user {
  max-width: min(260px, 32vw);
  font-weight: 700;
}

.role-layout__user :deep(.v-chip__content) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-layout__main {
  position: relative;
  z-index: 1;
}

.role-layout__container {
  max-width: 1400px;
  padding: 24px;
}

.role-layout__main--fill {
  height: 100dvh;
}

.role-layout__fill {
  height: 100%;
  padding: 8px 12px;
}

@media (max-width: 1144px) {
  .role-layout__main--fill {
    height: auto;
  }
}

@media (max-width: 839px) {
  .role-layout__title {
    margin-inline: 4px;
  }

  .role-layout__container {
    padding: 16px;
  }
}

@media (max-width: 599px) {
  .role-layout__container {
    padding: 12px;
  }

  .role-layout__fill {
    padding: 8px;
  }

  .role-layout__user {
    width: 34px;
    min-width: 34px;
    padding-inline: 0 !important;
  }

  .role-layout__user :deep(.v-chip__content) {
    display: none;
  }

  .role-layout__user :deep(.v-chip__prepend) {
    margin-inline: auto;
  }
}
</style>
