<template>
  <v-app class="auth-app">
    <v-main class="auth-main">
      <section class="auth-page" aria-labelledby="login-title">
        <!-- Filtros SVG: distorsión líquida (feTurbulence + feDisplacementMap) -->
        <svg class="svg-defs" width="0" height="0" aria-hidden="true" focusable="false">
          <defs>
            <filter id="liquid-distort" x="-35%" y="-35%" width="170%" height="170%">
              <feTurbulence type="fractalNoise" baseFrequency="0.009 0.013" numOctaves="2" seed="7" result="noise">
                <animate
                  attributeName="baseFrequency"
                  dur="22s"
                  values="0.009 0.013;0.014 0.009;0.009 0.013"
                  repeatCount="indefinite"
                />
              </feTurbulence>
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="46" xChannelSelector="R" yChannelSelector="G" />
            </filter>
            <filter id="liquid-edge" x="-20%" y="-20%" width="140%" height="140%">
              <feTurbulence type="turbulence" baseFrequency="0.02 0.03" numOctaves="1" seed="3" result="noise">
                <animate
                  attributeName="baseFrequency"
                  dur="14s"
                  values="0.02 0.03;0.03 0.02;0.02 0.03"
                  repeatCount="indefinite"
                />
              </feTurbulence>
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="7" xChannelSelector="R" yChannelSelector="G" />
            </filter>
          </defs>
        </svg>

        <!-- Red sináptica viva (canvas, reacciona al cursor) -->
        <SynapseBackdrop />
        <div class="auth-noise"></div>
        <div class="auth-vignette"></div>

        <v-container class="auth-container pa-4 pa-sm-6 pa-lg-8" fluid>
          <v-row class="auth-layout align-center" no-gutters>
            <v-col cols="12" lg="7" class="d-none d-lg-flex">
              <div class="auth-story pr-xl-12">
                <div class="brand-row d-flex align-center mb-10">
                  <div class="brand-symbol" aria-hidden="true">
                    <v-icon icon="mdi-brain" size="26"></v-icon>
                    <span class="brand-symbol-ring"></span>
                  </div>
                  <div>
                    <p class="brand-name mb-0">Tutor<span>IA</span></p>
                    <p class="brand-caption mb-0">Plataforma educativa con IA</p>
                  </div>
                </div>

                <div class="hero-copy">
                  <h1 id="login-title">
                    Aprende con
                    <span class="hero-word-slot">
                      <Transition name="word" mode="out-in">
                        <span :key="rotatingWord" class="hero-word">{{ rotatingWord }}</span>
                      </Transition>
                    </span>
                  </h1>
                  <p class="hero-description">
                    Tu espacio para crecer con IA. Conocimiento de tu institución,
                    conversaciones que enseñan.
                  </p>
                </div>

                <!-- Línea de señal: el conocimiento viaja del núcleo a cada pilar -->
                <div class="signal-strip mt-12" aria-label="Características de TutorIA">
                  <svg class="signal-svg" viewBox="0 0 560 56" preserveAspectRatio="none" aria-hidden="true">
                    <path class="signal-path signal-path--base" d="M4 28 C 90 4, 150 52, 236 28 S 400 4, 556 28" />
                    <path class="signal-path signal-path--pulse" d="M4 28 C 90 4, 150 52, 236 28 S 400 4, 556 28" />
                  </svg>
                  <div class="signal-cards">
                    <div class="signal-card">
                      <v-icon icon="mdi-chart-timeline-variant-shimmer" size="19"></v-icon>
                      <div>
                        <strong>Aprendizaje real</strong>
                        <span>conexión IA y estudiantes</span>
                      </div>
                    </div>
                    <div class="signal-card">
                      <v-icon icon="mdi-account-group-outline" size="19"></v-icon>
                      <div>
                        <strong>Gestión de grupos</strong>
                        <span>administra el conocimiento</span>
                      </div>
                    </div>
                    <div class="signal-card">
                      <v-icon icon="mdi-shield-check-outline" size="19"></v-icon>
                      <div>
                        <strong>Entorno protegido</strong>
                        <span>para cada institución</span>
                      </div>
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
                    <span class="brand-symbol-ring"></span>
                  </div>
                  <div>
                    <p class="brand-name mb-0">Tutor<span>IA</span></p>
                    <p class="brand-caption mb-0">Plataforma educativa con IA</p>
                  </div>
                </div>

                <!-- Cristal líquido: blob distorsionado detrás del panel -->
                <div class="liquid-stage" aria-hidden="true">
                  <div class="liquid-blob liquid-blob--a"></div>
                  <div class="liquid-blob liquid-blob--b"></div>
                </div>

                <v-card
                  class="auth-panel pa-5 pa-sm-8"
                  rounded="xl"
                  :style="panelStyle"
                  @pointermove="onPanelPointerMove"
                  @pointerleave="resetPanelTilt"
                >
                  <div class="panel-spotlight" aria-hidden="true"></div>
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import SynapseBackdrop from '../components/SynapseBackdrop.vue'

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

/* ============================================================
   Capa visual — sin efecto sobre la lógica de autenticación
   ============================================================ */

const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

/* --- Palabra rotativa del titular --- */
const rotatingWords = ['Inteligencia.', 'Curiosidad.', 'Propósito.', 'Confianza.']
const wordIndex = ref(0)
const rotatingWord = computed(() => rotatingWords[wordIndex.value])
let wordTimer = null

/* --- Tilt 3D + spotlight del panel --- */
const tilt = ref({ rx: 0, ry: 0, px: 50, py: 50, glow: 0 })

const panelStyle = computed(() => ({
  '--tilt-x': `${tilt.value.rx}deg`,
  '--tilt-y': `${tilt.value.ry}deg`,
  '--spot-x': `${tilt.value.px}%`,
  '--spot-y': `${tilt.value.py}%`,
  '--spot-glow': tilt.value.glow
}))

function onPanelPointerMove(event) {
  if (prefersReducedMotion) return
  const rect = event.currentTarget.getBoundingClientRect()
  const px = (event.clientX - rect.left) / rect.width
  const py = (event.clientY - rect.top) / rect.height
  tilt.value = {
    rx: (0.5 - py) * 5,
    ry: (px - 0.5) * 5,
    px: px * 100,
    py: py * 100,
    glow: 1
  }
}

function resetPanelTilt() {
  tilt.value = { rx: 0, ry: 0, px: 50, py: 50, glow: 0 }
}

/* --- Ciclo de vida --- */
onMounted(() => {
  if (!prefersReducedMotion) {
    wordTimer = setInterval(() => {
      wordIndex.value = (wordIndex.value + 1) % rotatingWords.length
    }, 3600)
  }
})

onBeforeUnmount(() => {
  if (wordTimer) clearInterval(wordTimer)
})
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
.svg-defs { position: absolute; width: 0; height: 0; overflow: hidden; }
.auth-container { position: relative; z-index: 2; max-width: 1500px; }
.auth-layout { min-height: auto; }
.auth-noise, .auth-vignette { position: absolute; inset: 0; z-index: 1; pointer-events: none; }
.auth-noise {
  opacity: 0.24;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}
.auth-vignette {
  background: radial-gradient(120% 95% at 50% 42%, transparent 42%, rgba(9, 11, 13, 0.55) 100%);
}
.auth-story { animation: story-enter 0.8s cubic-bezier(0.16, 1, 0.3, 1) both; }
.brand-row, .mobile-brand { gap: 12px; }
.brand-symbol {
  position: relative;
  display: grid; width: 48px; height: 48px; place-items: center;
  border: 1px solid rgba(155, 226, 153, 0.45); border-radius: 16px; color: #b6f2aa;
  background: linear-gradient(145deg, rgba(124, 197, 118, 0.24), rgba(124, 197, 118, 0.06));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 0 26px rgba(124, 197, 118, 0.2);
}
.brand-symbol-ring {
  position: absolute; inset: -6px; border-radius: 20px;
  border: 1px solid rgba(124, 197, 118, 0.28);
  animation: ring-pulse 3.4s ease-in-out infinite;
  pointer-events: none;
}
.brand-name { color: #f4f8f4; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.045em; }
.brand-name span { color: #9be692; }
.brand-caption { color: rgba(226, 235, 227, 0.58); font-size: 0.69rem; font-weight: 600; letter-spacing: 0.025em; }
.connection-pulse { width: 8px; height: 8px; border-radius: 50%; background: #92e487; box-shadow: 0 0 0 0 rgba(146, 228, 135, 0.65); animation: status-pulse 2s infinite; }
.hero-copy h1 { max-width: 650px; color: #f7faf7; font-size: clamp(3.1rem, 5.2vw, 5.3rem); font-weight: 800; letter-spacing: -0.065em; line-height: 0.98; }
.hero-word-slot { display: block; min-height: 1.02em; }
.hero-word {
  display: inline-block; color: #9ce294;
  text-shadow: 0 0 38px rgba(124, 197, 118, 0.26);
}
.word-enter-active, .word-leave-active { transition: opacity 0.45s ease, transform 0.45s cubic-bezier(0.16, 1, 0.3, 1), filter 0.45s ease; }
.word-enter-from { opacity: 0; transform: translateY(0.35em); filter: blur(6px); }
.word-leave-to { opacity: 0; transform: translateY(-0.3em); filter: blur(6px); }
.hero-description { max-width: 530px; margin-top: 26px; color: rgba(235, 242, 235, 0.68); font-size: 1.08rem; line-height: 1.65; }

/* --- Línea de señal --- */
.signal-strip { position: relative; width: min(100%, 620px); }
.signal-svg { position: absolute; top: -30px; left: 0; width: 100%; height: 56px; overflow: visible; }
.signal-path { fill: none; stroke-width: 1.5; }
.signal-path--base { stroke: rgba(124, 197, 118, 0.16); }
.signal-path--pulse {
  stroke: rgba(164, 233, 149, 0.85);
  stroke-dasharray: 46 620;
  stroke-linecap: round;
  animation: signal-travel 5.5s linear infinite;
  filter: drop-shadow(0 0 6px rgba(124, 197, 118, 0.55));
}
.signal-cards { display: flex; gap: 14px; }
.signal-card {
  display: flex; flex: 1; align-items: center; gap: 11px; min-width: 0; padding: 12px 13px;
  border: 1px solid rgba(191, 236, 185, 0.16); border-radius: 13px; color: #a7e6a0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.025));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 14px 30px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.signal-card:hover {
  transform: translateY(-4px);
  border-color: rgba(164, 233, 149, 0.4);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 18px 36px rgba(0, 0, 0, 0.22), 0 0 24px rgba(124, 197, 118, 0.12);
}
.signal-card strong, .signal-card span { display: block; }
.signal-card strong { color: #ecf7eb; font-size: 0.76rem; font-weight: 700; }
.signal-card span { margin-top: 2px; color: rgba(229, 241, 229, 0.57); font-size: 0.65rem; }

/* --- Panel con cristal líquido + tilt --- */
.auth-panel-wrap {
  position: relative;
  width: 100%;
  perspective: 1100px;
  animation: panel-enter 0.8s 0.08s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.liquid-stage { position: absolute; inset: -70px; z-index: 0; pointer-events: none; filter: url(#liquid-distort); }
.liquid-blob { position: absolute; border-radius: 50%; }
.liquid-blob--a {
  top: -20px; right: -30px; width: 300px; height: 300px;
  background: radial-gradient(circle at 38% 32%, rgba(124, 197, 118, 0.28), rgba(124, 197, 118, 0.04) 65%, transparent 75%);
  animation: blob-drift-a 17s ease-in-out infinite alternate;
}
.liquid-blob--b {
  bottom: -30px; left: -10px; width: 260px; height: 260px;
  background: radial-gradient(circle at 60% 60%, rgba(75, 168, 126, 0.24), rgba(75, 168, 126, 0.03) 62%, transparent 74%);
  animation: blob-drift-b 21s ease-in-out infinite alternate;
}
.auth-panel {
  position: relative; z-index: 1; overflow: hidden;
  border: 1px solid rgba(205, 237, 199, 0.18) !important;
  background: linear-gradient(145deg, rgba(42, 48, 52, 0.82), rgba(24, 29, 32, 0.88)) !important;
  box-shadow: 0 28px 76px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(124, 197, 118, 0.035);
  backdrop-filter: blur(22px) saturate(1.15);
  transform: rotateX(var(--tilt-x, 0deg)) rotateY(var(--tilt-y, 0deg));
  transform-style: preserve-3d;
  transition: transform 0.18s ease-out;
  will-change: transform;
}
.panel-spotlight {
  position: absolute; inset: 0; z-index: 0; pointer-events: none;
  opacity: var(--spot-glow, 0);
  background: radial-gradient(340px circle at var(--spot-x, 50%) var(--spot-y, 50%), rgba(164, 233, 149, 0.09), transparent 62%);
  transition: opacity 0.35s ease;
}
.auth-panel::before { position: absolute; top: -100px; right: -80px; width: 230px; height: 230px; border-radius: 50%; background: radial-gradient(circle, rgba(124, 197, 118, 0.12), transparent 70%); content: ''; pointer-events: none; }
.panel-topline {
  position: absolute; top: 0; left: 10%; width: 80%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(171, 238, 163, 0.95), transparent);
  filter: url(#liquid-edge);
}
.eyebrow { color: #a3e69b; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.13em; }
.panel-title { color: #f4f8f3; font-size: clamp(1.75rem, 3.3vw, 2.1rem); font-weight: 800; letter-spacing: -0.045em; line-height: 1.05; }
.panel-subtitle { max-width: 290px; color: rgba(225, 234, 225, 0.65); font-size: 0.86rem; line-height: 1.55; }
.secure-seal { display: grid; flex: 0 0 auto; width: 43px; height: 43px; place-items: center; border: 1px solid rgba(146, 225, 138, 0.32); border-radius: 14px; color: #a7ed9f; background: rgba(124, 197, 118, 0.1); }
.auth-field :deep(.v-field) { border-radius: 14px; background: rgba(7, 10, 11, 0.22); transition: background 0.22s ease, transform 0.22s ease, box-shadow 0.22s ease; }
.auth-field :deep(.v-field--focused) { background: rgba(124, 197, 118, 0.08); transform: translateY(-1px); box-shadow: 0 0 0 1px rgba(124, 197, 118, 0.25), 0 0 22px rgba(124, 197, 118, 0.1); }
.auth-field :deep(.v-field__prepend-inner .v-icon), .auth-field :deep(.v-field__append-inner .v-icon) { color: #a6e99d !important; }
.field-feedback { display: inline-flex; align-items: center; gap: 4px; font-size: 0.71rem; }
.field-feedback--success { color: #9ce493; }
.auth-error { border: 1px solid rgba(244, 114, 114, 0.26); border-radius: 13px; }
.auth-submit {
  position: relative; overflow: hidden;
  min-height: 54px; border-radius: 14px !important; color: #10200f !important; font-size: 0.93rem; font-weight: 800; letter-spacing: 0.01em;
  background: linear-gradient(118deg, #72c96c 0%, #a4e995 100%) !important; box-shadow: 0 12px 28px rgba(124, 197, 118, 0.22); transition: box-shadow 0.22s ease, transform 0.22s ease;
}
.auth-submit::after {
  position: absolute; top: 0; left: -80%; width: 55%; height: 100%; content: '';
  background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.42), transparent);
  transform: skewX(-18deg);
  transition: left 0.6s ease;
  pointer-events: none;
}
.auth-submit:hover:not(.v-btn--disabled) { box-shadow: 0 16px 34px rgba(124, 197, 118, 0.33); transform: translateY(-2px); }
.auth-submit:hover:not(.v-btn--disabled)::after { left: 125%; }
.auth-submit.v-btn--disabled { color: rgba(234, 245, 233, 0.4) !important; background: rgba(255, 255, 255, 0.08) !important; box-shadow: none; }
.auth-divider { border-color: rgba(225, 242, 224, 0.09) !important; }
.connection-note { color: rgba(223, 234, 222, 0.55); font-size: 0.71rem; }
.connection-pulse { width: 6px; height: 6px; flex: 0 0 auto; }
@keyframes story-enter { from { opacity: 0; transform: translateX(-26px); } to { opacity: 1; transform: translateX(0); } }
@keyframes panel-enter { from { opacity: 0; transform: translateX(26px) scale(0.985); } to { opacity: 1; transform: translateX(0) scale(1); } }
@keyframes status-pulse { 70% { box-shadow: 0 0 0 8px rgba(146, 228, 135, 0); } 100% { box-shadow: 0 0 0 0 rgba(146, 228, 135, 0); } }
@keyframes ring-pulse { 0%, 100% { opacity: 0.65; transform: scale(1); } 50% { opacity: 0.15; transform: scale(1.12); } }
@keyframes signal-travel { from { stroke-dashoffset: 666; } to { stroke-dashoffset: 0; } }
@keyframes blob-drift-a { to { transform: translate(-45px, 40px) scale(1.14); } }
@keyframes blob-drift-b { to { transform: translate(38px, -32px) scale(1.08); } }
@media (max-width: 1279px) {
  .auth-container { max-width: 560px; }
  .auth-page { align-items: flex-start; }
  .auth-layout { min-height: auto; padding-top: clamp(42px, 10vh, 90px); padding-bottom: 36px; }
  .auth-panel-wrap { animation-name: story-enter; }
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
  .liquid-stage { inset: -40px; }
}
@media (max-width: 379px) {
  .auth-container { padding: 12px !important; }
  .auth-layout { padding-top: 24px; }
  .auth-panel { padding: 20px !important; }
  .liquid-blob--a { width: 210px; height: 210px; }
  .liquid-blob--b { width: 180px; height: 180px; }
  .secure-seal { width: 38px; height: 38px; }
}
@media (hover: none) {
  .auth-panel { transform: none !important; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: 0.01ms !important; }
  .auth-panel { transform: none !important; }
  .panel-spotlight, .signal-path--pulse { display: none; }
}
</style>
