<template>
  <RoleLayout
    role="Administrador"
    icon="mdi-shield-crown-outline"
    :items="NAV_ITEMS"
    :active="tab"
    :toast="toast"
    @select="tab = $event"
  >
    <div class="admin d-flex flex-column ga-5">
      <PageHeader
        overline="Operación global"
        title="Centro de control institucional"
        subtitle="Administra instituciones, accesos, planes y suscripciones desde un solo espacio."
      />

      <RegionState v-if="loadError" :error="loadError" @retry="loadAll" />
      <v-progress-linear v-if="mutating" indeterminate color="primary" aria-label="Guardando operación" />
      <template v-if="!loadError">
      <!-- Instituciones -->
      <template v-if="tab === 'instituciones'">
        <v-row>
          <v-col cols="12" sm="4">
            <StatCard label="Instituciones" :value="instituciones.length" icon="mdi-domain" />
          </v-col>
          <v-col cols="12" sm="4">
            <StatCard label="Activas" :value="institucionesActivas" icon="mdi-check-decagram-outline" />
          </v-col>
          <v-col cols="12" sm="4">
            <StatCard label="Planes" :value="planes.length" icon="mdi-package-variant-closed" />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card class="surface-card pa-5" rounded="xl">
              <div class="d-flex align-center justify-space-between mb-3 ga-2 flex-wrap">
                <h2 class="text-body-large font-weight-bold">Instituciones</h2>
                <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" @click="showNewInstDialog = true">
                  Nueva institución
                </v-btn>
              </div>
              <v-text-field
                v-model="institucionSearch"
                label="Buscar instituciones por nombre"
                prepend-inner-icon="mdi-magnify"
                clearable
                hide-details
                class="mb-3"
              />
              <div v-if="loading" class="d-flex align-center ga-2" role="status">
                <v-progress-circular indeterminate color="primary" size="20"></v-progress-circular>
                <span class="text-body-medium text-subtle">Cargando...</span>
              </div>
              <p v-else-if="!instituciones.length" class="text-body-medium text-subtle mb-0">Sin instituciones.</p>
              <p v-else-if="!filteredInstituciones.length" class="text-body-medium text-subtle mb-0" role="status">No se encontraron instituciones.</p>
              <v-list v-else density="comfortable" class="admin-list pa-0">
                <v-list-item v-for="inst in instPager.items" :key="inst.id" class="mb-1">
                  <div class="admin-row">
                    <div class="admin-row__main">
                      <div v-if="editInstId === inst.id" class="d-flex flex-column ga-2">
                        <v-text-field v-model="editInst.nombre" density="compact" label="Nombre" />
                        <v-text-field v-model="editInst.dominio_permitido" density="compact" label="Dominio" />
                      </div>
                      <template v-else>
                        <p class="font-weight-medium mb-0">{{ inst.nombre }}</p>
                        <p class="text-body-small text-subtle mb-0">{{ inst.dominio_permitido || 'sin dominio' }}</p>
                      </template>
                    </div>
                    <div class="admin-row__actions">
                      <v-chip size="small" :color="SUB_ESTADO_COLOR[instSubEstado(inst.id)]" variant="tonal">{{ instSubEstado(inst.id) }}</v-chip>
                      <template v-if="editInstId === inst.id">
                        <v-btn size="small" color="primary" variant="flat" @click="saveInst(inst.id)">Guardar</v-btn>
                        <v-btn size="small" variant="text" @click="cancelInstEdit">Cancelar</v-btn>
                      </template>
                      <v-btn v-else variant="text" size="small" @click="startInstEdit(inst)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removeInstitucion(inst)">Eliminar</v-btn>
                    </div>
                  </div>
                </v-list-item>
              </v-list>
              <ListPagination v-model:page="instPager.state.page" v-model:page-size="instPager.state.pageSize" :total="instPager.total" />
            </v-card>
          </v-col>
        </v-row>
      </template>

      <!-- Coordinadores -->
      <v-row v-else-if="tab === 'coordinadores'">
        <v-col cols="12" md="4">
          <v-card class="surface-card pa-5" rounded="xl">
            <h2 class="text-body-large font-weight-bold mb-3">Institución</h2>
            <v-text-field
              v-model="coordinadorInstitucionSearch"
              label="Buscar instituciones por nombre"
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              density="compact"
              class="mb-3"
            />
            <v-select
              :model-value="selectedInstId"
              :items="coordinadorInstitucionOptions"
              label="Selecciona una institución"
              no-data-text="No se encontraron instituciones."
              density="compact"
              class="mb-2"
              @update:model-value="selectInstitution"
            >
              <template #selection>{{ institucionNombre(selectedInstId) }}</template>
            </v-select>
            <p v-if="selectedInstId" class="text-body-small text-subtle mb-0">
              Coordinadores: {{ coordinadores.length }} / {{ coordinadoresLimit }}
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="surface-card pa-5" rounded="xl">
            <div class="d-flex align-center justify-space-between mb-3 ga-2 flex-wrap">
              <h2 class="text-body-large font-weight-bold">Coordinadores</h2>
              <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-account-plus-outline"
                :disabled="!selectedInstId"
                @click="showNewCoordDialog = true"
              >
                Nuevo coordinador
              </v-btn>
            </div>
            <p v-if="!selectedInstId" class="text-body-medium text-subtle mb-0">Selecciona una institución.</p>
            <div v-else-if="loadingCoordinadores" class="empty-state" role="status">
              <v-progress-circular indeterminate color="primary" size="28" width="3"></v-progress-circular>
              <p class="font-weight-bold mb-0">Cargando coordinadores</p>
            </div>
            <RegionState v-else-if="coordinadorError" :error="coordinadorError" @retry="loadCoordinadores" />
            <p v-else-if="!coordinadores.length" class="text-body-medium text-subtle mb-0">Sin coordinadores.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="c in coordPager.items" :key="c.id" class="mb-1">
                <div class="admin-row">
                  <div class="admin-row__main">
                    <v-row v-if="editCoordId === c.id" density="compact">
                      <v-col cols="12" sm="6"><v-text-field v-model="editCoord.first_name" label="Nombres" density="compact" /></v-col>
                      <v-col cols="12" sm="6"><v-text-field v-model="editCoord.last_name" label="Apellidos" density="compact" /></v-col>
                      <v-col cols="12" sm="6"><v-text-field v-model="editCoord.email" label="Correo electrónico" density="compact" /></v-col>
                      <v-col cols="12" sm="6"><v-text-field v-model="editCoord.phone" label="Teléfono" density="compact" /></v-col>
                    </v-row>
                    <template v-else>
                      <p class="font-weight-medium mb-0">{{ c.full_name }}</p>
                      <p class="text-body-small text-subtle mb-0">{{ [c.email, c.phone].filter(Boolean).join(' · ') }}</p>
                    </template>
                  </div>
                  <div class="admin-row__actions">
                    <v-chip size="small" :color="c.is_active ? 'success' : 'default'" variant="tonal">{{ c.is_active ? 'activo' : 'inactivo' }}</v-chip>
                    <template v-if="editCoordId === c.id">
                      <v-btn size="small" color="primary" variant="flat" @click="saveCoord(c.id)">Guardar</v-btn>
                      <v-btn size="small" variant="text" @click="cancelCoordEdit">Cancelar</v-btn>
                    </template>
                    <v-btn v-else variant="text" size="small" @click="startCoordEdit(c)">Editar</v-btn>
                    <v-btn variant="text" size="small" color="warning" @click="toggleCoord(c)">{{ c.is_active ? 'Desactivar' : 'Activar' }}</v-btn>
                    <v-btn variant="text" size="small" color="error" @click="removeCoord(c)">Eliminar</v-btn>
                  </div>
                </div>
              </v-list-item>
            </v-list>
            <ListPagination v-model:page="coordPager.state.page" v-model:page-size="coordPager.state.pageSize" :total="coordPager.total" />
          </v-card>
        </v-col>
      </v-row>

      <!-- Suscripciones -->
      <v-row v-else-if="tab === 'suscripciones'">
        <v-col cols="12">
          <v-card class="surface-card pa-5" rounded="xl">
            <div class="d-flex align-center justify-space-between mb-3 ga-2 flex-wrap">
              <h2 class="text-body-large font-weight-bold">Suscripciones actuales</h2>
              <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" @click="showNewSubDialog = true">
                Asignar suscripción
              </v-btn>
            </div>
            <v-text-field
              v-model="suscripcionSearch"
              label="Buscar instituciones por nombre"
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              class="mb-3"
            />
            <RegionState v-if="loading" loading />
            <p v-else-if="!suscripciones.length" class="text-body-medium text-subtle mb-0">Sin suscripciones.</p>
            <p v-else-if="!filteredSuscripciones.length" class="text-body-medium text-subtle mb-0" role="status">No se encontraron suscripciones para esa institución.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="s in subPager.items" :key="s.id" class="mb-2">
                <div v-if="editSubId !== s.id" class="admin-row">
                  <div class="admin-row__main">
                    <p class="text-body-medium font-weight-medium mb-0">{{ institucionNombre(s.institucion_id) }}</p>
                    <p class="text-body-small text-subtle mb-0">{{ planNombre(s.plan_id) }} · {{ formatNumber(s.limite_tokens_mensual) }} tokens/mes</p>
                    <p class="text-body-small text-subtle mb-0">Inicio: {{ formatDate(s.fecha_inicio) }} · Fin: {{ formatDate(s.fecha_fin) }}</p>
                  </div>
                  <div class="admin-row__actions">
                    <v-chip size="small" :color="s.is_active ? 'success' : 'default'" variant="tonal">{{ s.is_active ? 'Activa' : 'Inactiva' }}</v-chip>
                    <v-btn variant="text" size="small" @click="startSubEdit(s)">Editar</v-btn>
                    <v-btn variant="text" size="small" color="error" @click="removeSuscripcion(s)">Eliminar</v-btn>
                  </div>
                </div>
                <v-card v-else class="pa-4 w-100" variant="tonal" color="primary" rounded="lg">
                  <p class="text-body-medium font-weight-bold mb-3">Editar suscripción de {{ institucionNombre(s.institucion_id) }}</p>
                  <v-row density="compact">
                    <v-col cols="12" sm="6">
                      <v-select v-model="editSub.plan_id" :items="planOptions" label="Plan" density="compact" />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field v-model.number="editSub.limite_tokens_mensual" type="number" min="0" label="Límite de tokens mensual" density="compact" />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field :model-value="editSub.fecha_inicio" type="date" label="Fecha de inicio" density="compact" readonly />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field v-model="editSub.fecha_fin" type="date" label="Fecha de finalización" density="compact" />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-select v-model="editSub.is_active" :items="ESTADO_OPTIONS" label="Estado" density="compact" />
                    </v-col>
                  </v-row>
                  <div class="d-flex ga-2 mt-2">
                    <v-btn color="primary" variant="flat" size="small" @click="saveSuscripcion(s)">Guardar</v-btn>
                    <v-btn variant="text" size="small" @click="cancelSubEdit">Cancelar</v-btn>
                  </div>
                </v-card>
              </v-list-item>
            </v-list>
            <ListPagination v-model:page="subPager.state.page" v-model:page-size="subPager.state.pageSize" :total="subPager.total" />
          </v-card>
        </v-col>
      </v-row>

      <!-- Planes -->
      <v-row v-else-if="tab === 'planes'">
        <v-col cols="12" md="4">
          <v-expansion-panels>
            <v-expansion-panel title="Nuevo plan" value="new-plan">
              <template #text>
                <v-form class="d-flex flex-column ga-3 pt-1" @submit.prevent="createPlan">
                  <v-text-field v-model="newPlan.nombre" label="Nombre del plan" />
                  <v-text-field v-model.number="newPlan.max_cuentas" type="number" min="1" label="Máx. cuentas" />
                  <v-text-field v-model.number="newPlan.max_almacenamiento_gb" type="number" min="1" label="Máx. almacenamiento (GB)" />
                  <v-btn type="submit" color="primary" variant="flat" block :loading="mutating">Crear plan</v-btn>
                </v-form>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="surface-card pa-5" rounded="xl">
            <h2 class="text-body-large font-weight-bold mb-3">Planes disponibles</h2>
            <RegionState v-if="loading" loading />
            <p v-else-if="!planes.length" class="text-body-medium text-subtle mb-0">Sin planes.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="p in planPager.items" :key="p.id" class="mb-1">
                <div class="admin-row" :class="{ 'admin-row--editing': editPlanId === p.id }">
                  <div class="admin-row__main">
                    <v-row v-if="editPlanId === p.id" density="compact">
                      <v-col cols="12" sm="4"><v-text-field v-model="editPlan.nombre" label="Nombre del plan" density="compact" /></v-col>
                      <v-col cols="12" sm="4"><v-text-field v-model.number="editPlan.max_cuentas" type="number" min="1" label="Máx. cuentas" density="compact" /></v-col>
                      <v-col cols="12" sm="4"><v-text-field v-model.number="editPlan.max_almacenamiento_gb" type="number" min="1" label="Máx. GB" density="compact" /></v-col>
                    </v-row>
                    <template v-else>
                      <p class="font-weight-medium mb-0">{{ p.nombre }}</p>
                      <p class="text-body-small text-subtle mb-0">{{ p.max_cuentas }} cuentas · {{ p.max_almacenamiento_gb }} GB</p>
                    </template>
                  </div>
                  <div class="admin-row__actions">
                    <template v-if="editPlanId === p.id">
                      <v-btn size="small" color="primary" variant="flat" @click="savePlan(p.id)">Guardar</v-btn>
                      <v-btn size="small" variant="text" @click="cancelPlanEdit">Cancelar</v-btn>
                    </template>
                    <v-btn v-else variant="text" size="small" @click="startPlanEdit(p)">Editar</v-btn>
                    <v-btn variant="text" size="small" color="error" @click="removePlan(p)">Eliminar</v-btn>
                  </div>
                </div>
              </v-list-item>
            </v-list>
            <ListPagination v-model:page="planPager.state.page" v-model:page-size="planPager.state.pageSize" :total="planPager.total" />
          </v-card>
        </v-col>
      </v-row>

      <ProfilePanel v-show="tab === 'perfil'" @notify="toast.notify" />
      </template>
    </div>

    <v-dialog v-model="institutionDialog" max-width="560" :persistent="creatingInstitucion" aria-labelledby="new-institution-title">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between ga-2">
          <span id="new-institution-title" class="text-body-large font-weight-bold">Nueva institución</span>
          <v-btn icon="mdi-close" variant="text" size="small" aria-label="Cerrar nueva institución" :disabled="creatingInstitucion" @click="institutionDialog = false" />
        </v-card-title>
        <v-card-text>
          <v-form class="d-flex flex-column ga-3" @submit.prevent="createInstitucion">
            <v-text-field v-model="newInst.nombre" label="Nombre" autofocus />
            <v-text-field v-model="newInst.dominio_permitido" label="Dominio permitido (ej. uni.edu)" />
            <div class="d-flex justify-end ga-2">
              <v-btn variant="text" :disabled="creatingInstitucion" @click="institutionDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="creatingInstitucion">Crear institución</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="subscriptionDialog" max-width="560" :persistent="assigningSuscripcion" scrollable aria-labelledby="new-subscription-title">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between ga-2">
          <span id="new-subscription-title" class="text-body-large font-weight-bold">Asignar suscripción</span>
          <v-btn icon="mdi-close" variant="text" size="small" aria-label="Cerrar asignación de suscripción" :disabled="assigningSuscripcion" @click="subscriptionDialog = false" />
        </v-card-title>
        <v-card-text>
          <v-form class="d-flex flex-column ga-3" @submit.prevent="assignSuscripcion">
            <v-select v-model="sub.institucion_id" :items="institucionOptions" label="Institución" />
            <v-select v-model="sub.plan_id" :items="planOptions" label="Plan" />
            <v-text-field v-model.number="sub.limite_tokens_mensual" type="number" min="0" label="Límite de tokens mensual" />
            <v-text-field v-model="sub.fecha_fin" type="date" label="Fecha de finalización" />
            <div class="d-flex justify-end ga-2">
              <v-btn variant="text" :disabled="assigningSuscripcion" @click="subscriptionDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="assigningSuscripcion">Asignar suscripción</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="coordinatorDialog" max-width="560" :persistent="mutating">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between ga-2">
          <span class="text-body-large font-weight-bold">Nuevo coordinador</span>
          <v-btn icon="mdi-close" variant="text" size="small" aria-label="Cerrar" @click="coordinatorDialog = false" />
        </v-card-title>
        <v-card-text>
          <v-form class="d-flex flex-column ga-3" @submit.prevent="createCoordinador">
            <v-text-field v-model="newCoord.first_name" label="Nombres" density="compact" />
            <v-text-field v-model="newCoord.last_name" label="Apellidos" density="compact" />
            <v-text-field v-model="newCoord.email" label="Correo" type="email" density="compact" />
            <v-text-field v-model="newCoord.phone" label="Teléfono" type="tel" density="compact" />
            <v-text-field
              v-model="newCoord.password"
              label="Contraseña inicial"
              type="password"
              autocomplete="new-password"
              hint="8+ caracteres, mayúscula, minúscula, número y símbolo"
              persistent-hint
              density="compact"
            />
            <div class="d-flex justify-end ga-2">
              <v-btn variant="text" :disabled="mutating" @click="coordinatorDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat" :loading="mutating">Crear coordinador</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </RoleLayout>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { superAdminService } from '../services'
import { createToast } from '../composables/useToast'
import { formatDate, formatNumber, normalizeSearch, toDateInput } from '../utils/format'
import RoleLayout from '../components/RoleLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import ProfilePanel from '../components/ProfilePanel.vue'
import ListPagination from '../components/ListPagination.vue'
import RegionState from '../components/RegionState.vue'
import { usePagination } from '../composables/usePagination'
import { useFormDraft, useGuardedDialog, confirmNavigation } from '../composables/useUnsavedChanges'
import { useRequestSequence } from '../composables/useRequestSequence'
import { confirmAction } from '../composables/useConfirm'

const NAV_ITEMS = [
  { value: 'instituciones', label: 'Instituciones', icon: 'mdi-domain' },
  { value: 'coordinadores', label: 'Coordinadores', icon: 'mdi-account-tie-outline' },
  { value: 'suscripciones', label: 'Suscripciones', icon: 'mdi-card-account-details-outline' },
  { value: 'planes', label: 'Planes', icon: 'mdi-package-variant-closed' },
  { value: 'perfil', label: 'Perfil', icon: 'mdi-account-circle' },
]
const SUB_ESTADO_COLOR = { activa: 'success', suspendida: 'warning', 'sin suscripción': 'default' }
const ESTADO_OPTIONS = [{ title: 'Activa', value: true }, { title: 'Inactiva', value: false }]

const toast = createToast()
const { notify, notifyError } = toast
const tab = ref('instituciones')

const instituciones = ref([])
const planes = ref([])
const suscripciones = ref([])
const loading = ref(false)
const loadError = ref('')
const mutating = ref(false)

const institucionSearch = ref('')
const coordinadorInstitucionSearch = ref('')
const suscripcionSearch = ref('')
const matchesInstitucion = (name, query) => normalizeSearch(name).includes(normalizeSearch(query))
const filteredInstituciones = computed(() => instituciones.value.filter((i) => matchesInstitucion(i.nombre, institucionSearch.value)))
const filteredSuscripciones = computed(() => suscripciones.value.filter((s) => matchesInstitucion(institucionNombre(s.institucion_id), suscripcionSearch.value)))
const institucionOptions = computed(() => instituciones.value
  .map((i) => ({ title: i.nombre, value: i.id }))
  .sort((a, b) => a.title.localeCompare(b.title, 'es', { sensitivity: 'base' })))
const coordinadorInstitucionOptions = computed(() => institucionOptions.value.filter((i) => matchesInstitucion(i.title, coordinadorInstitucionSearch.value)))
const planOptions = computed(() => planes.value.map((p) => ({ title: p.nombre, value: p.id })))
const institucionesActivas = computed(() => instituciones.value.filter((i) => i.is_active).length)
const institucionNombre = (id) => instituciones.value.find((i) => i.id === id)?.nombre || '—'
const planNombre = (id) => planes.value.find((p) => p.id === id)?.nombre || '—'

function instSubEstado(instId) {
  const s = suscripciones.value.find((item) => item.institucion_id === instId)
  if (!s) return 'sin suscripción'
  return s.is_active ? 'activa' : 'suspendida'
}

/** Runs a mutation, notifies the outcome and refreshes the affected data. */
async function mutate(action, successMessage, errorFallback, refresh = loadAll) {
  if (mutating.value) return false
  mutating.value = true
  try {
    await action()
    notify(successMessage)
    await refresh()
    return true
  } catch (e) {
    notifyError(e, errorFallback)
    return false
  } finally {
    mutating.value = false
  }
}

async function loadAll() {
  loading.value = true
  loadError.value = ''
  try {
    const [instResp, planesResp, subsResp] = await Promise.all([
      superAdminService.listInstituciones(),
      superAdminService.listPlanes(),
      superAdminService.listSuscripciones(),
    ])
    instituciones.value = instResp.instituciones || []
    planes.value = planesResp.planes || []
    suscripciones.value = subsResp.suscripciones || []
    if (selectedInstId.value) await loadCoordinadores()
  } catch (e) {
    loadError.value = 'No se pudieron cargar los datos de administración'
    notifyError(e, 'No se pudieron cargar los datos')
  } finally {
    loading.value = false
  }
}

/* ---------- Instituciones ---------- */
const newInst = ref({ nombre: '', dominio_permitido: '' })
const showNewInstDialog = ref(false)
const creatingInstitucion = ref(false)
const editInstId = ref('')
const editInst = ref({ nombre: '', dominio_permitido: '' })

async function createInstitucion() {
  if (creatingInstitucion.value) return
  if (!newInst.value.nombre.trim()) return notify('El nombre es requerido', true)
  creatingInstitucion.value = true
  try {
    const ok = await mutate(
      () => superAdminService.createInstitucion({
        nombre: newInst.value.nombre.trim(),
        dominio_permitido: newInst.value.dominio_permitido.trim() || null,
      }),
      'Institución creada',
      'Error al crear institución',
    )
    if (ok) {
      newInst.value = { nombre: '', dominio_permitido: '' }
      showNewInstDialog.value = false
    }
  } finally {
    creatingInstitucion.value = false
  }
}

async function startInstEdit(inst) {
  if (!await instDraft.canClose()) return
  editInstId.value = inst.id
  editInst.value = { nombre: inst.nombre, dominio_permitido: inst.dominio_permitido || '' }
  instDraft.accept()
}

async function saveInst(id) {
  const ok = await mutate(
    () => superAdminService.updateInstitucion(id, {
      nombre: editInst.value.nombre,
      dominio_permitido: editInst.value.dominio_permitido || null,
    }),
    'Institución actualizada',
    'No se pudo actualizar la institución',
  )
  if (ok) editInstId.value = ''
}

async function removeInstitucion(inst) {
  if (!await confirmAction({ title: 'Eliminar institución', message: `¿Eliminar ${inst.nombre}? Esta acción es irreversible.`, confirmText: 'Eliminar institución', destructive: true })) return
  await mutate(() => superAdminService.deleteInstitucion(inst.id), 'Institución eliminada', 'No se pudo eliminar la institución')
}

/* ---------- Planes ---------- */
const newPlan = ref({ nombre: '', max_cuentas: null, max_almacenamiento_gb: null })
const editPlanId = ref('')
const editPlan = ref({ nombre: '', max_cuentas: 0, max_almacenamiento_gb: 0 })

const isMissingNumber = (value) => value == null || value === '' || Number.isNaN(Number(value))

async function createPlan() {
  const plan = newPlan.value
  if (!plan.nombre.trim()) return notify('El nombre del plan es requerido', true)
  if (isMissingNumber(plan.max_cuentas)) return notify('Máx. cuentas es requerido', true)
  if (isMissingNumber(plan.max_almacenamiento_gb)) return notify('Máx. almacenamiento es requerido', true)

  const ok = await mutate(
    () => superAdminService.createPlan({
      nombre: plan.nombre.trim(),
      max_cuentas: Number(plan.max_cuentas),
      max_almacenamiento_gb: Number(plan.max_almacenamiento_gb),
    }),
    'Plan creado',
    'Error al crear plan',
  )
  if (ok) newPlan.value = { nombre: '', max_cuentas: null, max_almacenamiento_gb: null }
}

async function startPlanEdit(plan) {
  if (!await planDraft.canClose()) return
  editPlanId.value = plan.id
  editPlan.value = {
    nombre: plan.nombre,
    max_cuentas: Number(plan.max_cuentas),
    max_almacenamiento_gb: Number(plan.max_almacenamiento_gb),
  }
  planDraft.accept()
}

async function savePlan(id) {
  const ok = await mutate(
    () => superAdminService.updatePlan(id, {
      nombre: editPlan.value.nombre,
      max_cuentas: Number(editPlan.value.max_cuentas),
      max_almacenamiento_gb: Number(editPlan.value.max_almacenamiento_gb),
    }),
    'Plan actualizado',
    'No se pudo actualizar el plan',
  )
  if (ok) editPlanId.value = ''
}

async function removePlan(plan) {
  if (!await confirmAction({ title: 'Eliminar plan', message: `¿Eliminar el plan ${plan.nombre}?`, confirmText: 'Eliminar plan', destructive: true })) return
  await mutate(() => superAdminService.deletePlan(plan.id), 'Plan eliminado', 'No se pudo eliminar el plan')
}

/* ---------- Suscripciones ---------- */
const emptySub = () => ({ institucion_id: null, plan_id: null, limite_tokens_mensual: null, fecha_fin: '' })
const sub = ref(emptySub())
const showNewSubDialog = ref(false)
const assigningSuscripcion = ref(false)
const editSubId = ref('')
const editSub = ref({ plan_id: null, limite_tokens_mensual: 0, is_active: true, fecha_inicio: '', fecha_fin: '' })

async function assignSuscripcion() {
  if (assigningSuscripcion.value) return
  if (!sub.value.institucion_id || !sub.value.plan_id) return notify('Selecciona institución y plan', true)
  if (isMissingNumber(sub.value.limite_tokens_mensual)) return notify('Límite de tokens mensual es requerido', true)

  assigningSuscripcion.value = true
  try {
    const ok = await mutate(
      () => superAdminService.assignSuscripcion(sub.value.institucion_id, {
        plan_id: Number(sub.value.plan_id),
        limite_tokens_mensual: Number(sub.value.limite_tokens_mensual),
        fecha_fin: sub.value.fecha_fin || null,
      }),
      'Suscripción asignada',
      'Error al asignar suscripción',
    )
    if (ok) {
      sub.value = emptySub()
      showNewSubDialog.value = false
    }
  } finally {
    assigningSuscripcion.value = false
  }
}

async function startSubEdit(s) {
  if (!await subDraft.canClose()) return
  editSubId.value = s.id
  editSub.value = {
    plan_id: s.plan_id,
    limite_tokens_mensual: s.limite_tokens_mensual,
    is_active: s.is_active,
    fecha_inicio: toDateInput(s.fecha_inicio),
    fecha_fin: toDateInput(s.fecha_fin),
  }
  subDraft.accept()
}

async function saveSuscripcion(item) {
  const ok = await mutate(
    () => superAdminService.updateSuscripcion(item.institucion_id, {
      plan_id: Number(editSub.value.plan_id),
      limite_tokens_mensual: Number(editSub.value.limite_tokens_mensual),
      fecha_fin: editSub.value.fecha_fin || null,
      is_active: editSub.value.is_active === true,
    }),
    'Suscripción actualizada',
    'No se pudo actualizar la suscripción',
  )
  if (ok) editSubId.value = ''
}

async function removeSuscripcion(item) {
  if (!await confirmAction({ title: 'Eliminar suscripción', message: `¿Eliminar la suscripción de ${institucionNombre(item.institucion_id)}?`, confirmText: 'Eliminar suscripción', destructive: true })) return
  await mutate(() => superAdminService.deleteSuscripcion(item.institucion_id), 'Suscripción eliminada', 'No se pudo eliminar la suscripción')
}

/* ---------- Coordinadores ---------- */
const emptyCoord = () => ({ first_name: '', last_name: '', email: '', phone: '', password: '' })
const selectedInstId = ref(null)
const coordinadores = ref([])
const loadingCoordinadores = ref(false)
const coordinadorError = ref('')
const nextCoordinadorRequest = useRequestSequence()
const newCoord = ref(emptyCoord())
const editCoordId = ref('')
const editCoord = ref({ first_name: '', last_name: '', email: '', phone: '' })
const showNewCoordDialog = ref(false)

const coordinadoresLimit = computed(() => {
  const activeSub = suscripciones.value.find((s) => s.institucion_id === selectedInstId.value && s.is_active)
  const plan = activeSub && planes.value.find((p) => p.id === activeSub.plan_id)
  return plan ? Number(plan.max_cuentas) : 0
})

async function loadCoordinadores() {
  const current = nextCoordinadorRequest()
  coordinadores.value = []
  coordinadorError.value = ''
  if (!selectedInstId.value) { loadingCoordinadores.value = false; return }
  loadingCoordinadores.value = true
  try {
    const resp = await superAdminService.listCoordinadores(selectedInstId.value)
    if (!current()) return
    coordinadores.value = resp.coordinadores || []
  } catch (e) {
    if (current()) { coordinadorError.value = 'No se pudieron cargar los coordinadores'; notifyError(e, coordinadorError.value) }
  } finally {
    if (current()) loadingCoordinadores.value = false
  }
}

async function createCoordinador() {
  if (!selectedInstId.value) return notify('Selecciona una institución', true)
  const ok = await mutate(
    () => superAdminService.createCoordinador(selectedInstId.value, { ...newCoord.value }),
    'Coordinador creado',
    'No se pudo crear el coordinador',
    loadCoordinadores,
  )
  if (ok) {
    newCoord.value = emptyCoord()
    showNewCoordDialog.value = false
  }
}

async function startCoordEdit(c) {
  if (!await coordDraft.canClose()) return
  editCoordId.value = c.id
  editCoord.value = { first_name: c.first_name || '', last_name: c.last_name || '', email: c.email || '', phone: c.phone || '' }
  coordDraft.accept()
}

async function saveCoord(userId) {
  const ok = await mutate(
    () => superAdminService.updateCoordinador(selectedInstId.value, userId, { ...editCoord.value }),
    'Coordinador actualizado',
    'No se pudo actualizar el coordinador',
    loadCoordinadores,
  )
  if (ok) editCoordId.value = ''
}

async function toggleCoord(c) {
  await mutate(
    () => superAdminService.updateCoordinador(selectedInstId.value, c.id, { is_active: !c.is_active }),
    'Estado del coordinador actualizado',
    'No se pudo actualizar el estado',
    loadCoordinadores,
  )
}

async function removeCoord(c) {
  if (!await confirmAction({ title: 'Eliminar coordinador', message: `¿Eliminar al coordinador ${c.full_name}?`, confirmText: 'Eliminar coordinador', destructive: true })) return
  await mutate(
    () => superAdminService.deleteCoordinador(selectedInstId.value, c.id),
    'Coordinador eliminado',
    'No se pudo eliminar el coordinador',
    loadCoordinadores,
  )
}

const instPager = usePagination(filteredInstituciones)
const coordPager = usePagination(coordinadores)
const subPager = usePagination(filteredSuscripciones)
const planPager = usePagination(planes)
watch(institucionSearch, () => { instPager.state.page = 1 })
watch(suscripcionSearch, () => { subPager.state.page = 1 })
const instDraft = useFormDraft(() => editInst.value, () => Boolean(editInstId.value))
const planDraft = useFormDraft(() => editPlan.value, () => Boolean(editPlanId.value))
const coordDraft = useFormDraft(() => editCoord.value, () => Boolean(editCoordId.value))
const subDraft = useFormDraft(() => editSub.value, () => Boolean(editSubId.value))
const newInstDraft = useFormDraft(() => newInst.value, () => showNewInstDialog.value)
const newSubDraft = useFormDraft(() => sub.value, () => showNewSubDialog.value)
const newCoordDraft = useFormDraft(() => newCoord.value, () => showNewCoordDialog.value)
useFormDraft(() => newPlan.value, () => true, () => mutating.value)
const institutionDialog = useGuardedDialog(showNewInstDialog, newInstDraft, () => creatingInstitucion.value)
const subscriptionDialog = useGuardedDialog(showNewSubDialog, newSubDraft, () => assigningSuscripcion.value)
const coordinatorDialog = useGuardedDialog(showNewCoordDialog, newCoordDraft, () => mutating.value)
async function cancelInstEdit() { if (await instDraft.canClose()) editInstId.value = '' }
async function cancelPlanEdit() { if (await planDraft.canClose()) editPlanId.value = '' }
async function cancelCoordEdit() { if (await coordDraft.canClose()) editCoordId.value = '' }
async function cancelSubEdit() { if (await subDraft.canClose()) editSubId.value = '' }
async function selectInstitution(value) {
  if (!await confirmNavigation()) return
  selectedInstId.value = value
  editCoordId.value = ''
  coordPager.state.page = 1
  loadCoordinadores()
}
onMounted(loadAll)
</script>

<style scoped>
.admin :deep(.v-expansion-panel) {
  border: 1px solid var(--tutoria-border);
  border-radius: 16px !important;
  color: inherit;
  background: var(--tutoria-surface) !important;
  box-shadow: var(--tutoria-shadow);
}

.admin :deep(.v-expansion-panel-title) {
  font-weight: 700;
}

.admin-list :deep(.v-list-item) {
  padding: 12px !important;
  border: 1px solid transparent;
  border-radius: 13px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.admin-list :deep(.v-list-item:hover) {
  border-color: var(--tutoria-border);
  background: var(--tutoria-nav-active-bg);
}

.admin-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px 16px;
  width: 100%;
}

.admin-row__main {
  flex: 1 1 260px;
  min-width: 0;
}

.admin-row--editing {
  padding-block: 16px;
}

.admin-row__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
</style>
