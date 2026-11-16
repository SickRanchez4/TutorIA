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

    <RegionState v-else-if="loadError" :error="loadError" @retry="loadConfig" />
    <v-row v-else>
      <template v-if="resumen">
        <v-col cols="12" md="7">
          <StatCard label="Cursos de la institución" :value="formatNumber(resumen.total_cursos)" caption="Habilitados e inhabilitados" icon="mdi-book-multiple-outline" />
        </v-col>
        <v-col cols="12" md="5">
          <StatCard label="Cuentas de la institución" :value="formatNumber(resumen.total_cuentas)" caption="Estudiantes y coordinadores" icon="mdi-account-group-outline" />
        </v-col>
      </template>
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
            <v-form v-if="editing" class="d-flex flex-column ga-3" @submit.prevent="saveConfig">
              <v-text-field v-model="form.nombre" label="Nombre" />
              <v-text-field v-model="form.dominio_permitido" label="Dominio permitido" placeholder="ej. uni.edu" />
              <v-btn type="submit" color="primary" variant="flat" class="align-self-start" :loading="saving">
                Guardar cambios
              </v-btn>
            </v-form>
            <dl v-else class="institution-data">
              <div>
                <dt>Nombre</dt>
                <dd>{{ institucion.nombre || '—' }}</dd>
              </div>
              <div>
                <dt>Dominio permitido</dt>
                <dd>{{ institucion.dominio_permitido || 'Sin restricción de dominio' }}</dd>
              </div>
            </dl>
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
import { useCoordinadorToast } from '../../composables/useToast'
import { formatDate, formatNumber } from '../../utils/format'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import RegionState from '../../components/RegionState.vue'
import { useFormDraft } from '../../composables/useUnsavedChanges'

const { notify, notifyError } = useCoordinadorToast()

const institucion = ref({ nombre: '', dominio_permitido: '', is_active: true, created_at: null })
const form = reactive({ nombre: '', dominio_permitido: '' })
const suscripcion = ref(null)
const resumen = ref(null)
const loading = ref(true)
const saving = ref(false)
const editing = ref(false)
const loadError = ref('')
const draft = useFormDraft(() => form, () => editing.value, () => saving.value)

function resetForm() {
  form.nombre = institucion.value.nombre || ''
  form.dominio_permitido = institucion.value.dominio_permitido || ''
}

function startEdit() {
  resetForm()
  draft.accept()
  editing.value = true
}

async function cancelEdit() {
  if (saving.value || !await draft.canClose()) return
  resetForm()
  editing.value = false
}

async function loadConfig() {
  loading.value = true
  loadError.value = ''
  try {
    const r = await coordinadorService.getConfig()
    institucion.value = { ...institucion.value, ...(r.institucion || {}) }
    suscripcion.value = r.suscripcion || null
    resumen.value = r.resumen
    resetForm()
  } catch (e) {
    loadError.value = 'No se pudo cargar la configuración'
    notifyError(e, 'No se pudo cargar la configuración')
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  if (saving.value) return
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
.institution-data {
  display: grid;
  gap: 16px;
  cursor: default;
}

.institution-data > div {
  padding: 14px 16px;
  border: 1px solid var(--tutoria-border);
  border-radius: 12px;
}

.institution-data dt {
  margin-bottom: 5px;
  color: var(--tutoria-text-muted);
  font-size: 0.78rem;
}

.institution-data dd {
  margin: 0;
  overflow-wrap: anywhere;
  font-weight: 600;
}

.subscription-detail {
  padding-top: 10px;
  border-top: 1px solid var(--tutoria-border);
  color: var(--tutoria-text-muted);
  font-size: 0.78rem;
}
</style>
