<template>
  <RoleLayout
    role="Estudiante"
    :items="NAV_ITEMS"
    :active="tab"
    :toast="toast"
    :fill="tab === 'chat'"
    @select="tab = $event"
  >
    <!-- v-show keeps each section's state (open conversation, month) between tabs. -->
    <EstudianteChat v-show="tab === 'chat'" :grupos="grupos" :loading-grupos="loadingGrupos" @notify="toast.notify" />
    <EstudianteAgenda v-show="tab === 'agenda'" :grupos="grupos" @notify="toast.notify" />
    <ProfileSection v-show="tab === 'perfil'" @notify="toast.notify" />
  </RoleLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { estudianteService } from '../services'
import { createToast } from '../composables/useToast'
import RoleLayout from '../components/RoleLayout.vue'
import ProfileSection from '../components/ProfileSection.vue'
import EstudianteChat from './estudiante/EstudianteChat.vue'
import EstudianteAgenda from './estudiante/EstudianteAgenda.vue'

const NAV_ITEMS = [
  { value: 'chat', label: 'Asistente', icon: 'mdi-forum-outline' },
  { value: 'agenda', label: 'Agenda', icon: 'mdi-calendar-month-outline' },
  { value: 'perfil', label: 'Perfil', icon: 'mdi-account-circle' },
]

const toast = createToast()
const tab = ref('chat')
const grupos = ref([])
const loadingGrupos = ref(true)

async function loadGrupos() {
  loadingGrupos.value = true
  try {
    const r = await estudianteService.listGrupos()
    grupos.value = r.cursos || []
  } catch (e) {
    toast.notifyError(e, 'No se pudieron cargar tus cursos')
  } finally {
    loadingGrupos.value = false
  }
}

onMounted(loadGrupos)
</script>
