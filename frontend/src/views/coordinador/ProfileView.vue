<template>
  <div class="coord-profile-view">
    <v-card class="coord-hero" rounded="xl" variant="flat">
      <v-card-text class="d-flex align-center justify-space-between flex-wrap ga-4 py-5">
        <div>
          <p class="text-overline mb-1 coord-overline">Cuenta</p>
          <h2 class="text-h5 font-weight-black mb-1">Perfil de coordinador</h2>
          <p class="mb-0 coord-subtext">Actualiza tus datos y seguridad de acceso desde una única sección.</p>
        </div>
        <v-chip color="primary" variant="tonal" size="small" prepend-icon="mdi-shield-check-outline">
          Perfil protegido
        </v-chip>
      </v-card-text>
    </v-card>

    <div v-if="loading" class="coord-loading d-flex flex-column align-center justify-center py-16 ga-3">
      <v-progress-circular indeterminate color="primary" size="40" width="4" />
      <p class="text-body-2 coord-subtext mb-0">Cargando perfil...</p>
    </div>

    <v-card v-else class="coord-surface-card" rounded="xl" variant="flat">
      <v-card-text class="pa-5">
        <ProfileSection
          :profile="profileData"
          @update-profile="updateProfile"
          @update-password="updatePassword"
          @notify="notify"
        />
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { coordinadorService } from '../../services'
import ProfileSection from '../../components/ProfileSection.vue'
import { useAuthStore } from '../../stores/auth'
import { useCoordinadorToast } from './useCoordinadorToast'

const authStore = useAuthStore()
const { notify: toastNotify } = useCoordinadorToast()
const profileData = ref({ first_name: '', last_name: '', phone: '' })
const loading = ref(true)

function notify(payload, isError = false) {
  if (typeof payload === 'object' && payload !== null) {
    toastNotify(payload.message, !!payload.isError)
    return
  }
  toastNotify(payload, isError)
}

async function loadProfile() {
  loading.value = true
  try {
    const resp = await coordinadorService.getProfile()
    if (resp.user) {
      profileData.value = {
        first_name: resp.user.first_name,
        last_name: resp.user.last_name,
        phone: resp.user.phone || ''
      }
    }
  } catch (err) {
    console.error('Error al cargar perfil:', err)
  } finally {
    loading.value = false
  }
}

async function updateProfile(data) {
  try {
    const resp = await coordinadorService.updateProfile(data)
    authStore.setUserData(resp.user)
    notify('Perfil actualizado exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al actualizar perfil', true)
  }
}

async function updatePassword(data) {
  try {
    await coordinadorService.updatePassword(data)
    notify('Contrasena actualizada exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al cambiar contrasena', true)
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.coord-profile-view {
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

.coord-surface-card :deep(.v-card) {
  border-radius: 14px;
}

.coord-surface-card :deep(.v-btn.bg-primary) {
  color: #ffffff !important;
  background: linear-gradient(140deg, #7cc576 0%, #609f5b 100%) !important;
  font-weight: 700;
  box-shadow: 0 0 18px rgba(124, 197, 118, 0.24);
}
</style>
