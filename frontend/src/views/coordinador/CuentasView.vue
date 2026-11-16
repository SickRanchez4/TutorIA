<template>
  <div class="d-flex flex-column ga-5">
    <PageHeader
      overline="Administración"
      title="Cuentas de alumnos"
      subtitle="Visualiza, edita y depura las cuentas de los alumnos de tu institución."
    >
      <template #actions>
        <v-chip color="primary" variant="tonal" size="small">{{ filteredEstudiantes.length }} registros visibles</v-chip>
      </template>
    </PageHeader>

    <v-card class="surface-card" rounded="xl">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-3 cuentas-toolbar">
        <h2 class="text-body-large font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-account-multiple" color="primary"></v-icon>
          Cuentas
        </h2>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por nombre o email"
          aria-label="Buscar por nombre o email"
          density="compact"
          clearable
          class="cuentas-search"
        ></v-text-field>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-text>
        <div v-if="loading" class="d-flex flex-column align-center justify-center py-12 ga-3" role="status">
          <v-progress-circular indeterminate color="primary" size="40" width="4" />
          <p class="text-body-medium text-subtle mb-0">Cargando cuentas...</p>
        </div>

        <RegionState v-else-if="loadError" :error="loadError" @retry="loadEstudiantes" />
        <div v-else-if="!estudiantes.length" class="empty-state">
          <v-icon icon="mdi-account-search-outline" size="32"></v-icon>
          <p class="mb-0">No hay cuentas de alumnos registradas todavía.</p>
        </div>

        <div v-else-if="!filteredEstudiantes.length" class="empty-state">
          <v-icon icon="mdi-magnify-close" size="32"></v-icon>
          <p class="mb-0">Ninguna cuenta coincide con «{{ search }}».</p>
        </div>

        <div v-else class="table-scroll" tabindex="0" aria-label="Tabla de cuentas; desliza horizontalmente para ver todas las columnas">
          <v-table density="comfortable" class="data-table cuentas-table">
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
              <tr v-for="est in pager.items" :key="est.id">
                <td class="font-weight-medium">{{ est.full_name }}</td>
                <td class="text-subtle">{{ est.email }}</td>
                <td class="text-subtle">{{ est.phone || '—' }}</td>
                <td>
                  <v-chip size="x-small" :color="hasActiveEnrollment(est) ? 'success' : 'grey'" :variant="hasActiveEnrollment(est) ? 'flat' : 'outlined'">
                    {{ hasActiveEnrollment(est) ? 'Activa' : 'Inactiva' }}
                  </v-chip>
                </td>
                <td class="text-subtle">{{ cursosLabel(est) }}</td>
                <td class="text-right text-no-wrap">
                  <v-btn size="small" variant="text" color="primary" @click="openEdit(est)">Editar</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDelete = est">Eliminar</v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>
        <ListPagination v-model:page="pager.state.page" v-model:page-size="pager.state.pageSize" :total="pager.total" />
      </v-card-text>
    </v-card>

    <v-dialog :model-value="!!editing" max-width="520" :persistent="saving" @update:model-value="open => open || closeEdit()">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="pt-5">Editar cuenta</v-card-title>
        <v-card-text>
          <v-form class="d-flex flex-column ga-3" @submit.prevent="saveEdit">
            <v-text-field v-model="editForm.first_name" label="Nombre" />
            <v-text-field v-model="editForm.last_name" label="Apellido" />
            <v-text-field v-model="editForm.email" label="Email" type="email" />
            <v-text-field v-model="editForm.phone" label="Teléfono" type="tel" />
            <v-text-field v-model="editForm.password" label="Nueva contraseña (opcional)" type="password" autocomplete="new-password" />
            <v-switch v-model="editForm.is_active" label="Cuenta habilitada" />
            <div class="d-flex ga-2 justify-end mt-1">
              <v-btn variant="text" :disabled="saving" @click="closeEdit">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="saving">Guardar</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog :model-value="!!confirmDelete" max-width="520" :persistent="saving" @update:model-value="(open) => open || (confirmDelete = null)">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="pt-5">¿Eliminar cuenta permanentemente?</v-card-title>
        <v-card-text class="text-subtle">
          Esta acción eliminará la cuenta de <strong>{{ confirmDelete?.full_name }}</strong> y sus datos asociados (inscripciones, chats y consumo).
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-btn variant="text" :disabled="saving" @click="confirmDelete = null">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" variant="flat" :loading="saving" @click="deleteEstudiante">Sí, eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from '../../composables/useToast'
import PageHeader from '../../components/PageHeader.vue'
import ListPagination from '../../components/ListPagination.vue'
import RegionState from '../../components/RegionState.vue'
import { usePagination } from '../../composables/usePagination'
import { useFormDraft } from '../../composables/useUnsavedChanges'

const { notify, notifyError } = useCoordinadorToast()

const estudiantes = ref([])
const loading = ref(true)
const loadError = ref('')
const saving = ref(false)
const search = ref('')
const editing = ref(null)
const confirmDelete = ref(null)
const editForm = reactive({ first_name: '', last_name: '', email: '', phone: '', password: '', is_active: true })
const draft = useFormDraft(() => editForm, () => Boolean(editing.value), () => saving.value)

const filteredEstudiantes = computed(() => {
  const q = (search.value || '').trim().toLowerCase()
  if (!q) return estudiantes.value
  return estudiantes.value.filter((e) =>
    (e.full_name || '').toLowerCase().includes(q) || (e.email || '').toLowerCase().includes(q),
  )
})
const pager = usePagination(filteredEstudiantes)
watch(search, () => { pager.state.page = 1 })
async function closeEdit() {
  if (!saving.value && await draft.canClose()) editing.value = null
}

const cursosLabel = (est) => (est.cursos?.length ? est.cursos.map((c) => c.codigo || c.nombre).join(', ') : 'Sin cursos')
const hasActiveEnrollment = (est) => est.is_active && est.matriculado

async function loadEstudiantes() {
  loading.value = true
  loadError.value = ''
  try {
    const r = await coordinadorService.listEstudiantes()
    estudiantes.value = r.estudiantes || []
  } catch (e) {
    loadError.value = 'No se pudieron cargar las cuentas'
    notifyError(e, 'No se pudieron cargar las cuentas de alumnos')
  } finally {
    loading.value = false
  }
}

function openEdit(est) {
  Object.assign(editForm, {
    first_name: est.first_name || '',
    last_name: est.last_name || '',
    email: est.email || '',
    phone: est.phone || '',
    password: '',
    is_active: !!est.is_active,
  })
  editing.value = est
  draft.accept()
}

async function saveEdit() {
  if (!editing.value || saving.value) return
  const { password, ...payload } = editForm
  if (password) payload.password = password

  saving.value = true
  try {
    await coordinadorService.updateEstudiante(editing.value.id, payload)
    notify('Cuenta actualizada')
    editing.value = null
    await loadEstudiantes()
  } catch (e) {
    notifyError(e, 'No se pudo actualizar la cuenta')
  } finally {
    saving.value = false
  }
}

async function deleteEstudiante() {
  if (!confirmDelete.value || saving.value) return
  saving.value = true
  try {
    await coordinadorService.deleteEstudiante(confirmDelete.value.id)
    notify('Cuenta eliminada')
    confirmDelete.value = null
    await loadEstudiantes()
  } catch (e) {
    notifyError(e, 'No se pudo eliminar la cuenta')
  } finally {
    saving.value = false
  }
}

onMounted(loadEstudiantes)
</script>

<style scoped>
.cuentas-search {
  flex: 0 1 320px;
  width: min(100%, 320px);
}

.cuentas-table {
  min-width: 820px;
}

@media (max-width: 599px) {
  .cuentas-toolbar {
    flex-direction: column;
    align-items: stretch !important;
  }

  .cuentas-search {
    width: 100%;
    flex-basis: auto;
  }
}
</style>
