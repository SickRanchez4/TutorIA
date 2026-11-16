<template>
  <v-app class="role-layout">
    <a class="skip-link" href="#main-content">Saltar al contenido principal</a>
    <AppBackdrop />

    <RoleSidebar
      v-model="drawer"
      :role="role"
      :icon="icon"
      :user-name="authStore.displayName"
      :items="items"
      :active="active"
      permanent-on-desktop
      @select="selectSection"
      @logout="logout"
    />

    <v-snackbar
      :model-value="!!toast.state.message && (mdAndUp || !drawer)"
      :color="toast.state.isError ? 'error' : 'success'"
      location="top right"
      :timeout="-1"
      @update:model-value="(open) => open || toast.clear()"
    >
      {{ toast.state.message }}
      <template #actions>
        <v-btn variant="text" aria-label="Descartar aviso" @click="toast.clear()">Cerrar</v-btn>
      </template>
    </v-snackbar>

    <v-main id="main-content" tabindex="-1" :inert="drawer && !mdAndUp" :class="['role-layout__main', { 'role-layout__main--fill': fill }]">
      <v-btn
        v-if="!mdAndUp"
        icon="mdi-menu"
        size="small"
        color="primary"
        class="role-layout__menu"
        aria-label="Abrir navegación"
        @click="drawer = true"
      />
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
import { nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '../stores/auth'
import AppBackdrop from './AppBackdrop.vue'
import RoleSidebar from './RoleSidebar.vue'
import { confirmNavigation } from '../composables/useUnsavedChanges'

/**
 * Dashboard chrome shared by every role: backdrop, navigation,
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

async function selectSection(value) {
  if (value !== props.active && await confirmNavigation()) emit('select', value)
}

watch([() => route.path, () => props.active], async () => {
  const current = props.items.find(item => item.to ? route.path.startsWith(item.to) : item.value === props.active)
  document.title = `${current?.label || props.role} · TutorIA`
  await nextTick()
  document.getElementById('main-content')?.focus({ preventScroll: true })
}, { immediate: true, flush: 'post' })

async function logout() {
  if (!await confirmNavigation()) return
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.role-layout {
  background: transparent !important;
}

.role-layout__menu {
  margin: 12px 16px 0;
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

  .role-layout__menu {
    margin-inline: 12px;
  }
}
</style>
