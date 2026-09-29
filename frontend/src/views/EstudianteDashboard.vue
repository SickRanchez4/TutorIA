<template>
  <v-app class="d-flex flex-column student-app" style="height: 100vh;">
    <!-- Fondo ambiental compartido con el Login -->
    <div class="student-ambient" aria-hidden="true">
      <div class="student-ambient__noise"></div>
      <div class="student-ambient__vignette"></div>
    </div>

    <RoleSidebar
      v-model="mobileDrawer"
      role="Estudiante"
      :user-name="userName"
      :items="studentNavItems"
      :active="tab"
      permanent-on-desktop
      @select="tab = $event"
      @logout="logout"
    />

    <v-app-bar color="surface" elevation="0" :class="['border-b student-bar', { 'student-app-bar--chat': tab === 'chat' }]" :height="tab === 'chat' ? 58 : 80">
      <v-app-bar-nav-icon v-if="!mdAndUp" aria-label="Abrir navegación" @click="mobileDrawer = true"></v-app-bar-nav-icon>
      <v-app-bar-title class="student-toolbar-title py-2">
        <div class="d-flex align-center ga-3 student-toolbar-brand">
          <div class="student-brand-symbol" aria-hidden="true">
            <v-icon icon="mdi-brain" size="19"></v-icon>
            <span class="student-brand-ring"></span>
          </div>
          <PanelTitle role="Estudiante" class="student-toolbar-copy" />
        </div>
      </v-app-bar-title>

      <v-chip variant="tonal" color="secondary" class="mr-2 mr-sm-3 student-user-chip" prepend-icon="mdi-account-circle-outline">
        {{ userName }}
      </v-chip>
    </v-app-bar>

    <v-snackbar
      :model-value="!!toast"
      :color="toastError ? 'error' : 'success'"
      location="top right"
      timeout="3500"
    >
      {{ toast }}
    </v-snackbar>

    <v-main :class="['fade-in flex-grow-1 student-main-layer', tab === 'chat' ? 'student-chat-main' : 'overflow-auto']">
      <v-container fluid :class="[tab === 'chat' ? 'py-2 px-3 student-chat-container' : 'py-4 py-md-6 px-3 px-sm-4 px-md-6 student-content-container']" style="max-width: 1400px;">
        <!-- CHAT -->
        <Transition name="tabfade">
          <v-row v-show="tab === 'chat'" class="student-chat-view" density="compact">
          <!-- Sesiones -->
          <v-col cols="12" lg="3">
            <v-card class="student-chat-create pa-4 mb-2" rounded="xl">
              <div class="d-flex align-start justify-space-between mb-3">
                <div>
                  <p class="student-chat-eyebrow mb-1">ESPACIO DE ESTUDIO</p>
                  <h3 class="text-h6 font-weight-black mb-1">Elige una materia</h3>
                </div>
                <div class="student-chat-create-icon">
                  <v-icon icon="mdi-book-open-variant" size="22"></v-icon>
                </div>
              </div>
              <v-select
                v-model="newSesionGrupo"
                :items="grupos.map(g => ({ title: grupoLabel(g), value: g.id }))"
                label="Materia para explorar"
                prepend-inner-icon="mdi-book-open-variant-outline"
                variant="outlined"
                density="comfortable"
                hide-details
                class="mb-3 student-field"
              />
              <v-btn color="primary" block size="large" class="student-chat-primary student-shine" prepend-icon="mdi-arrow-up-right" @click="createSesion">
                Abrir conversación
              </v-btn>
              <v-alert v-if="!loadingBase && !grupos.length" type="warning" variant="tonal" density="compact" class="mt-2 text-caption">
                No estás inscrito en ningún grupo todavía.
              </v-alert>
            </v-card>

            <v-card class="student-chat-sessions pa-2 mb-2" rounded="xl">
              <div class="d-flex align-center justify-space-between px-2 pt-2 pb-3">
                <div>
                  <p class="text-subtitle-2 font-weight-black mb-0">Tus conversaciones</p>
                </div>
                <v-icon icon="mdi-message-text-outline" color="primary" size="20"></v-icon>
              </div>
              <div v-if="loadingBase" class="d-flex flex-column align-center justify-center py-6 ga-3 text-medium-emphasis">
                <v-progress-circular indeterminate color="primary" size="34" width="4"></v-progress-circular>
                <p class="text-caption mb-0">Cargando conversaciones...</p>
              </div>
              <div v-else-if="!sesiones.length" class="student-chat-empty-list text-center py-7 px-4">
                <v-icon icon="mdi-forum-outline" size="31" color="primary" class="mb-2"></v-icon>
                <p class="text-body-2 font-weight-bold mb-1">Tu primera conversación empieza aquí</p>
                <p class="text-caption text-medium-emphasis mb-0">Crea un espacio por cada materia que quieras dominar.</p>
              </div>
              <v-list v-else density="compact" nav class="pa-0">
                <v-list-item
                  v-for="s in sesiones"
                  :key="s.id"
                  :active="activeSesion?.id === s.id"
                  color="primary"
                  rounded="lg"
                  class="mb-1 student-session-item"
                >
                  <template v-if="renamingSesionId === s.id">
                    <div class="d-flex align-center ga-2 py-1">
                      <v-text-field v-model="renamingTitle" density="compact" hide-details maxlength="200" />
                      <v-btn size="small" color="primary" @click="confirmRename(s.id)">Guardar</v-btn>
                      <v-btn size="small" variant="text" @click="cancelRename">Cancelar</v-btn>
                    </div>
                  </template>
                  <template v-else>
                    <div class="d-flex align-center">
                      <div class="student-session-avatar mr-3">
                        <v-icon icon="mdi-forum-outline" size="17"></v-icon>
                      </div>
                      <v-list-item-title class="text-body-2 font-weight-bold flex-grow-1 text-truncate" style="cursor: pointer" @click="openSesion(s)">
                        {{ s.titulo }}
                      </v-list-item-title>
                      <v-btn icon="mdi-pencil-outline" variant="text" size="x-small" @click.stop="startRename(s)"></v-btn>
                      <v-btn icon="mdi-delete-outline" variant="text" size="x-small" color="error" @click.stop="deleteSesion(s)"></v-btn>
                    </div>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <!-- Conversación -->
          <v-col cols="12" lg="9" class="d-flex flex-column">
            <v-card class="student-chat-panel d-flex flex-column overflow-hidden flex-grow-1" rounded="xl">
              <div v-if="!activeSesion" class="student-chat-welcome flex-grow-1 d-flex align-center justify-center">
                <SynapseBackdrop :density="26000" :max-nodes="70" />
                <div class="text-center px-5">
                  <div class="student-chat-orbit mx-auto mb-5">
                    <div class="student-chat-orbit-core"><v-icon icon="mdi-brain" size="35"></v-icon></div>
                    <span class="student-chat-orbit-dot student-chat-orbit-dot--one"></span>
                    <span class="student-chat-orbit-dot student-chat-orbit-dot--two"></span>
                    <span class="student-chat-orbit-dot student-chat-orbit-dot--three"></span>
                  </div>
                  <p class="student-chat-eyebrow mb-2">TU COMPAÑERO DE APRENDIZAJE</p>
                  <h2 class="text-h5 font-weight-black mb-2">Convierte tus dudas en progreso.</h2>
                </div>
              </div>
              <template v-else>
                <div class="student-chat-header px-3 px-md-4 py-1">
                  <div class="d-flex align-center justify-space-between ga-2">
                    <div class="d-flex align-center ga-2 min-w-0">
                      <div class="student-chat-course-icon"><v-icon icon="mdi-book-education-outline" size="21"></v-icon></div>
                      <div class="min-w-0">
                        <p class="text-body-1 font-weight-black mb-0 text-truncate">{{ activeSesion.titulo }}</p>
                        <p class="text-caption text-medium-emphasis mb-0 text-truncate">{{ activeCourseLabel }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div ref="messagesBox" class="student-chat-messages flex-grow-1 overflow-y-auto pa-3 pa-md-4">
                  <div v-if="loadingSesion" class="fill-height d-flex flex-column align-center justify-center ga-3 text-medium-emphasis" style="min-height: 260px;">
                    <v-progress-circular indeterminate color="primary" size="40" width="4"></v-progress-circular>
                    <p class="text-caption mb-0">Cargando conversación...</p>
                  </div>
                  <template v-else>
                    <div v-if="!mensajes.length" class="student-chat-no-messages text-center py-10">
                      <div class="student-chat-no-messages-icon mx-auto mb-3"><v-icon icon="mdi-lightbulb-on-outline" size="27"></v-icon></div>
                      <p class="font-weight-black mb-1">¿Qué quieres entender hoy?</p>
                      <p class="text-caption text-medium-emphasis mb-0">Escribe una pregunta, plantea un ejercicio o genera un recurso para estudiar.</p>
                    </div>
                    <div v-for="m in mensajes" :key="m.id" :class="['d-flex flex-column mb-4', m.rol === 'user' ? 'align-end' : 'align-start']">
                      <span v-if="m.tipo_interaccion" class="chat-mode-tag mb-1">
                        <v-icon :icon="modeMeta(m.tipo_interaccion).icon" size="11" class="mr-1"></v-icon>{{ modeMeta(m.tipo_interaccion).label }}
                      </span>
                      <div class="d-flex align-end ga-2" :class="m.rol === 'user' ? 'flex-row-reverse' : ''">
                        <div v-if="m.rol !== 'user'" class="student-assistant-avatar"><v-icon icon="mdi-brain" size="15"></v-icon></div>
                        <div :class="['chat-bubble text-body-2', m.rol === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant', m.tipo_interaccion === 'recurso_sintetico' ? 'chat-bubble--resource' : '']">
                          <MermaidMessage
                            v-if="m.rol === 'assistant' && m.tipo_interaccion === 'recurso_sintetico'"
                            :content="m.contenido"
                          />
                          <template v-else>{{ m.contenido }}</template>
                          <div v-if="m.rol === 'user' && m.image_name" class="chat-image-resource" :title="`Imagen: ${m.image_name}`">
                            <v-icon icon="mdi-image-outline" size="16"></v-icon>
                            <span class="chat-image-resource__label">Imagen:</span>
                            <span class="chat-image-resource__name text-truncate">{{ m.image_name }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="sending" class="student-chat-thinking">
                      <div class="student-assistant-avatar"><v-icon icon="mdi-brain" size="15"></v-icon></div>
                      <div class="student-chat-thinking-bubble"><span></span><span></span><span></span></div>
                      <p class="text-caption text-medium-emphasis mb-0">Pensando contigo...</p>
                    </div>
                  </template>
                </div>
                <div class="student-chat-composer pa-2 pa-md-3">
                  <div class="student-chat-mode-bar d-flex flex-wrap align-center ga-2 mb-2">
                    <span class="student-chat-mode-label">Elige tu enfoque</span>
                    <v-btn
                      v-for="opt in chatModes"
                      :key="opt.value"
                      :color="selectedMode === opt.value ? 'primary' : 'default'"
                      :variant="selectedMode === opt.value ? 'flat' : 'tonal'"
                      :disabled="!isModeEnabled(opt.value)"
                      size="small"
                      class="student-chat-mode"
                      @click="selectedMode = opt.value"
                    >
                      {{ opt.label }}
                    </v-btn>
                  </div>
                  <div class="student-chat-input-wrap">
                    <input
                      ref="imageInput"
                      class="student-chat-image-input"
                      type="file"
                      accept="image/png,image/jpeg"
                      @change="selectImage"
                    />
                    <v-textarea
                      v-model="inputMsg"
                      rows="1"
                      auto-grow
                      placeholder="Escribe lo que quieres aprender..."
                      density="comfortable"
                      variant="solo"
                      flat
                      hide-details
                      class="student-chat-input"
                      :disabled="loadingSesion"
                      @keydown.enter.exact.prevent="sendByMode"
                    />
                    <v-btn
                      :color="isRecording ? 'error' : 'default'"
                      :class="['student-chat-microphone', { 'student-chat-microphone--recording': isRecording }]"
                      :disabled="sending || loadingSesion || !speechRecognitionSupported"
                      :aria-label="isRecording ? 'Detener grabación' : 'Grabar mensaje de voz'"
                      @click="toggleVoiceInput"
                    >
                      <v-icon :icon="isRecording ? 'mdi-stop' : 'mdi-microphone-outline'" size="20"></v-icon>
                      <v-tooltip activator="parent" location="top">
                        {{ speechRecognitionSupported ? (isRecording ? 'Detener y revisar texto' : 'Grabar mensaje de voz') : 'El navegador no admite dictado por voz' }}
                      </v-tooltip>
                    </v-btn>
                    <v-btn
                      class="student-chat-image-button"
                      :disabled="sending || loadingSesion"
                      aria-label="Adjuntar imagen"
                      @click="imageInput?.click()"
                    >
                      <v-icon icon="mdi-image-outline" size="20"></v-icon>
                      <v-tooltip activator="parent" location="top">Adjuntar imagen</v-tooltip>
                    </v-btn>
                    <v-btn color="primary" class="student-chat-send" :loading="sending" :disabled="!selectedMode || loadingSesion || isRecording" @click="sendByMode">
                      <v-icon icon="mdi-send" size="20"></v-icon>
                      <v-tooltip activator="parent" location="top">Enviar mensaje</v-tooltip>
                    </v-btn>
                  </div>
                  <div v-if="imageAttachment" class="student-chat-image-preview mt-2">
                    <img :src="imageAttachment.data_url" alt="Vista previa de imagen adjunta" />
                    <span class="text-truncate">{{ imageAttachment.name }}</span>
                    <v-btn icon="mdi-close" size="x-small" variant="text" aria-label="Quitar imagen" @click="clearImage" />
                  </div>
                  <p v-if="isRecording" class="student-chat-recording-status mb-0 mt-1" role="status">
                    <span></span> Escuchando… pulsa detener para revisar antes de enviar.
                  </p>
                </div>
              </template>
            </v-card>
          </v-col>
          </v-row>
        </Transition>

        <!-- AGENDA -->
        <Transition name="tabfade">
        <div v-show="tab === 'agenda'">
          <v-card class="pa-3 pa-sm-4 mb-4 d-flex flex-wrap align-center justify-space-between ga-3 student-panel agenda-toolbar" rounded="xl">
            <div class="d-flex align-center justify-center ga-2 agenda-month-nav">
              <v-btn icon="mdi-chevron-left" variant="tonal" size="small" @click="prevMonth"></v-btn>
              <h3 class="text-subtitle-1 font-weight-bold text-center agenda-month-label">{{ monthLabel }}</h3>
              <v-btn icon="mdi-chevron-right" variant="tonal" size="small" @click="nextMonth"></v-btn>
            </div>
            <div class="d-flex align-center ga-2 agenda-filter-row">
              <v-select
                v-model="agendaGrupoFilter"
                :items="[{ title: 'Todos mis cursos', value: '' }, ...grupos.map(g => ({ title: grupoLabel(g), value: g.id }))]"
                density="compact"
                hide-details
                class="student-field agenda-course-filter"
                @update:model-value="loadAgenda"
              />
              <v-btn color="primary" class="student-shine" @click="loadAgenda">Actualizar</v-btn>
            </div>
          </v-card>

          <v-card class="pa-3 pa-sm-4 mb-4 student-panel" rounded="xl">
            <div class="student-calendar-scroll" tabindex="0" aria-label="Calendario mensual; desliza horizontalmente para verlo completo">
              <div class="calendar-grid mb-2">
                <div v-for="d in weekDays" :key="d" class="text-center text-caption text-uppercase font-weight-bold text-medium-emphasis">{{ d }}</div>
              </div>
              <div class="calendar-grid">
                <article
                  v-for="day in calendarDays"
                  :key="day.key"
                  :class="['calendar-cell pa-2', day.inMonth ? 'calendar-cell--in' : 'calendar-cell--out', { 'calendar-cell--today': day.isToday }]"
                >
                  <p :class="['text-caption font-weight-bold mb-1', day.isToday ? 'text-primary' : day.inMonth ? '' : 'text-disabled']">{{ day.date.getDate() }}</p>
                  <div class="calendar-events">
                    <button
                      v-for="item in day.events.slice(0, 2)"
                      :key="item.id"
                      :title="item.titulo"
                      class="calendar-event text-truncate"
                      :class="eventColor(item.tipo)"
                    >
                      {{ item.titulo }}
                    </button>
                    <p v-if="day.events.length > 2" class="text-caption text-medium-emphasis mb-0">+{{ day.events.length - 2 }} más</p>
                  </div>
                </article>
              </div>
            </div>
          </v-card>

          <v-card class="pa-5 student-panel" rounded="xl">
            <h4 class="text-subtitle-1 font-weight-bold mb-3">Próximas actividades del mes</h4>
            <p v-if="!upcomingActivities.length" class="text-body-2 text-medium-emphasis">Sin actividades en este mes.</p>
            <v-list v-else density="comfortable" class="pa-0">
              <v-list-item v-for="a in upcomingActivities.slice(0, 8)" :key="a.id" class="px-0">
                <div class="d-flex align-center justify-space-between w-100 ga-3">
                  <div>
                    <p class="text-body-2 font-weight-medium mb-0">{{ a.titulo }}</p>
                    <p v-if="a.grupo?.materia_nombre" class="text-caption text-medium-emphasis mb-0">{{ a.grupo.materia_nombre }} · {{ a.grupo?.periodo_academico }} {{ a.grupo?.anio }}</p>
                    <p class="text-caption text-medium-emphasis mb-0">Límite: {{ formatDateTime(a.fecha_limite) }}</p>
                  </div>
                  <v-chip size="small" :color="tipoColor(a.tipo)" variant="tonal">{{ a.tipo }}</v-chip>
                </div>
              </v-list-item>
            </v-list>
          </v-card>
        </div>
        </Transition>

        <!-- PERFIL -->
        <Transition name="tabfade">
        <div v-show="tab === 'perfil'" class="student-profile">
          <ProfileSection 
            :profile="profileData" 
            @update-profile="updateProfile" 
            @update-password="updatePassword"
            @notify="(notif) => notify(notif.message, notif.isError)"
          />
        </div>
        </Transition>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { estudianteService } from '../services'
import { useAuthStore } from '../stores/auth'
import ProfileSection from '../components/ProfileSection.vue'
import MermaidMessage from '../components/MermaidMessage.vue'
import SynapseBackdrop from '../components/SynapseBackdrop.vue'
import RoleSidebar from '../components/RoleSidebar.vue'
import PanelTitle from '../components/PanelTitle.vue'
import { createToast } from '../composables/useToast'
import { useDisplay } from 'vuetify'

const authStore = useAuthStore()
const router = useRouter()
const { mdAndUp } = useDisplay()

const tab = ref('chat')
const studentNavItems = [
  { value: 'chat', label: 'Asistente', icon: 'mdi-forum-outline' },
  { value: 'agenda', label: 'Agenda', icon: 'mdi-calendar-month-outline' },
  { value: 'perfil', label: 'Perfil', icon: 'mdi-account-circle' },
]
const mobileDrawer = ref(mdAndUp.value)
const { message: toast, isError: toastError, notify } = createToast()
function err(e, fallback) { notify(e.response?.data?.message || fallback, true) }
function logout() { authStore.logout(); router.push('/login') }
const userName = computed(() => authStore.user?.full_name || authStore.user?.name || authStore.user?.email)

/* ---------- Datos base ---------- */
const grupos = ref([])
const sesiones = ref([])
const actividades = ref([])
const agendaGrupoFilter = ref('')
const loadingBase = ref(true)

async function loadBase() {
  loadingBase.value = true
  try {
    const [g, s] = await Promise.all([
      estudianteService.listGrupos(),
      estudianteService.listSesiones()
    ])
    grupos.value = g.cursos || []
    sesiones.value = s.sesiones || []
    await loadAgenda()
  } catch (e) { err(e, 'No se pudieron cargar tus datos') }
  finally { loadingBase.value = false }
}
onMounted(loadBase)
onMounted(initializeSpeechRecognition)
onBeforeUnmount(() => {
  if (speechRecognition && isRecording.value) speechRecognition.abort()
  speechRecognition = null
})

/* ---------- CU-08: Chat ---------- */
const activeSesion = ref(null)
const mensajes = ref([])
const inputMsg = ref('')
const sending = ref(false)
const loadingSesion = ref(false)
const newSesionGrupo = ref('')
const messagesBox = ref(null)
const sessionContext = ref(null)
const selectedMode = ref(null)
const renamingSesionId = ref(null)
const renamingTitle = ref('')
const imageInput = ref(null)
const imageAttachment = ref(null)
const isRecording = ref(false)
const speechRecognitionSupported = ref(false)
let speechRecognition = null
let voiceInputBase = ''

function initializeSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  speechRecognitionSupported.value = Boolean(SpeechRecognition)
  if (!SpeechRecognition) return

  speechRecognition = new SpeechRecognition()
  speechRecognition.lang = 'es-ES'
  speechRecognition.continuous = true
  speechRecognition.interimResults = true

  speechRecognition.onresult = (event) => {
    let finalTranscript = ''
    let interimTranscript = ''
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const transcript = event.results[index][0]?.transcript || ''
      if (event.results[index].isFinal) finalTranscript += transcript
      else interimTranscript += transcript
    }

    if (finalTranscript.trim()) {
      voiceInputBase = [voiceInputBase, finalTranscript.trim()].filter(Boolean).join(' ')
    }
    inputMsg.value = [voiceInputBase, interimTranscript.trim()].filter(Boolean).join(' ')
  }

  speechRecognition.onerror = (event) => {
    isRecording.value = false
    if (event.error === 'aborted' || event.error === 'no-speech') return
    const message = event.error === 'not-allowed'
      ? 'Permite el acceso al micrófono para enviar mensajes por voz.'
      : 'No se pudo reconocer el audio. Inténtalo nuevamente.'
    notify(message, true)
  }

  speechRecognition.onend = () => {
    isRecording.value = false
  }
}

function toggleVoiceInput() {
  if (!speechRecognition) return notify('El navegador no admite dictado por voz.', true)
  if (isRecording.value) {
    speechRecognition.stop()
    return
  }

  voiceInputBase = inputMsg.value.trim()
  try {
    speechRecognition.start()
    isRecording.value = true
  } catch (error) {
    console.error('No se pudo iniciar el reconocimiento de voz.', error)
    notify('No se pudo iniciar el micrófono.', true)
  }
}

function clearImage() {
  imageAttachment.value = null
  if (imageInput.value) imageInput.value.value = ''
}

function selectImage(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const allowedTypes = ['image/png', 'image/jpeg']
  const maxBytes = 4 * 1024 * 1024
  if (!allowedTypes.includes(file.type) || file.size > maxBytes) {
    clearImage()
    return notify('Adjunta una imagen PNG o JPG de hasta 4 MB.', true)
  }

  const reader = new FileReader()
  reader.onload = () => {
    imageAttachment.value = {
      name: file.name,
      mime_type: file.type,
      data_url: reader.result,
    }
  }
  reader.onerror = () => notify('No se pudo leer la imagen adjunta.', true)
  reader.readAsDataURL(file)
}

function imagePayload() {
  return imageAttachment.value
    ? { data_url: imageAttachment.value.data_url, mime_type: imageAttachment.value.mime_type, name: imageAttachment.value.name }
    : null
}

const chatModes = [
  { value: 'consulta', label: 'Chat' },
  { value: 'practicar', label: 'Práctica' },
  { value: 'recurso_sintetico', label: 'Recurso sintético' },
]

const grupoLabel = (g) => `${g.nombre || 'Materia'} ${g.codigo ? '(' + g.codigo + ')' : ''}`
const activeCourseLabel = computed(() => {
  if (sessionContext.value?.materia_nombre) {
    const code = sessionContext.value.codigo_curso
    return code ? `${sessionContext.value.materia_nombre} · ${code}` : sessionContext.value.materia_nombre
  }
  const course = grupos.value.find((item) => item.id === activeSesion.value?.curso_id)
  return course ? grupoLabel(course) : 'Curso de la conversación'
})

const isModeEnabled = (mode) => {
  if (!sessionContext.value || !Array.isArray(sessionContext.value.modos_permitidos)) return true
  const enabled = sessionContext.value.modos_permitidos
  if (mode === 'consulta') return enabled.includes('chat')
  if (mode === 'recurso_sintetico') return enabled.includes('recursos')
  return enabled.includes(mode)
}

const MODE_META = {
  consulta: { label: 'Chat', icon: 'mdi-chat-outline' },
  practicar: { label: 'Práctica', icon: 'mdi-head-question-outline' },
  recurso_sintetico: { label: 'Recurso', icon: 'mdi-file-document-outline' },
}
const modeMeta = (tipo) => MODE_META[tipo] || { label: tipo, icon: 'mdi-chat-outline' }

function pickDefaultMode() {
  const firstEnabled = chatModes.find((opt) => isModeEnabled(opt.value))
  return firstEnabled?.value || null
}

async function scrollBottom() {
  await nextTick()
  if (messagesBox.value) messagesBox.value.scrollTop = messagesBox.value.scrollHeight
}

async function createSesion() {
  if (!newSesionGrupo.value) return notify('Selecciona un grupo', true)
  try {
    const r = await estudianteService.createSesion({ curso_id: newSesionGrupo.value })
    sesiones.value.unshift(r.sesion)
    newSesionGrupo.value = ''
    await openSesion(r.sesion)
  } catch (e) { err(e, 'No se pudo crear la sesión') }
}

function startRename(sesion) {
  renamingSesionId.value = sesion.id
  renamingTitle.value = sesion.titulo || ''
}

function cancelRename() {
  renamingSesionId.value = null
  renamingTitle.value = ''
}

async function confirmRename(sesionId) {
  const title = (renamingTitle.value || '').trim()
  if (!title) return notify('El título no puede estar vacío', true)
  try {
    const r = await estudianteService.updateSesion(sesionId, { titulo: title })
    const idx = sesiones.value.findIndex((x) => x.id === sesionId)
    if (idx >= 0) sesiones.value[idx] = r.sesion
    if (activeSesion.value?.id === sesionId) activeSesion.value = r.sesion
    cancelRename()
    notify('Título actualizado')
  } catch (e) {
    err(e, 'No se pudo actualizar el título')
  }
}

async function deleteSesion(sesion) {
  const ok = window.confirm('¿Eliminar esta conversación?')
  if (!ok) return
  try {
    await estudianteService.deleteSesion(sesion.id)
    sesiones.value = sesiones.value.filter((x) => x.id !== sesion.id)
    if (activeSesion.value?.id === sesion.id) {
      activeSesion.value = null
      mensajes.value = []
      sessionContext.value = null
    }
    notify('Conversación eliminada')
  } catch (e) {
    err(e, 'No se pudo eliminar la conversación')
  }
}

async function openSesion(sesion) {
  activeSesion.value = sesion
  selectedMode.value = null
  loadingSesion.value = true
  try {
    const [r, ctx] = await Promise.all([
      estudianteService.getMensajes(sesion.id),
      estudianteService.getSesionContexto(sesion.id),
    ])
    mensajes.value = r.mensajes || []
    sessionContext.value = ctx.contexto || null
    selectedMode.value = pickDefaultMode()
  } catch (e) { err(e, 'No se pudieron cargar los mensajes') }
  finally { loadingSesion.value = false }
  await nextTick()
  await scrollBottom()
}

async function sendByMode() {
  if (!selectedMode.value) return notify('Selecciona un modo de chat', true)
  if (!isModeEnabled(selectedMode.value)) return notify('Este modo está deshabilitado por tu coordinador', true)
  if (selectedMode.value === 'practicar') return sendPracticar()
  if (selectedMode.value === 'recurso_sintetico') return generarRecurso()
  return sendMessage()
}

async function sendMessage() {
  if (!activeSesion.value || (!inputMsg.value.trim() && !imageAttachment.value)) return
  const contenido = inputMsg.value.trim() || 'Analiza la imagen adjunta.'
  const image = imagePayload()
  const tempId = 'tmp-' + Date.now()
  mensajes.value.push({ id: tempId, rol: 'user', contenido, tipo_interaccion: 'consulta', image_name: image?.name || null })
  inputMsg.value = ''
  clearImage()
  sending.value = true
  await scrollBottom()
  try {
    const r = await estudianteService.sendMensaje(activeSesion.value.id, { contenido, image })
    const idx = mensajes.value.findIndex((x) => x.id === tempId)
    if (idx >= 0 && r.mensaje_usuario) mensajes.value[idx] = { ...r.mensaje_usuario, image_name: image?.name || null }
    if (r.mensaje_asistente) mensajes.value.push(r.mensaje_asistente)
    await scrollBottom()
  } catch (e) { err(e, 'Error al enviar mensaje') }
  finally { sending.value = false }
}

/* ---------- CU-11: Modo práctica ---------- */
async function sendPracticar() {
  if (!isModeEnabled('practicar')) return notify('Modo práctica deshabilitado por tu coordinador', true)
  if (!activeSesion.value || (!inputMsg.value.trim() && !imageAttachment.value)) return
  const contenido = inputMsg.value.trim() || 'Ayúdame a resolver el ejercicio de la imagen adjunta.'
  const image = imagePayload()
  const tempId = 'tmp-' + Date.now()
  mensajes.value.push({ id: tempId, rol: 'user', contenido, tipo_interaccion: 'practicar', image_name: image?.name || null })
  inputMsg.value = ''
  clearImage()
  sending.value = true
  await scrollBottom()
  try {
    const r = await estudianteService.practicar(activeSesion.value.id, { ejercicio: contenido, contenido, image })
    const idx = mensajes.value.findIndex((x) => x.id === tempId)
    if (idx >= 0 && r.mensaje_usuario) mensajes.value[idx] = { ...r.mensaje_usuario, image_name: image?.name || null }
    if (r.mensaje_asistente) mensajes.value.push(r.mensaje_asistente)
    await scrollBottom()
  } catch (e) { err(e, 'Modo práctica no disponible') }
  finally { sending.value = false }
}

/* ---------- CU-10: Recurso sintético ---------- */
async function generarRecurso() {
  if (!isModeEnabled('recurso_sintetico')) return notify('Recurso sintético deshabilitado por tu coordinador', true)
  if (!activeSesion.value) return notify('Abre una sesión primero', true)
  const image = imagePayload()
  const contenido = inputMsg.value.trim() || (image ? 'Genera un recurso a partir de la imagen adjunta.' : 'Generar recurso sintético')
  const tempId = 'tmp-' + Date.now()
  mensajes.value.push({ id: tempId, rol: 'user', contenido, tipo_interaccion: 'recurso_sintetico', image_name: image?.name || null })
  inputMsg.value = ''
  clearImage()
  sending.value = true
  await scrollBottom()
  try {
    const r = await estudianteService.recursoSintetico(activeSesion.value.id, { contenido, image })
    const idx = mensajes.value.findIndex((x) => x.id === tempId)
    if (idx >= 0 && r.mensaje_usuario) mensajes.value[idx] = { ...r.mensaje_usuario, image_name: image?.name || null }
    if (r.mensaje_asistente) mensajes.value.push(r.mensaje_asistente)
    else if (r.recurso) mensajes.value.push(r.recurso)
    await scrollBottom()
  } catch (e) { err(e, 'No se pudo generar el recurso') }
  finally { sending.value = false }
}

const tipoColor = (tipo) => ({
  examen: 'success',
  tarea: 'primary',
  proyecto: 'secondary',
}[tipo] || 'default')

const eventColor = (tipo) => ({
  examen: 'calendar-event--examen',
  tarea: 'calendar-event--tarea',
  proyecto: 'calendar-event--proyecto',
}[tipo] || 'calendar-event--default')

const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const viewMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))

const monthLabel = computed(() => viewMonth.value.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }))

const agendaByDate = computed(() => {
  const map = {}
  for (const a of actividades.value) {
    const d = new Date(a.fecha_limite)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    if (!map[key]) map[key] = []
    map[key].push(a)
  }
  return map
})

const calendarDays = computed(() => {
  const first = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth(), 1)
  const firstWeekDay = (first.getDay() + 6) % 7
  const start = new Date(first)
  start.setDate(first.getDate() - firstWeekDay)

  const today = new Date()
  const days = []
  for (let i = 0; i < 42; i++) {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    days.push({
      key,
      date,
      inMonth: date.getMonth() === viewMonth.value.getMonth(),
      isToday: date.toDateString() === today.toDateString(),
      events: agendaByDate.value[key] || [],
    })
  }
  return days
})

const upcomingActivities = computed(() => {
  const y = viewMonth.value.getFullYear()
  const m = viewMonth.value.getMonth()
  return [...actividades.value]
    .filter((a) => {
      const d = new Date(a.fecha_limite)
      return d.getFullYear() === y && d.getMonth() === m
    })
    .sort((a, b) => new Date(a.fecha_limite) - new Date(b.fecha_limite))
})

const formatDateTime = (iso) => new Date(iso).toLocaleString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })

async function loadAgenda() {
  try {
    const r = await estudianteService.getAgenda(agendaGrupoFilter.value || null)
    actividades.value = r.actividades || []
  } catch (e) {
    err(e, 'No se pudo cargar la agenda')
  }
}

function prevMonth() {
  viewMonth.value = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth() - 1, 1)
}

function nextMonth() {
  viewMonth.value = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth() + 1, 1)
}

/* ---------- Perfil ---------- */
const profileData = ref({ first_name: '', last_name: '', phone: '' })

async function loadProfile() {
  try {
    const resp = await estudianteService.getProfile()
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

async function updateProfile(data) {
  try {
    const resp = await estudianteService.updateProfile(data)
    authStore.setUserData(resp.user)
    notify('Perfil actualizado exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al actualizar perfil', true)
  }
}

async function updatePassword(data) {
  try {
    await estudianteService.updatePassword(data)
    notify('Contrasena actualizada exitosamente')
  } catch (err) {
    notify(err.response?.data?.message || 'Error al cambiar contrasena', true)
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
/* ===== Capa ambiental compartida con el Login ===== */
.student-app {
  background:
    radial-gradient(100% 90% at 0% 0%, rgba(124, 197, 118, 0.1), transparent 55%),
    radial-gradient(70% 110% at 100% 100%, rgba(69, 148, 113, 0.11), transparent 58%),
    linear-gradient(127deg, #111419 0%, #171b20 52%, #121518 100%) !important;
}

.student-ambient {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.student-ambient__noise {
  position: absolute;
  inset: 0;
  opacity: 0.18;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}

.student-ambient__vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(120% 95% at 50% 42%, transparent 45%, rgba(9, 11, 13, 0.5) 100%);
}

.student-main-layer {
  position: relative;
  z-index: 1;
}

/* ===== Barra superior ===== */
.student-bar {
  border-bottom: 1px solid rgba(124, 197, 118, 0.16) !important;
  background: linear-gradient(180deg, rgba(26, 30, 35, 0.92), rgba(19, 23, 27, 0.86)) !important;
  backdrop-filter: blur(14px) saturate(1.1);
}

.student-brand-symbol {
  position: relative;
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid rgba(155, 226, 153, 0.42);
  border-radius: 12px;
  color: #b6f2aa;
  background: linear-gradient(145deg, rgba(124, 197, 118, 0.22), rgba(124, 197, 118, 0.05));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 0 20px rgba(124, 197, 118, 0.16);
}

.student-app-bar--chat .student-brand-symbol {
  width: 32px;
  height: 32px;
  border-radius: 10px;
}

.student-brand-ring {
  position: absolute;
  inset: -5px;
  border: 1px solid rgba(124, 197, 118, 0.26);
  border-radius: 15px;
  animation: student-ring-pulse 3.4s ease-in-out infinite;
  pointer-events: none;
}

.student-toolbar-title {
  flex: 1 1 0;
  min-width: 0;
}

.student-toolbar-brand,
.student-toolbar-copy { min-width: 0; }
.student-toolbar-copy { flex: 1; }
.student-brand-symbol { flex-shrink: 0; }

.student-user-chip {
  max-width: min(260px, 30vw);
}

.student-user-chip :deep(.v-chip__content) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ===== Paneles con el lenguaje del Login ===== */
.student-panel {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(205, 237, 199, 0.16) !important;
  background:
    radial-gradient(circle at 8% 0%, rgba(124, 197, 118, 0.09), transparent 38%),
    linear-gradient(145deg, rgba(42, 48, 52, 0.85), rgba(24, 29, 32, 0.9)) !important;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(14px);
}

.student-panel::before,
.student-chat-create::before,
.student-chat-panel::before {
  position: absolute;
  top: 0;
  left: 10%;
  width: 80%;
  height: 1px;
  content: '';
  background: linear-gradient(90deg, transparent, rgba(171, 238, 163, 0.7), transparent);
  pointer-events: none;
  z-index: 1;
}

/* ===== Botón con destello (reuso del Login) ===== */
.student-shine {
  position: relative;
  overflow: hidden;
}

.student-shine::after {
  position: absolute;
  top: 0;
  left: -80%;
  width: 55%;
  height: 100%;
  content: '';
  background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transform: skewX(-18deg);
  transition: left 0.6s ease;
  pointer-events: none;
}

.student-shine:hover::after {
  left: 125%;
}

/* ===== Campos con foco luminoso (reuso del Login) ===== */
.student-field :deep(.v-field) {
  border-radius: 13px;
  transition: background 0.22s ease, box-shadow 0.22s ease;
}

.student-field :deep(.v-field--focused) {
  background: rgba(124, 197, 118, 0.07);
  box-shadow: 0 0 0 1px rgba(124, 197, 118, 0.25), 0 0 18px rgba(124, 197, 118, 0.1);
}

/* ===== Transición entre pestañas ===== */
.tabfade-enter-active {
  animation: student-tab-enter 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes student-tab-enter {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes student-ring-pulse {
  0%, 100% { opacity: 0.65; transform: scale(1); }
  50% { opacity: 0.15; transform: scale(1.12); }
}

/* ===== Perfil: hereda el estilo de panel ===== */
.student-profile :deep(.v-card) {
  border: 1px solid rgba(205, 237, 199, 0.16);
  background:
    radial-gradient(circle at 8% 0%, rgba(124, 197, 118, 0.09), transparent 38%),
    linear-gradient(145deg, rgba(42, 48, 52, 0.85), rgba(24, 29, 32, 0.9));
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(14px);
}

.student-chat-view {
  width: 100%;
  --chat-green: #7cc576;
  --chat-green-bright: #9be692;
}

.student-chat-container {
  height: 100%;
  max-width: none !important;
  overflow: hidden;
}

.student-chat-main {
  min-height: 0;
  overflow: hidden !important;
}

.student-chat-view {
  height: 100%;
  margin-bottom: 0;
}

.student-chat-view > :deep(.v-col) {
  min-height: 0;
}

.student-app-bar--chat :deep(.v-toolbar__content) {
  min-height: 58px !important;
}

.student-chat-create,
.student-chat-sessions,
.student-chat-panel {
  border: 1px solid rgba(205, 237, 199, 0.16) !important;
  background:
    radial-gradient(circle at 6% 0%, rgba(124, 197, 118, 0.11), transparent 35%),
    linear-gradient(145deg, rgba(42, 48, 52, 0.88), rgba(24, 29, 32, 0.92)) !important;
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(14px);
}

.student-chat-create {
  position: relative;
  overflow: hidden;
}

.student-chat-create::after {
  position: absolute;
  right: -35px;
  bottom: -42px;
  width: 125px;
  height: 125px;
  border: 1px solid rgba(155, 230, 146, 0.17);
  border-radius: 50%;
  content: '';
}

.student-chat-eyebrow {
  color: var(--chat-green-bright);
  font-size: 0.65rem;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.student-chat-create-icon,
.student-chat-no-messages-icon {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border: 1px solid rgba(155, 230, 146, 0.34);
  border-radius: 14px;
  color: var(--chat-green-bright);
  background: rgba(124, 197, 118, 0.12);
  box-shadow: 0 0 20px rgba(124, 197, 118, 0.16);
}

.student-chat-primary {
  color: #fff !important;
  font-weight: 800;
  background: linear-gradient(135deg, #7cc576, #5f9d5a) !important;
  box-shadow: 0 0 20px rgba(124, 197, 118, 0.27);
}

.student-chat-sessions {
  max-height: calc(100vh - 238px);
  overflow: auto;
}

.student-chat-empty-list {
  border: 1px dashed rgba(124, 197, 118, 0.26);
  border-radius: 14px;
  background: rgba(124, 197, 118, 0.04);
}

.student-session-item {
  min-height: 54px;
  border: 1px solid transparent;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.student-session-item:hover {
  border-color: rgba(124, 197, 118, 0.2);
  background: rgba(124, 197, 118, 0.07);
  transform: translateX(2px);
}

.student-session-item:deep(.v-list-item--active) {
  border-color: rgba(124, 197, 118, 0.3);
  background: linear-gradient(100deg, rgba(124, 197, 118, 0.19), rgba(124, 197, 118, 0.06));
}

.student-session-avatar,
.student-assistant-avatar {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  color: var(--chat-green-bright);
  background: rgba(124, 197, 118, 0.12);
}

.student-session-avatar {
  width: 31px;
  height: 31px;
  border: 1px solid rgba(124, 197, 118, 0.2);
  border-radius: 10px;
}

.student-chat-panel {
  height: 100%;
  min-height: 0;
}

.student-chat-welcome {
  position: relative;
  overflow: hidden;
  min-height: 550px;
  background:
    radial-gradient(circle at 50% 43%, rgba(124, 197, 118, 0.13), transparent 29%),
    linear-gradient(145deg, rgba(49, 54, 62, 0.72), rgba(31, 35, 42, 0.44));
}

.student-chat-welcome::before,
.student-chat-welcome::after {
  position: absolute;
  border: 1px solid rgba(124, 197, 118, 0.12);
  border-radius: 50%;
  content: '';
}

.student-chat-welcome::before { width: 410px; height: 410px; }
.student-chat-welcome::after { width: 585px; height: 585px; }

.student-chat-welcome > div { position: relative; z-index: 1; }

.student-chat-welcome-copy { max-width: 450px; color: rgba(235, 242, 235, 0.62); }

.student-chat-orbit {
  position: relative;
  width: 112px;
  height: 112px;
  border: 1px solid rgba(124, 197, 118, 0.26);
  border-radius: 50%;
  animation: chat-orbit-spin 16s linear infinite;
}

.student-chat-orbit::before {
  position: absolute;
  inset: 14px;
  border: 1px dashed rgba(124, 197, 118, 0.24);
  border-radius: 50%;
  content: '';
}

.student-chat-orbit-core {
  position: absolute;
  inset: 27px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(155, 230, 146, 0.45);
  border-radius: 50%;
  color: var(--chat-green-bright);
  background: linear-gradient(145deg, rgba(124, 197, 118, 0.28), rgba(124, 197, 118, 0.1));
  box-shadow: 0 0 28px rgba(124, 197, 118, 0.33);
  animation: chat-orbit-counter-spin 16s linear infinite;
}

.student-chat-orbit-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--chat-green-bright);
  box-shadow: 0 0 12px var(--chat-green-bright);
}

.student-chat-orbit-dot--one { top: 7px; left: 31px; }
.student-chat-orbit-dot--two { right: 3px; bottom: 28px; }
.student-chat-orbit-dot--three { bottom: 8px; left: 24px; }

.student-chat-header {
  flex: 0 0 auto;
  border-bottom: 1px solid rgba(124, 197, 118, 0.16);
  background: linear-gradient(90deg, rgba(124, 197, 118, 0.1), rgba(124, 197, 118, 0.015));
}

.student-chat-header .text-body-1 {
  line-height: 1.15;
}

.student-chat-header .text-caption {
  line-height: 1.05;
}

.student-chat-course-icon {
  display: grid;
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  place-items: center;
  border: 1px solid rgba(124, 197, 118, 0.28);
  border-radius: 13px;
  color: var(--chat-green-bright);
  background: rgba(124, 197, 118, 0.11);
}

.student-chat-online-chip { color: var(--chat-green-bright); font-weight: 700; }

.student-chat-online-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 6px;
  border-radius: 50%;
  background: var(--chat-green-bright);
  box-shadow: 0 0 0 0 rgba(155, 230, 146, 0.55);
  animation: chat-online-pulse 1.9s infinite;
}

.student-chat-messages {
  min-height: 0;
  flex: 1 1 0;
  background: linear-gradient(180deg, rgba(26, 30, 35, 0.15), rgba(42, 46, 53, 0.12));
  scrollbar-color: rgba(124, 197, 118, 0.45) transparent;
}

.student-chat-no-messages { max-width: 390px; margin: auto; }

.student-assistant-avatar {
  width: 28px;
  height: 28px;
  margin-bottom: 2px;
  border: 1px solid rgba(124, 197, 118, 0.24);
  border-radius: 9px;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 197, 118, 0.12);
  flex-shrink: 0;
}

.chat-bubble {
  max-width: min(86%, 760px);
  border-radius: 18px;
  padding: 11px 15px;
  white-space: pre-wrap;
  line-height: 1.55;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
}

.chat-mode-tag {
  display: inline-flex;
  align-items: center;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: rgba(184, 237, 177, 0.86);
  background: rgba(124, 197, 118, 0.1);
  border: 1px solid rgba(124, 197, 118, 0.16);
  border-radius: 999px;
  padding: 2px 8px 2px 6px;
  line-height: 1.4;
}

.chat-bubble--user {
  background: linear-gradient(135deg, #8bd584, #6bb566);
  color: #10200f;
  border-bottom-right-radius: 4px;
}

.chat-image-resource {
  display: flex;
  align-items: center;
  gap: 5px;
  max-width: 100%;
  margin-top: 9px;
  padding: 6px 8px;
  border: 1px solid rgba(16, 32, 15, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.24);
  font-size: 0.72rem;
  line-height: 1.25;
}

.chat-image-resource__label {
  flex: 0 0 auto;
  font-weight: 800;
}

.chat-image-resource__name {
  min-width: 0;
  font-weight: 600;
}

.chat-bubble--assistant {
  background: rgba(255, 255, 255, 0.075);
  color: rgb(var(--v-theme-on-surface));
  border: 1px solid rgba(124, 197, 118, 0.16);
  border-bottom-left-radius: 4px;
}

.chat-bubble--resource {
  width: min(100%, 1180px);
  min-width: 50%;
  max-width: calc(100% - 36px);
  padding: 8px 10px;
}

.chat-bubble--resource :deep(.mermaid-message__diagram) {
  margin: 8px 0;
}

.chat-bubble--resource :deep(.mermaid-message__preview) {
  min-height: 220px;
  padding: 18px 20px;
}

.student-chat-thinking {
  display: flex;
  align-items: center;
  gap: 9px;
}

.student-chat-thinking-bubble {
  display: flex;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid rgba(124, 197, 118, 0.17);
  border-radius: 14px 14px 14px 4px;
  background: rgba(124, 197, 118, 0.08);
}

.student-chat-thinking-bubble span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--chat-green-bright);
  animation: chat-typing 1.1s ease-in-out infinite;
}

.student-chat-thinking-bubble span:nth-child(2) { animation-delay: 0.15s; }
.student-chat-thinking-bubble span:nth-child(3) { animation-delay: 0.3s; }

.student-chat-composer {
  flex: 0 0 auto;
  border-top: 1px solid rgba(124, 197, 118, 0.16);
  background: linear-gradient(180deg, rgba(52, 57, 65, 0.94), rgba(43, 48, 56, 0.98));
}

.student-chat-mode-label {
  margin-right: 3px;
  color: rgba(234, 241, 234, 0.56);
  font-size: 0.71rem;
  font-weight: 750;
}

.student-chat-mode { font-weight: 750; text-transform: none; }

.student-chat-input-wrap { position: relative; }

.student-chat-input :deep(.v-field) {
  padding-right: 148px;
  border: 1px solid rgba(124, 197, 118, 0.2);
  border-radius: 13px;
  background: rgba(17, 21, 25, 0.28);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.student-chat-input :deep(textarea) { padding-bottom: 6px; }

.student-chat-send {
  position: absolute;
  right: 10px;
  bottom: 10px;
  z-index: 2;
  min-width: 30px;
  width: 30px;
  height: 30px;
  padding: 0;
  color: #fff !important;
  background: linear-gradient(135deg, #7cc576, #5d9e58) !important;
  box-shadow: 0 0 17px rgba(124, 197, 118, 0.27);
}

.student-chat-microphone {
  position: absolute;
  right: 50px;
  bottom: 8px;
  z-index: 2;
  width: 36px;
  min-width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid rgba(124, 197, 118, 0.22);
  background: rgba(255, 255, 255, 0.07) !important;
}

.student-chat-image-input {
  display: none;
}

.student-chat-image-button {
  position: absolute;
  right: 90px;
  bottom: 8px;
  z-index: 2;
  width: 32px;
  min-width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid rgba(124, 197, 118, 0.22);
  color: var(--chat-green-bright);
  background: rgba(255, 255, 255, 0.07) !important;
}

.student-chat-image-preview {
  display: flex;
  max-width: 340px;
  align-items: center;
  gap: 8px;
  padding: 5px 7px;
  border: 1px solid rgba(124, 197, 118, 0.24);
  border-radius: 10px;
  background: rgba(124, 197, 118, 0.08);
  color: rgba(235, 242, 235, 0.84);
  font-size: 0.72rem;
}

.student-chat-image-preview img {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  object-fit: cover;
}

.student-chat-image-preview span {
  flex: 1;
}

.student-chat-microphone--recording {
  color: #fff !important;
  background: rgb(var(--v-theme-error)) !important;
  animation: chat-recording-pulse 1.25s ease-in-out infinite;
}

.student-chat-recording-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgb(var(--v-theme-error));
  font-size: 0.7rem;
  font-weight: 700;
}

.student-chat-recording-status span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.student-chat-composer-note {
  color: rgba(230, 239, 230, 0.46);
  font-size: 0.68rem;
}

@keyframes chat-orbit-spin { to { transform: rotate(360deg); } }
@keyframes chat-orbit-counter-spin { to { transform: rotate(-360deg); } }

@keyframes chat-online-pulse {
  70% { box-shadow: 0 0 0 7px rgba(155, 230, 146, 0); }
  100% { box-shadow: 0 0 0 0 rgba(155, 230, 146, 0); }
}

@keyframes chat-typing {
  50% { opacity: 0.35; transform: translateY(-3px); }
}

@keyframes chat-recording-pulse {
  50% { box-shadow: 0 0 0 6px rgba(var(--v-theme-error), 0.16); }
}

@media (max-width: 1279px) {
  .student-chat-container,
  .student-chat-view { height: auto; overflow: visible; }
  .student-chat-main { overflow: auto !important; }
  .student-chat-panel { height: auto; min-height: 580px; }
  .student-chat-sessions { max-height: none; }
}

@media (max-width: 959px) {
  .student-toolbar-title { margin-inline: 8px; }
  .student-chat-container { padding-inline: 12px !important; }
  .student-chat-panel { min-height: min(620px, calc(100dvh - 150px)); }
  .student-chat-sessions { max-height: 360px; }
}

@media (max-width: 600px) {
  .student-chat-container { padding-inline: 8px !important; }
  .student-content-container { padding-inline: 12px !important; }
  .student-chat-panel { min-height: min(560px, calc(100dvh - 140px)); border-radius: 18px !important; }
  .student-chat-welcome { min-height: min(440px, calc(100dvh - 190px)); }
  .student-chat-welcome::after { width: 450px; height: 450px; }
  .student-chat-online-chip { display: none; }
  .student-chat-mode-label { width: 100%; }
  .chat-bubble { max-width: calc(100vw - 76px); padding: 10px 12px; }
  .chat-bubble--resource { min-width: 0; max-width: calc(100vw - 42px); }
  .student-chat-composer-note { line-height: 1.4; }

  .student-user-chip {
    width: 34px;
    min-width: 34px;
    max-width: 34px;
    padding-inline: 0 !important;
  }

  .student-user-chip :deep(.v-chip__content) { display: none; }
  .student-user-chip :deep(.v-chip__prepend) { margin-inline: auto; }
  .student-app-bar--chat .student-brand-symbol { display: none; }

  .agenda-toolbar { align-items: stretch !important; }
  .agenda-month-nav,
  .agenda-filter-row { width: 100%; }
  .agenda-month-label { flex: 1; min-width: 0; text-transform: capitalize; }
  .agenda-filter-row { align-items: stretch !important; flex-direction: column; }
  .agenda-course-filter { width: 100%; min-width: 0; }
  .agenda-filter-row > :deep(.v-btn) { width: 100%; }

  .student-calendar-scroll {
    margin-inline: -4px;
    padding: 2px 4px 8px;
    overflow-x: auto;
    overscroll-behavior-inline: contain;
    scrollbar-color: rgba(124, 197, 118, 0.45) transparent;
  }

  .student-calendar-scroll > .calendar-grid { min-width: 650px; }

  .student-chat-input :deep(.v-field) { padding-right: 116px; }
  .student-chat-microphone { right: 44px; width: 30px; min-width: 30px; height: 30px; bottom: 9px; }
  .student-chat-image-button { right: 78px; width: 30px; min-width: 30px; height: 30px; bottom: 9px; }
  .student-chat-send { right: 8px; width: 28px; min-width: 28px; height: 28px; bottom: 10px; }
  .student-chat-image-preview { width: 100%; max-width: none; }
}

@media (max-width: 359px) {
  .student-chat-mode { padding-inline: 9px !important; font-size: 0.7rem; }
  .student-chat-input :deep(.v-field) { padding-right: 108px; }
  .chat-bubble { max-width: calc(100vw - 64px); }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.student-calendar-scroll {
  max-width: 100%;
}

.calendar-cell {
  min-height: 98px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.calendar-cell--in:hover {
  border-color: rgba(124, 197, 118, 0.32);
  background: rgba(124, 197, 118, 0.05);
  transform: translateY(-2px);
}

.calendar-cell--today {
  border-color: rgba(155, 230, 146, 0.55);
  background: rgba(124, 197, 118, 0.08);
  box-shadow: inset 0 0 18px rgba(124, 197, 118, 0.08);
}

.calendar-cell--in {
  background: rgba(255, 255, 255, 0.03);
}

.calendar-cell--out {
  background: rgba(255, 255, 255, 0.01);
}

.calendar-events {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 70px;
  overflow-y: auto;
}

.calendar-event {
  width: 100%;
  text-align: left;
  border-radius: 6px;
  padding: 4px 6px;
  font-size: 10px;
  font-weight: 500;
  color: #0a0a0c;
  border: none;
  cursor: pointer;
}

.calendar-event--examen { background: rgba(124, 197, 118, 0.95); }
.calendar-event--tarea { background: rgba(124, 197, 118, 0.7); }
.calendar-event--proyecto { background: rgba(255, 255, 255, 0.55); }
.calendar-event--default { background: rgba(154, 155, 163, 0.9); }

@media (prefers-reduced-motion: reduce) {
  .student-brand-ring,
  .student-chat-orbit,
  .student-chat-orbit-core,
  .student-chat-online-dot,
  .tabfade-enter-active {
    animation: none !important;
  }

  .student-shine::after { display: none; }
  .calendar-cell--in:hover { transform: none; }
  .student-session-item:hover { transform: none; }
}
</style>

