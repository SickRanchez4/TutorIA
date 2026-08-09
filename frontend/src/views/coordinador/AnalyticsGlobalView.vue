<template>
  <section class="analytics-page">
    <v-card class="analytics-hero mb-5" rounded="xl" variant="flat">
      <v-card-text class="pa-5 pa-md-6">
        <div class="d-flex align-start justify-space-between flex-wrap ga-4">
          <div>
            <p class="analytics-eyebrow mb-2">INTELIGENCIA ACADÉMICA</p>
            <h1 class="text-h5 font-weight-black mb-2">Uso del asistente por curso.</h1>
            <p class="analytics-hero-copy mb-0">Actividad, participación y respaldo documental dentro del período seleccionado.</p>
          </div>
          <div class="analytics-period-badge"><v-icon icon="mdi-calendar-range-outline" size="17"></v-icon>{{ periodLabel }}</div>
        </div>
      </v-card-text>
    </v-card>

    <v-card class="analytics-filters mb-5" rounded="xl" variant="flat">
      <v-card-text class="pa-4 pa-md-5">
        <div class="d-flex align-center justify-space-between flex-wrap ga-3 mb-4">
          <div>
            <p class="text-subtitle-2 font-weight-black mb-0">Explorar periodo</p>
            <p class="text-caption text-medium-emphasis mb-0">Ajusta la ventana y enfoca el análisis.</p>
          </div>
          <div class="analytics-report-logo"><v-icon icon="mdi-chart-box-outline" size="17"></v-icon><span>Reporte de uso</span></div>
        </div>
        <div class="d-flex align-center flex-wrap ga-3">
          <v-btn-toggle v-model="days" mandatory color="primary" density="compact" class="analytics-range-toggle" @update:model-value="load">
            <v-btn :value="7">7 días</v-btn>
            <v-btn :value="30">30 días</v-btn>
            <v-btn :value="90">90 días</v-btn>
            <v-btn :value="0">Personalizado</v-btn>
          </v-btn-toggle>
          <div v-if="days === 0" class="d-flex flex-wrap ga-2">
            <v-text-field v-model="customDateRange.start" type="date" label="Desde" density="compact" hide-details class="analytics-date-field" @change="useCustomRange" />
            <v-text-field v-model="customDateRange.end" type="date" label="Hasta" density="compact" hide-details class="analytics-date-field" @change="useCustomRange" />
          </div>
        </div>
        <div class="d-flex align-center flex-wrap ga-2 mt-4">
          <span class="analytics-filter-label">Tipo de interacción</span>
          <v-btn v-for="type in operationTypes" :key="type.value" size="small" :variant="tipoFilter === type.value ? 'flat' : 'tonal'" :color="tipoFilter === type.value ? 'primary' : 'default'" class="analytics-type-filter" @click="selectType(type.value)">
            <v-icon :icon="type.icon" size="15" class="mr-1"></v-icon>{{ type.label }}
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <div v-if="loading" class="analytics-loading">
      <v-progress-circular indeterminate color="primary" size="44" width="4" />
      <p class="font-weight-bold mb-1">Construyendo tu reporte</p>
      <p class="text-caption text-medium-emphasis mb-0">Analizando la actividad académica del periodo.</p>
    </div>

    <template v-else-if="analytics">
      <v-row class="mb-2">
        <v-col cols="12" sm="6" lg="3">
          <v-card class="analytics-kpi-card" rounded="xl">
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between align-start">
                <div><p class="analytics-kpi-label mb-1">Consultas al asistente</p><p class="text-h5 font-weight-black mb-1">{{ formatNumber(analytics.total_operaciones) }}</p><p class="analytics-kpi-delta mb-0" :class="deltaClass(analytics.comparativa_periodo_anterior?.operaciones_delta_pct)">{{ deltaLabel(analytics.comparativa_periodo_anterior?.operaciones_delta_pct) }}</p></div>
                <div class="analytics-kpi-icon"><v-icon icon="mdi-message-processing-outline" size="21"></v-icon></div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-card class="analytics-kpi-card" rounded="xl">
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between align-start">
                <div><p class="analytics-kpi-label mb-1">Estudiantes activos</p><p class="text-h5 font-weight-black mb-1">{{ formatNumber(analytics.alumnos_activos) }}</p><p class="analytics-kpi-caption mb-0">de {{ formatNumber(analytics.participacion?.estudiantes_habilitados) }} habilitados</p></div>
                <div class="analytics-kpi-icon"><v-icon icon="mdi-account-group-outline" size="21"></v-icon></div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-card class="analytics-kpi-card" rounded="xl">
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between align-start">
                <div><p class="analytics-kpi-label mb-1">Respuestas con fuentes</p><p class="text-h5 font-weight-black mb-1">{{ percentLabel(analytics.cobertura_documental?.porcentaje) }}</p><p class="analytics-kpi-caption mb-0">{{ analytics.cobertura_documental?.respuestas_con_fuentes || 0 }} de {{ analytics.cobertura_documental?.respuestas_totales || 0 }} respuestas</p></div>
                <div class="analytics-kpi-icon"><v-icon icon="mdi-file-check-outline" size="21"></v-icon></div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-card class="analytics-kpi-card" rounded="xl">
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between align-start">
                <div><p class="analytics-kpi-label mb-1">Costo estimado</p><p class="text-h5 font-weight-black mb-1">{{ currency(analytics.total_cost_usd) }}</p><p class="analytics-kpi-caption mb-0">{{ currency(analytics.costo_promedio_operacion) }} por consulta</p></div>
                <div class="analytics-kpi-icon"><v-icon icon="mdi-chart-line-variant" size="21"></v-icon></div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>



      <v-card class="analytics-report-section mb-5" rounded="xl">
        <v-card-text class="pa-5">
          <div class="d-flex align-start justify-space-between flex-wrap ga-3 mb-4">
            <div><p class="analytics-eyebrow mb-1">ACTIVIDAD POR CURSO</p><h2 class="text-subtitle-1 font-weight-black mb-1">¿En qué cursos se está utilizando más el asistente?</h2><p class="text-caption text-medium-emphasis mb-0">Las consultas se atribuyen solo cuando pertenecen a un curso válido.</p></div>
            <v-chip size="small" color="primary" variant="tonal">{{ analytics.breakdown_curso?.length || 0 }} cursos con actividad</v-chip>
          </div>
          <div v-if="!analytics.breakdown_curso?.length" class="analytics-empty-report"><v-icon icon="mdi-folder-chart-outline" size="28"></v-icon><span>Este periodo aún no tiene actividad por curso.</span></div>
          <div v-else class="analytics-course-grid">
            <button v-for="course in analytics.breakdown_curso" :key="course.curso_id ?? 'sin_curso'" type="button" class="analytics-course-card" :class="{ 'analytics-course-card--selected': selectedCourseId === course.curso_id }" @click="selectedCourseId = course.curso_id">
              <div class="d-flex justify-space-between align-start ga-2"><p class="font-weight-black text-body-2 mb-1 text-left">{{ course.curso_nombre }}</p><span class="analytics-course-percent">{{ course.porcentaje_actividad }}%</span></div>
              <p class="text-caption text-medium-emphasis text-left mb-3">{{ formatNumber(course.count) }} consultas · {{ formatNumber(course.tokens) }} tokens</p>
              <v-progress-linear :model-value="course.porcentaje_actividad" color="primary" height="6" rounded></v-progress-linear>
            </button>
          </div>
          <div v-if="selectedCourse" class="analytics-course-detail mt-4">
            <div><p class="text-caption text-medium-emphasis mb-0">Curso seleccionado</p><p class="font-weight-black mb-0">{{ selectedCourse.curso_nombre }} · {{ currency(selectedCourse.cost_usd) }} de inversión estimada</p></div>
            <router-link v-if="selectedCourse.curso_id" :to="`/coordinador/cursos/${selectedCourse.curso_id}`"><v-btn color="primary" variant="tonal" size="small" append-icon="mdi-arrow-right">Ver curso</v-btn></router-link>
          </div>
        </v-card-text>
      </v-card>

      <v-row>
        <v-col cols="12" md="6">
          <v-card class="analytics-surface h-100" rounded="xl">
            <v-card-text class="pa-5">
              <div class="d-flex align-center ga-2 mb-4">
                <div class="analytics-section-icon"><v-icon icon="mdi-shape-outline" size="18"></v-icon></div>
                <div><p class="text-subtitle-1 font-weight-black mb-0">Uso por enfoque</p><p class="text-caption text-medium-emphasis mb-0">Cómo usan los estudiantes el asistente.</p></div>
              </div>
              <div v-if="operationBreakdown.length" class="d-flex flex-column ga-3">
                <div v-for="item in operationBreakdown" :key="item.key">
                  <div class="d-flex justify-space-between text-body-2 mb-1"><span>{{ operationLabel(item.key) }}</span><strong>{{ formatNumber(item.count) }}</strong></div>
                  <v-progress-linear :model-value="item.percentage" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-caption text-medium-emphasis text-right mb-0 mt-1">{{ item.percentage }}% de interacciones</p>
                </div>
              </div>
              <div v-else class="analytics-empty-report">Sin datos de interacción.</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card class="analytics-surface h-100" rounded="xl">
            <v-card-text class="pa-5">
              <div class="d-flex align-center ga-2 mb-4">
                <div class="analytics-section-icon"><v-icon icon="mdi-gauge" size="18"></v-icon></div>
                <div><p class="text-subtitle-1 font-weight-black mb-0">Indicadores de uso</p><p class="text-caption text-medium-emphasis mb-0">Se calculan con la actividad del período seleccionado.</p></div>
              </div>
              <div class="d-flex flex-column ga-4">
                <div class="analytics-health-item">
                  <div class="d-flex justify-space-between mb-1"><span>Participación</span><strong>{{ percentLabel(analytics.participacion?.porcentaje) }}</strong></div>
                  <v-progress-linear :model-value="analytics.participacion?.porcentaje || 0" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-caption text-medium-emphasis mb-0 mt-1">{{ analytics.participacion?.estudiantes_activos || 0 }} de {{ analytics.participacion?.estudiantes_habilitados || 0 }} estudiantes habilitados usaron el asistente.</p>
                </div>
                <div class="analytics-health-item">
                  <div class="d-flex justify-space-between mb-1"><span>Uso de chat con material</span><strong>{{ percentLabel(chatWithMaterial.porcentaje) }}</strong></div>
                  <v-progress-linear :model-value="chatWithMaterial.porcentaje || 0" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-caption text-medium-emphasis mb-0 mt-1">{{ chatWithMaterial.message }}</p>
                </div>
                <div class="analytics-health-item">
                  <div class="d-flex justify-space-between mb-1"><span>Respaldo documental</span><strong>{{ percentLabel(analytics.cobertura_documental?.porcentaje) }}</strong></div>
                  <v-progress-linear :model-value="analytics.cobertura_documental?.porcentaje || 0" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-caption text-medium-emphasis mb-0 mt-1">{{ sourceMessage }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from './useCoordinadorToast'

const { notifyError } = useCoordinadorToast()

const days = ref(30)
const analytics = ref(null)
const loading = ref(false)
const customDateRange = ref({ start: '', end: '' })
const tipoFilter = ref('')
const selectedCourseId = ref(null)

const operationTypes = [
  { value: '', label: 'Todo', icon: 'mdi-view-grid-outline' },
  { value: 'chat_rag', label: 'Chat', icon: 'mdi-chat-processing-outline' },
  { value: 'practicar', label: 'Práctica', icon: 'mdi-head-question-outline' },
  { value: 'resumen_sintetico', label: 'Recursos', icon: 'mdi-file-document-outline' },
]

const periodLabel = computed(() => {
  if (days.value > 0) return `Últimos ${days.value} días`
  if (customDateRange.value.start && customDateRange.value.end) return `${formatShortDate(customDateRange.value.start)} — ${formatShortDate(customDateRange.value.end)}`
  return 'Rango personalizado'
})

const operationBreakdown = computed(() => {
  const breakdown = analytics.value?.breakdown_tipo_operacion || {}
  const total = analytics.value?.total_operaciones || 0
  return Object.entries(breakdown)
    .map(([key, item]) => ({ key, count: item.count || 0, percentage: total ? Math.round((item.count / total) * 100) : 0 }))
    .sort((a, b) => b.count - a.count)
})

const selectedCourse = computed(() => (analytics.value?.breakdown_curso || []).find((course) => course.curso_id === selectedCourseId.value) || null)

const chatWithMaterial = computed(() => {
  const chatCount = Number(analytics.value?.breakdown_tipo_operacion?.chat_rag?.count || 0)
  const total = Number(analytics.value?.total_operaciones || 0)
  if (!total) {
    return {
      porcentaje: null,
      message: 'Aún no hay interacciones para calcular este indicador.',
    }
  }
  const porcentaje = Math.round((chatCount / total) * 100)
  return {
    porcentaje,
    message: `${chatCount} de ${total} interacciones usaron chat con material de curso.`,
  }
})

const sourceMessage = computed(() => {
  const coverage = analytics.value?.cobertura_documental
  if (coverage?.porcentaje == null) return 'Aún no hay respuestas del asistente para medir citas de documentos.'
  return `${coverage.respuestas_con_fuentes} de ${coverage.respuestas_totales} respuestas incluyeron citas del material indexado.`
})

function setDefaultDateRange() {
  const today = new Date()
  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - days.value)
  
  customDateRange.value.start = startDate.toISOString().split('T')[0]
  customDateRange.value.end = today.toISOString().split('T')[0]
}

function useCustomRange() {
  days.value = 0
  if (customDateRange.value.start && customDateRange.value.end) load()
}

function selectType(type) {
  tipoFilter.value = type
  load()
}

async function load() {
  loading.value = true
  try {
    if (days.value > 0) {
      setDefaultDateRange()
      analytics.value = await coordinadorService.getConsumo(days.value, { tipo: tipoFilter.value })
    } else if (customDateRange.value.start && customDateRange.value.end) {
      analytics.value = await coordinadorService.getConsumo(null, {
        start_date: customDateRange.value.start,
        end_date: customDateRange.value.end,
        tipo: tipoFilter.value,
      })
    }
    selectedCourseId.value = null
  } catch (e) {
    notifyError(e, 'No se pudo cargar analytics')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  setDefaultDateRange()
  load()
})

function formatNumber(value) {
  return Number(value || 0).toLocaleString('es-BO')
}

function currency(value) {
  return `$${Number(value || 0).toFixed(4)}`
}

function percentLabel(value) {
  return value == null ? '—' : `${Number(value).toFixed(0)}%`
}

function deltaLabel(value) {
  if (value == null) return 'Sin comparación previa'
  return `${value >= 0 ? '+' : ''}${value}% vs. periodo anterior`
}

function deltaClass(value) {
  return value == null ? '' : value >= 0 ? 'analytics-kpi-delta--up' : 'analytics-kpi-delta--down'
}

function operationLabel(value) {
  return ({ chat_rag: 'Chat con material', practicar: 'Modo práctica', resumen_sintetico: 'Recurso sintético' })[value] || value
}

function formatShortDate(value) {
  const date = new Date(`${value}T00:00:00`)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('es-BO', { day: '2-digit', month: 'short' })
}

</script>

<style scoped>
.analytics-page {
  --analytics-green: #7cc576;
  --analytics-bright: #a3e99c;
}

.analytics-hero,
.analytics-filters,
.analytics-surface,
.analytics-report-section,
.analytics-kpi-card {
  border: 1px solid rgba(124, 197, 118, 0.19) !important;
  background: linear-gradient(145deg, rgba(47, 50, 58, 0.98), rgba(37, 40, 47, 0.98)) !important;
  box-shadow: 0 14px 27px rgba(0, 0, 0, 0.2);
}

.analytics-hero {
  overflow: hidden;
  background:
    radial-gradient(circle at 11% 30%, rgba(124, 197, 118, 0.23), transparent 38%),
    radial-gradient(circle at 88% 0%, rgba(124, 197, 118, 0.1), transparent 29%),
    linear-gradient(145deg, #343941, #454a55) !important;
}

.analytics-eyebrow {
  color: var(--analytics-bright);
  font-size: 0.66rem;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.analytics-hero-copy { color: rgba(237, 244, 237, 0.67); }

.analytics-period-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 12px;
  border: 1px solid rgba(124, 197, 118, 0.27);
  border-radius: 999px;
  color: var(--analytics-bright);
  font-size: 0.75rem;
  font-weight: 750;
  background: rgba(124, 197, 118, 0.1);
}

.analytics-report-logo {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border: 1px solid rgba(124, 197, 118, 0.22);
  border-radius: 999px;
  color: rgba(235, 243, 235, 0.82);
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(124, 197, 118, 0.08);
}

.analytics-range-toggle :deep(.v-btn) { font-size: 0.75rem; font-weight: 750; text-transform: none; }
.analytics-date-field { width: 152px; }
.analytics-filter-label { color: rgba(236, 243, 236, 0.58); font-size: 0.73rem; font-weight: 750; }
.analytics-type-filter { font-weight: 700; text-transform: none; }

.analytics-loading {
  display: flex;
  min-height: 360px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(237, 244, 237, 0.75);
}

.analytics-kpi-card {
  min-height: 142px;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
}

.analytics-kpi-card:hover {
  border-color: rgba(124, 197, 118, 0.43) !important;
  box-shadow: 0 0 24px rgba(124, 197, 118, 0.12) !important;
  transform: translateY(-3px);
}

.analytics-kpi-label { color: rgba(235, 243, 235, 0.61); font-size: 0.74rem; font-weight: 700; }
.analytics-kpi-caption { color: rgba(235, 243, 235, 0.51); font-size: 0.71rem; }
.analytics-kpi-delta { color: rgba(235, 243, 235, 0.5); font-size: 0.7rem; }
.analytics-kpi-delta--up { color: var(--analytics-bright); }
.analytics-kpi-delta--down { color: #ffa8a8; }

.analytics-kpi-icon,
.analytics-section-icon {
  display: grid;
  place-items: center;
  border: 1px solid rgba(124, 197, 118, 0.27);
  color: var(--analytics-bright);
  background: rgba(124, 197, 118, 0.11);
}

.analytics-kpi-icon { width: 42px; height: 42px; border-radius: 13px; }
.analytics-section-icon { width: 34px; height: 34px; border-radius: 10px; }

.analytics-empty-chart,
.analytics-empty-report {
  display: flex;
  min-height: 130px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px dashed rgba(124, 197, 118, 0.24);
  border-radius: 14px;
  color: rgba(233, 242, 233, 0.61);
  font-size: 0.82rem;
  background: rgba(124, 197, 118, 0.04);
}

.analytics-health-item + .analytics-health-item { margin-top: 22px; }
.analytics-health-item { color: rgba(238, 245, 238, 0.82); font-size: 0.78rem; }
.analytics-health-item p { line-height: 1.45; }
.analytics-institution-fact { display: flex; align-items: flex-start; gap: 8px; margin-top: 24px; padding: 11px; border: 1px solid rgba(124, 197, 118, 0.16); border-radius: 12px; color: rgba(235, 243, 235, 0.7); font-size: 0.75rem; background: rgba(124, 197, 118, 0.06); }

.analytics-course-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }
.analytics-course-card { padding: 15px; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 15px; color: inherit; cursor: pointer; background: rgba(18, 21, 26, 0.18); transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease; }
.analytics-course-card:hover,
.analytics-course-card--selected { border-color: rgba(124, 197, 118, 0.43); background: rgba(124, 197, 118, 0.1); transform: translateY(-2px); }
.analytics-course-percent { padding: 3px 6px; border-radius: 7px; color: var(--analytics-bright); font-size: 0.68rem; font-weight: 800; background: rgba(124, 197, 118, 0.13); }
.analytics-course-detail { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 13px 15px; border: 1px solid rgba(124, 197, 118, 0.25); border-radius: 14px; background: rgba(124, 197, 118, 0.08); }

.analytics-student-row { display: flex; align-items: center; gap: 10px; padding: 9px; border: 1px solid transparent; border-radius: 11px; transition: background 0.2s ease; }
.analytics-student-row:hover { background: rgba(124, 197, 118, 0.07); }
.analytics-rank { display: grid; width: 25px; height: 25px; flex: 0 0 auto; place-items: center; border-radius: 8px; color: var(--analytics-bright); font-size: 0.7rem; font-weight: 850; background: rgba(124, 197, 118, 0.13); }
.analytics-student-cost { color: rgba(233, 243, 233, 0.75); font-size: 0.72rem; font-weight: 750; }

@media (max-width: 600px) {
  .analytics-date-field { width: 100%; min-width: 100%; max-width: none; }
  .analytics-range-toggle { width: 100%; overflow-x: auto; }
  .analytics-range-toggle :deep(.v-btn) { padding-inline: 10px; }
  .analytics-course-detail { align-items: flex-start; flex-direction: column; }
  .analytics-hero :deep(.v-card-text) { padding: 20px !important; }
}
</style>
