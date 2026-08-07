<template>
  <div class="coord-cursos-view">
    <v-card class="coord-hero mb-6" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5">
        <div>
          <p class="text-overline mb-1 coord-overline">Coordinación</p>
          <h2 class="text-h5 font-weight-bold mb-1">Gestión de cursos</h2>
          <p class="mb-0 coord-subtext">Crea, activa y supervisa cursos en una experiencia unificada.</p>
        </div>
        <div class="d-flex align-center ga-3">
          <v-btn
            @click="showCreateModal = true"
            color="primary"
            prepend-icon="mdi-plus"
            size="large"
            rounded="lg"
            class="coord-primary-btn"
          >
            Nuevo curso
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Modal con 2 tabs: Añadir curso / Importar desde Excel -->
    <v-dialog v-model="showCreateModal" max-width="620">
      <v-card class="coord-dialog-card" rounded="xl" variant="flat">
        <v-card-title class="pt-5 pb-2 px-6">Nuevo curso</v-card-title>
        <v-tabs v-model="activeTab" class="px-4" color="primary" density="comfortable">
          <v-tab value="add" prepend-icon="mdi-plus-circle">Añadir curso</v-tab>
          <v-tab value="import" prepend-icon="mdi-file-excel">Importar desde Excel</v-tab>
        </v-tabs>
        
        <v-card-text class="pt-5">
          <!-- Tab 1: Añadir curso -->
          <div v-show="activeTab === 'add'" class="space-y-4">
            <form @submit.prevent="createCursoAndClose" class="space-y-4">
              <v-text-field
                v-model="newCurso.nombre"
                label="Nombre del curso"
                variant="solo-filled"
                density="compact"
                required
              />
              <v-text-field
                v-model="newCurso.codigo"
                label="Código único (MAT-101)"
                variant="solo-filled"
                density="compact"
                class="font-mono uppercase"
                required
              />
              <v-textarea
                v-model="newCurso.descripcion"
                label="Descripción (opcional)"
                variant="solo-filled"
                density="compact"
                rows="3"
              />
              <div class="d-flex ga-2 justify-end">
                <v-btn @click="showCreateModal = false" variant="text" rounded="lg">Cancelar</v-btn>
                <v-btn type="submit" color="primary" rounded="lg" class="coord-primary-btn">Crear curso</v-btn>
              </div>
            </form>
          </div>
          
          <!-- Tab 2: Importar desde Excel -->
          <div v-show="activeTab === 'import'" class="space-y-4">
            <p class="text-body-2 coord-subtext">Columnas requeridas: nombre, codigo</p>
            <v-file-input
              v-model="cursosExcelFiles"
              accept=".xlsx,.xls"
              variant="solo-filled"
              density="comfortable"
              prepend-icon="mdi-file-excel-outline"
              label="Seleccionar archivo Excel"
              show-size
              @change="onExcelFileSelected"
            ></v-file-input>
            <div class="d-flex ga-2 justify-end">
              <v-btn @click="showCreateModal = false" variant="text" rounded="lg">Cancelar</v-btn>
              <v-btn @click="importCursosExcelAndClose" color="primary" rounded="lg" class="coord-primary-btn">Importar cursos</v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Resumen y stats -->
    <v-row class="mb-2">
      <v-col cols="12" md="6">
        <v-card class="coord-stat-card" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption coord-subtext mb-1">Cursos activos y en borrador</p>
              <p class="text-h4 font-weight-black mb-0">{{ cursos.length }}</p>
            </div>
            <v-icon icon="mdi-book-open-variant" size="34" color="primary"></v-icon>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="coord-stat-card" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption coord-subtext mb-1">Alumnos inscritos</p>
              <p class="text-h4 font-weight-black mb-0">{{ totalAlumnos }}</p>
            </div>
            <v-icon icon="mdi-account-multiple" size="34" color="primary"></v-icon>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Cursos disponibles -->
    <v-card class="coord-surface-card" rounded="xl" variant="flat">
      <v-card-title class="d-flex align-center ga-3 py-4">
        <v-icon icon="mdi-book-multiple" color="primary"></v-icon>
        <span class="text-h6 font-weight-bold">Cursos disponibles</span>
        <v-spacer></v-spacer>
        <v-chip v-if="cursos.length" color="primary" variant="tonal" size="small">{{ cursos.length }}</v-chip>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="pt-5">
        <div v-if="loading" class="py-2">
          <v-row>
            <v-col v-for="n in 3" :key="n" cols="12" md="6" lg="4">
              <v-skeleton-loader type="article, actions" class="coord-skeleton" />
            </v-col>
          </v-row>
          <p class="text-body-2 coord-subtext mt-2">Cargando cursos...</p>
        </div>

        <div v-else-if="!cursos.length" class="text-center py-10 coord-subtext">
          <v-icon icon="mdi-folder-open-outline" size="32" class="mb-2"></v-icon>
          <p class="text-body-2 mb-0">No hay cursos creados aún. Usa "Nuevo curso" para comenzar.</p>
        </div>

        <v-row v-else>
          <v-col
            v-for="(curso, index) in cursos"
            :key="curso.id"
            cols="12"
            md="6"
            lg="4"
            class="stagger-item"
            :style="{ animationDelay: `${index * 80}ms` }"
          >
            <v-hover v-slot="{ isHovering, props }">
              <v-card
                v-bind="props"
                rounded="xl"
                class="coord-course-card"
                :class="{ 'coord-course-card--hover': isHovering }"
                variant="flat"
              >
                <v-card-text>
                  <div class="d-flex align-start justify-space-between mb-4 ga-2">
                    <div>
                      <h5 class="text-subtitle-1 font-weight-bold mb-1">{{ curso.nombre }}</h5>
                      <p class="text-caption mb-0 coord-subtext font-mono">{{ curso.codigo || 'SIN-CODIGO' }}</p>
                    </div>
                    <v-chip size="x-small" variant="tonal" color="primary">{{ curso.estudiantes_count || 0 }} alumnos</v-chip>
                  </div>

                  <div class="d-flex align-center justify-space-between flex-wrap ga-2">
                    <v-chip
                      size="small"
                      :color="curso.is_active ? 'success' : 'grey'
                      "
                      :variant="curso.is_active ? 'flat' : 'outlined'"
                    >
                      {{ curso.is_active ? 'Habilitado' : 'Inhabilitado' }}
                    </v-chip>

                    <div class="d-flex ga-2">
                      <v-btn
                        @click="toggleActivo(curso)"
                        size="small"
                        variant="outlined"
                        rounded="lg"
                        class="coord-outline-btn"
                      >
                        {{ curso.is_active ? 'Inhabilitar' : 'Habilitar' }}
                      </v-btn>
                      <v-btn
                        @click="goToCurso(curso.id)"
                        size="small"
                        color="primary"
                        rounded="lg"
                        class="coord-primary-btn"
                        append-icon="mdi-arrow-right"
                      >
                        Ajustes
                      </v-btn>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-hover>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from './useCoordinadorToast'

const { notify, notifyError } = useCoordinadorToast()
const router = useRouter()

const cursos = ref([])
const loading = ref(true)
const newCurso = ref({ nombre: '', codigo: '', descripcion: '' })
const cursosExcelFiles = ref([])
const showCreateModal = ref(false)
const activeTab = ref('add')

function goToCurso(cursoId) {
  router.push(`/coordinador/cursos/${cursoId}`)
}

const totalAlumnos = computed(() => cursos.value.reduce((sum, c) => sum + (c.estudiantes_count || 0), 0))

async function loadCursos() {
  loading.value = true
  try {
    const r = await coordinadorService.listCursos()
    cursos.value = r.cursos || []
  } catch (e) {
    notifyError(e, 'No se pudo cargar cursos')
  } finally {
    loading.value = false
  }
}

async function createCurso() {
  if (!newCurso.value.nombre.trim() || !newCurso.value.codigo.trim()) {
    return notify('Nombre y código del curso son requeridos', true)
  }
  try {
    await coordinadorService.createCurso({
      nombre: newCurso.value.nombre,
      codigo: newCurso.value.codigo,
      descripcion: newCurso.value.descripcion,
    })
    newCurso.value = { nombre: '', codigo: '', descripcion: '' }
    notify('Curso creado')
    await loadCursos()
  } catch (e) {
    notifyError(e, 'No se pudo crear curso')
  }
}

async function createCursoAndClose() {
  await createCurso()
  if (newCurso.value.nombre === '') {
    showCreateModal.value = false
  }
}

async function toggleActivo(curso) {
  try {
    await coordinadorService.updateCurso(curso.id, { is_active: !curso.is_active })
    notify(curso.is_active ? 'Curso inhabilitado' : 'Curso habilitado')
    await loadCursos()
  } catch (e) {
    notifyError(e, 'No se pudo actualizar el estado del curso')
  }
}

async function importCursosExcel() {
  const file = cursosExcelFiles.value?.[0]
  if (!file) {
    notify('Selecciona un archivo Excel', true)
    return false
  }
  try {
    const r = await coordinadorService.importCursosExcel(file)
    notify(`Cursos importados: ${r.created}`)
    cursosExcelFiles.value = []
    await loadCursos()
    return true
  } catch (e) {
    notifyError(e, 'No se pudo importar cursos')
    return false
  }
}

async function importCursosExcelAndClose() {
  const ok = await importCursosExcel()
  if (!ok) return
  showCreateModal.value = false
}

function onExcelFileSelected() {
  // Solo se dispara cuando cambia el file input
}

onMounted(loadCursos)
</script>

<style scoped>
.coord-cursos-view {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.coord-hero {
  border-radius: 16px;
  border: 1px solid rgba(124, 197, 118, 0.2);
  background:
    radial-gradient(circle at 15% 20%, rgba(124, 197, 118, 0.16), rgba(124, 197, 118, 0) 48%),
    linear-gradient(145deg, #242429 0%, #2c2d33 100%);
  box-shadow: 0 18px 28px rgba(0, 0, 0, 0.35);
}

.coord-overline {
  color: #8fd189;
  letter-spacing: 0.08em;
}

.coord-subtext {
  opacity: 0.72;
}

.coord-live-chip {
  border-radius: 999px;
  border: 1px solid rgba(124, 197, 118, 0.2);
  background: rgba(124, 197, 118, 0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7cc576;
  box-shadow: 0 0 0 rgba(124, 197, 118, 0.55);
  animation: status-pulse 1.8s ease-out infinite;
}

.coord-primary-btn {
  color: #ffffff !important;
  background: linear-gradient(140deg, #7cc576 0%, #609f5b 100%) !important;
  font-weight: 700;
  box-shadow: 0 0 20px rgba(124, 197, 118, 0.25);
}

.coord-primary-btn:hover {
  box-shadow: 0 0 26px rgba(124, 197, 118, 0.34);
}

.coord-outline-btn {
  border-color: rgba(124, 197, 118, 0.35);
}

.coord-dialog-card {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background: linear-gradient(145deg, #25262b 0%, #2c2d33 100%);
}

.coord-stat-card,
.coord-surface-card,
.coord-course-card {
  border: 1px solid rgba(124, 197, 118, 0.2);
  background: linear-gradient(140deg, #25262c 0%, #2f3037 100%);
  backdrop-filter: blur(8px);
}

.coord-stat-card {
  min-height: 120px;
}

.coord-course-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.coord-course-card--hover {
  transform: translateY(-4px);
  box-shadow: 0 0 22px rgba(124, 197, 118, 0.2);
  border-color: rgba(124, 197, 118, 0.36);
}

.coord-skeleton {
  border-radius: 14px;
  border: 1px solid rgba(124, 197, 118, 0.12);
  overflow: hidden;
}

.stagger-item {
  opacity: 0;
  transform: translateY(10px);
  animation: item-in 0.38s ease-out forwards;
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

@keyframes item-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
