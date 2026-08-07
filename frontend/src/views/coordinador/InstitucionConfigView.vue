<template>
  <div class="coord-institucion-view">
    <v-card class="coord-hero" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5">
        <div>
          <p class="text-overline mb-1 coord-overline">Configuración</p>
          <h2 class="text-h5 font-weight-black mb-1">Institución</h2>
          <p class="mb-0 coord-subtext">Administra tu identidad institucional.</p>
        </div>
        <v-chip :color="institucion.is_active ? 'success' : 'grey'" :variant="institucion.is_active ? 'flat' : 'outlined'" size="small">
          {{ institucion.is_active ? 'Activa' : 'Inactiva' }}
        </v-chip>
      </v-card-text>
    </v-card>

    <div v-if="loading" class="coord-loading d-flex flex-column align-center justify-center py-16 ga-3">
      <v-progress-circular indeterminate color="primary" size="40" width="4" />
      <p class="text-body-2 coord-subtext mb-0">Cargando configuración...</p>
    </div>

    <v-row v-else>
      <v-col cols="12" lg="7">
        <v-card class="coord-surface-card mb-4" rounded="xl" variant="flat">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-domain" color="primary"></v-icon>
            Datos institucionales
            <v-spacer></v-spacer>
            <v-btn v-if="!editing" size="small" variant="tonal" color="primary" @click="startEdit">Editar</v-btn>
            <v-btn v-else size="small" variant="text" @click="cancelEdit">Cancelar</v-btn>
          </v-card-title>
          <v-card-text>
            <v-form @submit.prevent="saveConfig" class="d-flex flex-column ga-3">
              <v-text-field v-model="institucion.nombre" label="Nombre" :readonly="!editing" variant="solo-filled" density="comfortable"></v-text-field>
              <v-text-field v-model="institucion.dominio_permitido" label="Dominio permitido" :readonly="!editing" placeholder="ej. uni.edu" variant="solo-filled" density="comfortable"></v-text-field>
              <v-btn v-if="editing" type="submit" color="primary" rounded="lg" class="coord-primary-btn align-self-start">
                Guardar cambios
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <v-card class="coord-surface-card mb-4" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption coord-subtext mb-1">Fecha de creación</p>
              <p class="text-subtitle-2 font-weight-medium mb-0">{{ formattedCreatedAt }}</p>
            </div>
            <v-icon icon="mdi-calendar" color="primary"></v-icon>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="5">
        <v-card class="coord-surface-card mb-4" rounded="xl" variant="flat">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-lightning-bolt-outline" color="primary"></v-icon>
            Suscripción y tokens
          </v-card-title>
          <v-card-text v-if="suscripcion">
            <div class="d-flex align-center justify-space-between ga-3 mb-3">
              <div>
                <p class="text-caption coord-subtext mb-1">Tokens disponibles este mes</p>
                <p class="text-h5 font-weight-black mb-0">{{ formatTokens(suscripcion.tokens_disponibles) }}</p>
              </div>
              <v-chip :color="suscripcion.is_active ? 'success' : 'error'" variant="tonal" size="small">
                {{ suscripcion.is_active ? suscripcion.plan_nombre || 'Activa' : 'No disponible' }}
              </v-chip>
            </div>
            <div class="d-flex justify-space-between text-caption mb-1"><span>{{ formatTokens(suscripcion.tokens_usados_mes) }} usados</span><span>{{ formatTokens(suscripcion.limite_tokens_mensual) }} habilitados</span></div>
            <v-progress-linear :model-value="Math.min(suscripcion.porcentaje_consumido || 0, 100)" color="primary" height="8" rounded class="mb-3" />
            <div class="d-flex align-center justify-space-between ga-2 coord-subscription-detail">
              <span>Finaliza</span>
              <strong>{{ formatSubscriptionDate(suscripcion.fecha_fin) }}</strong>
            </div>
            <p v-if="!suscripcion.is_active" class="text-caption text-error mb-0 mt-3">{{ suscripcion.motivo_no_disponible }}</p>
          </v-card-text>
          <v-card-text v-else class="coord-subtext">No hay una suscripción de tokens habilitada para esta institución.</v-card-text>
        </v-card>

        <v-card class="coord-surface-card mb-4" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption coord-subtext mb-1">Estado</p>
              <p class="text-subtitle-1 font-weight-bold mb-0">{{ institucion.is_active ? 'Activa' : 'Inactiva' }}</p>
            </div>
            <v-avatar :color="institucion.is_active ? 'success' : 'grey'" variant="tonal" size="36">
              <v-icon icon="mdi-check-circle-outline"></v-icon>
            </v-avatar>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { coordinadorService } from '../../services'
import { useCoordinadorToast } from './useCoordinadorToast'

const { notify, notifyError } = useCoordinadorToast()

const institucion = ref({ nombre: '', dominio_permitido: '', is_active: true, created_at: null })
const suscripcion = ref(null)
const loading = ref(true)
const editing = ref(false)
let snapshot = null

const formattedCreatedAt = computed(() => {
  if (!institucion.value.created_at) return 'N/A'
  const date = new Date(institucion.value.created_at)
  return date.toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })
})

function startEdit() {
  snapshot = { ...institucion.value }
  editing.value = true
}

async function loadConfig() {
  loading.value = true
  try {
    const r = await coordinadorService.getConfig()
    institucion.value = { ...institucion.value, ...(r.institucion || {}) }
    suscripcion.value = r.suscripcion || null
  } catch (e) {
    notifyError(e, 'No se pudo cargar configuración')
  } finally {
    loading.value = false
  }
}

function cancelEdit() {
  if (snapshot) institucion.value = { ...snapshot }
  editing.value = false
}

function formatTokens(value) {
  return Number(value || 0).toLocaleString('es-BO')
}

function formatSubscriptionDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function saveConfig() {
  try {
    await coordinadorService.updateConfig({
      nombre: institucion.value.nombre,
      dominio_permitido: institucion.value.dominio_permitido,
    })
    notify('Configuración guardada')
    editing.value = false
  } catch (e) {
    notifyError(e, 'No se pudo guardar configuración')
  }
}

onMounted(async () => {
  await loadConfig()
  snapshot = { ...institucion.value }
})
</script>

<style scoped>
.coord-institucion-view {
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
.coord-loading {
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

.coord-subscription-detail {
  padding-top: 10px;
  border-top: 1px solid rgba(124, 197, 118, 0.14);
  color: rgba(235, 242, 235, 0.74);
  font-size: 0.78rem;
}
</style>
