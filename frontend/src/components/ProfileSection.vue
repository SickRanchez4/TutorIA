<template>
  <div>
    <v-row>
      <v-col cols="12" md="6">
        <v-card class="pa-5" border elevation="1">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">Mi Perfil</h3>
          <v-form @submit.prevent="onUpdateProfile" class="mb-4">
            <v-text-field v-model="localProfile.first_name" label="Nombres" class="mb-2" />
            <v-text-field v-model="localProfile.last_name" label="Apellidos" class="mb-2" />
            <v-text-field v-model="localProfile.phone" label="Telefono" class="mb-3" />
            <v-btn type="submit" color="primary" block>Guardar cambios</v-btn>
          </v-form>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="pa-5" border elevation="1">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">Cambiar Contrasena</h3>
          <v-form @submit.prevent="onUpdatePassword">
            <v-text-field v-model="localPassword.current" type="password" label="Contrasena actual" class="mb-2" />
            <v-text-field v-model="localPassword.new" type="password" label="Nueva contrasena" class="mb-2" />
            <v-text-field v-model="localPassword.confirm" type="password" label="Confirmar nueva contrasena" class="mb-3" />
            <v-btn type="submit" color="primary" block>Cambiar contrasena</v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  profile: {
    type: Object,
    default: () => ({ first_name: '', last_name: '', phone: '' })
  }
})

const emit = defineEmits(['update-profile', 'update-password', 'notify'])

const localProfile = ref({ ...props.profile })
const localPassword = ref({ current: '', new: '', confirm: '' })

watch(() => props.profile, (newVal) => {
  localProfile.value = { ...newVal }
}, { deep: true })

const onUpdateProfile = async () => {
  emit('update-profile', localProfile.value)
}

const onUpdatePassword = async () => {
  if (localPassword.value.new !== localPassword.value.confirm) {
    emit('notify', { message: 'Las nuevas contrasenas no coinciden', isError: true })
    return
  }
  if (localPassword.value.new.length < 8) {
    emit('notify', { message: 'La contrasena debe tener al menos 8 caracteres', isError: true })
    return
  }
  
  emit('update-password', {
    current_password: localPassword.value.current,
    new_password: localPassword.value.new
  })
  
  // Clear form after submit (parent will handle the rest)
  localPassword.value = { current: '', new: '', confirm: '' }
}
</script>
