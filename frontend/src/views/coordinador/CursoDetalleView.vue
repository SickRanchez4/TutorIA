<template>
  <div v-if="loading.curso" class="empty-state surface-card detail-placeholder" role="status">
    <v-progress-circular indeterminate color="primary" size="42" width="4" />
    <p class="mb-0">Cargando curso...</p>
  </div>

  <div v-else-if="!curso" class="empty-state surface-card detail-placeholder" role="alert">
    <v-icon icon="mdi-alert-circle-outline" size="34" color="error"></v-icon>
    <p class="mb-0">No se pudo cargar este curso. Puede que ya no exista o que no tengas acceso.</p>
    <div class="d-flex ga-2">
      <v-btn variant="text" prepend-icon="mdi-arrow-left" to="/coordinador/cursos">Volver a cursos</v-btn>
      <v-btn color="primary" variant="flat" @click="loadAll">Reintentar</v-btn>
    </div>
  </div>

  <div v-else class="d-flex flex-column ga-5">
    <PageHeader>
      <template #before>
        <v-btn to="/coordinador/cursos" variant="text" prepend-icon="mdi-arrow-left" class="mb-2 px-1">Volver a cursos</v-btn>
      </template>
      <template #title>
        <div class="d-flex align-center flex-wrap ga-2">
          <h1 class="text-headline-small font-weight-black">{{ curso.nombre }}</h1>
          <v-chip size="small" variant="outlined" class="font-mono">{{ curso.codigo }}</v-chip>
          <v-chip size="small" :color="curso.is_active ? 'success' : 'grey'" :variant="curso.is_active ? 'flat' : 'outlined'">
            {{ curso.is_active ? 'Habilitado' : 'Inhabilitado' }}
          </v-chip>
        </div>
      </template>
    </PageHeader>

    <v-tabs v-model="tab" class="detail-tabs" align-tabs="start">
      <v-tab v-for="t in TABS" :key="t.key" :value="t.key" rounded="lg">
        <v-icon start :icon="t.icon"></v-icon>
        {{ t.label }}
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <!-- Resumen -->
      <v-window-item value="resumen">
        <v-row>
          <v-col cols="12" sm="6">
            <StatCard label="Alumnos inscritos" :value="curso.estudiantes_count || 0" icon="mdi-account-multiple" />
          </v-col>
          <v-col cols="12" sm="6">
            <StatCard
              label="Estado del curso"
              :value="curso.is_active ? 'Habilitado' : 'Inhabilitado'"
              :icon="curso.is_active ? 'mdi-check-circle-outline' : 'mdi-close-circle-outline'"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-card class="surface-card" rounded="xl">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-pencil-ruler" color="primary"></v-icon>
                <h2 class="text-body-large font-weight-bold">Datos del curso</h2>
                <v-spacer></v-spacer>
                <v-btn v-if="!editingDatos" size="small" variant="tonal" color="primary" @click="editingDatos = true">Editar</v-btn>
                <v-btn v-else size="small" variant="text" @click="cancelEditDatos">Cancelar</v-btn>
              </v-card-title>
              <v-card-text>
                <v-form class="d-flex flex-column ga-3" :disabled="busy.datos" @submit.prevent="updateCurso">
                  <v-text-field v-model="editCurso.nombre" label="Nombre" :readonly="!editingDatos" />
                  <v-text-field v-model="editCurso.codigo" label="Código" class="font-mono" :readonly="!editingDatos" />
                  <v-textarea v-model="editCurso.descripcion" label="Descripción" rows="3" :readonly="!editingDatos" />
                  <v-btn v-if="editingDatos" type="submit" color="primary" variant="flat" class="align-self-start" :loading="busy.datos">
                    Guardar cambios
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="6" class="d-flex flex-column ga-5">
            <v-card class="surface-card" rounded="xl">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-tune-variant" color="primary"></v-icon>
                <h2 class="text-body-large font-weight-bold">Opciones de interacción</h2>
              </v-card-title>
              <v-card-text>
                <p class="text-body-small text-subtle mb-2">Habilita o deshabilita funciones del asistente para este curso.</p>
                <v-switch
                  v-for="m in MODOS"
                  :key="m.key"
                  :model-value="modos[m.key]"
                  :label="m.label"
                  :disabled="loading.agente || busy.agente || !!errors.agente"
                  @update:model-value="(val) => toggleModo(m.key, val)"
                />
              </v-card-text>
            </v-card>

            <v-card class="surface-card" rounded="xl">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-shield-alert-outline" color="primary"></v-icon>
                <h2 class="text-body-large font-weight-bold">Estado del curso</h2>
              </v-card-title>
              <v-card-text class="d-flex flex-wrap ga-2">
                <v-btn variant="outlined" :loading="busy.estado" @click="toggleActivo">
                  {{ curso.is_active ? 'Inhabilitar curso' : 'Habilitar curso' }}
                </v-btn>
                <v-btn color="error" variant="outlined" @click="confirmDelete = true">Eliminar curso</v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- Alumnos -->
      <v-window-item value="alumnos">
        <v-card class="surface-card" rounded="xl">
          <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-3">
            <div>
              <h2 class="text-title-large font-weight-bold mb-1 d-flex align-center ga-2">
                Alumnos inscritos
                <v-chip v-if="estudiantes.length" color="primary" variant="tonal" size="x-small">{{ estudiantes.length }}</v-chip>
              </h2>
              <p class="text-body-small text-subtle mb-0">Gestiona altas individuales o importación masiva por Excel.</p>
            </div>
            <v-btn color="primary" variant="flat" prepend-icon="mdi-plus-circle" @click="openAlumnoDialog">Añadir alumno</v-btn>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-text>
            <ImportSummary :result="importResult" />
            <v-text-field v-model="studentSearch" label="Buscar alumnos por nombre o correo" prepend-inner-icon="mdi-magnify" clearable />
            <div v-if="loading.alumnos" class="d-flex flex-column align-center justify-center py-10 ga-3" role="status">
              <v-progress-circular indeterminate color="primary" size="38" width="4" />
              <p class="text-body-medium text-subtle mb-0">Cargando alumnos...</p>
            </div>

            <RegionState v-else-if="errors.alumnos" :error="errors.alumnos" @retry="loadEstudiantes" />
            <div v-else-if="!estudiantes.length" class="empty-state">
              <v-icon icon="mdi-account-off-outline" size="30"></v-icon>
              <p class="mb-0">No hay alumnos inscritos en este curso.</p>
            </div>

            <div v-else class="table-scroll" tabindex="0" aria-label="Tabla de alumnos; desliza horizontalmente para ver todas las columnas">
              <v-table density="comfortable" class="data-table alumnos-table">
                <thead>
                  <tr>
                    <th class="text-left">Alumno</th>
                    <th class="text-left">Email</th>
                    <th class="text-left">Inscrito el</th>
                    <th class="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in studentPager.items" :key="a.user_id">
                    <td>{{ a.full_name }}</td>
                    <td class="text-subtle">{{ a.email }}</td>
                    <td class="text-subtle">{{ formatDate(a.fecha_inscripcion, undefined, 'Sin fecha') }}</td>
                    <td class="text-right">
                      <v-btn variant="text" color="error" size="small" :loading="removingId === a.user_id" @click="removeEstudiante(a)">Desinscribir</v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </div>
            <ListPagination v-model:page="studentPager.state.page" v-model:page-size="studentPager.state.pageSize" :total="studentPager.total" />
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Agente IA -->
      <v-window-item value="agente">
        <div v-if="loading.agente" class="d-flex flex-column align-center justify-center py-12 ga-3" role="status">
          <v-progress-circular indeterminate color="primary" size="40" width="4" />
          <p class="text-body-medium text-subtle mb-0">Cargando configuración del agente...</p>
        </div>

        <RegionState v-else-if="errors.agente" :error="errors.agente" @retry="loadAgente" />
        <v-row v-else>
          <v-col cols="12" md="7">
            <v-card class="surface-card" rounded="xl">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-robot-outline" color="primary"></v-icon>
                <h2 class="text-body-large font-weight-bold">Configuración del agente</h2>
              </v-card-title>
              <v-card-text>
                <v-form class="d-flex flex-column ga-4" :disabled="busy.agente" @submit.prevent="saveAgente">
                  <v-textarea v-model="agente.system_prompt" label="System prompt" rows="6" auto-grow />

                  <div>
                    <p class="text-body-small text-subtle mb-2">Temperatura: {{ agente.temperatura }}</p>
                    <v-slider v-model="agente.temperatura" min="0" max="2" step="0.1" color="primary" thumb-label aria-label="Temperatura"></v-slider>
                  </div>

                  <div class="toggle-row d-flex align-center justify-space-between">
                    <div class="d-flex align-center ga-2">
                      <span>Extender conocimiento</span>
                      <v-tooltip text="Amplía el contexto usando capacidades propias del modelo de IA además del material indexado.">
                        <template #activator="{ props: tooltipProps }">
                          <v-icon v-bind="tooltipProps" icon="mdi-information-outline" size="18" color="primary" aria-label="Más información" tabindex="0"></v-icon>
                        </template>
                      </v-tooltip>
                    </div>
                    <v-switch v-model="agente.extender_conocimiento" aria-label="Extender conocimiento" />
                  </div>

                  <v-btn type="submit" color="primary" variant="flat" class="align-self-start" :loading="busy.agente">
                    Guardar configuración
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="5">
            <v-card class="surface-card" rounded="xl">
              <v-card-title class="d-flex align-center ga-2">
                <v-icon icon="mdi-file-document-multiple-outline" color="primary"></v-icon>
                <h2 class="text-body-large font-weight-bold">Base de conocimiento (PDF)</h2>
              </v-card-title>
              <v-card-text class="d-flex flex-column ga-3">
                <p class="text-body-small text-subtle mb-0">Hasta 10 PDF por carga, de 20 MiB como máximo cada uno.</p>

                <v-skeleton-loader v-if="loading.conocimiento" type="list-item-two-line" class="bg-transparent" />
                <RegionState v-else-if="errors.conocimiento" :error="errors.conocimiento" @retry="loadConocimiento" />
                <div v-else-if="conocimiento" class="knowledge-box">
                  <div class="d-flex align-center justify-space-between ga-2 mb-2">
                    <span class="text-body-small font-weight-bold">Estado de la base</span>
                    <v-chip size="x-small" :color="knowledgeStatus.color" variant="tonal">{{ knowledgeStatus.label }}</v-chip>
                  </div>
                  <v-chip size="small" variant="outlined">{{ conocimiento.resumen?.documentos_indexados || 0 }} PDF</v-chip>
                  <p v-if="conocimiento.resumen?.ultimo_procesamiento_at" class="text-body-small text-subtle mb-0 mt-2">
                    Última indexación: {{ formatDateTime(conocimiento.resumen.ultimo_procesamiento_at) }}
                  </p>
                  <v-alert v-if="latestFailedJob" type="warning" variant="tonal" density="compact" class="mt-3 text-body-small">
                    <div class="d-flex align-center justify-space-between ga-2">
                      <span>La última carga requiere atención.</span>
                      <v-btn size="x-small" variant="text" color="warning" :loading="retryingJobId === latestFailedJob.id" @click="retryConocimiento(latestFailedJob)">Reintentar</v-btn>
                    </div>
                  </v-alert>
                </div>

                <div v-if="conocimiento?.documentos?.length" class="knowledge-box knowledge-documents">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <span class="text-body-small font-weight-bold">PDF indexados</span>
                    <v-btn size="x-small" color="error" variant="text" :loading="busy.vaciar" @click="clearConocimiento">Vaciar base</v-btn>
                  </div>
                  <div v-for="documento in conocimiento.documentos" :key="documento.archivo" class="knowledge-document">
                    <div class="min-w-0">
                      <p class="text-body-medium text-truncate mb-0">{{ documento.archivo }}</p>
                      <p v-if="documento.tamano_bytes" class="text-body-small text-subtle mb-0">{{ formatFileSize(documento.tamano_bytes) }}</p>
                    </div>
                    <v-btn
                      icon="mdi-delete-outline"
                      size="x-small"
                      color="error"
                      variant="text"
                      :aria-label="`Quitar ${documento.archivo}`"
                      :loading="deletingDocument === documento.archivo"
                      :disabled="busy.vaciar"
                      @click="removeDocumento(documento.archivo)"
                    >
                      <v-tooltip activator="parent" location="top">Quitar de la base de conocimiento</v-tooltip>
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
                ></v-file-input>
                <v-btn color="primary" variant="flat" :loading="busy.subida" @click="uploadConocimiento">
                  Subir y procesar PDF
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>

    <v-dialog v-model="alumnoDialog" max-width="640" :persistent="busy.alumno">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="pt-5 pb-2 px-6">Gestionar alumnos</v-card-title>
        <v-tabs v-model="alumnoDialogTab" class="px-4">
          <v-tab value="add" prepend-icon="mdi-account-plus">Añadir alumno</v-tab>
          <v-tab value="import" prepend-icon="mdi-file-excel">Importar desde Excel</v-tab>
        </v-tabs>
        <v-card-text class="pt-5">
          <v-form v-if="alumnoDialogTab === 'add'" class="d-flex flex-column ga-3" :disabled="busy.alumno" @submit.prevent="addEstudiante">
            <div class="d-flex flex-column ga-2">
              <div class="text-subtitle-1 font-weight-medium">Buscar alumno registrado</div>
              <v-text-field
                v-model="institutionStudentSearch"
                label="Buscar por nombre o correo"
                prepend-inner-icon="mdi-magnify"
                clearable
                :loading="searchingInstitutionStudents"
                hint="Escribe al menos 2 caracteres."
                persistent-hint
              />
              <v-alert v-if="institutionSearchError" type="error" variant="tonal" density="compact">
                {{ institutionSearchError }}
              </v-alert>
              <v-list v-else-if="availableInstitutionStudents.length" density="compact" class="rounded-lg">
                <v-list-item
                  v-for="student in availableInstitutionStudents"
                  :key="student.id"
                  :title="studentDisplayName(student)"
                  :subtitle="student.is_active ? student.email : `${student.email} · Cuenta inactiva`"
                >
                  <template #append>
                    <v-btn
                      size="small"
                      color="primary"
                      variant="tonal"
                      :disabled="busy.alumno || !student.is_active"
                      @click.stop="enrollExistingStudent(student)"
                    >
                      Inscribir
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
              <div
                v-else-if="institutionStudentSearch.trim().length >= 2 && !searchingInstitutionStudents"
                class="text-body-small text-subtle"
              >
                No hay alumnos coincidentes disponibles para inscribir.
              </div>
            </div>

            <v-divider class="my-1" />
            <div class="text-subtitle-1 font-weight-medium">Registrar un alumno nuevo</div>
            <v-text-field v-model="newAlumno.email" label="Email" type="email" />
            <v-text-field v-model="newAlumno.first_name" label="Nombre" />
            <v-text-field v-model="newAlumno.last_name" label="Apellido" />
            <v-text-field v-model="newAlumno.phone" label="Teléfono (opcional)" type="tel" />
            <v-text-field
              v-model="newAlumno.password"
              label="Contraseña inicial (solo cuentas nuevas)"
              type="password"
              autocomplete="new-password"
              hint="8+ caracteres, mayúscula, minúscula, número y símbolo"
              persistent-hint
            />
            <div class="d-flex ga-2 justify-end mt-1">
              <v-btn variant="text" :disabled="busy.alumno" @click="alumnoDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="busy.alumno">Inscribir alumno</v-btn>
            </div>
          </v-form>

          <div v-else class="d-flex flex-column ga-3">
            <p class="text-body-medium text-subtle mb-0">Columnas: email, nombre, apellido, password (para cuentas nuevas), phone (opcional).</p>
            <v-file-input
              v-model="alumnosExcelFile"
              accept=".xlsx"
              label="Seleccionar archivo Excel"
              prepend-icon="mdi-file-excel-outline"
              show-size
            ></v-file-input>
            <div class="d-flex ga-2 justify-end">
              <v-btn variant="text" :disabled="busy.alumno" @click="alumnoDialog = false">Cancelar</v-btn>
              <v-btn color="primary" variant="flat" :loading="busy.alumno" @click="importAlumnosExcel">Importar alumnos</v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDelete" max-width="460">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="pt-5">¿Eliminar curso permanentemente?</v-card-title>
        <v-card-text class="text-subtle">
          Esta acción eliminará <strong>{{ curso.nombre }}</strong> y todas sus inscripciones. No se puede deshacer.
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-btn variant="text" @click="confirmDelete = false">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" variant="flat" :loading="busy.eliminar" @click="deleteCurso">Sí, eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from '../../composables/useToast'
import { firstFile, formatDate, formatDateTime, formatFileSize } from '../../utils/format'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import RegionState from '../../components/RegionState.vue'
import ListPagination from '../../components/ListPagination.vue'
import ImportSummary from '../../components/ImportSummary.vue'
import { importSummary } from '../../utils/importSummary'
import { normalizeSearch } from '../../utils/format'
import { usePagination } from '../../composables/usePagination'
import { useFormDraft, useGuardedDialog } from '../../composables/useUnsavedChanges'
import { useRequestSequence } from '../../composables/useRequestSequence'
import { confirmAction } from '../../composables/useConfirm'

const route = useRoute()
const router = useRouter()
const { notify, notifyError } = useCoordinadorToast()

const TABS = [
  { key: 'resumen', label: 'Resumen', icon: 'mdi-chart-line' },
  { key: 'alumnos', label: 'Alumnos', icon: 'mdi-account-multiple' },
  { key: 'agente', label: 'Agente IA', icon: 'mdi-robot' },
]

const MODOS = [
  { key: 'chat', label: 'Chat' },
  { key: 'practicar', label: 'Modo práctica' },
  { key: 'recursos', label: 'Recursos sintéticos' },
]

const KNOWLEDGE_STATUS = {
  completed: { label: 'Indexada', color: 'success' },
  processing: { label: 'Procesando', color: 'primary' },
  queued: { label: 'En cola', color: 'primary' },
  failed: { label: 'Con error', color: 'warning' },
  unknown: { label: 'Por confirmar', color: 'warning' },
  sin_material: { label: 'Sin material', color: 'default' },
}

const emptyAlumno = () => ({ email: '', first_name: '', last_name: '', phone: '', password: '' })

const cursoId = computed(() => route.params.id)
const curso = ref(null)
const tab = ref('resumen')
const editingDatos = ref(false)
const editCurso = reactive({ nombre: '', codigo: '', descripcion: '' })
const confirmDelete = ref(false)

const estudiantes = ref([])
const removingId = ref(null)
const showAlumnoDialog = ref(false)
const alumnoDialogTab = ref('add')
const newAlumno = reactive(emptyAlumno())
const alumnosExcelFile = ref(null)
const institutionStudentSearch = ref('')
const institutionStudents = ref([])
const searchingInstitutionStudents = ref(false)
const institutionSearchError = ref('')

const agente = reactive({ system_prompt: '', temperatura: 0.2, extender_conocimiento: false, modos_permitidos: [] })
const modos = reactive({ chat: true, practicar: true, recursos: true })
const conocimiento = ref(null)
const conocimientoFiles = ref([])
const retryingJobId = ref('')
const deletingDocument = ref('')

const loading = reactive({ curso: true, alumnos: true, agente: true, conocimiento: true })
const busy = reactive({ datos: false, estado: false, eliminar: false, alumno: false, agente: false, subida: false, vaciar: false })
const errors = reactive({ alumnos: '', agente: '', conocimiento: '' })
const requests = {
  curso: useRequestSequence(),
  alumnos: useRequestSequence(),
  alumnosInstitucion: useRequestSequence(),
  agente: useRequestSequence(),
  conocimiento: useRequestSequence(),
}
const cursoDraft = useFormDraft(() => editCurso, () => editingDatos.value, () => busy.datos || busy.estado || busy.eliminar)
const agenteDraft = useFormDraft(() => agente, () => !loading.agente && !errors.agente, () => busy.agente || busy.subida || busy.vaciar || Boolean(deletingDocument.value || retryingJobId.value))
const alumnoDraft = useFormDraft(() => newAlumno, () => showAlumnoDialog.value, () => busy.alumno || Boolean(removingId.value))
const alumnoDialog = useGuardedDialog(showAlumnoDialog, alumnoDraft, () => busy.alumno)
const importResult = ref(null)
const studentSearch = ref('')
const filteredStudents = computed(() => estudiantes.value.filter(student => normalizeSearch(`${student.full_name} ${student.email}`).includes(normalizeSearch(studentSearch.value))))
const studentPager = usePagination(filteredStudents)
watch(studentSearch, () => { studentPager.state.page = 1 })
const availableInstitutionStudents = computed(() => {
  const enrolledIds = new Set(estudiantes.value.map(student => String(student.user_id)))
  return institutionStudents.value.filter(student => !enrolledIds.has(String(student.id)))
})

watch(
  [showAlumnoDialog, alumnoDialogTab, institutionStudentSearch, cursoId],
  ([isOpen, activeTab, query], _previous, onCleanup) => {
    const current = requests.alumnosInstitucion()
    const normalizedQuery = query.trim()
    institutionStudents.value = []
    institutionSearchError.value = ''
    searchingInstitutionStudents.value = false

    if (!isOpen || activeTab !== 'add' || normalizedQuery.length < 2) return

    const timer = setTimeout(async () => {
      searchingInstitutionStudents.value = true
      try {
        const response = await coordinadorService.searchAlumnos(normalizedQuery)
        if (!current()) return
        institutionStudents.value = response.estudiantes || []
      } catch (error) {
        if (!current()) return
        institutionSearchError.value = 'No se pudo buscar alumnos en la institución.'
        notifyError(error, 'No se pudo buscar alumnos en la institución')
      } finally {
        if (current()) searchingInstitutionStudents.value = false
      }
    }, 300)

    onCleanup(() => clearTimeout(timer))
  },
)

const latestFailedJob = computed(() => conocimiento.value?.trabajos?.find((job) => ['failed', 'unknown'].includes(job.estado)) || null)
const knowledgeStatus = computed(() => {
  const estado = conocimiento.value?.resumen?.ultimo_estado || 'sin_material'
  return KNOWLEDGE_STATUS[estado] || { label: estado, color: 'default' }
})

/* ---------- Curso ---------- */
function syncEditCurso() {
  editCurso.nombre = curso.value?.nombre || ''
  editCurso.codigo = curso.value?.codigo || ''
  editCurso.descripcion = curso.value?.descripcion || ''
}

async function loadCurso() {
  const current = requests.curso()
  try {
    const r = await coordinadorService.getCurso(cursoId.value)
    if (!current()) return
    curso.value = r.curso || null
    if (!cursoDraft.dirty.value) { syncEditCurso(); cursoDraft.accept() }
  } catch (e) {
    if (!current()) return
    curso.value = null
    notifyError(e, 'No se pudo cargar el curso')
  } finally {
    if (current()) loading.curso = false
  }
}

async function cancelEditDatos() {
  if (busy.datos || !await cursoDraft.canClose()) return
  syncEditCurso()
  editingDatos.value = false
}

async function updateCurso() {
  if (busy.datos) return
  busy.datos = true
  try {
    const r = await coordinadorService.updateCurso(cursoId.value, { ...editCurso })
    curso.value = { ...curso.value, ...r.curso }
    cursoDraft.accept()
    editingDatos.value = false
    notify('Curso actualizado')
  } catch (e) {
    notifyError(e, 'No se pudo actualizar el curso')
  } finally {
    busy.datos = false
  }
}

async function toggleActivo() {
  if (busy.estado) return
  busy.estado = true
  try {
    const r = await coordinadorService.updateCurso(cursoId.value, { is_active: !curso.value.is_active })
    curso.value = { ...curso.value, ...r.curso }
    notify(curso.value.is_active ? 'Curso habilitado' : 'Curso inhabilitado')
  } catch (e) {
    notifyError(e, 'No se pudo actualizar el estado del curso')
  } finally {
    busy.estado = false
  }
}

async function deleteCurso() {
  if (busy.eliminar) return
  busy.eliminar = true
  try {
    await coordinadorService.deleteCurso(cursoId.value)
    editingDatos.value = false
    cursoDraft.accept()
    agenteDraft.accept()
    notify('Curso eliminado permanentemente')
    router.push('/coordinador/cursos')
  } catch (e) {
    notifyError(e, 'No se pudo eliminar el curso')
    confirmDelete.value = false
  } finally {
    busy.eliminar = false
  }
}

/* ---------- Alumnos ---------- */
async function loadEstudiantes() {
  const current = requests.alumnos()
  loading.alumnos = true
  errors.alumnos = ''
  try {
    const r = await coordinadorService.listEstudiantesCurso(cursoId.value)
    if (!current()) return
    estudiantes.value = r.estudiantes || []
  } catch (e) {
    if (!current()) return
    errors.alumnos = 'No se pudieron cargar los alumnos'
    notifyError(e, 'No se pudieron cargar los alumnos')
  } finally {
    if (current()) loading.alumnos = false
  }
}

const refreshAlumnos = () => Promise.all([loadEstudiantes(), loadCurso()])

function openAlumnoDialog() {
  alumnoDialogTab.value = 'add'
  institutionStudentSearch.value = ''
  showAlumnoDialog.value = true
}

function studentDisplayName(student) {
  return student.full_name || [student.first_name, student.last_name].filter(Boolean).join(' ') || student.email
}

async function enrollExistingStudent(student) {
  if (busy.alumno || !student.is_active) return
  busy.alumno = true
  try {
    await coordinadorService.addEstudianteCurso(cursoId.value, { email: student.email })
    await refreshAlumnos()
    notify('Alumno inscrito')
  } catch (error) {
    notifyError(error, 'No se pudo inscribir al alumno')
  } finally {
    busy.alumno = false
  }
}

async function addEstudiante() {
  if (busy.alumno) return
  if (!newAlumno.email.trim()) return notify('El email es requerido', true)
  busy.alumno = true
  try {
    await coordinadorService.addEstudianteCurso(cursoId.value, { ...newAlumno })
    Object.assign(newAlumno, emptyAlumno())
    showAlumnoDialog.value = false
    notify('Alumno inscrito')
    await refreshAlumnos()
  } catch (e) {
    notifyError(e, 'No se pudo inscribir al alumno')
  } finally {
    busy.alumno = false
  }
}

async function importAlumnosExcel() {
  if (busy.alumno) return
  const file = firstFile(alumnosExcelFile.value)
  if (!file) return notify('Selecciona un archivo Excel', true)

  busy.alumno = true
  try {
    const r = await coordinadorService.importEstudiantesCursoExcel(cursoId.value, file)
    importResult.value = importSummary(r)
    const skipped = r.skipped?.length || 0
    notify(
      `Importación: ${r.enrolled || 0} inscripciones, ${r.created || 0} cuentas nuevas${skipped ? `, ${skipped} filas omitidas` : ''}`,
      skipped > 0,
    )
    alumnosExcelFile.value = null
    showAlumnoDialog.value = false
    await refreshAlumnos()
  } catch (e) {
    notifyError(e, 'No se pudieron importar los alumnos')
  } finally {
    busy.alumno = false
  }
}

async function removeEstudiante(alumno) {
  if (removingId.value) return
  if (!await confirmAction({ title: 'Desinscribir alumno', message: `¿Desinscribir a ${alumno.full_name || alumno.email} de este curso? Su cuenta y el acceso a otros cursos se conservan.`, confirmText: 'Desinscribir', destructive: true })) return
  removingId.value = alumno.user_id
  try {
    await coordinadorService.removeEstudianteCurso(cursoId.value, alumno.user_id)
    notify('Alumno desinscrito')
    await refreshAlumnos()
  } catch (e) {
    notifyError(e, 'No se pudo desinscribir al alumno')
  } finally {
    removingId.value = null
  }
}

/* ---------- Agente IA ---------- */
function applyAgente(data) {
  Object.assign(agente, data || {})
  const activos = agente.modos_permitidos || []
  for (const m of MODOS) modos[m.key] = activos.includes(m.key)
}

async function loadAgente() {
  const current = requests.agente()
  loading.agente = true
  errors.agente = ''
  try {
    const r = await coordinadorService.getAgenteCurso(cursoId.value)
    if (!current()) return
    applyAgente(r.agente)
    agenteDraft.accept()
  } catch (e) {
    if (!current()) return
    errors.agente = 'No se pudo cargar la configuración del agente'
    notifyError(e, 'No se pudo cargar la configuración del agente')
  } finally {
    if (current()) loading.agente = false
  }
}

async function saveAgente() {
  if (busy.agente) return
  busy.agente = true
  try {
    const r = await coordinadorService.updateAgenteCurso(cursoId.value, {
      system_prompt: agente.system_prompt,
      temperatura: agente.temperatura,
      extender_conocimiento: agente.extender_conocimiento,
    })
    applyAgente(r.agente)
    agenteDraft.accept()
    notify('Configuración del agente guardada')
  } catch (e) {
    notifyError(e, 'No se pudo guardar la configuración del agente')
  } finally {
    busy.agente = false
  }
}

async function toggleModo(modo, value) {
  if (busy.agente) return
  busy.agente = true
  const previous = { ...modos }
  modos[modo] = value
  try {
    const r = await coordinadorService.updateAgenteCurso(cursoId.value, {
      modos_permitidos: MODOS.map((m) => m.key).filter((k) => modos[k]),
    })
    for (const option of MODOS) modos[option.key] = r.agente.modos_permitidos.includes(option.key)
  } catch (e) {
    Object.assign(modos, previous)
    notifyError(e, 'No se pudo actualizar la opción')
  } finally {
    busy.agente = false
  }
}

/* ---------- Base de conocimiento ---------- */
async function loadConocimiento() {
  const current = requests.conocimiento()
  loading.conocimiento = true
  errors.conocimiento = ''
  try {
    const result = await coordinadorService.getConocimientoCurso(cursoId.value)
    if (!current()) return
    conocimiento.value = result
  } catch (e) {
    if (!current()) return
    errors.conocimiento = 'No se pudo cargar el estado de la base de conocimiento'
    notifyError(e, 'No se pudo cargar el estado de la base de conocimiento')
  } finally {
    if (current()) loading.conocimiento = false
  }
}

async function retryConocimiento(job) {
  if (retryingJobId.value) return
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

async function removeDocumento(filename) {
  if (deletingDocument.value || busy.vaciar) return
  if (!await confirmAction({ title: 'Quitar documento', message: `¿Quitar "${filename}" del material disponible del curso?`, confirmText: 'Quitar documento', destructive: true })) return
  deletingDocument.value = filename
  try {
    await coordinadorService.operarConocimientoCurso(cursoId.value, { action: 'delete_document', archivo: filename })
    notify('Documento eliminado de la base de conocimiento')
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo eliminar el documento')
  } finally {
    deletingDocument.value = ''
  }
}

async function clearConocimiento() {
  if (busy.vaciar || deletingDocument.value) return
  if (!await confirmAction({ title: 'Vaciar base de conocimiento', message: 'Se eliminará todo el material indexado de este curso. No se puede deshacer.', confirmText: 'Vaciar base', destructive: true })) return
  busy.vaciar = true
  try {
    await coordinadorService.operarConocimientoCurso(cursoId.value, { action: 'clear_course' })
    notify('Base de conocimiento vaciada')
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo vaciar la base de conocimiento')
  } finally {
    busy.vaciar = false
  }
}

async function uploadConocimiento() {
  if (busy.subida) return
  const files = conocimientoFiles.value || []
  if (!files.length) return notify('Selecciona al menos un archivo PDF', true)
  if (files.length > 10) return notify('Selecciona como máximo 10 PDF por carga', true)
  if (files.some(file => file.size > 20 * 1024 * 1024)) return notify('Cada PDF debe pesar como máximo 20 MiB', true)
  const invalid = files.find((file) => !file.name.toLowerCase().endsWith('.pdf'))
  if (invalid) return notify(`"${invalid.name}" no es un PDF válido`, true)

  busy.subida = true
  try {
    await coordinadorService.uploadMaterialCurso(cursoId.value, files)
    notify('Material procesado correctamente')
    conocimientoFiles.value = []
    await loadConocimiento()
  } catch (e) {
    notifyError(e, 'No se pudo procesar el material')
  } finally {
    busy.subida = false
  }
}

/* ---------- Carga ---------- */
async function loadAll() {
  loading.curso = true
  await Promise.all([loadCurso(), loadEstudiantes(), loadAgente(), loadConocimiento()])
}

watch(cursoId, (id) => {
  if (!id) return
  tab.value = 'resumen'
  editingDatos.value = false
  estudiantes.value = []
  conocimiento.value = null
  loadAll()
}, { immediate: true })
</script>

<style scoped>
.detail-placeholder {
  min-height: 260px;
}

.detail-tabs {
  max-width: 100%;
  border-bottom: 1px solid var(--tutoria-border);
}

.alumnos-table {
  min-width: 660px;
}

.toggle-row {
  padding: 10px 12px;
  border: 1px solid var(--tutoria-border);
  border-radius: 12px;
  background: var(--tutoria-nav-active-bg);
}

.knowledge-box {
  padding: 12px;
  border: 1px solid var(--tutoria-border);
  border-radius: 12px;
  background: var(--tutoria-nav-active-bg);
}

.knowledge-documents {
  max-height: 220px;
  overflow: auto;
  background: var(--tutoria-nav-active-bg);
}

.knowledge-document {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 7px 2px;
}

.knowledge-document + .knowledge-document {
  border-top: 1px solid var(--tutoria-border);
}

.knowledge-document > div {
  flex: 1;
}
</style>
