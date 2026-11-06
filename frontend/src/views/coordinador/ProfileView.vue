<template>
  <div class="d-flex flex-column ga-5">
    <PageHeader
      overline="Cuenta"
      title="Perfil de coordinador"
      subtitle="Actualiza tus datos y la seguridad de tu acceso."
    />
    <ProfileSection @notify="notify" />
  </div>
</template>

<script setup>
import PageHeader from '../../components/PageHeader.vue'
import ProfileSection from '../../components/ProfileSection.vue'
import { coordinadorToast } from '../../composables/useToast'

const { notify } = coordinadorToast
</script>
