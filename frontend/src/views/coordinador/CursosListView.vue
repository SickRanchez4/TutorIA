<template>
  <div class="d-flex flex-column ga-5">
    <PageHeader
      overline="Coordinación"
      title="Gestión de cursos"
      subtitle="Crea, activa y supervisa los cursos de tu institución."
    >
      <template #actions>
        <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" size="large" @click="openCreateDialog">
          Nuevo curso
        </v-btn>
      </template>
    </PageHeader>

    <v-row>
      <v-col cols="12" sm="6">
        <StatCard label="Cursos activos y en borrador" :value="cursos.length" icon="mdi-book-open-variant" />
      </v-col>
      <v-col cols="12" sm="6">
        <StatCard label="Alumnos inscritos" :value="totalAlumnos" icon="mdi-account-multiple" />
      </v-col>
    </v-row>

    <v-card class="surface-card" rounded="xl">
      <v-card-title class="d-flex align-center ga-3 py-4">
        <v-icon icon="mdi-book-multiple" color="primary"></v-icon>
        <h2 class="text-title-large font-weight-bold">Cursos disponibles</h2>
        <v-spacer></v-spacer>
        <v-chip v-if="cursos.length" color="primary" variant="tonal" size="small">{{ cursos.length }}</v-chip>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="pt-5">
        <v-row v-if="loading" role="status" aria-label="Cargando cursos">
          <v-col v-for="n in 3" :key="n" cols="12" sm="6" lg="4">
            <v-skeleton-loader type="article, actions" class="course-skeleton" />
          </v-col>
        </v-row>

        <div v-else-if="!cursos.length" class="empty-state">
          <v-icon icon="mdi-folder-open-outline" size="32"></v-icon>
          <p class="mb-0">No hay cursos creados aún. Usa «Nuevo curso» para comenzar.</p>
        </div>

        <v-row v-else>
          <v-col
            v-for="(curso, index) in cursos"
            :key="curso.id"
            cols="12"
            sm="6"
            lg="4"
            class="stagger-item"
            :style="{ animationDelay: `${index * 60}ms` }"
          >
            <v-card class="course-card h-100" rounded="xl" variant="flat">
              <v-card-text class="d-flex flex-column h-100">
                <div class="d-flex align-start justify-space-between mb-4 ga-2">
                  <div class="min-w-0">
                    <h3 class="text-body-large font-weight-bold mb-1">{{ curso.nombre }}</h3>
                    <p class="text-body-small text-subtle mb-0 font-mono">{{ curso.codigo || 'SIN-CÓDIGO' }}</p>
                  </div>
                  <v-chip size="x-small" variant="tonal" color="primary" class="flex-shrink-0">{{ curso.estudiantes_count || 0 }} alumnos</v-chip>
                </div>

                <div class="d-flex align-center justify-space-between flex-wrap ga-2 mt-auto">
                  <v-chip size="small" :color="curso.is_active ? 'success' : 'grey'" :variant="curso.is_active ? 'flat' : 'outlined'">
                    {{ curso.is_active ? 'Habilitado' : 'Inhabilitado' }}
                  </v-chip>
                  <div class="d-flex flex-wrap ga-2 course-card__actions">
                    <v-btn size="small" variant="outlined" :loading="togglingId === curso.id" @click="toggleActivo(curso)">
                      {{ curso.is_active ? 'Inhabilitar' : 'Habilitar' }}
                    </v-btn>
                    <v-btn size="small" color="primary" variant="flat" append-icon="mdi-arrow-right" :to="`/coordinador/cursos/${curso.id}`">
                      Ajustes
                    </v-btn>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showCreateDialog" max-width="620">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="pt-5 pb-2 px-6">Nuevo curso</v-card-title>
        <v-tabs v-model="dialogTab" class="px-4" density="comfortable">
          <v-tab value="add" prepend-icon="mdi-plus-circle">Añadir curso</v-tab>
          <v-tab value="import" prepend-icon="mdi-file-excel">Importar desde Excel</v-tab>
        </v-tabs>

        <v-card-text class="pt-5">
          <v-form v-if="dialogTab === 'add'" class="d-flex flex-column ga-3" @submit.prevent="createCurso">
            <v-text-field v-model="newCurso.nombre" label="Nombre del curso" />
            <v-text-field v-model="newCurso.codigo" label="Código único (MAT-101)" class="font-mono" />
            <v-textarea v-model="newCurso.descripcion" label="Descripción (opcional)" rows="3" />
            <div class="d-flex ga-2 justify-end">
              <v-btn variant="text" @click="showCreateDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="saving">Crear curso</v-btn>
            </div>
          </v-form>

          <div v-else class="d-flex flex-column ga-3">
            <p class="text-body-medium text-subtle mb-0">Columnas requeridas: nombre, codigo. Opcional: descripcion.</p>
            <v-file-input
              v-model="excelFile"
              accept=".xlsx,.xls"
              prepend-icon="mdi-file-excel-outline"
              label="Seleccionar archivo Excel"
              show-size
            ></v-file-input>
            <div class="d-flex ga-2 justify-end">
              <v-btn variant="text" @click="showCreateDialog = false">Cancelar</v-btn>
              <v-btn color="primary" variant="flat" :loading="saving" @click="importCursosExcel">Importar cursos</v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { coordinadorService } from '../../services'
import { coordinadorToast } from '../../composables/useToast'
import { firstFile } from '../../utils/format'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

const { notify, notifyError } = coordinadorToast

const cursos = ref([])
const loading = ref(true)
const saving = ref(false)
const togglingId = ref(null)
const showCreateDialog = ref(false)
const dialogTab = ref('add')
const newCurso = reactive({ nombre: '', codigo: '', descripcion: '' })
const excelFile = ref(null)

const totalAlumnos = computed(() => cursos.value.reduce((sum, c) => sum + (c.estudiantes_count || 0), 0))

function openCreateDialog() {
  dialogTab.value = 'add'
  showCreateDialog.value = true
}

async function loadCursos() {
  loading.value = true
  try {
    const r = await coordinadorService.listCursos()
    cursos.value = r.cursos || []
  } catch (e) {
    notifyError(e, 'No se pudieron cargar los cursos')
  } finally {
    loading.value = false
  }
}

async function createCurso() {
  const nombre = newCurso.nombre.trim()
  const codigo = newCurso.codigo.trim()
  if (!nombre || !codigo) return notify('Nombre y código del curso son requeridos', true)

  saving.value = true
  try {
    await coordinadorService.createCurso({ nombre, codigo, descripcion: newCurso.descripcion })
    Object.assign(newCurso, { nombre: '', codigo: '', descripcion: '' })
    showCreateDialog.value = false
    notify('Curso creado')
    await loadCursos()
  } catch (e) {
    notifyError(e, 'No se pudo crear el curso')
  } finally {
    saving.value = false
  }
}

async function importCursosExcel() {
  const file = firstFile(excelFile.value)
  if (!file) return notify('Selecciona un archivo Excel', true)

  saving.value = true
  try {
    const r = await coordinadorService.importCursosExcel(file)
    const skipped = r.skipped?.length || 0
    notify(`Cursos importados: ${r.created || 0}${skipped ? ` · omitidos: ${skipped}` : ''}`, skipped > 0)
    excelFile.value = null
    showCreateDialog.value = false
    await loadCursos()
  } catch (e) {
    notifyError(e, 'No se pudieron importar los cursos')
  } finally {
    saving.value = false
  }
}

async function toggleActivo(curso) {
  togglingId.value = curso.id
  try {
    await coordinadorService.updateCurso(curso.id, { is_active: !curso.is_active })
    notify(curso.is_active ? 'Curso inhabilitado' : 'Curso habilitado')
    await loadCursos()
  } catch (e) {
    notifyError(e, 'No se pudo actualizar el estado del curso')
  } finally {
    togglingId.value = null
  }
}

onMounted(loadCursos)
</script>

<style scoped>
.course-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.035) !important;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.course-card:hover {
  border-color: var(--tutoria-border-strong);
  transform: translateY(-3px);
}

.course-skeleton {
  overflow: hidden;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.12);
  border-radius: 14px;
  background: transparent;
}

.stagger-item {
  animation: item-in 0.38s ease-out both;
}

@keyframes item-in {
  from { opacity: 0; transform: translateY(10px); }
}

@media (max-width: 599px) {
  .course-card__actions {
    width: 100%;
  }

  .course-card__actions :deep(.v-btn) {
    flex: 1 1 120px;
  }
}
</style>
