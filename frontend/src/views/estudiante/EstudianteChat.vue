<template>
  <v-row class="chat-view" density="compact">
    <!-- Sesiones -->
    <v-col cols="12" lg="4" xl="3" class="chat-view__aside">
      <v-card class="chat-create surface-card pa-4" rounded="xl">
        <div class="d-flex align-start justify-space-between mb-3">
          <div>
            <p class="eyebrow mb-1">Espacio de estudio</p>
            <h2 class="text-title-large font-weight-black mb-1">Elige una materia</h2>
          </div>
          <div class="icon-tile" aria-hidden="true">
            <v-icon icon="mdi-book-open-variant" size="22"></v-icon>
          </div>
        </div>
        <v-select
          v-model="newSesionGrupo"
          :items="grupoOptions"
          label="Materia para explorar"
          prepend-inner-icon="mdi-book-open-variant-outline"
          class="mb-3"
        />
        <v-btn color="primary" variant="flat" block size="large" class="chat-create__cta" prepend-icon="mdi-arrow-up-right" :loading="creating" @click="createSesion">
          Abrir conversación
        </v-btn>
        <v-alert v-if="!loadingGrupos && !grupos.length" type="warning" variant="tonal" density="compact" class="mt-2 text-body-small">
          No estás inscrito en ningún grupo todavía.
        </v-alert>
      </v-card>

      <v-card class="chat-sessions surface-card pa-2" rounded="xl">
        <div class="d-flex align-center justify-space-between px-2 pt-2 pb-3">
          <h2 class="text-title-small font-weight-black mb-0">Tus conversaciones</h2>
          <v-icon icon="mdi-message-text-outline" color="primary" size="20"></v-icon>
        </div>
        <div v-if="loadingSesiones" class="d-flex flex-column align-center justify-center py-6 ga-3 text-subtle" role="status">
          <v-progress-circular indeterminate color="primary" size="34" width="4"></v-progress-circular>
          <p class="text-body-small mb-0">Cargando conversaciones...</p>
        </div>
        <div v-else-if="!sesiones.length" class="empty-state mx-2 mb-2">
          <v-icon icon="mdi-forum-outline" size="31" color="primary"></v-icon>
          <p class="text-body-medium font-weight-bold mb-0">Tu primera conversación empieza aquí</p>
          <p class="text-body-small mb-0">Crea un espacio por cada materia que quieras dominar.</p>
        </div>
        <v-list v-else density="compact" nav class="pa-0">
          <v-list-item
            v-for="s in sesiones"
            :key="s.id"
            :active="activeSesion?.id === s.id"
            color="primary"
            rounded="lg"
            class="mb-1 chat-session"
            @click="renamingSesionId !== s.id && openSesion(s)"
          >
            <div v-if="renamingSesionId === s.id" class="d-flex align-center ga-2 py-1" @click.stop>
              <v-text-field v-model="renamingTitle" density="compact" maxlength="200" aria-label="Nuevo título" autofocus @keydown.enter.prevent="confirmRename(s.id)" @keydown.esc="cancelRename" />
              <v-btn size="small" color="primary" variant="flat" @click="confirmRename(s.id)">Guardar</v-btn>
              <v-btn size="small" variant="text" @click="cancelRename">Cancelar</v-btn>
            </div>
            <div v-else class="d-flex align-center">
              <div class="chat-session__avatar mr-3" aria-hidden="true">
                <v-icon icon="mdi-forum-outline" size="17"></v-icon>
              </div>
              <v-list-item-title class="text-body-medium font-weight-bold flex-grow-1 text-truncate">{{ s.titulo }}</v-list-item-title>
              <v-btn icon="mdi-pencil-outline" variant="text" size="x-small" :aria-label="`Renombrar ${s.titulo}`" @click.stop="startRename(s)"></v-btn>
              <v-btn icon="mdi-delete-outline" variant="text" size="x-small" color="error" :aria-label="`Eliminar ${s.titulo}`" @click.stop="deleteSesion(s)"></v-btn>
            </div>
          </v-list-item>
        </v-list>
      </v-card>
    </v-col>

    <!-- Conversación -->
    <v-col cols="12" lg="8" xl="9" class="chat-view__main">
      <v-card class="chat-panel surface-card d-flex flex-column overflow-hidden" rounded="xl">
        <div v-if="!activeSesion" class="chat-welcome flex-grow-1 d-flex align-center justify-center">
          <SynapseBackdrop :density="26000" :max-nodes="70" />
          <div class="chat-welcome__copy text-center px-5">
            <div class="chat-orbit mx-auto mb-5" aria-hidden="true">
              <div class="chat-orbit__core"><v-icon icon="mdi-brain" size="35"></v-icon></div>
              <span class="chat-orbit__dot chat-orbit__dot--one"></span>
              <span class="chat-orbit__dot chat-orbit__dot--two"></span>
              <span class="chat-orbit__dot chat-orbit__dot--three"></span>
            </div>
            <p class="eyebrow mb-2">Tu compañero de aprendizaje</p>
            <h2 class="text-headline-small font-weight-black mb-2">Convierte tus dudas en progreso.</h2>
            <p class="text-body-medium text-subtle mb-0">Elige una materia o abre una conversación para empezar.</p>
          </div>
        </div>

        <template v-else>
          <div class="chat-header px-3 px-md-4 py-2">
            <div class="d-flex align-center ga-2 min-w-0">
              <div class="chat-header__icon" aria-hidden="true"><v-icon icon="mdi-book-education-outline" size="19"></v-icon></div>
              <div class="min-w-0">
                <h2 class="text-body-large font-weight-black mb-0 text-truncate">{{ activeSesion.titulo }}</h2>
                <p class="text-body-small text-subtle mb-0 text-truncate">{{ activeCourseLabel }}</p>
              </div>
            </div>
          </div>

          <div ref="messagesBox" class="chat-messages flex-grow-1 pa-3 pa-md-4" aria-live="polite">
            <div v-if="loadingSesion" class="d-flex flex-column align-center justify-center ga-3 text-subtle chat-messages__loading" role="status">
              <v-progress-circular indeterminate color="primary" size="40" width="4"></v-progress-circular>
              <p class="text-body-small mb-0">Cargando conversación...</p>
            </div>
            <template v-else>
              <div v-if="!mensajes.length" class="chat-messages__empty text-center py-10">
                <div class="icon-tile mx-auto mb-3" aria-hidden="true"><v-icon icon="mdi-lightbulb-on-outline" size="27"></v-icon></div>
                <p class="font-weight-black mb-1">¿Qué quieres entender hoy?</p>
                <p class="text-body-small text-subtle mb-0">Escribe una pregunta, plantea un ejercicio o genera un recurso para estudiar.</p>
              </div>
              <div v-for="m in mensajes" :key="m.id" :class="['d-flex flex-column mb-4', m.rol === 'user' ? 'align-end' : 'align-start']">
                <span v-if="m.tipo_interaccion" class="chat-mode-tag mb-1">
                  <v-icon :icon="modeMeta(m.tipo_interaccion).icon" size="11" class="mr-1"></v-icon>{{ modeMeta(m.tipo_interaccion).label }}
                </span>
                <div :class="['chat-message', { 'chat-message--user': m.rol === 'user', 'chat-message--resource': isResource(m) }]">
                  <div v-if="m.rol !== 'user'" class="chat-assistant-avatar" aria-hidden="true"><v-icon icon="mdi-brain" size="15"></v-icon></div>
                  <div :class="['chat-bubble text-body-medium', m.rol === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant', { 'chat-bubble--resource': isResource(m) }]">
                    <MermaidMessage v-if="isResource(m)" :content="m.contenido" />
                    <template v-else>{{ m.contenido }}</template>
                    <div v-if="m.rol === 'user' && m.image_name" class="chat-image-resource" :title="`Imagen: ${m.image_name}`">
                      <v-icon icon="mdi-image-outline" size="16"></v-icon>
                      <span class="font-weight-bold">Imagen:</span>
                      <span class="text-truncate">{{ m.image_name }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="sending" class="chat-thinking" role="status">
                <div class="chat-assistant-avatar" aria-hidden="true"><v-icon icon="mdi-brain" size="15"></v-icon></div>
                <div class="chat-thinking__bubble" aria-hidden="true"><span></span><span></span><span></span></div>
                <p class="text-body-small text-subtle mb-0">Pensando contigo...</p>
              </div>
            </template>
          </div>

          <div class="chat-composer pa-2 pa-md-3">
            <div class="d-flex flex-wrap align-center ga-2 mb-2" role="group" aria-label="Enfoque de la respuesta">
              <span class="chat-composer__label">Elige tu enfoque</span>
              <v-btn
                v-for="opt in CHAT_MODES"
                :key="opt.value"
                :color="selectedMode === opt.value ? 'primary' : 'default'"
                :variant="selectedMode === opt.value ? 'flat' : 'tonal'"
                :disabled="!isModeEnabled(opt.value)"
                :aria-pressed="selectedMode === opt.value"
                size="small"
                class="chat-composer__mode"
                @click="selectedMode = opt.value"
              >
                {{ opt.label }}
              </v-btn>
            </div>
            <div class="chat-input">
              <input ref="imageInput" class="d-none" type="file" accept="image/png,image/jpeg" @change="selectImage" />
              <v-textarea
                v-model="inputMsg"
                rows="1"
                max-rows="6"
                auto-grow
                :placeholder="xs ? 'Escribe aquí…' : 'Escribe lo que quieres aprender…'"
                aria-label="Mensaje"
                variant="solo"
                flat
                class="chat-input__field"
                :disabled="loadingSesion"
                @keydown.enter.exact.prevent="send"
              />
              <div class="chat-input__actions">
                <v-btn
                  icon
                  size="small"
                  variant="tonal"
                  class="chat-input__tool"
                  :disabled="sending || loadingSesion"
                  aria-label="Adjuntar imagen"
                  @click="imageInput?.click()"
                >
                  <v-icon icon="mdi-image-outline" size="19"></v-icon>
                  <v-tooltip activator="parent" location="top">Adjuntar imagen</v-tooltip>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  :variant="isRecording ? 'flat' : 'tonal'"
                  :color="isRecording ? 'error' : undefined"
                  :class="['chat-input__tool', { 'chat-input__tool--recording': isRecording }]"
                  :disabled="sending || loadingSesion || !speechSupported"
                  :aria-label="isRecording ? 'Detener grabación' : 'Grabar mensaje de voz'"
                  @click="toggleVoiceInput"
                >
                  <v-icon :icon="isRecording ? 'mdi-stop' : 'mdi-microphone-outline'" size="19"></v-icon>
                  <v-tooltip activator="parent" location="top">
                    {{ speechSupported ? (isRecording ? 'Detener y revisar texto' : 'Grabar mensaje de voz') : 'El navegador no admite dictado por voz' }}
                  </v-tooltip>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  color="primary"
                  variant="flat"
                  :loading="sending"
                  :disabled="!selectedMode || loadingSesion || isRecording"
                  aria-label="Enviar mensaje"
                  @click="send"
                >
                  <v-icon icon="mdi-send" size="19"></v-icon>
                </v-btn>
              </div>
            </div>
            <div v-if="imageAttachment" class="chat-image-preview mt-2">
              <img :src="imageAttachment.data_url" alt="Vista previa de imagen adjunta" />
              <span class="text-truncate">{{ imageAttachment.name }}</span>
              <v-btn icon="mdi-close" size="x-small" variant="text" aria-label="Quitar imagen" @click="clearImage" />
            </div>
            <p v-if="isRecording" class="chat-recording mb-0 mt-1" role="status">
              <span></span> Escuchando… pulsa detener para revisar antes de enviar.
            </p>
          </div>
        </template>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useDisplay } from 'vuetify'
import { estudianteService } from '../../services'
import { errorMessage } from '../../composables/useToast'
import MermaidMessage from '../../components/MermaidMessage.vue'
import SynapseBackdrop from '../../components/SynapseBackdrop.vue'

const props = defineProps({
  grupos: { type: Array, default: () => [] },
  loadingGrupos: { type: Boolean, default: false },
})
const emit = defineEmits(['notify'])
const { xs } = useDisplay()

const notify = (message, isError = false) => emit('notify', message, isError)
const fail = (e, fallback) => notify(errorMessage(e, fallback), true)

const CHAT_MODES = [
  { value: 'consulta', label: 'Chat' },
  { value: 'practicar', label: 'Práctica' },
  { value: 'recurso_sintetico', label: 'Recurso sintético' },
]

const MODE_META = {
  consulta: { label: 'Chat', icon: 'mdi-chat-outline' },
  practicar: { label: 'Práctica', icon: 'mdi-head-question-outline' },
  recurso_sintetico: { label: 'Recurso', icon: 'mdi-file-document-outline' },
}

// Backend permission keys differ from the interaction types used by the chat.
const MODE_PERMISSION = { consulta: 'chat', practicar: 'practicar', recurso_sintetico: 'recursos' }

const SEND_STRATEGIES = {
  consulta: {
    defaultText: () => 'Analiza la imagen adjunta.',
    request: (id, contenido, image) => estudianteService.sendMensaje(id, { contenido, image }),
    error: 'Error al enviar mensaje',
  },
  practicar: {
    defaultText: () => 'Ayúdame a resolver el ejercicio de la imagen adjunta.',
    request: (id, contenido, image) => estudianteService.practicar(id, { ejercicio: contenido, contenido, image }),
    error: 'Modo práctica no disponible',
  },
  recurso_sintetico: {
    allowEmpty: true,
    defaultText: (image) => (image ? 'Genera un recurso a partir de la imagen adjunta.' : 'Generar recurso sintético'),
    request: (id, contenido, image) => estudianteService.recursoSintetico(id, { contenido, image }),
    error: 'No se pudo generar el recurso',
  },
}

const sesiones = ref([])
const loadingSesiones = ref(true)
const creating = ref(false)
const activeSesion = ref(null)
const mensajes = ref([])
const inputMsg = ref('')
const sending = ref(false)
const loadingSesion = ref(false)
const newSesionGrupo = ref(null)
const messagesBox = ref(null)
const sessionContext = ref(null)
const selectedMode = ref(null)
const renamingSesionId = ref(null)
const renamingTitle = ref('')
const imageInput = ref(null)
const imageAttachment = ref(null)
let openRequest = 0

const grupoLabel = (g) => `${g.nombre || 'Materia'}${g.codigo ? ` (${g.codigo})` : ''}`
const grupoOptions = computed(() => props.grupos.map((g) => ({ title: grupoLabel(g), value: g.id })))
const isResource = (m) => m.rol === 'assistant' && m.tipo_interaccion === 'recurso_sintetico'
const modeMeta = (tipo) => MODE_META[tipo] || { label: tipo, icon: 'mdi-chat-outline' }

const activeCourseLabel = computed(() => {
  const ctx = sessionContext.value
  if (ctx?.materia_nombre) return ctx.codigo_curso ? `${ctx.materia_nombre} · ${ctx.codigo_curso}` : ctx.materia_nombre
  const course = props.grupos.find((item) => item.id === activeSesion.value?.curso_id)
  return course ? grupoLabel(course) : 'Curso de la conversación'
})

function isModeEnabled(mode) {
  const enabled = sessionContext.value?.modos_permitidos
  if (!Array.isArray(enabled)) return true
  return enabled.includes(MODE_PERMISSION[mode])
}

async function scrollBottom() {
  await nextTick()
  if (messagesBox.value) messagesBox.value.scrollTop = messagesBox.value.scrollHeight
}

/* ---------- Sesiones ---------- */
async function loadSesiones() {
  loadingSesiones.value = true
  try {
    const r = await estudianteService.listSesiones()
    sesiones.value = r.sesiones || []
  } catch (e) {
    fail(e, 'No se pudieron cargar tus conversaciones')
  } finally {
    loadingSesiones.value = false
  }
}

async function createSesion() {
  if (!newSesionGrupo.value) return notify('Selecciona una materia', true)
  creating.value = true
  try {
    const r = await estudianteService.createSesion({ curso_id: newSesionGrupo.value })
    sesiones.value.unshift(r.sesion)
    newSesionGrupo.value = null
    await openSesion(r.sesion)
  } catch (e) {
    fail(e, 'No se pudo crear la conversación')
  } finally {
    creating.value = false
  }
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
  const title = renamingTitle.value.trim()
  if (!title) return notify('El título no puede estar vacío', true)
  try {
    const r = await estudianteService.updateSesion(sesionId, { titulo: title })
    sesiones.value = sesiones.value.map((x) => (x.id === sesionId ? r.sesion : x))
    if (activeSesion.value?.id === sesionId) activeSesion.value = r.sesion
    cancelRename()
    notify('Título actualizado')
  } catch (e) {
    fail(e, 'No se pudo actualizar el título')
  }
}

async function deleteSesion(sesion) {
  if (!window.confirm('¿Eliminar esta conversación?')) return
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
    fail(e, 'No se pudo eliminar la conversación')
  }
}

async function openSesion(sesion) {
  const request = ++openRequest
  activeSesion.value = sesion
  selectedMode.value = null
  mensajes.value = []
  sessionContext.value = null
  loadingSesion.value = true
  try {
    const [r, ctx] = await Promise.all([
      estudianteService.getMensajes(sesion.id),
      estudianteService.getSesionContexto(sesion.id),
    ])
    if (request !== openRequest) return
    mensajes.value = r.mensajes || []
    sessionContext.value = ctx.contexto || null
    selectedMode.value = CHAT_MODES.find((opt) => isModeEnabled(opt.value))?.value || null
  } catch (e) {
    if (request === openRequest) fail(e, 'No se pudieron cargar los mensajes')
  } finally {
    if (request === openRequest) loadingSesion.value = false
  }
  await scrollBottom()
}

/* ---------- Envío (CU-08 chat, CU-10 recurso, CU-11 práctica) ---------- */
async function send() {
  const mode = selectedMode.value
  if (sending.value || !activeSesion.value) return
  if (!mode) return notify('Selecciona un modo de chat', true)
  if (!isModeEnabled(mode)) return notify('Este modo está deshabilitado por tu coordinador', true)

  const strategy = SEND_STRATEGIES[mode]
  const text = inputMsg.value.trim()
  const image = imageAttachment.value
    ? { data_url: imageAttachment.value.data_url, mime_type: imageAttachment.value.mime_type, name: imageAttachment.value.name }
    : null
  if (!text && !image && !strategy.allowEmpty) return

  const sesionId = activeSesion.value.id
  const contenido = text || strategy.defaultText(image)
  const imageName = image?.name || null
  const tempId = `tmp-${Date.now()}`
  mensajes.value.push({ id: tempId, rol: 'user', contenido, tipo_interaccion: mode, image_name: imageName })
  inputMsg.value = ''
  clearImage()
  sending.value = true
  await scrollBottom()

  try {
    const r = await strategy.request(sesionId, contenido, image)
    if (activeSesion.value?.id !== sesionId) return
    const idx = mensajes.value.findIndex((x) => x.id === tempId)
    if (idx >= 0 && r.mensaje_usuario) mensajes.value[idx] = { ...r.mensaje_usuario, image_name: imageName }
    const reply = r.mensaje_asistente || r.recurso
    if (reply) mensajes.value.push(reply)
    await scrollBottom()
  } catch (e) {
    fail(e, strategy.error)
  } finally {
    sending.value = false
  }
}

/* ---------- Imagen adjunta ---------- */
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg']
const MAX_IMAGE_BYTES = 4 * 1024 * 1024

function clearImage() {
  imageAttachment.value = null
  if (imageInput.value) imageInput.value.value = ''
}

function selectImage(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!ALLOWED_IMAGE_TYPES.includes(file.type) || file.size > MAX_IMAGE_BYTES) {
    clearImage()
    return notify('Adjunta una imagen PNG o JPG de hasta 4 MB.', true)
  }
  const reader = new FileReader()
  reader.onload = () => {
    imageAttachment.value = { name: file.name, mime_type: file.type, data_url: reader.result }
  }
  reader.onerror = () => notify('No se pudo leer la imagen adjunta.', true)
  reader.readAsDataURL(file)
}

/* ---------- Dictado por voz ---------- */
const isRecording = ref(false)
const speechSupported = ref(false)
let speechRecognition = null
let voiceInputBase = ''

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  speechSupported.value = Boolean(SpeechRecognition)
  if (!SpeechRecognition) return

  speechRecognition = new SpeechRecognition()
  speechRecognition.lang = 'es-ES'
  speechRecognition.continuous = true
  speechRecognition.interimResults = true

  speechRecognition.onresult = (event) => {
    let finalTranscript = ''
    let interimTranscript = ''
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0]?.transcript || ''
      if (event.results[i].isFinal) finalTranscript += transcript
      else interimTranscript += transcript
    }
    if (finalTranscript.trim()) voiceInputBase = [voiceInputBase, finalTranscript.trim()].filter(Boolean).join(' ')
    inputMsg.value = [voiceInputBase, interimTranscript.trim()].filter(Boolean).join(' ')
  }

  speechRecognition.onerror = (event) => {
    isRecording.value = false
    if (event.error === 'aborted' || event.error === 'no-speech') return
    notify(event.error === 'not-allowed'
      ? 'Permite el acceso al micrófono para enviar mensajes por voz.'
      : 'No se pudo reconocer el audio. Inténtalo nuevamente.', true)
  }

  speechRecognition.onend = () => {
    isRecording.value = false
  }
}

function toggleVoiceInput() {
  if (!speechRecognition) return notify('El navegador no admite dictado por voz.', true)
  if (isRecording.value) return speechRecognition.stop()

  voiceInputBase = inputMsg.value.trim()
  try {
    speechRecognition.start()
    isRecording.value = true
  } catch (error) {
    console.error('No se pudo iniciar el reconocimiento de voz.', error)
    notify('No se pudo iniciar el micrófono.', true)
  }
}

onMounted(() => {
  loadSesiones()
  initSpeechRecognition()
})

onBeforeUnmount(() => {
  if (speechRecognition && isRecording.value) speechRecognition.abort()
  speechRecognition = null
})
</script>

<style scoped>
.chat-view {
  height: 100%;
  margin: 0;
}

.chat-view > .v-col {
  min-height: 0;
}

.chat-view__aside {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-view__main {
  display: flex;
  flex-direction: column;
}

.chat-create {
  flex: 0 0 auto;
  overflow: hidden;
}

.chat-create__cta {
  font-weight: 800;
}

.chat-sessions {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.chat-session {
  min-height: 54px;
  border: 1px solid transparent;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.chat-session:hover {
  border-color: rgba(var(--tutoria-green-rgb), 0.2);
  background: rgba(var(--tutoria-green-rgb), 0.07);
}

.chat-session.v-list-item--active {
  border-color: rgba(var(--tutoria-green-rgb), 0.3);
}

.chat-session__avatar,
.chat-assistant-avatar,
.chat-header__icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.24);
  color: var(--tutoria-green-bright);
  background: rgba(var(--tutoria-green-rgb), 0.12);
}

.chat-session__avatar {
  width: 31px;
  height: 31px;
  border-radius: 10px;
}

.chat-assistant-avatar {
  width: 28px;
  height: 28px;
  margin-bottom: 2px;
  border-radius: 9px;
}

.chat-header__icon {
  width: 30px;
  height: 30px;
  border-radius: 10px;
}

.chat-panel {
  flex: 1 1 auto;
  min-height: 0;
}

/* ---------- Bienvenida ---------- */
.chat-welcome {
  position: relative;
  overflow: hidden;
  min-height: 440px;
  background: radial-gradient(circle at 50% 43%, rgba(var(--tutoria-green-rgb), 0.13), transparent 29%);
}

.chat-welcome::before,
.chat-welcome::after {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.12);
  border-radius: 50%;
  content: '';
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.chat-welcome::before { width: 410px; height: 410px; }
.chat-welcome::after { width: 585px; height: 585px; }

.chat-welcome__copy {
  position: relative;
  z-index: 1;
  max-width: 460px;
}

.chat-orbit {
  position: relative;
  width: 112px;
  height: 112px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.26);
  border-radius: 50%;
  animation: chat-orbit-spin 16s linear infinite;
}

.chat-orbit::before {
  position: absolute;
  inset: 14px;
  border: 1px dashed rgba(var(--tutoria-green-rgb), 0.24);
  border-radius: 50%;
  content: '';
}

.chat-orbit__core {
  position: absolute;
  inset: 27px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(155, 230, 146, 0.45);
  border-radius: 50%;
  color: var(--tutoria-green-bright);
  background: linear-gradient(145deg, rgba(var(--tutoria-green-rgb), 0.28), rgba(var(--tutoria-green-rgb), 0.1));
  box-shadow: 0 0 28px rgba(var(--tutoria-green-rgb), 0.33);
  animation: chat-orbit-spin 16s linear infinite reverse;
}

.chat-orbit__dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--tutoria-green-bright);
  box-shadow: 0 0 12px var(--tutoria-green-bright);
}

.chat-orbit__dot--one { top: 7px; left: 31px; }
.chat-orbit__dot--two { right: 3px; bottom: 28px; }
.chat-orbit__dot--three { bottom: 8px; left: 24px; }

/* ---------- Conversación ---------- */
.chat-header {
  flex: 0 0 auto;
  border-bottom: 1px solid rgba(var(--tutoria-green-rgb), 0.16);
  background: linear-gradient(90deg, rgba(var(--tutoria-green-rgb), 0.1), rgba(var(--tutoria-green-rgb), 0.015));
}

.chat-messages {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
}

.chat-messages__loading {
  min-height: 260px;
  height: 100%;
}

.chat-messages__empty {
  max-width: 390px;
  margin: auto;
}

.chat-mode-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px 2px 6px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.16);
  border-radius: 999px;
  color: rgba(184, 237, 177, 0.86);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.02em;
  line-height: 1.4;
  background: rgba(var(--tutoria-green-rgb), 0.1);
}

.chat-message {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  max-width: min(86%, 760px);
}

.chat-message--user {
  flex-direction: row-reverse;
}

.chat-message--resource {
  width: 100%;
  max-width: min(100%, 1180px);
}

.chat-bubble {
  min-width: 0;
  padding: 11px 15px;
  border-radius: 16px;
  line-height: 1.55;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
}

.chat-bubble--user {
  border-bottom-right-radius: 4px;
  color: #10200f;
  background: linear-gradient(135deg, #8bd584, #6bb566);
}

.chat-bubble--assistant {
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.16);
  border-bottom-left-radius: 4px;
  color: var(--tutoria-text);
  background: rgba(255, 255, 255, 0.075);
}

.chat-bubble--resource {
  flex: 1 1 auto;
  padding: 8px 10px;
  white-space: normal;
}

.chat-bubble--resource :deep(.mermaid-message__preview) {
  min-height: 220px;
  padding: 18px 20px;
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
  font-size: 0.72rem;
  line-height: 1.25;
  background: rgba(255, 255, 255, 0.24);
}

.chat-thinking {
  display: flex;
  align-items: center;
  gap: 9px;
}

.chat-thinking__bubble {
  display: flex;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.17);
  border-radius: 14px 14px 14px 4px;
  background: rgba(var(--tutoria-green-rgb), 0.08);
}

.chat-thinking__bubble span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--tutoria-green-bright);
  animation: chat-typing 1.1s ease-in-out infinite;
}

.chat-thinking__bubble span:nth-child(2) { animation-delay: 0.15s; }
.chat-thinking__bubble span:nth-child(3) { animation-delay: 0.3s; }

/* ---------- Composer ---------- */
.chat-composer {
  flex: 0 0 auto;
  border-top: 1px solid rgba(var(--tutoria-green-rgb), 0.16);
  background: rgba(30, 35, 40, 0.92);
}

.chat-composer__label {
  margin-right: 3px;
  color: var(--tutoria-text-muted);
  font-size: 0.72rem;
  font-weight: 700;
}

.chat-composer__mode {
  font-weight: 700;
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 6px 8px 6px 4px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.22);
  border-radius: 14px;
  background: rgba(17, 21, 25, 0.35);
}

.chat-input:focus-within {
  border-color: rgba(var(--tutoria-green-rgb), 0.5);
}

.chat-input__field {
  flex: 1 1 auto;
  min-width: 0;
}

.chat-input__field :deep(.v-field) {
  background: transparent;
  box-shadow: none;
}

.chat-input__actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 6px;
  padding-bottom: 4px;
}

.chat-input__tool {
  color: var(--tutoria-green-bright);
}

.chat-input__tool--recording {
  color: #fff;
  animation: chat-recording-pulse 1.25s ease-in-out infinite;
}

.chat-image-preview {
  display: flex;
  max-width: 340px;
  align-items: center;
  gap: 8px;
  padding: 5px 7px;
  border: 1px solid rgba(var(--tutoria-green-rgb), 0.24);
  border-radius: 10px;
  color: var(--tutoria-text-muted);
  font-size: 0.72rem;
  background: rgba(var(--tutoria-green-rgb), 0.08);
}

.chat-image-preview img {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  object-fit: cover;
}

.chat-image-preview span {
  flex: 1;
}

.chat-recording {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgb(var(--v-theme-error));
  font-size: 0.7rem;
  font-weight: 700;
}

.chat-recording span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

@keyframes chat-orbit-spin { to { transform: rotate(360deg); } }
@keyframes chat-typing { 50% { opacity: 0.35; transform: translateY(-3px); } }
@keyframes chat-recording-pulse { 50% { box-shadow: 0 0 0 6px rgba(var(--v-theme-error), 0.16); } }

/* Below Vuetify's lg breakpoint the columns stack and the page scrolls. */
@media (max-width: 1144px) {
  .chat-view { height: auto; }
  .chat-sessions { max-height: 360px; }
  .chat-panel { height: min(680px, calc(100dvh - 96px)); min-height: 480px; }
}

@media (max-width: 599px) {
  .chat-panel { height: calc(100dvh - 84px); min-height: 420px; }
  .chat-welcome::after { width: 450px; height: 450px; }
  .chat-composer__label { width: 100%; }
  .chat-message { max-width: 94%; }
  .chat-bubble { padding: 10px 12px; }
  .chat-image-preview { width: 100%; max-width: none; }
}
</style>
