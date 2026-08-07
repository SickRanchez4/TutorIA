<template>
  <v-app class="admin-shell">
    <v-app-bar color="surface" elevation="0" class="admin-topbar" height="76">
      <v-app-bar-title class="d-flex align-center py-2">
        <div class="d-flex align-center ga-3">
          <div class="admin-brand-mark">
            <v-icon icon="mdi-shield-crown-outline" size="21"></v-icon>
          </div>
          <div>
            <p class="text-subtitle-1 font-weight-black mb-0">Control central</p>
            <p class="admin-topbar-caption mb-0">Tutor<span>IA</span> · Super Admin</p>
          </div>
        </div>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <v-chip variant="flat" color="primary" class="mr-2 admin-user-chip" prepend-icon="mdi-account-circle-outline">
        {{ userName }}
      </v-chip>
      <v-btn variant="tonal" color="error" prepend-icon="mdi-logout" class="admin-logout" @click="logout">
        <span class="d-none d-sm-inline">Cerrar sesión</span>
        <v-tooltip activator="parent" location="bottom">Cerrar sesión</v-tooltip>
      </v-btn>

      <template #extension>
        <v-tabs v-model="tab" color="primary" align-tabs="start" class="admin-tabs">
          <v-tab value="instituciones" prepend-icon="mdi-domain">Instituciones</v-tab>
          <v-tab value="coordinadores" prepend-icon="mdi-account-tie-outline">Coordinadores</v-tab>
          <v-tab value="suscripciones" prepend-icon="mdi-card-account-details-outline">Suscripciones</v-tab>
          <v-tab value="planes" prepend-icon="mdi-package-variant-closed">Planes</v-tab>
          <v-tab value="perfil" prepend-icon="mdi-account-circle">Perfil</v-tab>
        </v-tabs>
      </template>
    </v-app-bar>

    <v-snackbar
      :model-value="!!toast"
      :color="toastError ? 'error' : 'success'"
      location="top right"
      timeout="3500"
    >
      {{ toast }}
    </v-snackbar>

    <v-main class="admin-main fade-in">
      <v-container fluid class="admin-content py-6 px-6" style="max-width: 1400px;">
        <v-card class="admin-hero mb-6" rounded="xl" variant="flat">
          <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5 px-5 px-md-6">
            <div>
              <p class="admin-overline mb-1">OPERACIÓN GLOBAL</p>
              <h1 class="text-h5 font-weight-black mb-1">Centro de control institucional</h1>
              <p class="admin-subtext mb-0">Administra instituciones, accesos, planes y suscripciones desde un solo espacio.</p>
            </div>
          </v-card-text>
        </v-card>

        <!-- Stats -->
        <v-row v-show="tab === 'instituciones'" class="mb-4">
          <v-col cols="12" sm="4">
            <v-card class="pa-5 admin-stat-card">
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Instituciones</p>
                  <p class="text-h4 font-weight-bold">{{ instituciones.length }}</p>
                </div>
                <div class="admin-stat-icon"><v-icon icon="mdi-domain" size="23"></v-icon></div>
              </div>
            </v-card>
          </v-col>
                    <v-col cols="12" sm="4">
            <v-card class="pa-5 admin-stat-card">
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Activas</p>
                  <p class="text-h4 font-weight-bold">{{ instituciones.filter(i => i.is_active).length }}</p>
                </div>
                <div class="admin-stat-icon"><v-icon icon="mdi-check-decagram-outline" size="23"></v-icon></div>
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="4">
            <v-card class="pa-5 admin-stat-card">
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Planes</p>
                  <p class="text-h4 font-weight-bold">{{ planes.length }}</p>
                </div>
                <div class="admin-stat-icon"><v-icon icon="mdi-package-variant-closed" size="23"></v-icon></div>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Instituciones -->
        <v-row v-show="tab === 'instituciones'">
          <v-col cols="12" lg="4">
            <v-expansion-panels>
              <v-expansion-panel title="+ Nueva institución" value="new-inst">
                <template #text>
                  <v-form @submit.prevent="createInstitucion" class="pa-3">
                    <v-text-field v-model="newInst.nombre" label="Nombre" class="mb-2" />
                    <v-text-field v-model="newInst.dominio_permitido" label="Dominio permitido (ej. uni.edu)" class="mb-2" />
                    <v-btn type="submit" color="primary" block>Crear</v-btn>
                  </v-form>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>

          <v-col cols="12" lg="8">
            <v-card class="pa-5" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-3">Listado</h3>
              <div v-if="loading" class="d-flex align-center ga-2">
                <v-progress-circular indeterminate color="primary" size="20"></v-progress-circular>
                <span class="text-body-2 text-medium-emphasis">Cargando...</span>
              </div>
              <p v-else-if="!instituciones.length" class="text-body-2 text-medium-emphasis">Sin instituciones.</p>
              <v-list v-else density="comfortable" class="pa-0">
                <v-list-item v-for="inst in instituciones" :key="inst.id" class="px-0 mb-1">
                  <div class="d-flex align-center justify-space-between w-100 ga-4">
                    <div class="flex-grow-1">
                      <div v-if="editInstId === inst.id" class="d-flex flex-column ga-2">
                        <v-text-field v-model="editInst.nombre" density="compact" hide-details label="Nombre" />
                        <v-text-field v-model="editInst.dominio_permitido" density="compact" hide-details label="Dominio" />
                        <div class="d-flex ga-2">
                          <v-btn size="small" color="primary" @click="saveInst(inst.id)">Guardar</v-btn>
                          <v-btn size="small" variant="text" @click="cancelInstEdit">Cancelar</v-btn>
                        </div>
                      </div>
                      <div v-else>
                        <p class="font-weight-medium mb-0">{{ inst.nombre }}</p>
                        <p class="text-caption text-medium-emphasis mb-0">{{ inst.dominio_permitido || 'sin dominio' }}</p>
                      </div>
                    </div>
                    <div class="d-flex align-center ga-2">
                      <v-chip size="small" :color="instSubColor(inst.id)" variant="tonal">{{ instSubEstado(inst.id) }}</v-chip>
                      <v-btn variant="text" size="small" @click="startInstEdit(inst)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removeInstitucion(inst)">Eliminar</v-btn>
                    </div>
                  </div>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>

        <!-- Coordinadores -->
        <v-row v-show="tab === 'coordinadores'">
          <v-col cols="12" lg="4">
            <v-card class="pa-5 mb-3" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-3">Institución</h3>
              <v-select
                v-model="selectedInstId"
                :items="instituciones.map(i => ({ title: i.nombre, value: i.id }))"
                label="Selecciona..."
                density="compact"
                class="mb-2"
                @update:model-value="loadCoordinadores"
              />
              <p v-if="selectedInstId" class="text-caption text-medium-emphasis mb-0">
                Coordinadores: {{ coordinadores.length }} / {{ coordinadoresLimit }}
              </p>
            </v-card>
          </v-col>

          <v-col cols="12" lg="8">
            <v-card class="pa-5" border elevation="1">
              <div class="d-flex align-center justify-space-between mb-3 ga-2 flex-wrap">
                <h3 class="text-subtitle-1 font-weight-bold mb-0">Coordinadores</h3>
                <v-btn
                  color="primary"
                  prepend-icon="mdi-account-plus-outline"
                  :disabled="!selectedInstId"
                  @click="showNewCoordDialog = true"
                >
                  Nuevo coordinador
                </v-btn>
              </div>
              <p v-if="!selectedInstId" class="text-body-2 text-medium-emphasis">Selecciona una institución.</p>
              <div v-else-if="loadingCoordinadores" class="admin-loading-state">
                <v-progress-circular indeterminate color="primary" size="28" width="3"></v-progress-circular>
                <div>
                  <p class="font-weight-bold mb-0">Cargando coordinadores</p>
                  <p class="text-caption text-medium-emphasis mb-0">Consultando los accesos de la institución.</p>
                </div>
              </div>
              <p v-else-if="!coordinadores.length" class="text-body-2 text-medium-emphasis">Sin coordinadores.</p>
              <v-list v-else density="comfortable" class="pa-0">
                <v-list-item v-for="c in coordinadores" :key="c.id" class="px-0 mb-1">
                  <div class="d-flex align-center justify-space-between w-100 ga-4">
                    <div class="flex-grow-1">
                      <v-row v-if="editCoordId === c.id" dense>
                        <v-col cols="6"><v-text-field v-model="editCoord.first_name" label="Nombres" density="compact" hide-details /></v-col>
                        <v-col cols="6"><v-text-field v-model="editCoord.last_name" label="Apellidos" density="compact" hide-details /></v-col>
                        <v-col cols="6"><v-text-field v-model="editCoord.email" label="Correo electrónico" density="compact" hide-details /></v-col>
                        <v-col cols="6"><v-text-field v-model="editCoord.phone" label="Teléfono" density="compact" hide-details /></v-col>
                      </v-row>
                      <div v-else>
                        <p class="font-weight-medium mb-0">{{ c.full_name }}</p>
                        <p class="text-caption text-medium-emphasis mb-0">{{ c.email }} · {{ c.phone }}</p>
                      </div>
                    </div>

                    <div class="d-flex align-center ga-2">
                      <v-chip size="small" :color="c.is_active ? 'success' : 'default'" variant="tonal">
                        {{ c.is_active ? 'activo' : 'inactivo' }}
                      </v-chip>
                      <v-btn v-if="editCoordId === c.id" variant="text" size="small" color="primary" @click="saveCoord(c.id)">Guardar</v-btn>
                      <v-btn v-if="editCoordId === c.id" variant="text" size="small" @click="cancelCoordEdit">Cancelar</v-btn>
                      <v-btn v-if="editCoordId !== c.id" variant="text" size="small" @click="startCoordEdit(c)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="warning" @click="toggleCoord(c)">{{ c.is_active ? 'Desactivar' : 'Activar' }}</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removeCoord(c)">Eliminar</v-btn>
                    </div>
                  </div>
                </v-list-item>
              </v-list>
            </v-card>

            <v-dialog v-model="showNewCoordDialog" max-width="560">
              <v-card border>
                <v-card-title class="d-flex align-center justify-space-between ga-2">
                  <span class="text-subtitle-1 font-weight-bold">Nuevo coordinador</span>
                  <v-btn icon="mdi-close" variant="text" size="small" @click="showNewCoordDialog = false" />
                </v-card-title>
                <v-card-text>
                  <v-form @submit.prevent="createCoordinador" class="pa-1">
                    <v-text-field v-model="newCoord.first_name" label="Nombres" density="compact" class="mb-2" />
                    <v-text-field v-model="newCoord.last_name" label="Apellidos" density="compact" class="mb-2" />
                    <v-text-field v-model="newCoord.email" label="Correo" density="compact" class="mb-2" />
                    <v-text-field v-model="newCoord.phone" label="Teléfono" density="compact" class="mb-3" />
                    <div class="d-flex justify-end ga-2">
                      <v-btn variant="text" @click="showNewCoordDialog = false">Cancelar</v-btn>
                      <v-btn type="submit" color="primary">Crear coordinador</v-btn>
                    </div>
                  </v-form>
                </v-card-text>
              </v-card>
            </v-dialog>
          </v-col>
        </v-row>

        <!-- Planes -->
        <v-row v-show="tab === 'planes'">
          <v-col cols="12" lg="4">
            <v-expansion-panels>
              <v-expansion-panel title="+ Nuevo plan" value="new-plan">
                <template #text>
                  <v-form @submit.prevent="createPlan" class="pa-3">
                    <v-text-field v-model="newPlan.nombre" label="Nombre del plan" class="mb-2" />
                    <v-text-field v-model.number="newPlan.max_cuentas" type="number" min="1" label="Máx. cuentas" class="mb-2" />
                    <v-text-field v-model.number="newPlan.max_almacenamiento_gb" type="number" min="1" label="Máx. almacenamiento (GB)" class="mb-2" />
                    <v-btn type="submit" color="primary" block>Crear plan</v-btn>
                  </v-form>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>

          <v-col cols="12" lg="8">
            <v-card class="pa-5" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-3">Planes disponibles</h3>
              <p v-if="!planes.length" class="text-body-2 text-medium-emphasis">Sin planes.</p>
              <v-list v-else density="comfortable" class="pa-0">
                <v-list-item v-for="p in planes" :key="p.id" class="px-0 mb-1">
                  <div class="d-flex align-center justify-space-between w-100 ga-4">
                    <div class="flex-grow-1">
                      <v-row v-if="editPlanId === p.id" dense>
                        <v-col cols="4"><v-text-field v-model="editPlan.nombre" label="Nombre del plan" density="compact" hide-details /></v-col>
                        <v-col cols="4"><v-text-field v-model.number="editPlan.max_cuentas" type="number" min="1" label="Máx. cuentas" density="compact" hide-details /></v-col>
                        <v-col cols="4"><v-text-field v-model.number="editPlan.max_almacenamiento_gb" type="number" min="1" label="Máx. GB" density="compact" hide-details /></v-col>
                      </v-row>
                      <div v-else>
                        <p class="font-weight-medium mb-0">{{ p.nombre }}</p>
                        <p class="text-caption text-medium-emphasis mb-0">{{ p.max_cuentas }} cuentas · {{ p.max_almacenamiento_gb }} GB</p>
                      </div>
                    </div>
                    <div class="d-flex align-center ga-2">
                      <v-btn v-if="editPlanId === p.id" variant="text" size="small" color="primary" @click="savePlan(p.id)">Guardar</v-btn>
                      <v-btn v-if="editPlanId === p.id" variant="text" size="small" @click="cancelPlanEdit">Cancelar</v-btn>
                      <v-btn v-if="editPlanId !== p.id" variant="text" size="small" @click="startPlanEdit(p)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removePlan(p)">Eliminar</v-btn>
                    </div>
                  </div>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>

        <!-- Suscripciones -->
        <v-row v-show="tab === 'suscripciones'">
          <v-col cols="12" lg="4">
            <v-expansion-panels>
              <v-expansion-panel title="+ Asignar suscripción" value="new-sub">
                <template #text>
                  <v-form @submit.prevent="assignSuscripcion" class="pa-3">
                    <v-select
                      v-model="sub.institucion_id"
                      :items="instituciones.map(i => ({ title: i.nombre, value: i.id }))"
                      label="Institución"
                      class="mb-2"
                    />
                    <v-select
                      v-model="sub.plan_id"
                      :items="planes.map(p => ({ title: p.nombre, value: p.id }))"
                      label="Plan"
                      class="mb-2"
                    />
                    <v-text-field
                      v-model.number="sub.limite_tokens_mensual"
                      type="number"
                      min="0"
                      label="Límite de tokens mensual"
                      class="mb-2"
                    />
                    <v-text-field
                      v-model="sub.fecha_fin"
                      type="date"
                      label="Fecha de finalización"
                      class="mb-2"
                    />
                    <v-btn type="submit" color="primary" block>Asignar suscripción</v-btn>
                  </v-form>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>

          <v-col cols="12" lg="8">
            <v-card class="pa-5" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-3">Suscripciones actuales</h3>
              <p v-if="!suscripciones.length" class="text-body-2 text-medium-emphasis">Sin suscripciones.</p>
              <v-list v-else density="comfortable" class="pa-0">
                <v-list-item v-for="s in suscripciones" :key="s.id" class="px-0 mb-2">
                  <div v-if="editSubId !== s.id" class="d-flex align-center justify-space-between w-100 ga-4">
                    <div>
                      <p class="text-body-2 font-weight-medium mb-0">{{ institucionNombre(s.institucion_id) }}</p>
                      <p class="text-caption text-medium-emphasis mb-0">{{ planNombre(s.plan_id) }} · {{ s.limite_tokens_mensual?.toLocaleString() }} tokens/mes</p>
                      <p class="text-caption text-medium-emphasis mb-0">Inicio: {{ formatFecha(s.fecha_inicio) }} · Fin: {{ formatFecha(s.fecha_fin) }}</p>
                    </div>
                    <div class="d-flex align-center ga-2">
                      <v-chip size="small" :color="s.is_active ? 'success' : 'default'" variant="tonal">{{ s.is_active ? 'Activa' : 'Inactiva' }}</v-chip>
                      <v-btn variant="text" size="small" @click="startSubEdit(s)">Editar</v-btn>
                      <v-btn variant="text" size="small" color="error" @click="removeSuscripcion(s)">Eliminar</v-btn>
                    </div>
                  </div>
                  <v-card v-else class="pa-4 w-100" variant="tonal" color="primary" border>
                    <p class="text-body-2 font-weight-bold mb-3">Editar suscripción de {{ institucionNombre(s.institucion_id) }}</p>
                    <v-row dense>
                      <v-col cols="12" md="6">
                        <v-select
                          v-model.number="editSub.plan_id"
                          :items="planes.map(p => ({ title: p.nombre, value: p.id }))"
                          label="Plan"
                          density="compact"
                        />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field v-model.number="editSub.limite_tokens_mensual" type="number" min="0" label="Límite de tokens mensual" density="compact" />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field :model-value="formatFechaInput(editSub.fecha_inicio)" type="date" label="Fecha de inicio" density="compact" readonly />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field v-model="editSub.fecha_fin" type="date" label="Fecha de finalización" density="compact" />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-select
                          v-model="editSub.is_active"
                          :items="[{ title: 'Activa', value: true }, { title: 'Inactiva', value: false }]"
                          label="Estado"
                          density="compact"
                        />
                      </v-col>
                    </v-row>
                    <div class="d-flex ga-2 mt-2">
                      <v-btn color="primary" size="small" @click="saveSuscripcion(s)">Guardar</v-btn>
                      <v-btn variant="tonal" size="small" @click="cancelSubEdit">Cancelar</v-btn>
                    </div>
                  </v-card>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>

        <!-- Perfil -->
        <v-row v-show="tab === 'perfil'">
          <v-col cols="12" md="6">
            <v-card class="pa-5" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-4">Mi Perfil</h3>
              <v-form @submit.prevent="updateProfile" class="mb-4">
                <v-text-field v-model="profileData.first_name" label="Nombres" class="mb-2" />
                <v-text-field v-model="profileData.last_name" label="Apellidos" class="mb-2" />
                <v-text-field v-model="profileData.phone" label="Telefono" class="mb-3" />
                <v-btn type="submit" color="primary" block>Guardar cambios</v-btn>
              </v-form>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card class="pa-5" border elevation="1">
              <h3 class="text-subtitle-1 font-weight-bold mb-4">Cambiar Contrasena</h3>
              <v-form @submit.prevent="updatePassword">
                <v-text-field v-model="passwordForm.current" type="password" label="Contrasena actual" class="mb-2" />
                <v-text-field v-model="passwordForm.new" type="password" label="Nueva contrasena" class="mb-2" />
                <v-text-field v-model="passwordForm.confirm" type="password" label="Confirmar nueva contrasena" class="mb-3" />
                <v-btn type="submit" color="primary" block>Cambiar contrasena</v-btn>
              </v-form>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { superAdminService } from '../services'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const instituciones = ref([])
const planes = ref([])
const suscripciones = ref([])
const coordinadores = ref([])
const loading = ref(false)
const loadingCoordinadores = ref(false)
const toast = ref('')
const toastError = ref(false)

// Profile & Password
const profileData = ref({ first_name: '', last_name: '', phone: '' })
const passwordForm = ref({ current: '', new: '', confirm: '' })

function notify(msg, isError = false) {
  toast.value = msg
  toastError.value = isError
  setTimeout(() => { toast.value = '' }, 3500)
}

function logout() {
  authStore.logout()
  router.push('/login')
}

async function loadAll() {
  loading.value = true
  try {
    const [instResp, planesResp, subsResp] = await Promise.all([
      superAdminService.listInstituciones(),
      superAdminService.listPlanes(),
      superAdminService.listSuscripciones()
    ])
    instituciones.value = instResp.instituciones || []
    planes.value = planesResp.planes || []
    suscripciones.value = subsResp.suscripciones || []
    if (selectedInstId.value) {
      await loadCoordinadores()
    }
  } catch (err) {
    notify('No se pudieron cargar los datos', true)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAll()
  loadProfile()
})

/* ---------- Instituciones ---------- */
const newInst = ref({ nombre: '', dominio_permitido: '' })
const editInstId = ref('')
const editInst = ref({ nombre: '', dominio_permitido: '' })

async function createInstitucion() {
  if (!newInst.value.nombre.trim()) return notify('El nombre es requerido', true)
  try {
    await superAdminService.createInstitucion({
      nombre: newInst.value.nombre.trim(),
      dominio_permitido: newInst.value.dominio_permitido.trim() || null
    })
    newInst.value = { nombre: '', dominio_permitido: '' }
    notify('Institución creada')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'Error al crear institución', true)
  }
}

function startInstEdit(inst) {
  editInstId.value = inst.id
  editInst.value = {
    nombre: inst.nombre || '',
    dominio_permitido: inst.dominio_permitido || ''
  }
}

function cancelInstEdit() {
  editInstId.value = ''
  editInst.value = { nombre: '', dominio_permitido: '' }
}

async function saveInst(id) {
  try {
    await superAdminService.updateInstitucion(id, {
      nombre: editInst.value.nombre,
      dominio_permitido: editInst.value.dominio_permitido || null
    })
    notify('Institución actualizada')
    cancelInstEdit()
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo actualizar la institución', true)
  }
}

async function removeInstitucion(inst) {
  if (!window.confirm(`Eliminar ${inst.nombre}? Esta acción es irreversible.`)) return
  try {
    await superAdminService.deleteInstitucion(inst.id)
    notify('Institución eliminada')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo eliminar la institución', true)
  }
}

async function toggleActive(inst) {
  try {
    await superAdminService.toggleActive(inst.id)
    notify('Estado actualizado')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo cambiar el estado', true)
  }
}

/* ---------- CU-02: Planes ---------- */
const newPlan = ref({ nombre: '', max_cuentas: null, max_almacenamiento_gb: null })
const editPlanId = ref('')
const editPlan = ref({ nombre: '', max_cuentas: 0, max_almacenamiento_gb: 0 })

async function createPlan() {
  if (!newPlan.value.nombre.trim()) return notify('El nombre del plan es requerido', true)
  if (newPlan.value.max_cuentas == null || Number.isNaN(Number(newPlan.value.max_cuentas))) {
    return notify('Máx. cuentas es requerido', true)
  }
  if (newPlan.value.max_almacenamiento_gb == null || Number.isNaN(Number(newPlan.value.max_almacenamiento_gb))) {
    return notify('Máx. almacenamiento es requerido', true)
  }
  try {
    await superAdminService.createPlan({
      nombre: newPlan.value.nombre.trim(),
      max_cuentas: Number(newPlan.value.max_cuentas),
      max_almacenamiento_gb: Number(newPlan.value.max_almacenamiento_gb)
    })
    newPlan.value = { nombre: '', max_cuentas: null, max_almacenamiento_gb: null }
    notify('Plan creado')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'Error al crear plan', true)
  }
}

function startPlanEdit(plan) {
  editPlanId.value = plan.id
  editPlan.value = {
    nombre: plan.nombre,
    max_cuentas: Number(plan.max_cuentas),
    max_almacenamiento_gb: Number(plan.max_almacenamiento_gb)
  }
}

function cancelPlanEdit() {
  editPlanId.value = ''
  editPlan.value = { nombre: '', max_cuentas: 0, max_almacenamiento_gb: 0 }
}

async function savePlan(id) {
  try {
    await superAdminService.updatePlan(id, {
      nombre: editPlan.value.nombre,
      max_cuentas: Number(editPlan.value.max_cuentas),
      max_almacenamiento_gb: Number(editPlan.value.max_almacenamiento_gb)
    })
    notify('Plan actualizado')
    cancelPlanEdit()
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo actualizar el plan', true)
  }
}

async function removePlan(plan) {
  if (!window.confirm(`Eliminar plan ${plan.nombre}?`)) return
  try {
    await superAdminService.deletePlan(plan.id)
    notify('Plan eliminado')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo eliminar el plan', true)
  }
}

/* ---------- Suscripciones ---------- */
const sub = ref({ institucion_id: '', plan_id: '', limite_tokens_mensual: null, fecha_fin: '' })

async function assignSuscripcion() {
  if (!sub.value.institucion_id || !sub.value.plan_id) {
    return notify('Selecciona institución y plan', true)
  }
  if (sub.value.limite_tokens_mensual == null || Number.isNaN(Number(sub.value.limite_tokens_mensual))) {
    return notify('Límite de tokens mensual es requerido', true)
  }
  try {
    await superAdminService.assignSuscripcion(sub.value.institucion_id, {
      plan_id: Number(sub.value.plan_id),
      limite_tokens_mensual: Number(sub.value.limite_tokens_mensual),
      fecha_fin: sub.value.fecha_fin || null
    })
    notify('Suscripción asignada')
    sub.value = { institucion_id: '', plan_id: '', limite_tokens_mensual: null, fecha_fin: '' }
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'Error al asignar suscripción', true)
  }
}

const editSubId = ref('')
const editSub = ref({ plan_id: '', limite_tokens_mensual: 0, is_active: true, fecha_inicio: '', fecha_fin: '' })

function startSubEdit(s) {
  editSubId.value = s.id
  editSub.value = {
    plan_id: s.plan_id,
    limite_tokens_mensual: s.limite_tokens_mensual,
    is_active: s.is_active,
    fecha_inicio: formatFechaInput(s.fecha_inicio),
    fecha_fin: formatFechaInput(s.fecha_fin)
  }
}

function cancelSubEdit() {
  editSubId.value = ''
  editSub.value = { plan_id: '', limite_tokens_mensual: 0, is_active: true, fecha_inicio: '', fecha_fin: '' }
}

async function saveSuscripcion(item) {
  try {
    await superAdminService.updateSuscripcion(item.institucion_id, {
      plan_id: Number(editSub.value.plan_id),
      limite_tokens_mensual: Number(editSub.value.limite_tokens_mensual),
      fecha_fin: editSub.value.fecha_fin || null,
      is_active: editSub.value.is_active === true || editSub.value.is_active === 'true'
    })
    notify('Suscripción actualizada')
    cancelSubEdit()
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo actualizar la suscripción', true)
  }
}

async function removeSuscripcion(item) {
  if (!window.confirm(`Eliminar suscripción de ${institucionNombre(item.institucion_id)}?`)) return
  try {
    await superAdminService.deleteSuscripcion(item.institucion_id)
    notify('Suscripción eliminada')
    await loadAll()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo eliminar la suscripción', true)
  }
}

/* ---------- Coordinadores ---------- */
const selectedInstId = ref('')
const newCoord = ref({ first_name: '', last_name: '', email: '', phone: '' })
const editCoordId = ref('')
const editCoord = ref({ first_name: '', last_name: '', email: '', phone: '' })
const showNewCoordDialog = ref(false)

const coordinadoresLimit = computed(() => {
  if (!selectedInstId.value) return 0
  const subItem = suscripciones.value.find(s => s.institucion_id === selectedInstId.value && s.is_active)
  if (!subItem) return 0
  const plan = planes.value.find(p => p.id === subItem.plan_id)
  return plan ? Number(plan.max_cuentas) : 0
})

async function loadCoordinadores() {
  if (!selectedInstId.value) {
    coordinadores.value = []
    loadingCoordinadores.value = false
    return
  }
  loadingCoordinadores.value = true
  try {
    const resp = await superAdminService.listCoordinadores(selectedInstId.value)
    coordinadores.value = resp.coordinadores || []
  } catch (err) {
    coordinadores.value = []
    notify(err.response?.data?.message || 'No se pudieron cargar coordinadores', true)
  } finally {
    loadingCoordinadores.value = false
  }
}

async function createCoordinador() {
  if (!selectedInstId.value) return notify('Selecciona una institución', true)
  try {
    await superAdminService.createCoordinador(selectedInstId.value, { ...newCoord.value })
    notify('Coordinador creado exitosamente')
    newCoord.value = { first_name: '', last_name: '', email: '', phone: '' }
    showNewCoordDialog.value = false
    await loadCoordinadores()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo crear el coordinador', true)
  }
}

function startCoordEdit(c) {
  editCoordId.value = c.id
  editCoord.value = {
    first_name: c.first_name,
    last_name: c.last_name,
    email: c.email,
    phone: c.phone
  }
}

function cancelCoordEdit() {
  editCoordId.value = ''
  editCoord.value = { first_name: '', last_name: '', email: '', phone: '' }
}

async function saveCoord(userId) {
  try {
    await superAdminService.updateCoordinador(selectedInstId.value, userId, { ...editCoord.value })
    notify('Coordinador actualizado')
    cancelCoordEdit()
    await loadCoordinadores()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo actualizar el coordinador', true)
  }
}

async function toggleCoord(c) {
  try {
    await superAdminService.updateCoordinador(selectedInstId.value, c.id, { is_active: !c.is_active })
    notify('Estado de coordinador actualizado')
    await loadCoordinadores()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo actualizar el estado', true)
  }
}

async function removeCoord(c) {
  if (!window.confirm(`Eliminar coordinador ${c.full_name}?`)) return
  try {
    await superAdminService.deleteCoordinador(selectedInstId.value, c.id)
    notify('Coordinador eliminado')
    await loadCoordinadores()
  } catch (err) {
    notify(err.response?.data?.message || 'No se pudo eliminar el coordinador', true)
  }
}

const tab = ref('instituciones')

function instSubEstado(instId) {
  const sub = suscripciones.value.find(s => s.institucion_id === instId)
  if (!sub) return 'sin suscripción'
  return sub.is_active ? 'activa' : 'suspendida'
}

function instSubColor(instId) {
  const estado = instSubEstado(instId)
  return {
    'activa': 'success',
    'suspendida': 'warning',
    'sin suscripción': 'default',
  }[estado] || 'default'
}

function formatFecha(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('es-BO')
}

function formatFechaInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toISOString().slice(0, 10)
}

const institucionNombre = (id) => instituciones.value.find(i => i.id === id)?.nombre || '—'
const planNombre = (id) => planes.value.find(p => p.id === id)?.nombre || '—'
const userName = computed(() => authStore.user?.full_name || authStore.user?.name || authStore.user?.email)

/* ---------- Perfil ---------- */
async function loadProfile() {
  try {
    const resp = await superAdminService.getProfile()
    if (resp.user) {
      profileData.value = {
        first_name: resp.user.first_name,
        last_name: resp.user.last_name,
        phone: resp.user.phone || ''
      }
    }
  } catch (err) {
    console.error('Error al cargar perfil:', err)
  }
}

async function updateProfile() {
  try {
    const resp = await superAdminService.updateProfile({
      first_name: profileData.value.first_name,
      last_name: profileData.value.last_name,
      phone: profileData.value.phone
    })
    authStore.setUserData(resp.user)
    notify('Perfil actualizado exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al actualizar perfil', true)
  }
}

async function updatePassword() {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    return notify('Las nuevas contrasenas no coinciden', true)
  }
  if (passwordForm.value.new.length < 8) {
    return notify('La contrasena debe tener al menos 8 caracteres', true)
  }
  
  try {
    await superAdminService.updatePassword({
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.new
    })
    passwordForm.value = { current: '', new: '', confirm: '' }
    notify('Contrasena actualizada exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al cambiar contrasena', true)
  }
}</script>

<style scoped>
.admin-shell {
  background:
    radial-gradient(circle at 9% 0%, rgba(124, 197, 118, 0.2), transparent 30%),
    radial-gradient(circle at 96% 12%, rgba(124, 197, 118, 0.12), transparent 26%),
    linear-gradient(140deg, #252830 0%, #2d313a 55%, #383c46 100%);
}

.admin-main { background: transparent; }

.admin-content { animation: admin-content-in 0.42s ease-out both; }

.admin-topbar {
  border-bottom: 1px solid rgba(124, 197, 118, 0.18) !important;
  background: rgba(48, 52, 61, 0.88) !important;
  backdrop-filter: blur(16px);
}

.admin-brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid rgba(150, 227, 144, 0.38);
  border-radius: 13px;
  color: #abeca3;
  background: linear-gradient(145deg, rgba(124, 197, 118, 0.22), rgba(124, 197, 118, 0.07));
  box-shadow: 0 0 20px rgba(124, 197, 118, 0.2);
}

.admin-topbar-caption {
  color: rgba(231, 241, 231, 0.54);
  font-size: 0.67rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.admin-topbar-caption span, .admin-overline { color: #9be692; }

.admin-user-chip {
  color: #132313 !important;
  font-weight: 800;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.22);
}

.admin-logout {
  border: 1px solid rgba(255, 128, 128, 0.26);
  border-radius: 11px;
  font-weight: 750;
}

.admin-tabs { padding-inline: 16px; }

.admin-tabs :deep(.v-tab) {
  min-height: 46px;
  border-radius: 10px 10px 0 0;
  color: rgba(231, 238, 231, 0.64);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.admin-tabs :deep(.v-tab--selected) {
  color: #b4efa9;
  background: rgba(124, 197, 118, 0.08);
}

.admin-hero, .admin-content :deep(.v-card) {
  border: 1px solid rgba(124, 197, 118, 0.18) !important;
  background: linear-gradient(145deg, rgba(58, 63, 73, 0.97), rgba(47, 52, 61, 0.97)) !important;
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(10px);
}

.admin-hero {
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 25%, rgba(124, 197, 118, 0.27), transparent 40%),
    linear-gradient(145deg, #383d46 0%, #454b56 100%) !important;
}

.admin-overline {
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.admin-subtext { color: rgba(229, 238, 229, 0.67); font-size: 0.88rem; }

.admin-hero-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 11px;
  border: 1px solid rgba(124, 197, 118, 0.25);
  border-radius: 999px;
  color: #b0eaa9;
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(124, 197, 118, 0.09);
}

.admin-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8ee486;
  box-shadow: 0 0 0 0 rgba(142, 228, 134, 0.58);
  animation: admin-pulse 1.9s ease-out infinite;
}

.admin-stat-card {
  min-height: 122px;
  overflow: hidden;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
}

.admin-stat-card:hover {
  border-color: rgba(124, 197, 118, 0.38) !important;
  box-shadow: 0 0 24px rgba(124, 197, 118, 0.15) !important;
  transform: translateY(-3px);
}

.admin-stat-icon {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border: 1px solid rgba(124, 197, 118, 0.25);
  border-radius: 14px;
  color: #a6e99e;
  background: rgba(124, 197, 118, 0.11);
}

.admin-content :deep(.v-expansion-panel) {
  border: 1px solid rgba(124, 197, 118, 0.2) !important;
  border-radius: 16px !important;
  color: inherit !important;
  background: linear-gradient(145deg, rgba(57, 62, 72, 0.97), rgba(46, 51, 60, 0.97)) !important;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.admin-content :deep(.v-expansion-panel-title) { color: #f0f5ef; font-weight: 750; }

.admin-content :deep(.v-list-item) {
  padding: 12px !important;
  border: 1px solid transparent;
  border-radius: 13px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.admin-content :deep(.v-list-item:hover) {
  border-color: rgba(124, 197, 118, 0.18);
  background: rgba(124, 197, 118, 0.06);
}

.admin-content :deep(.v-btn.bg-primary) {
  color: #fff !important;
  font-weight: 750;
  background: linear-gradient(140deg, #7cc576 0%, #609f5b 100%) !important;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.22);
}

.admin-content :deep(.v-field--variant-outlined),
.admin-content :deep(.v-field--variant-filled),
.admin-content :deep(.v-field--variant-solo-filled) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
}

.admin-content :deep(.v-chip) { font-weight: 700; }

.admin-loading-state {
  display: flex;
  align-items: center;
  gap: 13px;
  min-height: 120px;
  padding: 20px;
  border: 1px dashed rgba(124, 197, 118, 0.3);
  border-radius: 14px;
  background: rgba(124, 197, 118, 0.06);
}

@keyframes admin-content-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes admin-pulse {
  70% { box-shadow: 0 0 0 8px rgba(142, 228, 134, 0); }
  100% { box-shadow: 0 0 0 0 rgba(142, 228, 134, 0); }
}

@media (max-width: 600px) {
  .admin-content { padding: 20px !important; }
  .admin-tabs { padding-inline: 4px; overflow-x: auto; }
  .admin-tabs :deep(.v-tab) { font-size: 0.7rem; padding-inline: 11px; }
  .admin-user-chip { max-width: 150px; }
  .admin-hero-status { width: 100%; justify-content: center; }
}
</style>

