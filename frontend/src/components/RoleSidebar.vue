<template>
  <div
    v-if="temporary && open"
    class="role-sidebar-backdrop"
    aria-hidden="true"
    @click="open = false"
  ></div>
  <v-navigation-drawer
    v-model="open"
    :permanent="!temporary"
    :temporary="temporary"
    :rail="compact"
    :scrim="false"
    color="surface"
    width="280"
    rail-width="76"
    class="role-sidebar"
    :class="{ 'role-sidebar--mobile': temporary }"
    @keydown.esc="closeSidebar"
  >
    <div class="role-sidebar__header pa-4">
      <div v-if="!compact" class="role-sidebar__brand">
        <div class="role-sidebar__symbol" aria-hidden="true">
          <v-icon :icon="icon" size="21"></v-icon>
        </div>
        <div class="role-sidebar__heading">
          <PanelTitle :role="role" />
        </div>
      </div>
      <v-btn
        icon
        variant="text"
        size="small"
        class="role-sidebar__close"
        :aria-label="temporary ? 'Cerrar navegación' : compact ? 'Expandir navegación' : 'Contraer navegación'"
        @click="closeSidebar"
      >
        <v-icon :icon="temporary ? 'mdi-close' : compact ? 'mdi-chevron-right' : 'mdi-chevron-left'" size="20"></v-icon>
      </v-btn>
    </div>
    <v-divider></v-divider>
    <v-list nav class="pa-2" density="comfortable">
      <v-list-item
        v-for="item in items"
        :key="item.value || item.to"
        :to="item.to"
        :active="item.to ? undefined : active === item.value"
        :prepend-icon="item.icon"
        :title="compact ? undefined : item.label"
        rounded="lg"
        class="role-sidebar__item mb-1"
        @click="selectItem(item)"
      >
        <v-tooltip v-if="compact" activator="parent" location="end">{{ item.label }}</v-tooltip>
      </v-list-item>
    </v-list>
    <template #append>
      <v-divider></v-divider>
      <div class="pa-3">
        <p v-if="!compact && userName" class="role-sidebar__user text-caption text-medium-emphasis mb-3">{{ userName }}</p>
        <v-btn
          :block="!compact"
          :icon="compact"
          variant="tonal"
          color="error"
          rounded="lg"
          aria-label="Cerrar sesión"
          @click="emit('logout')"
        >
          <v-icon icon="mdi-logout" :class="{ 'mr-2': !compact }"></v-icon>
          <span v-if="!compact">Cerrar sesión</span>
          <v-tooltip v-if="compact" activator="parent" location="end">Cerrar sesión</v-tooltip>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import PanelTitle from './PanelTitle.vue'

const props = defineProps({
  role: { type: String, required: true },
  icon: { type: String, default: 'mdi-brain' },
  userName: { type: String, default: '' },
  items: { type: Array, required: true },
  active: { type: String, default: '' },
  permanentOnDesktop: { type: Boolean, default: false },
})
const open = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['select', 'logout'])
const { mdAndUp } = useDisplay()
const rail = ref(false)
const temporary = computed(() => !props.permanentOnDesktop || !mdAndUp.value)
const compact = computed(() => !temporary.value && rail.value)

watch(mdAndUp, (isDesktop) => {
  open.value = isDesktop && props.permanentOnDesktop
  rail.value = false
})

function closeSidebar() {
  if (temporary.value) open.value = false
  else rail.value = !rail.value
}

function selectItem(item) {
  if (item.value) emit('select', item.value)
  if (temporary.value) open.value = false
}
</script>

<style scoped>
.role-sidebar {
  border-right: 1px solid rgba(124, 197, 118, 0.2) !important;
  background: linear-gradient(180deg, rgba(36, 37, 43, 0.98), rgba(45, 47, 55, 0.98)) !important;
}
.role-sidebar--mobile { z-index: 1100 !important; }
.role-sidebar-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1090;
  background: rgba(7, 10, 12, 0.3);
  backdrop-filter: blur(7px);
  -webkit-backdrop-filter: blur(7px);
}
.role-sidebar__header,
.role-sidebar__brand { display: flex; align-items: center; gap: 12px; }
.role-sidebar__brand { flex: 1; min-width: 0; }
.role-sidebar__heading { min-width: 0; overflow-wrap: anywhere; }
.role-sidebar__heading p { white-space: normal; }
.role-sidebar__symbol {
  display: grid;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  place-items: center;
  border: 1px solid rgba(124, 197, 118, 0.28);
  border-radius: 12px;
  color: #abeca3;
  background: rgba(124, 197, 118, 0.14);
}
.role-sidebar__close { flex-shrink: 0; color: rgba(235, 243, 235, 0.65); }
.role-sidebar__close:hover { color: #abeca3; }
.role-sidebar__user { overflow-wrap: anywhere; }
.role-sidebar__item { border: 1px solid transparent; }
.role-sidebar__item.v-list-item--active {
  background: rgba(124, 197, 118, 0.12);
  border-color: rgba(124, 197, 118, 0.34);
  color: rgb(var(--v-theme-primary));
}
</style>