<template>
  <div v-if="loading" class="empty-state surface-card profile-loading" role="status">
    <v-progress-circular indeterminate color="primary" size="36" width="4" />
    <span>Cargando perfil...</span>
  </div>

  <v-row v-else>
    <v-col cols="12" md="6">
      <v-card class="surface-card pa-5 h-100" rounded="xl">
        <h2 class="text-body-large font-weight-bold mb-4">Mi perfil</h2>
        <v-form class="d-flex flex-column ga-3" @submit.prevent="saveProfile">
          <v-text-field v-model="profile.first_name" label="Nombres" autocomplete="given-name" />
          <v-text-field v-model="profile.last_name" label="Apellidos" autocomplete="family-name" />
          <v-text-field v-model="profile.phone" label="Teléfono" type="tel" autocomplete="tel" />
          <v-btn type="submit" color="primary" variant="flat" block :loading="savingProfile">Guardar cambios</v-btn>
        </v-form>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="surface-card pa-5 h-100" rounded="xl">
        <h2 class="text-body-large font-weight-bold mb-4">Cambiar contraseña</h2>
        <v-form class="d-flex flex-column ga-3" @submit.prevent="savePassword">
          <v-text-field
            v-model="passwords.current"
            label="Contraseña actual"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="current-password"
          />
          <v-text-field
            v-model="passwords.next"
            label="Nueva contraseña"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="new-password"
          />
          <v-text-field
            v-model="passwords.confirm"
            label="Confirmar nueva contraseña"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="new-password"
          />
          <v-checkbox v-model="showPasswords" label="Mostrar contraseñas" />
          <v-btn type="submit" color="primary" variant="flat" block :loading="savingPassword">Cambiar contraseña</v-btn>
        </v-form>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { authService } from '../services'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../composables/useToast'

/** Self-contained "my profile" panel shared by every role. */
const emit = defineEmits(['notify'])

const authStore = useAuthStore()
const loading = ref(true)
const savingProfile = ref(false)
const savingPassword = ref(false)
const showPasswords = ref(false)
const profile = reactive({ first_name: '', last_name: '', phone: '' })
const passwords = reactive({ current: '', next: '', confirm: '' })

function notify(message, isError = false) {
  emit('notify', message, isError)
}

function fillProfile(user) {
  profile.first_name = user?.first_name || ''
  profile.last_name = user?.last_name || ''
  profile.phone = user?.phone || ''
}

async function loadProfile() {
  loading.value = true
  try {
    const resp = await authService.getProfile()
    fillProfile(resp.user)
  } catch (e) {
    notify(errorMessage(e, 'No se pudo cargar tu perfil'), true)
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  savingProfile.value = true
  try {
    const resp = await authService.updateProfile({ ...profile })
    authStore.setUserData(resp.user)
    notify('Perfil actualizado')
  } catch (e) {
    notify(errorMessage(e, 'No se pudo actualizar el perfil'), true)
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  if (passwords.next !== passwords.confirm) return notify('Las contraseñas nuevas no coinciden', true)
  if (passwords.next.length < 8) return notify('La contraseña debe tener al menos 8 caracteres', true)

  savingPassword.value = true
  try {
    await authService.updatePassword({ current_password: passwords.current, new_password: passwords.next })
    Object.assign(passwords, { current: '', next: '', confirm: '' })
    notify('Contraseña actualizada')
  } catch (e) {
    notify(errorMessage(e, 'No se pudo cambiar la contraseña'), true)
  } finally {
    savingPassword.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-loading {
  min-height: 220px;
}
</style>
