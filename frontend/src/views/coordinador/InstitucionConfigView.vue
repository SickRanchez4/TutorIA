<template>
  <div class="d-flex flex-column ga-5">
    <PageHeader overline="Configuración" title="Institución" subtitle="Administra la identidad de tu institución.">
      <template #actions>
        <v-chip v-if="!loading" :color="institucion.is_active ? 'success' : 'grey'" :variant="institucion.is_active ? 'flat' : 'outlined'" size="small">
          {{ institucion.is_active ? 'Activa' : 'Inactiva' }}
        </v-chip>
      </template>
    </PageHeader>

    <div v-if="loading" class="empty-state surface-card" role="status">
      <v-progress-circular indeterminate color="primary" size="40" width="4" />
      <p class="mb-0">Cargando configuración...</p>
    </div>

    <v-row v-else>
      <v-col cols="12" md="7">
        <v-card class="surface-card mb-4" rounded="xl">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-domain" color="primary"></v-icon>
            <h2 class="text-body-large font-weight-bold">Datos institucionales</h2>
            <v-spacer></v-spacer>
            <v-btn v-if="!editing" size="small" variant="tonal" color="primary" @click="startEdit">Editar</v-btn>
            <v-btn v-else size="small" variant="text" @click="cancelEdit">Cancelar</v-btn>
          </v-card-title>
          <v-card-text>
            <v-form class="d-flex flex-column ga-3" @submit.prevent="saveConfig">
              <v-text-field v-model="form.nombre" label="Nombre" :readonly="!editing" />
              <v-text-field v-model="form.dominio_permitido" label="Dominio permitido" placeholder="ej. uni.edu" :readonly="!editing" />
              <v-btn v-if="editing" type="submit" color="primary" variant="flat" class="align-self-start" :loading="saving">
                Guardar cambios
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <v-card class="surface-card" rounded="xl">
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <p class="text-body-small text-subtle mb-1">Fecha de creación</p>
              <p class="text-title-small font-weight-medium mb-0">{{ formatDate(institucion.created_at, { year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
            </div>
            <v-icon icon="mdi-calendar" color="primary"></v-icon>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card class="surface-card" rounded="xl">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-lightning-bolt-outline" color="primary"></v-icon>
            <h2 class="text-body-large font-weight-bold">Suscripción y tokens</h2>
          </v-card-title>
          <v-card-text v-if="suscripcion">
            <div class="d-flex align-center justify-space-between ga-3 mb-3">
              <div>
                <p class="text-body-small text-subtle mb-1">Tokens disponibles este mes</p>
                <p class="text-headline-small font-weight-black mb-0">{{ formatNumber(suscripcion.tokens_disponibles) }}</p>
              </div>
              <v-chip :color="suscripcion.is_active ? 'success' : 'error'" variant="tonal" size="small">
                {{ suscripcion.is_active ? suscripcion.plan_nombre || 'Activa' : 'No disponible' }}
              </v-chip>
            </div>
            <div class="d-flex justify-space-between text-body-small mb-1">
              <span>{{ formatNumber(suscripcion.tokens_usados_mes) }} usados</span>
              <span>{{ formatNumber(suscripcion.limite_tokens_mensual) }} habilitados</span>
            </div>
            <v-progress-linear
              :model-value="Math.min(suscripcion.porcentaje_consumido || 0, 100)"
              color="primary"
              height="8"
              rounded
              class="mb-3"
              aria-label="Porcentaje de tokens consumidos"
            />
            <div class="d-flex align-center justify-space-between ga-2 subscription-detail">
              <span>Finaliza</span>
              <strong>{{ formatDate(suscripcion.fecha_fin) }}</strong>
            </div>
            <p v-if="!suscripcion.is_active" class="text-body-small text-error mb-0 mt-3">{{ suscripcion.motivo_no_disponible }}</p>
          </v-card-text>
          <v-card-text v-else class="text-subtle">No hay una suscripción de tokens habilitada para esta institución.</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { coordinadorService } from '../../services'
import { coordinadorToast } from '../../composables/useToast'
import { formatDate, formatNumber } from '../../utils/format'
import PageHeader from '../../components/PageHeader.vue'

const { notify, notifyError } = coordinadorToast

const institucion = ref({ nombre: '', dominio_permitido: '', is_active: true, created_at: null })
const form = reactive({ nombre: '', dominio_permitido: '' })
const suscripcion = ref(null)
const loading = ref(true)
const saving = ref(false)
const editing = ref(false)

function resetForm() {
  form.nombre = institucion.value.nombre || ''
  form.dominio_permitido = institucion.value.dominio_permitido || ''
}

function startEdit() {
  resetForm()
  editing.value = true
}

function cancelEdit() {
  resetForm()
  editing.value = false
}

async function loadConfig() {
  loading.value = true
  try {
    const r = await coordinadorService.getConfig()
    institucion.value = { ...institucion.value, ...(r.institucion || {}) }
    suscripcion.value = r.suscripcion || null
    resetForm()
  } catch (e) {
    notifyError(e, 'No se pudo cargar la configuración')
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await coordinadorService.updateConfig({ ...form })
    institucion.value = { ...institucion.value, ...form }
    editing.value = false
    notify('Configuración guardada')
  } catch (e) {
    notifyError(e, 'No se pudo guardar la configuración')
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.subscription-detail {
  padding-top: 10px;
  border-top: 1px solid rgba(var(--tutoria-green-rgb), 0.14);
  color: var(--tutoria-text-muted);
  font-size: 0.78rem;
}
</style>
