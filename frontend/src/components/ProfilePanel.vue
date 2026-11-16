<template>
  <div>
    <v-card class="surface-card pa-5 mb-6" rounded="xl">
      <v-row align="center">
        <v-col cols="12" md="6">
          <h2 class="text-body-large font-weight-bold mb-2">Apariencia</h2>
          <p class="text-body-medium text-subtle">Elige el tema de este navegador. Los cambios se aplican al instante.</p>
        </v-col>
        <v-col cols="12" md="6">
          <AppearanceSelector :model-value="appearance.selection" @update:model-value="setAppearance" />
        </v-col>
      </v-row>
    </v-card>
    <ProfileSection
      v-model:profile="profile"
      v-model:passwords="passwords"
      :loading="loading"
      :error="loadError"
      :saving-profile="savingProfile"
      :saving-password="savingPassword"
      @retry="loadProfile"
      @save-profile="saveProfile"
      @save-password="savePassword"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ProfileSection from './ProfileSection.vue'
import AppearanceSelector from './AppearanceSelector.vue'
import { useAppearance } from '../composables/useAppearance'
import { authService } from '../services'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../composables/useToast'
import { useFormDraft } from '../composables/useUnsavedChanges'

const emit = defineEmits(['notify'])
const { appearance, setAppearance } = useAppearance()
const auth = useAuthStore()
const token = auth.token
const loading = ref(true)
const loadError = ref('')
const savingProfile = ref(false)
const savingPassword = ref(false)
const profile = ref({ first_name: '', last_name: '', phone: '' })
const passwords = ref({ current: '', next: '', confirm: '' })
const profileDraft = useFormDraft(() => profile.value, () => !loading.value && !loadError.value, () => savingProfile.value)
const passwordDraft = useFormDraft(() => passwords.value, () => true, () => savingPassword.value)

async function loadProfile() {
  loading.value = true
  loadError.value = ''
  try {
    const response = await authService.getProfile()
    if (auth.token !== token) return
    for (const key of Object.keys(profile.value)) profile.value[key] = response.user?.[key] || ''
    profileDraft.accept()
  } catch (error) {
    if (auth.token === token) loadError.value = errorMessage(error, 'No se pudo cargar tu perfil')
  } finally { loading.value = false }
}
async function saveProfile() {
  if (savingProfile.value) return
  savingProfile.value = true
  try {
    const response = await authService.updateProfile({ ...profile.value })
    if (auth.token !== token) return
    auth.setUserData(response.user)
    profileDraft.accept()
    emit('notify', 'Perfil actualizado')
  } catch (error) {
    if (auth.token === token) emit('notify', errorMessage(error, 'No se pudo actualizar el perfil'), true)
  } finally { savingProfile.value = false }
}
async function savePassword() {
  if (savingPassword.value) return
  if (passwords.value.next !== passwords.value.confirm) return emit('notify', 'Las contraseñas nuevas no coinciden', true)
  if (passwords.value.next.length < 8) return emit('notify', 'La contraseña debe tener al menos 8 caracteres', true)
  savingPassword.value = true
  try {
    await authService.updatePassword({ current_password: passwords.value.current, new_password: passwords.value.next })
    if (auth.token !== token) return
    passwords.value = { current: '', next: '', confirm: '' }
    passwordDraft.accept()
    emit('notify', 'Contraseña actualizada')
  } catch (error) {
    if (auth.token === token) emit('notify', errorMessage(error, 'No se pudo cambiar la contraseña'), true)
  } finally { savingPassword.value = false }
}
onMounted(loadProfile)
</script>
