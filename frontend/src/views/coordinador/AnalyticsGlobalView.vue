<template>
  <section class="d-flex flex-column ga-5">
    <PageHeader
      overline="Inteligencia académica"
      title="Uso del asistente por curso"
      subtitle="Actividad, participación y respaldo documental dentro del período seleccionado."
    >
      <template #actions>
        <div class="analytics-pill"><v-icon icon="mdi-calendar-range-outline" size="17"></v-icon>{{ periodLabel }}</div>
      </template>
    </PageHeader>

    <v-card class="surface-card" rounded="xl">
      <v-card-text class="pa-4 pa-md-5">
        <div class="mb-4">
          <h2 class="text-title-small font-weight-black">Explorar período</h2>
          <p class="text-body-small text-subtle mb-0">Ajusta la ventana y enfoca el análisis.</p>
        </div>
        <div class="d-flex align-center flex-wrap ga-3">
          <v-btn-toggle v-model="days" mandatory color="primary" density="compact" class="analytics-range" @update:model-value="load">
            <v-btn :value="7">7 días</v-btn>
            <v-btn :value="30">30 días</v-btn>
            <v-btn :value="90">90 días</v-btn>
            <v-btn :value="0">Personalizado</v-btn>
          </v-btn-toggle>
          <div v-if="days === 0" class="d-flex flex-wrap ga-2">
            <v-text-field v-model="customRange.start" type="date" label="Desde" density="compact" class="analytics-date" @change="loadCustomRange" />
            <v-text-field v-model="customRange.end" type="date" label="Hasta" density="compact" class="analytics-date" @change="loadCustomRange" />
          </div>
        </div>
        <div class="d-flex align-center flex-wrap ga-2 mt-4" role="group" aria-label="Tipo de interacción">
          <span class="analytics-filter-label">Tipo de interacción</span>
          <v-btn
            v-for="type in OPERATION_TYPES"
            :key="type.value"
            size="small"
            :variant="tipoFilter === type.value ? 'flat' : 'tonal'"
            :color="tipoFilter === type.value ? 'primary' : 'default'"
            :aria-pressed="tipoFilter === type.value"
            class="font-weight-bold"
            @click="selectType(type.value)"
          >
            <v-icon :icon="type.icon" size="15" class="mr-1"></v-icon>{{ type.label }}
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <div v-if="loading" class="empty-state surface-card analytics-loading" role="status">
      <v-progress-circular indeterminate color="primary" size="44" width="4" />
      <p class="font-weight-bold mb-0">Construyendo tu reporte</p>
      <p class="text-body-small mb-0">Analizando la actividad académica del período.</p>
    </div>

    <template v-else-if="analytics">
      <v-row>
        <v-col cols="12" sm="6" lg="3">
          <StatCard label="Consultas al asistente" :value="formatNumber(analytics.total_operaciones)" icon="mdi-message-processing-outline">
            <template #caption>
              <p class="analytics-delta mb-0" :class="deltaClass(analytics.comparativa_periodo_anterior?.operaciones_delta_pct)">
                {{ deltaLabel(analytics.comparativa_periodo_anterior?.operaciones_delta_pct) }}
              </p>
            </template>
          </StatCard>
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <StatCard
            label="Estudiantes activos"
            :value="formatNumber(analytics.alumnos_activos)"
            :caption="`de ${formatNumber(analytics.participacion?.estudiantes_habilitados)} habilitados`"
            icon="mdi-account-group-outline"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <StatCard
            label="Respuestas con fuentes"
            :value="percentLabel(analytics.cobertura_documental?.porcentaje)"
            :caption="`${analytics.cobertura_documental?.respuestas_con_fuentes || 0} de ${analytics.cobertura_documental?.respuestas_totales || 0} respuestas`"
            icon="mdi-file-check-outline"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <StatCard
            label="Costo estimado"
            :value="currency(analytics.total_cost_usd)"
            :caption="`${currency(analytics.costo_promedio_operacion)} por consulta`"
            icon="mdi-chart-line-variant"
          />
        </v-col>
      </v-row>

      <v-card class="surface-card" rounded="xl">
        <v-card-text class="pa-5">
          <div class="d-flex align-start justify-space-between flex-wrap ga-3 mb-4">
            <div>
              <p class="eyebrow mb-1">Actividad por curso</p>
              <h2 class="text-body-large font-weight-black mb-1">¿En qué cursos se está utilizando más el asistente?</h2>
              <p class="text-body-small text-subtle mb-0">Las consultas se atribuyen solo cuando pertenecen a un curso válido.</p>
            </div>
            <v-chip size="small" color="primary" variant="tonal">{{ analytics.breakdown_curso?.length || 0 }} cursos con actividad</v-chip>
          </div>
          <div v-if="!analytics.breakdown_curso?.length" class="empty-state">
            <v-icon icon="mdi-folder-chart-outline" size="28"></v-icon>
            <span>Este período aún no tiene actividad por curso.</span>
          </div>
          <div v-else class="analytics-course-grid">
            <button
              v-for="course in analytics.breakdown_curso"
              :key="course.curso_id ?? 'sin_curso'"
              type="button"
              class="analytics-course"
              :class="{ 'analytics-course--selected': selectedCourseId === course.curso_id }"
              :aria-pressed="selectedCourseId === course.curso_id"
              @click="selectedCourseId = course.curso_id"
            >
              <div class="d-flex justify-space-between align-start ga-2">
                <p class="font-weight-black text-body-medium mb-1 text-left">{{ course.curso_nombre }}</p>
                <span class="analytics-course__percent">{{ course.porcentaje_actividad }}%</span>
              </div>
              <p class="text-body-small text-subtle text-left mb-3">{{ formatNumber(course.count) }} consultas · {{ formatNumber(course.tokens) }} tokens</p>
              <v-progress-linear :model-value="course.porcentaje_actividad" color="primary" height="6" rounded></v-progress-linear>
            </button>
          </div>
          <div v-if="selectedCourse" class="analytics-course-detail mt-4">
            <div>
              <p class="text-body-small text-subtle mb-0">Curso seleccionado</p>
              <p class="font-weight-black mb-0">{{ selectedCourse.curso_nombre }} · {{ currency(selectedCourse.cost_usd) }} de inversión estimada</p>
            </div>
            <v-btn
              v-if="selectedCourse.curso_id"
              :to="`/coordinador/cursos/${selectedCourse.curso_id}`"
              color="primary"
              variant="tonal"
              size="small"
              append-icon="mdi-arrow-right"
            >
              Ver curso
            </v-btn>
          </div>
        </v-card-text>
      </v-card>

      <v-row>
        <v-col cols="12" md="6">
          <v-card class="surface-card h-100" rounded="xl">
            <v-card-text class="pa-5">
              <div class="d-flex align-center ga-2 mb-4">
                <div class="icon-tile analytics-section-icon" aria-hidden="true"><v-icon icon="mdi-shape-outline" size="18"></v-icon></div>
                <div>
                  <h2 class="text-body-large font-weight-black">Uso por enfoque</h2>
                  <p class="text-body-small text-subtle mb-0">Cómo usan los estudiantes el asistente.</p>
                </div>
              </div>
              <div v-if="operationBreakdown.length" class="d-flex flex-column ga-3">
                <div v-for="item in operationBreakdown" :key="item.key">
                  <div class="d-flex justify-space-between text-body-medium mb-1"><span>{{ operationLabel(item.key) }}</span><strong>{{ formatNumber(item.count) }}</strong></div>
                  <v-progress-linear :model-value="item.percentage" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-body-small text-subtle text-right mb-0 mt-1">{{ item.percentage }}% de interacciones</p>
                </div>
              </div>
              <div v-else class="empty-state">Sin datos de interacción.</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card class="surface-card h-100" rounded="xl">
            <v-card-text class="pa-5">
              <div class="d-flex align-center ga-2 mb-4">
                <div class="icon-tile analytics-section-icon" aria-hidden="true"><v-icon icon="mdi-gauge" size="18"></v-icon></div>
                <div>
                  <h2 class="text-body-large font-weight-black">Indicadores de uso</h2>
                  <p class="text-body-small text-subtle mb-0">Se calculan con la actividad del período seleccionado.</p>
                </div>
              </div>
              <div class="d-flex flex-column ga-5">
                <div v-for="indicator in indicators" :key="indicator.label" class="analytics-indicator">
                  <div class="d-flex justify-space-between mb-1"><span>{{ indicator.label }}</span><strong>{{ percentLabel(indicator.value) }}</strong></div>
                  <v-progress-linear :model-value="indicator.value || 0" color="primary" height="8" rounded></v-progress-linear>
                  <p class="text-body-small text-subtle mb-0 mt-1">{{ indicator.message }}</p>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { coordinadorService } from '../../services'
import { coordinadorToast } from '../../composables/useToast'
import { formatDate, formatNumber, toDateInput } from '../../utils/format'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

const { notifyError } = coordinadorToast

const OPERATION_TYPES = [
  { value: '', label: 'Todo', icon: 'mdi-view-grid-outline' },
  { value: 'chat_rag', label: 'Chat', icon: 'mdi-chat-processing-outline' },
  { value: 'practicar', label: 'Práctica', icon: 'mdi-head-question-outline' },
  { value: 'resumen_sintetico', label: 'Recursos', icon: 'mdi-file-document-outline' },
]

const OPERATION_LABELS = { chat_rag: 'Chat con material', practicar: 'Modo práctica', resumen_sintetico: 'Recurso sintético' }

const days = ref(30)
const analytics = ref(null)
const loading = ref(false)
const customRange = reactive({ start: '', end: '' })
const tipoFilter = ref('')
const selectedCourseId = ref(null)

const shortDate = (value) => formatDate(`${value}T00:00:00`, { day: '2-digit', month: 'short' }, value)

const periodLabel = computed(() => {
  if (days.value > 0) return `Últimos ${days.value} días`
  if (customRange.start && customRange.end) return `${shortDate(customRange.start)} — ${shortDate(customRange.end)}`
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

const indicators = computed(() => {
  const a = analytics.value || {}
  const total = Number(a.total_operaciones || 0)
  const chatCount = Number(a.breakdown_tipo_operacion?.chat_rag?.count || 0)
  const coverage = a.cobertura_documental
  return [
    {
      label: 'Participación',
      value: a.participacion?.porcentaje,
      message: `${a.participacion?.estudiantes_activos || 0} de ${a.participacion?.estudiantes_habilitados || 0} estudiantes habilitados usaron el asistente.`,
    },
    {
      label: 'Uso de chat con material',
      value: total ? Math.round((chatCount / total) * 100) : null,
      message: total
        ? `${chatCount} de ${total} interacciones usaron chat con material de curso.`
        : 'Aún no hay interacciones para calcular este indicador.',
    },
    {
      label: 'Respaldo documental',
      value: coverage?.porcentaje,
      message: coverage?.porcentaje == null
        ? 'Aún no hay respuestas del asistente para medir citas de documentos.'
        : `${coverage.respuestas_con_fuentes} de ${coverage.respuestas_totales} respuestas incluyeron citas del material indexado.`,
    },
  ]
})

function setRangeFromDays() {
  const today = new Date()
  const start = new Date(today)
  start.setDate(start.getDate() - days.value)
  customRange.start = toDateInput(start)
  customRange.end = toDateInput(today)
}

function loadCustomRange() {
  days.value = 0
  if (customRange.start && customRange.end) load()
}

function selectType(type) {
  tipoFilter.value = type
  load()
}

async function load() {
  let request
  if (days.value > 0) {
    setRangeFromDays()
    request = coordinadorService.getConsumo(days.value, { tipo: tipoFilter.value })
  } else if (customRange.start && customRange.end) {
    request = coordinadorService.getConsumo(null, { start_date: customRange.start, end_date: customRange.end, tipo: tipoFilter.value })
  } else {
    return
  }

  loading.value = true
  try {
    analytics.value = await request
    selectedCourseId.value = null
  } catch (e) {
    notifyError(e, 'No se pudieron cargar las analíticas')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function currency(value) {
  return `$${Number(value || 0).toFixed(4)}`
}

function percentLabel(value) {
  return value == null ? '—' : `${Number(value).toFixed(0)}%`
}

function deltaLabel(value) {
  if (value == null) return 'Sin comparación previa'
  return `${value >= 0 ? '+' : ''}${value}% vs. período anterior`
}

function deltaClass(value) {
  if (value == null) return ''
  return value >= 0 ? 'analytics-delta--up' : 'analytics-delta--down'
}

function operationLabel(value) {
  return OPERATION_LABELS[value] || value
}
</script>

<style scoped>
.analytics-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 12px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.27);
  border-radius: 999px;
  color: var(--tutoria-green-bright);
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(var(--tutoria-green-rgb), 0.1);
}

.analytics-range :deep(.v-btn) {
  font-size: 0.75rem;
  font-weight: 700;
}

.analytics-date {
  width: 160px;
}

.analytics-filter-label {
  color: var(--tutoria-text-muted);
  font-size: 0.73rem;
  font-weight: 700;
}

.analytics-loading {
  min-height: 320px;
}

.analytics-delta {
  color: var(--tutoria-text-muted);
  font-size: 0.72rem;
}

.analytics-delta--up { color: var(--tutoria-green-bright); }
.analytics-delta--down { color: #ffa8a8; }

.analytics-section-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
}

.analytics-indicator {
  color: rgba(238, 245, 238, 0.85);
  font-size: 0.8rem;
}

.analytics-course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(210px, 100%), 1fr));
  gap: 12px;
}

.analytics-course {
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 15px;
  color: inherit;
  font: inherit;
  cursor: pointer;
  background: rgba(18, 21, 26, 0.18);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.analytics-course:hover,
.analytics-course--selected {
  border-color: rgba(var(--tutoria-green-rgb), 0.43);
  background: rgba(var(--tutoria-green-rgb), 0.1);
  transform: translateY(-2px);
}

.analytics-course:focus-visible {
  outline: 2px solid var(--tutoria-green-bright);
  outline-offset: 2px;
}

.analytics-course__percent {
  padding: 3px 6px;
  border-radius: 7px;
  color: var(--tutoria-green-bright);
  font-size: 0.68rem;
  font-weight: 800;
  background: rgba(var(--tutoria-green-rgb), 0.13);
}

.analytics-course-detail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 13px 15px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.25);
  border-radius: 14px;
  background: rgba(var(--tutoria-green-rgb), 0.08);
}

@media (max-width: 839px) {
  .analytics-range {
    max-width: 100%;
    overflow-x: auto;
  }
}

@media (max-width: 599px) {
  .analytics-date {
    width: 100%;
  }

  .analytics-range {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    height: auto !important;
    overflow: visible;
  }

  .analytics-range :deep(.v-btn) {
    width: 100%;
  }

  .analytics-course-detail {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
