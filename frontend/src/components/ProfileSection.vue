<template>
  <div v-if="loading" class="empty-state surface-card profile-loading" role="status">
    <v-progress-circular indeterminate color="primary" size="36" width="4" />
    <span>Cargando perfil...</span>
  </div>

  <RegionState v-else-if="error" :error="error" @retry="emit('retry')" />
  <v-row v-else>
    <v-col cols="12" md="6">
      <v-card class="surface-card pa-5 h-100" rounded="xl">
        <h2 class="text-body-large font-weight-bold mb-4">Mi perfil</h2>
        <v-form class="d-flex flex-column ga-3" :disabled="savingProfile" @submit.prevent="event => submit(event, 'save-profile')">
          <v-text-field v-model="profile.first_name" label="Nombres (requerido)" autocomplete="given-name" :rules="[required]" :aria-invalid="attempted.profile && !profile.first_name.trim() ? 'true' : undefined" />
          <v-text-field v-model="profile.last_name" label="Apellidos (requerido)" autocomplete="family-name" :rules="[required]" :aria-invalid="attempted.profile && !profile.last_name.trim() ? 'true' : undefined" />
          <v-text-field v-model="profile.phone" label="Teléfono" type="tel" autocomplete="tel" />
          <v-btn type="submit" color="primary" variant="flat" block :loading="savingProfile">Guardar cambios</v-btn>
        </v-form>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="surface-card pa-5 h-100" rounded="xl">
        <h2 class="text-body-large font-weight-bold mb-4">Cambiar contraseña</h2>
        <v-form class="d-flex flex-column ga-3" :disabled="savingPassword" @submit.prevent="event => submit(event, 'save-password')">
          <v-text-field
            v-model="passwords.current"
            label="Contraseña actual"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="current-password"
            :rules="[required]"
            :aria-invalid="attempted.password && !passwords.current ? 'true' : undefined"
          />
          <v-text-field
            v-model="passwords.next"
            label="Nueva contraseña"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="new-password"
            :rules="[required, value => value.length >= 8 || 'Usa al menos 8 caracteres']"
            :aria-invalid="attempted.password && passwords.next.length < 8 ? 'true' : undefined"
          />
          <v-text-field
            v-model="passwords.confirm"
            label="Confirmar nueva contraseña"
            :type="showPasswords ? 'text' : 'password'"
            autocomplete="new-password"
            :rules="[value => value === passwords.next || 'Las contraseñas no coinciden']"
            :aria-invalid="attempted.password && passwords.confirm !== passwords.next ? 'true' : undefined"
          />
          <v-checkbox v-model="showPasswords" label="Mostrar contraseñas" />
          <v-btn type="submit" color="primary" variant="flat" block :loading="savingPassword">Cambiar contraseña</v-btn>
        </v-form>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { nextTick, reactive, ref } from 'vue'
import RegionState from './RegionState.vue'

defineProps({ loading: Boolean, savingProfile: Boolean, savingPassword: Boolean, error: { type: String, default: '' } })
const profile = defineModel('profile', { type: Object, required: true })
const passwords = defineModel('passwords', { type: Object, required: true })
const emit = defineEmits(['save-profile', 'save-password', 'retry'])
const showPasswords = ref(false)
const attempted = reactive({ profile: false, password: false })
const required = value => Boolean(value?.trim()) || 'Este campo es requerido'
async function submit(event, name) {
  attempted[name === 'save-profile' ? 'profile' : 'password'] = true
  const result = await event
  if (result.valid) emit(name)
  else { await nextTick(); event.target.querySelector('[aria-invalid="true"]')?.focus() }
}
</script>

<style scoped>
.profile-loading {
  min-height: 220px;
}
</style>
