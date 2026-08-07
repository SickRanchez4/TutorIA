<template>
  <div class="coord-cuentas-view">
    <v-card class="coord-hero" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5">
        <div>
          <p class="text-overline mb-1 coord-overline">Administración</p>
          <h2 class="text-h5 font-weight-black mb-1">Cuentas de alumnos</h2>
          <p class="mb-0 coord-subtext">Visualiza, edita y depura cuentas con control total por curso.</p>
        </div>
        <v-chip color="primary" variant="tonal" size="small">
          {{ filteredEstudiantes.length }} registros visibles
        </v-chip>
      </v-card-text>
    </v-card>

    <v-card class="coord-surface-card" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-3">
        <h3 class="text-subtitle-1 font-weight-bold d-flex align-center ga-2 mb-0">
          <v-icon icon="mdi-account-multiple" color="primary"></v-icon>
          Cuentas
        </h3>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por nombre o email"
          variant="solo-filled"
          density="compact"
          hide-details
          style="max-width: 320px"
        ></v-text-field>
      </v-card-text>
    </v-card>

    <v-card class="coord-surface-card" rounded="xl" variant="flat">
      <v-card-text>
        <div v-if="loading" class="d-flex flex-column align-center justify-center py-12 ga-3">
          <v-progress-circular indeterminate color="primary" size="40" width="4" />
          <p class="text-body-2 coord-subtext mb-0">Cargando cuentas...</p>
        </div>

        <div v-else-if="!estudiantes.length" class="text-center py-9 coord-subtext">
          <v-icon icon="mdi-account-search-outline" size="32" class="mb-2"></v-icon>
          <p class="text-body-2 mb-0">No hay cuentas de alumnos registradas todavía.</p>
        </div>

        <v-table v-else density="comfortable" class="coord-table">
          <thead>
            <tr>
              <th class="text-left">Nombre</th>
              <th class="text-left">Email</th>
              <th class="text-left">Teléfono</th>
              <th class="text-left">Matrícula</th>
              <th class="text-left">Cursos</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="est in filteredEstudiantes" :key="est.id">
              <td class="font-weight-medium">{{ est.full_name }}</td>
              <td class="coord-subtext">{{ est.email }}</td>
              <td class="coord-subtext">{{ est.phone || '—' }}</td>
              <td>
                <v-chip size="x-small" :color="est.matriculado ? 'success' : 'grey'" :variant="est.matriculado ? 'flat' : 'outlined'">
                  {{ est.matriculado ? 'Activa' : 'Inactiva' }}
                </v-chip>
              </td>
              <td class="coord-subtext">
                <span v-if="est.cursos.length">{{ est.cursos.map(c => c.codigo || c.nombre).join(', ') }}</span>
                <span v-else>Sin cursos</span>
              </td>
              <td class="text-right">
                <v-btn size="small" variant="text" color="primary" @click="openEdit(est)">Editar</v-btn>
                <v-btn size="small" variant="text" color="error" @click="confirmDeleteEstudiante = est">Eliminar</v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="isEditDialogOpen" max-width="520">
      <v-card class="coord-dialog-card" rounded="xl" variant="flat">
        <v-card-title class="pt-5">Editar cuenta</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveEdit" class="d-flex flex-column ga-3">
            <v-text-field v-model="editForm.first_name" label="Nombre" variant="solo-filled" density="comfortable" required />
            <v-text-field v-model="editForm.last_name" label="Apellido" variant="solo-filled" density="comfortable" />
            <v-text-field v-model="editForm.email" label="Email" type="email" variant="solo-filled" density="comfortable" required />
            <v-text-field v-model="editForm.phone" label="Teléfono" variant="solo-filled" density="comfortable" />
            <v-text-field v-model="editForm.password" label="Nueva contraseña (opcional)" type="password" variant="solo-filled" density="comfortable" />
            <div class="d-flex align-center justify-space-between mt-1">
              <span>Cuenta habilitada</span>
              <v-switch v-model="editForm.is_active" color="primary" hide-details density="comfortable"></v-switch>
            </div>
            <div class="d-flex ga-2 justify-end mt-2">
              <v-btn type="button" variant="text" @click="closeEditDialog">Cancelar</v-btn>
              <v-btn type="submit" color="primary" rounded="lg" class="coord-primary-btn">Guardar</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isDeleteDialogOpen" max-width="520">
      <v-card class="coord-dialog-card" rounded="xl" variant="flat">
        <v-card-title class="pt-5">¿Eliminar cuenta permanentemente?</v-card-title>
        <v-card-text class="coord-subtext">
          Esta acción eliminará la cuenta de <strong>{{ confirmDeleteEstudiante?.full_name }}</strong> y sus datos asociados (inscripciones, chats y consumo).
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-btn variant="text" @click="confirmDeleteEstudiante = null">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" variant="flat" @click="deleteEstudiante">Sí, eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from './useCoordinadorToast'

const { notify, notifyError } = useCoordinadorToast()

const estudiantes = ref([])
const loading = ref(true)
const search = ref('')
const editing = ref(null)
const editForm = reactive({ first_name: '', last_name: '', email: '', phone: '', password: '', is_active: true })
const confirmDeleteEstudiante = ref(null)

const isEditDialogOpen = computed({
  get: () => !!editing.value,
  set: (val) => {
    if (!val) editing.value = null
  }
})

const isDeleteDialogOpen = computed({
  get: () => !!confirmDeleteEstudiante.value,
  set: (val) => {
    if (!val) confirmDeleteEstudiante.value = null
  }
})

const filteredEstudiantes = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return estudiantes.value
  return estudiantes.value.filter((e) =>
    (e.full_name || '').toLowerCase().includes(q) || (e.email || '').toLowerCase().includes(q)
  )
})

async function loadEstudiantes() {
  loading.value = true
  try {
    const r = await coordinadorService.listEstudiantes()
    estudiantes.value = r.estudiantes || []
  } catch (e) {
    notifyError(e, 'No se pudo cargar las cuentas de alumnos')
  } finally {
    loading.value = false
  }
}

function openEdit(est) {
  editing.value = est
  editForm.first_name = est.first_name || ''
  editForm.last_name = est.last_name || ''
  editForm.email = est.email || ''
  editForm.phone = est.phone || ''
  editForm.password = ''
  editForm.is_active = !!est.is_active
}

function closeEditDialog() {
  editing.value = null
}

async function saveEdit() {
  if (!editing.value) return
  try {
    const payload = {
      first_name: editForm.first_name,
      last_name: editForm.last_name,
      email: editForm.email,
      phone: editForm.phone,
      is_active: editForm.is_active,
    }
    if (editForm.password) payload.password = editForm.password
    await coordinadorService.updateEstudiante(editing.value.id, payload)
    notify('Cuenta actualizada')
    editing.value = null
    await loadEstudiantes()
  } catch (e) {
    notifyError(e, 'No se pudo actualizar la cuenta')
  }
}

async function deleteEstudiante() {
  if (!confirmDeleteEstudiante.value) return
  try {
    await coordinadorService.deleteEstudiante(confirmDeleteEstudiante.value.id)
    notify('Cuenta eliminada')
    confirmDeleteEstudiante.value = null
    await loadEstudiantes()
  } catch (e) {
    notifyError(e, 'No se pudo eliminar la cuenta')
  }
}

onMounted(loadEstudiantes)
</script>

<style scoped>
.coord-cuentas-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.coord-overline {
  color: #8fd189;
  letter-spacing: 0.08em;
}

.coord-subtext {
  opacity: 0.74;
}

.coord-hero {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background:
    radial-gradient(circle at 16% 22%, rgba(124, 197, 118, 0.14), rgba(124, 197, 118, 0) 48%),
    linear-gradient(145deg, #25262b 0%, #2f3038 100%);
  box-shadow: 0 14px 26px rgba(0, 0, 0, 0.34);
}

.coord-surface-card,
.coord-dialog-card {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background: linear-gradient(145deg, #26272d 0%, #31323a 100%);
  backdrop-filter: blur(8px);
}

.coord-primary-btn {
  color: #ffffff !important;
  background: linear-gradient(140deg, #7cc576 0%, #609f5b 100%) !important;
  font-weight: 700;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.24);
}

.coord-table :deep(thead th) {
  font-weight: 700;
  opacity: 0.82;
}

.coord-table :deep(tbody tr) {
  transition: background-color 0.2s ease;
}

.coord-table :deep(tbody tr:hover) {
  background: rgba(124, 197, 118, 0.08);
}
</style>
