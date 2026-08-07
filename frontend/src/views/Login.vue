<template>
  <v-app class="auth-app">
    <v-main class="auth-main">
      <section class="auth-page" aria-labelledby="login-title">
        <div class="auth-noise"></div>
        <div class="auth-grid"></div>
        <div class="auth-orb auth-orb--one"></div>
        <div class="auth-orb auth-orb--two"></div>
        <div class="auth-orb auth-orb--three"></div>

        <v-container class="auth-container pa-4 pa-sm-6 pa-lg-8" fluid>
          <v-row class="auth-layout align-center" no-gutters>
            <v-col cols="12" lg="7" class="d-none d-lg-flex">
              <div class="auth-story pr-xl-12">
                <div class="brand-row d-flex align-center mb-10">
                  <div class="brand-symbol" aria-hidden="true">
                    <v-icon icon="mdi-brain" size="26"></v-icon>
                  </div>
                  <div>
                    <p class="brand-name mb-0">Tutor<span>IA</span></p>
                  </div>
                </div>

                <div class="hero-copy">
                  <h1 id="login-title">
                    Aprende con
                    <span>Inteligencia.</span>
                  </h1>
                  <p class="hero-description">
                    Tu espacio para crecer con IA.
                  </p>
                </div>

                <div class="learning-orbit mt-10" aria-label="Características de TutorIA">
                  <div class="orbit-line orbit-line--one"></div>
                  <div class="orbit-line orbit-line--two"></div>
                  <div class="orbit-core">
                    <v-icon icon="mdi-sparkles" size="23"></v-icon>
                  </div>
                  <div class="orbit-card orbit-card--top">
                    <v-icon icon="mdi-chart-timeline-variant-shimmer" size="19"></v-icon>
                    <div>
                      <strong>Aprendizaje real</strong>
                      <span>conexión IA y estudiantes</span>
                    </div>
                  </div>
                  <div class="orbit-card orbit-card--left">
                    <v-icon icon="mdi-account-group-outline" size="19"></v-icon>
                    <div>
                      <strong>Gestión de grupos</strong>
                      <span>administra el conocimiento</span>
                    </div>
                  </div>
                  <div class="orbit-card orbit-card--right">
                    <v-icon icon="mdi-shield-check-outline" size="19"></v-icon>
                    <div>
                      <strong>Entorno protegido</strong>
                      <span>para cada institución</span>
                    </div>
                  </div>
                </div>
              </div>
            </v-col>

            <v-col cols="12" lg="5" xl="4" offset-xl="1">
              <div class="auth-panel-wrap">
                <div class="mobile-brand d-flex d-lg-none align-center mb-8">
                  <div class="brand-symbol" aria-hidden="true">
                    <v-icon icon="mdi-brain" size="23"></v-icon>
                  </div>
                  <div>
                    <p class="brand-name mb-0">Tutor<span>IA</span></p>
                  </div>
                </div>

                <v-card class="auth-panel pa-5 pa-sm-8" rounded="xl">
                  <div class="panel-topline"></div>
                  <div class="d-flex align-start justify-space-between ga-3 mb-7">
                    <div>
                      <p class="eyebrow mb-2">ACCESO INSTITUCIONAL</p>
                      <h2 class="panel-title mb-2">Qué bueno verte.</h2>
                      <p class="panel-subtitle mb-0">
                        {{ identityMessage }}
                      </p>
                    </div>
                    <div class="secure-seal" aria-label="Conexión segura">
                      <v-icon icon="mdi-shield-check" size="21"></v-icon>
                    </div>
                  </div>

                  <v-form @submit.prevent="handleSubmit">
                    <v-text-field
                      v-model.trim="form.email"
                      label="Correo institucional"
                      type="email"
                      autocomplete="email"
                      prepend-inner-icon="mdi-at"
                      :error-messages="errors.email ? [errors.email] : []"
                      class="auth-field mb-3"
                      @blur="validateEmail"
                      @update:model-value="clearFieldError('email')"
                    >
                      <template #details>
                        <span v-if="form.email && !errors.email" class="field-feedback field-feedback--success">
                          <v-icon icon="mdi-check-circle" size="14"></v-icon>
                          Identidad lista para verificar
                        </span>
                      </template>
                    </v-text-field>

                    <v-text-field
                      v-model="form.password"
                      label="Contraseña"
                      :type="showPassword ? 'text' : 'password'"
                      autocomplete="current-password"
                      prepend-inner-icon="mdi-lock-outline"
                      :append-inner-icon="showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                      :error-messages="errors.password ? [errors.password] : []"
                      class="auth-field mb-1"
                      @click:append-inner="showPassword = !showPassword"
                      @blur="validatePassword"
                      @update:model-value="clearFieldError('password')"
                    ></v-text-field>

                    <v-alert
                      v-if="authStore.error"
                      type="error"
                      variant="tonal"
                      density="compact"
                      class="auth-error mt-5"
                      closable
                      @click:close="authStore.error = ''"
                    >
                      <template #title>No fue posible acceder</template>
                      {{ authStore.error }}
                    </v-alert>

                    <v-btn
                      type="submit"
                      color="primary"
                      variant="flat"
                      block
                      size="x-large"
                      class="auth-submit mt-7"
                      :loading="authStore.isLoading"
                      :disabled="!isFormValid"
                    >
                      <v-icon icon="mdi-arrow-right" class="mr-2"></v-icon>
                      {{ authStore.isLoading ? 'Verificando tu acceso…' : 'Entrar a TutorIA' }}
                    </v-btn>
                  </v-form>

                  <v-divider class="my-6 auth-divider"></v-divider>
                  <div class="d-flex align-center ga-2 connection-note">
                    <span class="connection-pulse"></span>
                    <span>Conexión segura</span>
                  </div>
                </v-card>

              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: ''
})

const errors = ref({
  email: '',
  password: ''
})

const showPassword = ref(false)
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const isFormValid = computed(() => (
  emailRegex.test(form.value.email)
  && form.value.password.length >= 8
  && !errors.value.email
  && !errors.value.password
))

const identityMessage = computed(() => {
  if (form.value.email && !errors.value.email) return 'Tu identidad está lista. Completa la verificación para continuar.'
  return 'Ingresa con las credenciales asignadas por tu institución.'
})

const validateEmail = () => {
  if (!form.value.email) {
    errors.value.email = 'El correo electrónico es requerido'
  } else if (!emailRegex.test(form.value.email)) {
    errors.value.email = 'Ingresa un correo electrónico válido'
  } else {
    errors.value.email = ''
  }
}

const validatePassword = () => {
  if (!form.value.password) {
    errors.value.password = 'La contraseña es requerida'
  } else if (form.value.password.length < 8) {
    errors.value.password = 'La contraseña debe tener al menos 8 caracteres'
  } else {
    errors.value.password = ''
  }
}

const clearFieldError = (field) => {
  errors.value[field] = ''
  if (authStore.error) authStore.error = ''
}

const handleSubmit = async () => {
  validateEmail()
  validatePassword()

  if (!isFormValid.value) return

  const result = await authStore.login({
    email: form.value.email,
    password: form.value.password
  })

  if (result.success) {
    if (result.user.role === 'super_admin') router.push('/super-admin')
    else if (result.user.role === 'coordinador') router.push('/coordinador')
    else if (result.user.role === 'estudiante') router.push('/estudiante')
    else router.push('/login')
  }
}
</script>

<style scoped>
.auth-app { background: #101216; }
.auth-main, .auth-page { min-height: 100vh; }
.auth-page {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding-block: 24px;
  background: radial-gradient(100% 90% at 0% 0%, rgba(124, 197, 118, 0.12), transparent 55%), radial-gradient(70% 110% at 100% 100%, rgba(69, 148, 113, 0.13), transparent 58%), linear-gradient(127deg, #111419 0%, #171b20 52%, #121518 100%);
}
.auth-container { position: relative; z-index: 2; max-width: 1500px; }
.auth-layout { min-height: auto; }
.auth-noise, .auth-grid { position: absolute; inset: 0; pointer-events: none; }
.auth-noise {
  z-index: -1;
  opacity: 0.28;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}
.auth-grid {
  z-index: -1;
  opacity: 0.4;
  background-image: linear-gradient(rgba(180, 216, 190, 0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(180, 216, 190, 0.045) 1px, transparent 1px);
  background-size: 54px 54px;
  mask-image: radial-gradient(ellipse at 32% 50%, black 0%, transparent 64%);
}
.auth-orb { position: absolute; z-index: -1; border-radius: 50%; filter: blur(8px); pointer-events: none; }
.auth-orb--one {
  top: -175px; left: 22%; width: 460px; height: 460px;
  background: radial-gradient(circle, rgba(124, 197, 118, 0.2) 0%, rgba(124, 197, 118, 0) 68%);
  animation: float-one 13s ease-in-out infinite alternate;
}
.auth-orb--two {
  right: -170px; bottom: -200px; width: 560px; height: 560px;
  background: radial-gradient(circle, rgba(75, 168, 126, 0.17) 0%, rgba(75, 168, 126, 0) 68%);
  animation: float-two 16s ease-in-out infinite alternate;
}
.auth-orb--three {
  top: 38%; left: 47%; width: 160px; height: 160px;
  background: radial-gradient(circle, rgba(230, 255, 232, 0.12), transparent 69%);
  animation: breathe 5s ease-in-out infinite;
}
.auth-story { animation: story-enter 0.8s cubic-bezier(0.16, 1, 0.3, 1) both; }
.brand-row, .mobile-brand { gap: 12px; }
.brand-symbol {
  display: grid; width: 48px; height: 48px; place-items: center;
  border: 1px solid rgba(155, 226, 153, 0.45); border-radius: 16px; color: #b6f2aa;
  background: linear-gradient(145deg, rgba(124, 197, 118, 0.24), rgba(124, 197, 118, 0.06));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 0 26px rgba(124, 197, 118, 0.2);
}
.brand-name { color: #f4f8f4; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.045em; }
.brand-name span { color: #9be692; }
.brand-caption { color: rgba(226, 235, 227, 0.58); font-size: 0.69rem; font-weight: 600; letter-spacing: 0.025em; }
.live-label { display: inline-flex; align-items: center; gap: 9px; color: #b7e9b0; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; }
.live-dot, .connection-pulse { width: 8px; height: 8px; border-radius: 50%; background: #92e487; box-shadow: 0 0 0 0 rgba(146, 228, 135, 0.65); animation: status-pulse 2s infinite; }
.hero-copy h1 { max-width: 650px; color: #f7faf7; font-size: clamp(3.1rem, 5.2vw, 5.3rem); font-weight: 800; letter-spacing: -0.065em; line-height: 0.98; }
.hero-copy h1 span { display: block; color: #9ce294; text-shadow: 0 0 38px rgba(124, 197, 118, 0.26); }
.hero-description { max-width: 530px; margin-top: 26px; color: rgba(235, 242, 235, 0.68); font-size: 1.08rem; line-height: 1.65; }
.learning-orbit { position: relative; width: min(100%, 580px); height: 196px; }
.orbit-core {
  position: absolute; top: 69px; left: 50%; display: grid; width: 60px; height: 60px; place-items: center;
  border: 1px solid rgba(162, 238, 151, 0.55); border-radius: 50%; color: #d5ffd0;
  background: radial-gradient(circle at 35% 30%, #87cf7e, #356d48);
  box-shadow: 0 0 0 10px rgba(124, 197, 118, 0.06), 0 0 35px rgba(124, 197, 118, 0.33);
  transform: translateX(-50%); animation: core-pulse 4s ease-in-out infinite;
}
.orbit-line { position: absolute; height: 1px; transform-origin: left center; background: linear-gradient(90deg, rgba(139, 220, 132, 0.65), rgba(139, 220, 132, 0)); }
.orbit-line--one { top: 98px; left: 16%; width: 35%; transform: rotate(-27deg); }
.orbit-line--two { top: 97px; left: 52%; width: 32%; transform: rotate(24deg); }
.orbit-card {
  position: absolute; display: flex; align-items: center; gap: 11px; min-width: 182px; padding: 11px 13px;
  border: 1px solid rgba(191, 236, 185, 0.16); border-radius: 13px; color: #a7e6a0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.025));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 14px 30px rgba(0, 0, 0, 0.15); backdrop-filter: blur(10px);
}
.orbit-card strong, .orbit-card span { display: block; }
.orbit-card strong { color: #ecf7eb; font-size: 0.76rem; font-weight: 700; }
.orbit-card span { margin-top: 2px; color: rgba(229, 241, 229, 0.57); font-size: 0.65rem; }
.orbit-card--top { top: 0; left: 50%; transform: translateX(-50%); animation: float-card-top 5s ease-in-out infinite; }
.orbit-card--left { bottom: 0; left: 0; animation: float-card 5.5s ease-in-out infinite 0.4s; }
.orbit-card--right { right: 0; bottom: 0; animation: float-card 4.8s ease-in-out infinite 0.8s; }
.trust-row { display: flex; align-items: center; gap: 9px; color: rgba(219, 233, 220, 0.56); font-size: 0.76rem; }
.trust-row :deep(.v-icon) { color: #9adf92; }
.auth-panel-wrap { width: 100%; animation: panel-enter 0.8s 0.08s cubic-bezier(0.16, 1, 0.3, 1) both; }
.auth-panel {
  position: relative; overflow: hidden; border: 1px solid rgba(205, 237, 199, 0.18) !important;
  background: linear-gradient(145deg, rgba(42, 48, 52, 0.88), rgba(24, 29, 32, 0.91)) !important;
  box-shadow: 0 28px 76px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(124, 197, 118, 0.035); backdrop-filter: blur(22px);
}
.auth-panel::before { position: absolute; top: -100px; right: -80px; width: 230px; height: 230px; border-radius: 50%; background: radial-gradient(circle, rgba(124, 197, 118, 0.12), transparent 70%); content: ''; pointer-events: none; }
.panel-topline { position: absolute; top: 0; left: 10%; width: 80%; height: 1px; background: linear-gradient(90deg, transparent, rgba(171, 238, 163, 0.95), transparent); }
.eyebrow { color: #a3e69b; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.13em; }
.panel-title { color: #f4f8f3; font-size: clamp(1.75rem, 3.3vw, 2.1rem); font-weight: 800; letter-spacing: -0.045em; line-height: 1.05; }
.panel-subtitle { max-width: 290px; color: rgba(225, 234, 225, 0.65); font-size: 0.86rem; line-height: 1.55; }
.secure-seal { display: grid; flex: 0 0 auto; width: 43px; height: 43px; place-items: center; border: 1px solid rgba(146, 225, 138, 0.32); border-radius: 14px; color: #a7ed9f; background: rgba(124, 197, 118, 0.1); }
.auth-field :deep(.v-field) { border-radius: 14px; background: rgba(7, 10, 11, 0.22); transition: background 0.22s ease, transform 0.22s ease; }
.auth-field :deep(.v-field--focused) { background: rgba(124, 197, 118, 0.08); transform: translateY(-1px); }
.auth-field :deep(.v-field__prepend-inner .v-icon), .auth-field :deep(.v-field__append-inner .v-icon) { color: #a6e99d !important; }
.field-feedback { display: inline-flex; align-items: center; gap: 4px; font-size: 0.71rem; }
.field-feedback--success { color: #9ce493; }
.auth-error { border: 1px solid rgba(244, 114, 114, 0.26); border-radius: 13px; }
.auth-submit {
  min-height: 54px; border-radius: 14px !important; color: #10200f !important; font-size: 0.93rem; font-weight: 800; letter-spacing: 0.01em;
  background: linear-gradient(118deg, #72c96c 0%, #a4e995 100%) !important; box-shadow: 0 12px 28px rgba(124, 197, 118, 0.22); transition: box-shadow 0.22s ease, transform 0.22s ease;
}
.auth-submit:hover:not(.v-btn--disabled) { box-shadow: 0 16px 34px rgba(124, 197, 118, 0.33); transform: translateY(-2px); }
.auth-submit.v-btn--disabled { color: rgba(234, 245, 233, 0.4) !important; background: rgba(255, 255, 255, 0.08) !important; box-shadow: none; }
.auth-divider { border-color: rgba(225, 242, 224, 0.09) !important; }
.connection-note { color: rgba(223, 234, 222, 0.55); font-size: 0.71rem; }
.connection-pulse { width: 6px; height: 6px; flex: 0 0 auto; }
.legal-note { color: rgba(221, 233, 221, 0.42); font-size: 0.7rem; }
@keyframes story-enter { from { opacity: 0; transform: translateX(-26px); } to { opacity: 1; transform: translateX(0); } }
@keyframes panel-enter { from { opacity: 0; transform: translateX(26px) scale(0.985); } to { opacity: 1; transform: translateX(0) scale(1); } }
@keyframes float-one { to { transform: translate(60px, 45px) scale(1.12); } }
@keyframes float-two { to { transform: translate(-50px, -35px) scale(1.1); } }
@keyframes breathe { 50% { opacity: 0.5; transform: scale(1.25); } }
@keyframes status-pulse { 70% { box-shadow: 0 0 0 8px rgba(146, 228, 135, 0); } 100% { box-shadow: 0 0 0 0 rgba(146, 228, 135, 0); } }
@keyframes core-pulse { 50% { box-shadow: 0 0 0 14px rgba(124, 197, 118, 0.035), 0 0 42px rgba(124, 197, 118, 0.42); } }
@keyframes float-card { 50% { transform: translateY(-5px); } }
@keyframes float-card-top { 50% { transform: translateX(-50%) translateY(-5px); } }
@media (max-width: 1279px) {
  .auth-container { max-width: 560px; }
  .auth-page { align-items: flex-start; }
  .auth-layout { min-height: auto; padding-top: clamp(42px, 10vh, 90px); padding-bottom: 36px; }
  .auth-panel-wrap { animation-name: story-enter; }
  .auth-orb--one { left: -150px; }
}

@media (min-width: 1280px) {
  .auth-page {
    align-items: flex-start;
    padding-block: 16px;
  }

  .auth-layout {
    min-height: auto;
    padding-top: 18px;
    padding-bottom: 18px;
  }

  .auth-story {
    transform: translateY(-10px);
  }
}
@media (max-width: 599px) {
  .auth-container { padding: 18px !important; }
  .auth-layout { padding-top: 36px; }
  .auth-panel { border-radius: 22px !important; }
  .mobile-brand { margin-left: 4px; }
  .brand-symbol { width: 43px; height: 43px; border-radius: 14px; }
  .panel-title { font-size: 1.68rem; }
  .panel-subtitle { font-size: 0.8rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: 0.01ms !important; }
}
</style>
