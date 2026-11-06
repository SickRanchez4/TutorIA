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
          <v-col cols="12" md="4">
            <v-expansion-panels>
              <v-expansion-panel title="Nueva institución" value="new-inst">
                <template #text>
                  <v-form class="d-flex flex-column ga-3 pt-1" @submit.prevent="createInstitucion">
                    <v-text-field v-model="newInst.nombre" label="Nombre" />
                    <v-text-field v-model="newInst.dominio_permitido" label="Dominio permitido (ej. uni.edu)" />
                    <v-btn type="submit" color="primary" variant="flat" block>Crear</v-btn>
                  </v-form>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>

          <v-col cols="12" md="8">
            <v-card class="surface-card pa-5" rounded="xl">
              <h2 class="text-body-large font-weight-bold mb-3">Listado</h2>
              <div v-if="loading" class="d-flex align-center ga-2" role="status">
                <v-progress-circular indeterminate color="primary" size="20"></v-progress-circular>
                <span class="text-body-medium text-subtle">Cargando...</span>
              </div>
              <p v-else-if="!instituciones.length" class="text-body-medium text-subtle mb-0">Sin instituciones.</p>
              <v-list v-else density="comfortable" class="admin-list pa-0">
                <v-list-item v-for="inst in instituciones" :key="inst.id" class="mb-1">
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
                        <v-btn size="small" variant="text" @click="editInstId = ''">Cancelar</v-btn>
                      </template>
                      <v-btn v-else variant="text" size="small" @click="startInstEdit(inst)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removeInstitucion(inst)">Eliminar</v-btn>
                    </div>
                  </div>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>
      </template>

      <!-- Coordinadores -->
      <v-row v-else-if="tab === 'coordinadores'">
        <v-col cols="12" md="4">
          <v-card class="surface-card pa-5" rounded="xl">
            <h2 class="text-body-large font-weight-bold mb-3">Institución</h2>
            <v-select
              v-model="selectedInstId"
              :items="institucionOptions"
              label="Selecciona una institución"
              density="compact"
              class="mb-2"
              @update:model-value="loadCoordinadores"
            />
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
            <p v-else-if="!coordinadores.length" class="text-body-medium text-subtle mb-0">Sin coordinadores.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="c in coordinadores" :key="c.id" class="mb-1">
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
                      <v-btn size="small" variant="text" @click="editCoordId = ''">Cancelar</v-btn>
                    </template>
                    <v-btn v-else variant="text" size="small" @click="startCoordEdit(c)">Editar</v-btn>
                    <v-btn variant="text" size="small" color="warning" @click="toggleCoord(c)">{{ c.is_active ? 'Desactivar' : 'Activar' }}</v-btn>
                    <v-btn variant="text" size="small" color="error" @click="removeCoord(c)">Eliminar</v-btn>
                  </div>
                </div>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>

      <!-- Suscripciones -->
      <v-row v-else-if="tab === 'suscripciones'">
        <v-col cols="12" md="4">
          <v-expansion-panels>
            <v-expansion-panel title="Asignar suscripción" value="new-sub">
              <template #text>
                <v-form class="d-flex flex-column ga-3 pt-1" @submit.prevent="assignSuscripcion">
                  <v-select v-model="sub.institucion_id" :items="institucionOptions" label="Institución" />
                  <v-select v-model="sub.plan_id" :items="planOptions" label="Plan" />
                  <v-text-field v-model.number="sub.limite_tokens_mensual" type="number" min="0" label="Límite de tokens mensual" />
                  <v-text-field v-model="sub.fecha_fin" type="date" label="Fecha de finalización" />
                  <v-btn type="submit" color="primary" variant="flat" block>Asignar suscripción</v-btn>
                </v-form>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="surface-card pa-5" rounded="xl">
            <h2 class="text-body-large font-weight-bold mb-3">Suscripciones actuales</h2>
            <p v-if="!suscripciones.length" class="text-body-medium text-subtle mb-0">Sin suscripciones.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="s in suscripciones" :key="s.id" class="mb-2">
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
                    <v-btn variant="text" size="small" @click="editSubId = ''">Cancelar</v-btn>
                  </div>
                </v-card>
              </v-list-item>
            </v-list>
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
                  <v-btn type="submit" color="primary" variant="flat" block>Crear plan</v-btn>
                </v-form>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="surface-card pa-5" rounded="xl">
            <h2 class="text-body-large font-weight-bold mb-3">Planes disponibles</h2>
            <p v-if="!planes.length" class="text-body-medium text-subtle mb-0">Sin planes.</p>
            <v-list v-else density="comfortable" class="admin-list pa-0">
              <v-list-item v-for="p in planes" :key="p.id" class="mb-1">
                <div class="admin-row">
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
                      <v-btn size="small" variant="text" @click="editPlanId = ''">Cancelar</v-btn>
                    </template>
                    <v-btn v-else variant="text" size="small" @click="startPlanEdit(p)">Editar</v-btn>
                    <v-btn variant="text" size="small" color="error" @click="removePlan(p)">Eliminar</v-btn>
                  </div>
                </div>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>

      <ProfileSection v-show="tab === 'perfil'" @notify="toast.notify" />
    </div>

    <v-dialog v-model="showNewCoordDialog" max-width="560">
      <v-card class="surface-card" rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between ga-2">
          <span class="text-body-large font-weight-bold">Nuevo coordinador</span>
          <v-btn icon="mdi-close" variant="text" size="small" aria-label="Cerrar" @click="showNewCoordDialog = false" />
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
              <v-btn variant="text" @click="showNewCoordDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="primary" variant="flat">Crear coordinador</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </RoleLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { superAdminService } from '../services'
import { createToast } from '../composables/useToast'
import { formatDate, formatNumber, toDateInput } from '../utils/format'
import RoleLayout from '../components/RoleLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import ProfileSection from '../components/ProfileSection.vue'

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

const institucionOptions = computed(() => instituciones.value.map((i) => ({ title: i.nombre, value: i.id })))
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
  try {
    await action()
    notify(successMessage)
    await refresh()
    return true
  } catch (e) {
    notifyError(e, errorFallback)
    return false
  }
}

async function loadAll() {
  loading.value = true
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
    notifyError(e, 'No se pudieron cargar los datos')
  } finally {
    loading.value = false
  }
}

/* ---------- Instituciones ---------- */
const newInst = ref({ nombre: '', dominio_permitido: '' })
const editInstId = ref('')
const editInst = ref({ nombre: '', dominio_permitido: '' })

async function createInstitucion() {
  if (!newInst.value.nombre.trim()) return notify('El nombre es requerido', true)
  const ok = await mutate(
    () => superAdminService.createInstitucion({
      nombre: newInst.value.nombre.trim(),
      dominio_permitido: newInst.value.dominio_permitido.trim() || null,
    }),
    'Institución creada',
    'Error al crear institución',
  )
  if (ok) newInst.value = { nombre: '', dominio_permitido: '' }
}

function startInstEdit(inst) {
  editInstId.value = inst.id
  editInst.value = { nombre: inst.nombre, dominio_permitido: inst.dominio_permitido || '' }
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
  if (!window.confirm(`¿Eliminar ${inst.nombre}? Esta acción es irreversible.`)) return
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

function startPlanEdit(plan) {
  editPlanId.value = plan.id
  editPlan.value = {
    nombre: plan.nombre,
    max_cuentas: Number(plan.max_cuentas),
    max_almacenamiento_gb: Number(plan.max_almacenamiento_gb),
  }
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
  if (!window.confirm(`¿Eliminar el plan ${plan.nombre}?`)) return
  await mutate(() => superAdminService.deletePlan(plan.id), 'Plan eliminado', 'No se pudo eliminar el plan')
}

/* ---------- Suscripciones ---------- */
const emptySub = () => ({ institucion_id: null, plan_id: null, limite_tokens_mensual: null, fecha_fin: '' })
const sub = ref(emptySub())
const editSubId = ref('')
const editSub = ref({ plan_id: null, limite_tokens_mensual: 0, is_active: true, fecha_inicio: '', fecha_fin: '' })

async function assignSuscripcion() {
  if (!sub.value.institucion_id || !sub.value.plan_id) return notify('Selecciona institución y plan', true)
  if (isMissingNumber(sub.value.limite_tokens_mensual)) return notify('Límite de tokens mensual es requerido', true)

  const ok = await mutate(
    () => superAdminService.assignSuscripcion(sub.value.institucion_id, {
      plan_id: Number(sub.value.plan_id),
      limite_tokens_mensual: Number(sub.value.limite_tokens_mensual),
      fecha_fin: sub.value.fecha_fin || null,
    }),
    'Suscripción asignada',
    'Error al asignar suscripción',
  )
  if (ok) sub.value = emptySub()
}

function startSubEdit(s) {
  editSubId.value = s.id
  editSub.value = {
    plan_id: s.plan_id,
    limite_tokens_mensual: s.limite_tokens_mensual,
    is_active: s.is_active,
    fecha_inicio: toDateInput(s.fecha_inicio),
    fecha_fin: toDateInput(s.fecha_fin),
  }
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
  if (!window.confirm(`¿Eliminar la suscripción de ${institucionNombre(item.institucion_id)}?`)) return
  await mutate(() => superAdminService.deleteSuscripcion(item.institucion_id), 'Suscripción eliminada', 'No se pudo eliminar la suscripción')
}

/* ---------- Coordinadores ---------- */
const emptyCoord = () => ({ first_name: '', last_name: '', email: '', phone: '', password: '' })
const selectedInstId = ref(null)
const coordinadores = ref([])
const loadingCoordinadores = ref(false)
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
  coordinadores.value = []
  if (!selectedInstId.value) return
  loadingCoordinadores.value = true
  try {
    const resp = await superAdminService.listCoordinadores(selectedInstId.value)
    coordinadores.value = resp.coordinadores || []
  } catch (e) {
    notifyError(e, 'No se pudieron cargar los coordinadores')
  } finally {
    loadingCoordinadores.value = false
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

function startCoordEdit(c) {
  editCoordId.value = c.id
  editCoord.value = { first_name: c.first_name || '', last_name: c.last_name || '', email: c.email || '', phone: c.phone || '' }
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
  if (!window.confirm(`¿Eliminar al coordinador ${c.full_name}?`)) return
  await mutate(
    () => superAdminService.deleteCoordinador(selectedInstId.value, c.id),
    'Coordinador eliminado',
    'No se pudo eliminar el coordinador',
    loadCoordinadores,
  )
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
  border-color: rgba(var(--tutoria-green-rgb), 0.18);
  background: rgba(var(--tutoria-green-rgb), 0.06);
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

.admin-row__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
</style>
