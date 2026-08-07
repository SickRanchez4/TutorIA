<template>
  <div v-if="loading.curso" class="coord-loading d-flex flex-column align-center justify-center py-16 ga-3">
    <v-progress-circular indeterminate color="primary" size="42" width="4" />
    <p class="text-body-2 coord-subtext">Cargando curso...</p>
  </div>

  <div v-else class="coord-detalle-view">
    <v-card class="coord-hero" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5">
        <div>
          <v-btn to="/coordinador/cursos" variant="text" prepend-icon="mdi-arrow-left" class="mb-2 px-0">
            Volver a cursos
          </v-btn>
          <div class="d-flex align-center flex-wrap ga-2">
            <h2 class="text-h5 font-weight-black mb-0">{{ curso.nombre }}</h2>
            <v-chip size="small" variant="outlined" class="font-mono">{{ curso.codigo }}</v-chip>
            <v-chip size="small" :color="curso.is_active ? 'success' : 'grey'" :variant="curso.is_active ? 'flat' : 'outlined'">
              {{ curso.is_active ? 'Habilitado' : 'Inhabilitado' }}
            </v-chip>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <v-tabs v-model="tab" color="primary" class="coord-tabs" align-tabs="start" slider-color="primary">
      <v-tab v-for="t in tabs" :key="t.key" :value="t.key" rounded="lg">
        <v-icon start :icon="t.icon"></v-icon>
        {{ t.label }}
      </v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-2">
      <v-window-item value="resumen">
        <v-row>
          <v-col cols="12" md="6" lg="6">
            <v-card class="coord-stat-card h-100" rounded="xl" variant="flat">
              <v-card-text class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption coord-subtext mb-1">Alumnos inscritos</p>
                  <p class="text-h4 font-weight-black mb-0">{{ curso.estudiantes_count || 0 }}</p>
                </div>
                <v-icon icon="mdi-account-multiple" color="primary" size="34"></v-icon>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="6" lg="6">
            <v-card class="coord-stat-card h-100" rounded="xl" variant="flat">
              <v-card-text class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption coord-subtext mb-1">Estado del curso</p>
                  <p class="text-h6 font-weight-black mb-0">
                    {{ curso.is_active ? 'Habilitado' : 'Inhabilitado' }}
                  </p>
                </div>
                <v-icon :icon="curso.is_active ? 'mdi-check-circle-outline' : 'mdi-close-circle-outline'" :color="curso.is_active ? 'success' : 'error'" size="34"></v-icon>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" lg="6">
            <v-card class="coord-surface-card" rounded="xl" variant="flat">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-pencil-ruler"></v-icon>
                Datos del curso
                <v-spacer></v-spacer>
                <v-btn v-if="!editingDatos" size="small" variant="tonal" color="primary" @click="startEditDatos">Editar</v-btn>
                <v-btn v-else size="small" variant="text" @click="cancelEditDatos">Cancelar</v-btn>
              </v-card-title>
              <v-card-text>
                <form @submit.prevent="updateCurso" class="d-flex flex-column ga-3">
                  <v-text-field v-model="editCurso.nombre" label="Nombre" variant="solo-filled" density="comfortable" :readonly="!editingDatos" required />
                  <v-text-field v-model="editCurso.codigo" label="Código" variant="solo-filled" density="comfortable" class="font-mono uppercase" :readonly="!editingDatos" required />
                  <v-textarea v-model="editCurso.descripcion" label="Descripción" variant="solo-filled" density="comfortable" rows="3" :readonly="!editingDatos" />
                  <v-btn v-if="editingDatos" type="submit" color="primary" rounded="lg" class="coord-primary-btn align-self-start">
                    Guardar cambios
                  </v-btn>
                </form>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" lg="6">
            <v-card class="coord-surface-card mb-5" rounded="xl" variant="flat">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-tune-variant"></v-icon>
                Opciones de interacción
              </v-card-title>
              <v-card-text>
                <p class="text-caption coord-subtext mb-3">Habilita o deshabilita funciones del asistente para este curso.</p>
                <div class="d-flex align-center justify-space-between mb-2">
                  <span>Chat</span>
                  <v-switch :model-value="modos.chat" color="primary" hide-details density="comfortable" @update:model-value="(val) => toggleModo('chat', val)" />
                </div>
                <div class="d-flex align-center justify-space-between mb-2">
                  <span>Modo socrático</span>
                  <v-switch :model-value="modos.socratico" color="primary" hide-details density="comfortable" @update:model-value="(val) => toggleModo('socratico', val)" />
                </div>
                <div class="d-flex align-center justify-space-between">
                  <span>Recursos sintéticos</span>
                  <v-switch :model-value="modos.recursos" color="primary" hide-details density="comfortable" @update:model-value="(val) => toggleModo('recursos', val)" />
                </div>
              </v-card-text>
            </v-card>

            <v-card class="coord-surface-card" rounded="xl" variant="flat">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-shield-alert-outline"></v-icon>
                Estado del curso
              </v-card-title>
              <v-card-text class="d-flex flex-wrap ga-2">
                <v-btn @click="toggleActivo" variant="outlined" rounded="lg" class="coord-outline-btn">
                  {{ curso.is_active ? 'Inhabilitar curso' : 'Habilitar curso' }}
                </v-btn>
                <v-btn @click="confirmDelete = true" color="error" variant="outlined" rounded="lg">
                  Eliminar curso
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item value="alumnos">
        <v-card class="coord-surface-card mb-5" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-3">
            <div>
              <h4 class="text-h6 font-weight-bold mb-1">Alumnos inscritos</h4>
              <p class="text-caption coord-subtext mb-0">Gestiona altas individuales o importación masiva por Excel.</p>
            </div>
            <v-btn @click="showAltaAlumnoModal = true; alumnosActiveTab = 'add'" color="primary" rounded="lg" prepend-icon="mdi-plus-circle" class="coord-primary-btn">
              Añadir alumno
            </v-btn>
          </v-card-text>
        </v-card>

        <v-dialog v-model="showAltaAlumnoModal" max-width="640">
          <v-card class="coord-dialog-card" rounded="xl" variant="flat">
            <v-card-title class="pt-5 pb-2 px-6">Gestionar alumnos</v-card-title>
            <v-tabs v-model="alumnosActiveTab" color="primary" class="px-4">
              <v-tab value="add" prepend-icon="mdi-account-plus">Añadir alumno</v-tab>
              <v-tab value="import" prepend-icon="mdi-file-excel">Importar desde Excel</v-tab>
            </v-tabs>
            <v-card-text class="pt-5">
              <div v-show="alumnosActiveTab === 'add'">
                <form @submit.prevent="addEstudianteAndClose" class="d-flex flex-column ga-3">
                  <v-text-field v-model="newAlumno.email" label="Email" type="email" variant="solo-filled" density="comfortable" required />
                  <v-text-field v-model="newAlumno.first_name" label="Nombre" variant="solo-filled" density="comfortable" />
                  <v-text-field v-model="newAlumno.last_name" label="Apellido" variant="solo-filled" density="comfortable" />
                  <v-text-field v-model="newAlumno.phone" label="Teléfono (opcional)" variant="solo-filled" density="comfortable" />
                  <div class="d-flex ga-2 justify-end mt-1">
                    <v-btn @click="showAltaAlumnoModal = false" variant="text">Cancelar</v-btn>
                    <v-btn type="submit" color="primary" rounded="lg" class="coord-primary-btn">Inscribir alumno</v-btn>
                  </div>
                </form>
              </div>

              <div v-show="alumnosActiveTab === 'import'" class="d-flex flex-column ga-3">
                <p class="text-body-2 coord-subtext mb-0">Columnas: email, nombre, apellido, phone (opcional)</p>
                <v-file-input
                  v-model="alumnosExcelFiles"
                  accept=".xlsx,.xls"
                  label="Seleccionar archivo Excel"
                  prepend-icon="mdi-file-excel-outline"
                  variant="solo-filled"
                  density="comfortable"
                  show-size
                ></v-file-input>
                <div class="d-flex ga-2 justify-end">
                  <v-btn @click="showAltaAlumnoModal = false" variant="text">Cancelar</v-btn>
                  <v-btn @click="importAlumnosExcelAndClose" color="primary" rounded="lg" class="coord-primary-btn">Importar alumnos</v-btn>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-dialog>

        <v-card class="coord-surface-card" rounded="xl" variant="flat">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-account-multiple"></v-icon>
            Alumnos inscritos
            <v-chip v-if="estudiantes.length" color="primary" variant="tonal" size="x-small">{{ estudiantes.length }}</v-chip>
          </v-card-title>
          <v-card-text>
            <div v-if="loading.alumnos" class="d-flex flex-column align-center justify-center py-10 ga-3">
              <v-progress-circular indeterminate color="primary" size="38" width="4" />
              <p class="text-body-2 coord-subtext">Cargando alumnos...</p>
            </div>

            <div v-else-if="!estudiantes.length" class="text-center py-8 coord-subtext">
              <p class="text-body-2 mb-0">No hay alumnos inscritos en este curso.</p>
            </div>

            <v-table v-else density="comfortable" class="coord-table">
              <thead>
                <tr>
                  <th class="text-left">Alumno</th>
                  <th class="text-left">Email</th>
                  <th class="text-left">Inscrito el</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in estudiantes" :key="a.user_id">
                  <td>{{ a.full_name }}</td>
                  <td class="coord-subtext">{{ a.email }}</td>
                  <td class="coord-subtext">{{ formatFechaInscripcion(a.fecha_inscripcion) }}</td>
                  <td class="text-right">
                    <v-btn variant="text" color="error" size="small" @click="removeEstudiante(a.user_id)">Desinscribir</v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-window-item>

      <v-window-item value="agente">
        <div v-if="loading.agente" class="d-flex flex-column align-center justify-center py-12 ga-3">
          <v-progress-circular indeterminate color="primary" size="40" width="4" />
          <p class="text-body-2 coord-subtext">Cargando configuración del agente...</p>
        </div>

        <v-row v-else>
          <v-col cols="12" lg="7">
            <v-card class="coord-surface-card" rounded="xl" variant="flat">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-robot-outline"></v-icon>
                Configuración del agente
              </v-card-title>
              <v-card-text>
                <form @submit.prevent="saveAgente" class="d-flex flex-column ga-4">
                  <v-textarea
                    v-model="agente.system_prompt"
                    label="System prompt"
                    variant="solo-filled"
                    rows="6"
                    auto-grow
                    required
                  ></v-textarea>

                  <div>
                    <p class="text-caption coord-subtext mb-2">Temperatura: {{ agente.temperatura }}</p>
                    <v-slider v-model="agente.temperatura" min="0" max="2" step="0.1" color="primary" thumb-label></v-slider>
                  </div>

                  <div class="coord-toggle-row d-flex align-center justify-space-between">
                    <div class="d-flex align-center ga-2">
                      <span>Extender conocimiento</span>
                      <v-tooltip text="Amplía el contexto usando capacidades propias del modelo de IA además del material indexado.">
                        <template #activator="{ props }">
                          <v-icon v-bind="props" icon="mdi-information-outline" size="18" color="primary"></v-icon>
                        </template>
                      </v-tooltip>
                    </div>
                    <v-switch v-model="agente.extender_conocimiento" color="primary" hide-details density="comfortable"></v-switch>
                  </div>

                  <v-btn type="submit" color="primary" rounded="lg" class="coord-primary-btn align-self-start">
                    Guardar configuración
                  </v-btn>
                </form>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" lg="5">
            <v-card class="coord-surface-card" rounded="xl" variant="flat">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-file-document-multiple-outline"></v-icon>
                Base de conocimiento (PDFs)
              </v-card-title>
              <v-card-text class="d-flex flex-column ga-3">
                <p class="text-caption coord-subtext mb-0">Sube uno o más PDF para ampliar el conocimiento disponible del curso.</p>
                <div v-if="conocimiento" class="knowledge-summary">
                  <div class="d-flex align-center justify-space-between ga-2 mb-2">
                    <span class="text-caption font-weight-bold">Estado de la base</span>
                    <v-chip size="x-small" :color="knowledgeStatus.color" variant="tonal">
                      {{ knowledgeStatus.label }}
                    </v-chip>
                  </div>
                  <div class="d-flex flex-wrap ga-2">
                    <v-chip size="small" variant="outlined">{{ conocimiento.resumen.documentos_indexados }} PDF</v-chip>
                  </div>
                  <p v-if="conocimiento.resumen.ultimo_procesamiento_at" class="text-caption coord-subtext mb-0 mt-2">
                    Última indexación: {{ formatDateTime(conocimiento.resumen.ultimo_procesamiento_at) }}
                  </p>
                  <v-alert v-if="latestFailedJob" type="warning" variant="tonal" density="compact" class="mt-3">
                    <div class="d-flex align-center justify-space-between ga-2">
                      <span>La última carga requiere atención.</span>
                      <v-btn size="x-small" variant="text" color="warning" :loading="retryingJobId === latestFailedJob.id" @click="retryConocimiento(latestFailedJob)">Reintentar</v-btn>
                    </div>
                  </v-alert>
                </div>
                <v-skeleton-loader v-else-if="loading.conocimiento" type="list-item-two-line" />
                <div v-if="conocimiento?.documentos?.length" class="knowledge-documents">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <span class="text-caption font-weight-bold">PDFs indexados</span>
                    <v-btn
                      size="x-small"
                      color="error"
                      variant="text"
                      :loading="clearingConocimiento"
                      @click="clearConocimiento"
                    >
                      Vaciar base
                    </v-btn>
                  </div>
                  <div v-for="documento in conocimiento.documentos" :key="documento.archivo" class="knowledge-document-row">
                    <div class="min-w-0">
                      <p class="text-body-2 text-truncate mb-0">{{ documento.archivo }}</p>
                      <p v-if="documento.tamano_bytes" class="text-caption coord-subtext mb-0">{{ formatFileSize(documento.tamano_bytes) }}</p>
                    </div>
                    <v-btn
                      icon="mdi-delete-outline"
                      size="x-small"
                      color="error"
                      variant="text"
                      :loading="deletingDocument === documento.archivo"
                      :disabled="clearingConocimiento"
                      @click="removeDocumentoConocimiento(documento.archivo)"
                    >
                      <v-tooltip activator="parent" location="top">Quitar de Pinecone</v-tooltip>
                    </v-btn>
                  </div>
                </div>
                <v-file-input
                  v-model="conocimientoFiles"
                  accept=".pdf"
                  multiple
                  chips
                  show-size
                  label="Seleccionar archivos PDF"
                  prepend-icon="mdi-file-pdf-box"
                  variant="solo-filled"
                  density="comfortable"
                ></v-file-input>

                <v-btn
                  @click="uploadConocimiento"
                  type="button"
                  color="primary"
                  rounded="lg"
                  class="coord-primary-btn"
                  :loading="uploadingConocimiento"
                  :disabled="uploadingConocimiento"
                >
                  {{ uploadingConocimiento ? 'Procesando...' : 'Subir y procesar PDFs' }}
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>

    <v-dialog v-model="confirmDelete" max-width="460">
      <v-card class="coord-dialog-card" rounded="xl" variant="flat">
        <v-card-title class="pt-5">¿Eliminar curso permanentemente?</v-card-title>
        <v-card-text class="coord-subtext">
          Esta acción eliminará <strong>{{ curso.nombre }}</strong> y todas sus inscripciones. No se puede deshacer.
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-btn @click="confirmDelete = false" variant="text">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn @click="deleteCurso" color="error" variant="flat">Sí, eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from './useCoordinadorToast'

const route = useRoute()
const router = useRouter()
const { notify, notifyError } = useCoordinadorToast()

const cursoId = ref(route.params.id)
const curso = ref(null)
const editCurso = reactive({ nombre: '', codigo: '', descripcion: '' })
const editingDatos = ref(false)
const confirmDelete = ref(false)

const tab = ref('resumen')
const tabs = [
  { key: 'resumen', label: 'Resumen', icon: 'mdi-chart-line' },
  { key: 'alumnos', label: 'Alumnos', icon: 'mdi-account-multiple' },
  { key: 'agente', label: 'Agente IA', icon: 'mdi-robot' },
]

const estudiantes = ref([])
const newAlumno = reactive({ email: '', first_name: '', last_name: '', phone: '' })
const alumnosExcelFiles = ref([])
const showAltaAlumnoModal = ref(false)
const alumnosActiveTab = ref('add')

const agente = reactive({ system_prompt: '', temperatura: 0.2, extender_conocimiento: false })
const modos = reactive({ chat: true, socratico: true, recursos: true })
const conocimientoFiles = ref([])
const uploadingConocimiento = ref(false)
const conocimiento = ref(null)
const retryingJobId = ref('')
const deletingDocument = ref('')
const clearingConocimiento = ref(false)

const loading = reactive({ curso: true, alumnos: true, agente: true, conocimiento: true })

const latestFailedJob = computed(() => conocimiento.value?.trabajos?.find((job) => ['failed', 'unknown'].includes(job.estado)) || null)
const knowledgeStatus = computed(() => {
  const estado = conocimiento.value?.resumen?.ultimo_estado || 'sin_material'
  return {
    completed: { label: 'Indexada', color: 'success' },
    processing: { label: 'Procesando', color: 'primary' },
    queued: { label: 'En cola', color: 'primary' },
    failed: { label: 'Con error', color: 'warning' },
    unknown: { label: 'Por confirmar', color: 'warning' },
    sin_material: { label: 'Sin material', color: 'default' },
  }[estado] || { label: estado, color: 'default' }
})

function formatFechaInscripcion(value) {
  if (!value) return 'Sin fecha'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return 'Sin fecha'
  return d.toLocaleDateString()
}

async function loadCurso() {
  loading.curso = true
  try {
    const r = await coordinadorService.getCurso(cursoId.value)
    curso.value = r.curso
    editCurso.nombre = r.curso.nombre
    editCurso.codigo = r.curso.codigo
    editCurso.descripcion = r.curso.descripcion || ''
  } catch (e) {
    notifyError(e, 'No se pudo cargar el curso')
  } finally {
    loading.curso = false
  }
}

async function updateCurso() {
  try {
    const r = await coordinadorService.updateCurso(cursoId.value, {
      nombre: editCurso.nombre,
      codigo: editCurso.codigo,
      descripcion: editCurso.descripcion,
    })
    curso.value = { ...curso.value, ...r.curso }
    editingDatos.value = false
    notify('Curso actualizado')
  } catch (e) {
    notifyError(e, 'No se pudo actualizar curso')
  }
}

function startEditDatos() {
  editingDatos.value = true
}

function cancelEditDatos() {
  editCurso.nombre = curso.value.nombre
  editCurso.codigo = curso.value.codigo
  editCurso.descripcion = curso.value.descripcion || ''
  editingDatos.value = false
}

async function toggleActivo() {
  try {
    const r = await coordinadorService.updateCurso(cursoId.value, { is_active: !curso.value.is_active })
    curso.value = { ...curso.value, ...r.curso }
    notify(curso.value.is_active ? 'Curso habilitado' : 'Curso inhabilitado')
  } catch (e) {
    notifyError(e, 'No se pudo actualizar el estado del curso')
  }
}

async function deleteCurso() {
  try {
    await coordinadorService.deleteCurso(cursoId.value)
    notify('Curso eliminado permanentemente')
    router.push('/coordinador/cursos')
  } catch (e) {
    notifyError(e, 'No se pudo eliminar curso')
    confirmDelete.value = false
  }
}

async function loadEstudiantes() {
  loading.alumnos = true
  try {
    const r = await coordinadorService.listEstudiantesCurso(cursoId.value)
    estudiantes.value = r.estudiantes || []
  } catch (e) {
    notifyError(e, 'No se pudo cargar alumnos')
  } finally {
    loading.alumnos = false
  }
}

async function addEstudiante() {
  if (!newAlumno.email.trim()) return notify('El email es requerido', true)
  try {
    await coordinadorService.addEstudianteCurso(cursoId.value, { ...newAlumno })
    notify('Alumno inscrito')
    Object.assign(newAlumno, { email: '', first_name: '', last_name: '', phone: '' })
    await Promise.all([loadEstudiantes(), loadCurso()])
  } catch (e) {
    notifyError(e, 'No se pudo inscribir al alumno')
  }
}

async function removeEstudiante(userId) {
  try {
    await coordinadorService.removeEstudianteCurso(cursoId.value, userId)
    notify('Alumno desinscrito')
    await Promise.all([loadEstudiantes(), loadCurso()])
  } catch (e) {
    notifyError(e, 'No se pudo desinscribir al alumno')
  }
}

async function importAlumnosExcel() {
  const file = alumnosExcelFiles.value?.[0]
  if (!file) {
    notify('Selecciona un archivo Excel', true)
    return false
  }
  try {
    const r = await coordinadorService.importEstudiantesCursoExcel(cursoId.value, file)
    notify(`Alumnos importados: ${r.enrolled} inscripciones, ${r.created} cuentas nuevas`)
    alumnosExcelFiles.value = []
    await Promise.all([loadEstudiantes(), loadCurso()])
    return true
  } catch (e) {
    notifyError(e, 'No se pudo importar alumnos')
    return false
  }
}

async function addEstudianteAndClose() {
  await addEstudiante()
  if (newAlumno.email === '') {
    showAltaAlumnoModal.value = false
  }
}

async function importAlumnosExcelAndClose() {
  const ok = await importAlumnosExcel()
  if (!ok) return
  showAltaAlumnoModal.value = false
}

async function loadAgente() {
  loading.agente = true
  try {
    const r = await coordinadorService.getAgenteCurso(cursoId.value)
    Object.assign(agente, r.agente)
    syncModosFromAgente()
  } catch (e) {
    notifyError(e, 'No se pudo cargar la configuración del agente')
  } finally {
    loading.agente = false
  }
}

async function loadConocimiento() {
  loading.conocimiento = true
  try {
    conocimiento.value = await coordinadorService.getConocimientoCurso(cursoId.value)
  } catch (e) {
    notifyError(e, 'No se pudo cargar el estado de la base de conocimiento')
  } finally {
    loading.conocimiento = false
  }
}

async function retryConocimiento(job) {
  retryingJobId.value = job.id
  try {
    await coordinadorService.retryConocimientoCurso(cursoId.value, job.id)
    notify('Indexación reintentada')
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo reintentar la indexación')
  } finally {
    retryingJobId.value = ''
  }
}

async function removeDocumentoConocimiento(filename) {
  if (!window.confirm(`¿Quitar "${filename}" de la base de conocimiento? Esta acción eliminará sus vectores de Pinecone.`)) return
  deletingDocument.value = filename
  try {
    await coordinadorService.operarConocimientoCurso(cursoId.value, {
      action: 'delete_document',
      archivo: filename,
    })
    notify('Documento eliminado de la base de conocimiento')
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo eliminar el documento')
  } finally {
    deletingDocument.value = ''
  }
}

async function clearConocimiento() {
  if (!window.confirm('¿Vaciar toda la base de conocimiento de este curso? Esta acción eliminará todos los vectores de Pinecone.')) return
  clearingConocimiento.value = true
  try {
    await coordinadorService.operarConocimientoCurso(cursoId.value, { action: 'clear_course' })
    notify('Base de conocimiento vaciada')
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo vaciar la base de conocimiento')
  } finally {
    clearingConocimiento.value = false
  }
}

async function saveAgente() {
  try {
    const r = await coordinadorService.updateAgenteCurso(cursoId.value, {
      system_prompt: agente.system_prompt,
      temperatura: agente.temperatura,
      extender_conocimiento: agente.extender_conocimiento,
    })
    Object.assign(agente, r.agente)
    syncModosFromAgente()
    notify('Configuración del agente guardada')
  } catch (e) {
    notifyError(e, 'No se pudo guardar la configuración del agente')
  }
}

function syncModosFromAgente() {
  const activos = agente.modos_permitidos || []
  modos.chat = activos.includes('chat')
  modos.socratico = activos.includes('socratico')
  modos.recursos = activos.includes('recursos')
}

async function toggleModo(modo, value) {
  const previous = { ...modos }
  modos[modo] = value
  const modosActivos = Object.keys(modos).filter((k) => modos[k])
  try {
    const r = await coordinadorService.updateAgenteCurso(cursoId.value, { modos_permitidos: modosActivos })
    Object.assign(agente, r.agente)
    syncModosFromAgente()
  } catch (e) {
    Object.assign(modos, previous)
    notifyError(e, 'No se pudo actualizar la opción')
  }
}

async function uploadConocimiento() {
  const files = conocimientoFiles.value
  if (!files || !files.length) return notify('Selecciona al menos un archivo PDF', true)
  
  // Validar que todos sean PDFs
  for (const file of files) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return notifyError(null, `"${file.name}" no es un PDF válido`)
    }
  }
  
  uploadingConocimiento.value = true
  try {
    await coordinadorService.uploadMaterialCurso(cursoId.value, files)
    notify('Material procesado correctamente')
    conocimientoFiles.value = []
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo procesar el material')
  } finally {
    uploadingConocimiento.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadCurso(), loadEstudiantes(), loadAgente(), loadConocimiento()])
})

watch(() => route.params.id, async (id) => {
  if (!id) return
  cursoId.value = id
  tab.value = 'resumen'
  estudiantes.value = []
  loading.curso = true
  loading.alumnos = true
  loading.agente = true
  loading.conocimiento = true
  conocimiento.value = null
  await Promise.all([loadCurso(), loadEstudiantes(), loadAgente(), loadConocimiento()])
})

function formatDateTime(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Fecha no disponible' : date.toLocaleString('es-BO', { dateStyle: 'medium', timeStyle: 'short' })
}

function formatFileSize(bytes) {
  if (!bytes) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / (1024 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`
}
</script>

<style scoped>
.coord-detalle-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.coord-subtext {
  opacity: 0.74;
}

.coord-hero {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background:
    radial-gradient(circle at 16% 18%, rgba(124, 197, 118, 0.14), rgba(124, 197, 118, 0) 46%),
    linear-gradient(145deg, #25262b 0%, #2e3037 100%);
  box-shadow: 0 14px 26px rgba(0, 0, 0, 0.34);
}

.coord-tabs {
  border-bottom: 1px solid rgba(124, 197, 118, 0.16);
}

.coord-primary-btn {
  color: #ffffff !important;
  background: linear-gradient(140deg, #7cc576 0%, #609f5b 100%) !important;
  font-weight: 700;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.24);
}

.coord-primary-btn:hover {
  box-shadow: 0 0 26px rgba(124, 197, 118, 0.34);
}

.coord-outline-btn {
  border-color: rgba(124, 197, 118, 0.32);
}

.coord-stat-card,
.coord-surface-card,
.coord-dialog-card {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background: linear-gradient(145deg, #26272d 0%, #31323a 100%);
  backdrop-filter: blur(8px);
}

.coord-toggle-row {
  border: 1px solid rgba(124, 197, 118, 0.2);
  border-radius: 12px;
  padding: 10px 12px;
  background: rgba(124, 197, 118, 0.08);
}

.knowledge-summary {
  padding: 12px;
  border: 1px solid rgba(124, 197, 118, 0.2);
  border-radius: 12px;
  background: rgba(124, 197, 118, 0.06);
}

.knowledge-documents {
  max-height: 190px;
  padding: 10px;
  overflow: auto;
  border: 1px solid rgba(124, 197, 118, 0.16);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.12);
}

.knowledge-document-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 7px 2px;
}

.knowledge-document-row + .knowledge-document-row {
  border-top: 1px solid rgba(124, 197, 118, 0.12);
}

.knowledge-document-row > div {
  min-width: 0;
  flex: 1;
}

.knowledge-document-row p:first-child {
  color: rgba(244, 248, 244, 0.72);
  font-size: 0.76rem;
}

.coord-table :deep(thead th) {
  font-weight: 700;
  opacity: 0.8;
}

.coord-table :deep(tbody tr) {
  transition: background-color 0.2s ease;
}

.coord-table :deep(tbody tr:hover) {
  background: rgba(124, 197, 118, 0.08);
}

.coord-loading {
  border: 1px solid rgba(124, 197, 118, 0.16);
  border-radius: 16px;
  background: linear-gradient(145deg, #25262b 0%, #2f3038 100%);
}
</style>
