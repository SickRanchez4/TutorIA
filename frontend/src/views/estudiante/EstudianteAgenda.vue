<template>
  <div class="agenda d-flex flex-column ga-4">
    <v-card class="agenda-toolbar surface-card pa-3 pa-sm-4" rounded="xl">
      <div class="agenda-toolbar__month">
        <v-btn icon="mdi-chevron-left" variant="tonal" size="small" aria-label="Mes anterior" @click="shiftMonth(-1)"></v-btn>
        <h2 class="text-body-large font-weight-bold text-center agenda-toolbar__label" aria-live="polite">{{ monthLabel }}</h2>
        <v-btn icon="mdi-chevron-right" variant="tonal" size="small" aria-label="Mes siguiente" @click="shiftMonth(1)"></v-btn>
      </div>
      <div class="agenda-toolbar__filters">
        <v-select
          v-model="grupoFilter"
          :items="filterOptions"
          label="Curso"
          density="compact"
          class="agenda-toolbar__select"
          @update:model-value="loadAgenda"
        />
        <v-btn color="primary" variant="flat" :loading="loading" @click="loadAgenda">Actualizar</v-btn>
      </div>
    </v-card>

    <v-card class="surface-card pa-3 pa-sm-4" rounded="xl">
      <div class="agenda-calendar" tabindex="0" aria-label="Calendario mensual; desliza horizontalmente para verlo completo">
        <div class="agenda-grid mb-2" aria-hidden="true">
          <div v-for="d in WEEK_DAYS" :key="d" class="text-center text-body-small text-uppercase font-weight-bold text-subtle">{{ d }}</div>
        </div>
        <div class="agenda-grid">
          <div
            v-for="day in calendarDays"
            :key="day.key"
            :class="['agenda-day pa-2', day.inMonth ? 'agenda-day--in' : 'agenda-day--out', { 'agenda-day--today': day.isToday }]"
            :aria-current="day.isToday ? 'date' : undefined"
          >
            <p :class="['text-body-small font-weight-bold mb-1', day.isToday ? 'text-primary' : day.inMonth ? '' : 'text-disabled']">{{ day.date.getDate() }}</p>
            <div class="agenda-day__events">
              <span
                v-for="item in day.events.slice(0, 2)"
                :key="item.id"
                :title="item.titulo"
                :class="['agenda-event text-truncate', `agenda-event--${TIPO_STYLE[item.tipo] ? item.tipo : 'default'}`]"
              >
                {{ item.titulo }}
              </span>
              <p v-if="day.events.length > 2" class="text-body-small text-subtle mb-0">+{{ day.events.length - 2 }} más</p>
            </div>
          </div>
        </div>
      </div>
    </v-card>

    <v-card class="surface-card pa-5" rounded="xl">
      <h2 class="text-body-large font-weight-bold mb-3">Actividades del mes</h2>
      <p v-if="!monthActivities.length" class="text-body-medium text-subtle mb-0">Sin actividades en este mes.</p>
      <v-list v-else density="comfortable" class="pa-0">
        <v-list-item v-for="a in monthActivities" :key="a.id" class="px-0">
          <div class="d-flex align-center justify-space-between w-100 ga-3">
            <div class="min-w-0">
              <p class="text-body-medium font-weight-medium mb-0">{{ a.titulo }}</p>
              <p v-if="a.grupo?.materia_nombre" class="text-body-small text-subtle mb-0">
                {{ a.grupo.materia_nombre }} · {{ a.grupo.periodo_academico }} {{ a.grupo.anio }}
              </p>
              <p class="text-body-small text-subtle mb-0">Límite: {{ formatDateTime(a.fecha_limite, DEADLINE_FORMAT) }}</p>
            </div>
            <v-chip size="small" :color="TIPO_STYLE[a.tipo] || 'default'" variant="tonal">{{ a.tipo }}</v-chip>
          </div>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { estudianteService } from '../../services'
import { errorMessage } from '../../composables/useToast'
import { formatDate, formatDateTime } from '../../utils/format'

/** Read-only monthly agenda of the student's activities. */
const props = defineProps({
  grupos: { type: Array, default: () => [] },
})
const emit = defineEmits(['notify'])

const WEEK_DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const TIPO_STYLE = { examen: 'success', tarea: 'primary', proyecto: 'secondary' }
const DEADLINE_FORMAT = { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }

const actividades = ref([])
const grupoFilter = ref('')
const loading = ref(false)
const today = new Date()
const viewMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))

const filterOptions = computed(() => [
  { title: 'Todos mis cursos', value: '' },
  ...props.grupos.map((g) => ({ title: `${g.nombre || 'Materia'}${g.codigo ? ` (${g.codigo})` : ''}`, value: g.id })),
])

const monthLabel = computed(() => {
  const label = formatDate(viewMonth.value, { month: 'long', year: 'numeric' })
  return label.charAt(0).toUpperCase() + label.slice(1)
})

const dayKey = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const activitiesByDay = computed(() => {
  const map = {}
  for (const a of actividades.value) {
    const key = dayKey(new Date(a.fecha_limite))
    ;(map[key] ||= []).push(a)
  }
  return map
})

const calendarDays = computed(() => {
  const first = viewMonth.value
  const start = new Date(first)
  start.setDate(first.getDate() - ((first.getDay() + 6) % 7))

  return Array.from({ length: 42 }, (_, i) => {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    const key = dayKey(date)
    return {
      key,
      date,
      inMonth: date.getMonth() === first.getMonth(),
      isToday: key === dayKey(today),
      events: activitiesByDay.value[key] || [],
    }
  })
})

const monthActivities = computed(() => {
  const y = viewMonth.value.getFullYear()
  const m = viewMonth.value.getMonth()
  return actividades.value
    .filter((a) => {
      const d = new Date(a.fecha_limite)
      return d.getFullYear() === y && d.getMonth() === m
    })
    .sort((a, b) => new Date(a.fecha_limite) - new Date(b.fecha_limite))
})

function shiftMonth(delta) {
  viewMonth.value = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth() + delta, 1)
}

async function loadAgenda() {
  loading.value = true
  try {
    const r = await estudianteService.getAgenda(grupoFilter.value || null)
    actividades.value = r.actividades || []
  } catch (e) {
    emit('notify', errorMessage(e, 'No se pudo cargar la agenda'), true)
  } finally {
    loading.value = false
  }
}

onMounted(loadAgenda)
</script>

<style scoped>
.agenda-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.agenda-toolbar__month,
.agenda-toolbar__filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agenda-toolbar__label {
  min-width: 170px;
}

.agenda-toolbar__select {
  min-width: 220px;
}

.agenda-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.agenda-day {
  min-height: 98px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.agenda-day--in { background: rgba(255, 255, 255, 0.03); }
.agenda-day--out { background: rgba(255, 255, 255, 0.01); }

.agenda-day--in:hover {
  border-color: rgba(var(--tutoria-green-rgb), 0.32);
  background: rgba(var(--tutoria-green-rgb), 0.05);
}

.agenda-day--today {
  border-color: rgba(155, 230, 146, 0.55);
  background: rgba(var(--tutoria-green-rgb), 0.08);
}

.agenda-day__events {
  display: flex;
  max-height: 70px;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
  overflow-y: auto;
}

.agenda-event {
  display: block;
  padding: 4px 6px;
  border-radius: 6px;
  color: #0a0a0c;
  font-size: 10px;
  font-weight: 600;
}

.agenda-event--examen { background: rgba(var(--tutoria-green-rgb), 0.95); }
.agenda-event--tarea { background: rgba(var(--tutoria-green-rgb), 0.7); }
.agenda-event--proyecto { background: rgba(255, 255, 255, 0.7); }
.agenda-event--default { background: rgba(154, 155, 163, 0.9); }

@media (max-width: 599px) {
  .agenda-toolbar__month,
  .agenda-toolbar__filters {
    width: 100%;
  }

  .agenda-toolbar__label {
    flex: 1;
    min-width: 0;
  }

  .agenda-toolbar__filters {
    flex-direction: column;
    align-items: stretch;
  }

  .agenda-toolbar__select {
    min-width: 0;
  }

  .agenda-calendar {
    margin-inline: -4px;
    padding: 2px 4px 8px;
    overflow-x: auto;
    overscroll-behavior-inline: contain;
  }

  .agenda-calendar > .agenda-grid {
    min-width: 650px;
  }
}
</style>
