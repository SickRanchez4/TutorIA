<template>
  <div class="mermaid-message">
    <template v-for="(part, index) in parts" :key="index">
      <p v-if="part.type === 'text'" class="mermaid-message__text">{{ part.value }}</p>
      <div v-else class="mermaid-message__diagram" :aria-label="diagramLabel(part.value)">
        <div v-if="renderErrors[index]" class="mermaid-message__error">
          No se pudo renderizar este diagrama.
        </div>
        <div v-else class="mermaid-message__preview">
          <button
            type="button"
            class="mermaid-message__expand-button"
            :aria-label="`Ampliar ${diagramLabel(part.value).toLowerCase()}`"
            title="Ampliar diagrama"
            @click="expandDiagram(index)"
          >
            <v-icon icon="mdi-magnify-plus-outline" size="20"></v-icon>
          </button>
          <div v-if="!renderedSvgs[index]" class="mermaid-message__loading">
            <v-progress-circular indeterminate color="primary" size="24" width="3"></v-progress-circular>
            Generando diagrama...
          </div>
          <div v-else class="mermaid-message__svg" v-html="renderedSvgs[index]"></div>
        </div>
      </div>
    </template>

    <v-dialog v-model="expanded" max-width="1200" scrollable>
      <v-card class="mermaid-message__dialog position-relative" rounded="xl">
        <v-btn
          icon="mdi-close"
          class="mermaid-message__dialog-close"
          size="small"
          aria-label="Cerrar diagrama ampliado"
          @click="expanded = false"
        ></v-btn>
        <v-card-text class="mermaid-message__dialog-content">
          <div class="mermaid-message__expanded-svg" v-html="expandedSvg"></div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import mermaid from 'mermaid'

let mermaidInitialized = false
let nextDiagramId = 0

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

const renderErrors = ref({})
const renderedSvgs = ref({})
const expanded = ref(false)
const expandedSvg = ref('')
let renderSequence = 0

const parts = computed(() => {
  const result = []
  const matcher = /```mermaid\s*\r?\n([\s\S]*?)```/gi
  let lastIndex = 0
  let match

  while ((match = matcher.exec(props.content)) !== null) {
    const text = props.content.slice(lastIndex, match.index).trim()
    if (text) result.push({ type: 'text', value: text })
    result.push({ type: 'diagram', value: cleanMermaidSource(match[1]) })
    lastIndex = matcher.lastIndex
  }

  const trailingText = props.content.slice(lastIndex).trim()
  if (trailingText) result.push({ type: 'text', value: trailingText })
  return result.length ? result : [{ type: 'text', value: props.content }]
})

function cleanMermaidSource(source) {
  return String(source || '')
    .replace(/^\uFEFF/, '')
    .trim()
    .replace(/^```mermaid\s*\r?\n/i, '')
    .replace(/\r?\n```\s*$/, '')
    .trim()
}

const diagramLabel = () => 'Diagrama generado para el recurso de estudio'

function prepareSvg(svg) {
  // Mermaid genera SVG sin fondo. Se fija aquí para aislar cada gráfico de los
  // estilos y colores del cuadro de chat que lo contiene.
  return svg.replace(/<svg\b([^>]*)>/i, '<svg$1 style="background:#ffffff; color:#172033; display:block; max-width:100%; height:auto; margin:0 auto;">')
}

function expandDiagram(index) {
  const svg = renderedSvgs.value[index]
  if (!svg) return
  expandedSvg.value = svg
  expanded.value = true
}

async function renderDiagrams() {
  const sequence = ++renderSequence
  renderErrors.value = {}
  renderedSvgs.value = {}

  for (const [index, part] of parts.value.entries()) {
    if (part.type !== 'diagram') continue

    try {
      const source = cleanMermaidSource(part.value)
      const renderId = `tutoria-mermaid-${Date.now()}-${++nextDiagramId}-${index}`
      const { svg } = await mermaid.render(renderId, source)
      if (sequence === renderSequence) {
        renderedSvgs.value = { ...renderedSvgs.value, [index]: prepareSvg(svg) }
      }
    } catch (error) {
      console.error('No se pudo renderizar el diagrama Mermaid.', error)
      if (sequence === renderSequence) renderErrors.value = { ...renderErrors.value, [index]: true }
    }
  }
}

onMounted(() => {
  if (!mermaidInitialized) {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'strict',
      suppressErrorRendering: true,
      themeVariables: {
      background: '#ffffff',
      primaryColor: '#e8f0ff',
      primaryTextColor: '#172033',
      primaryBorderColor: '#315da8',
      secondaryColor: '#eef7f2',
      secondaryTextColor: '#172033',
      secondaryBorderColor: '#3f8a65',
      tertiaryColor: '#fff5df',
      tertiaryTextColor: '#172033',
      tertiaryBorderColor: '#b47516',
      lineColor: '#53657d',
      textColor: '#172033',
      mainBkg: '#ffffff',
      nodeBorder: '#315da8',
      clusterBkg: '#f7faff',
      clusterBorder: '#b7c9e7',
      titleColor: '#172033',
      edgeLabelBackground: '#ffffff',
      timelineSectionBkgColor: '#f7faff',
      timelineSectionBkgColor2: '#ffffff',
      timelineTaskBkgColor: '#e8f0ff',
      timelineTaskTextColor: '#172033',
      timelineTaskBorderColor: '#315da8',
      },
    })
    mermaidInitialized = true
  }
  renderDiagrams()
})

watch(() => props.content, renderDiagrams)
onUnmounted(() => { renderSequence += 1 })
</script>

<style scoped>
.mermaid-message {
  width: 100%;
}

.mermaid-message__text {
  white-space: pre-line;
  margin: 0 0 12px;
}

.mermaid-message__text:last-child {
  margin-bottom: 0;
}

.mermaid-message__diagram {
  margin: 12px 0;
  overflow: hidden;
  border: 1px solid rgba(var(--v-theme-primary), 0.18);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 6px 18px rgba(19, 43, 79, 0.08);
}

.mermaid-message__diagram:last-child {
  margin-bottom: 0;
}

.mermaid-message__svg :deep(svg) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  background: #fff !important;
  color: #172033 !important;
}

.mermaid-message__svg :deep(text),
.mermaid-message__svg :deep(tspan),
.mermaid-message__svg :deep(.label),
.mermaid-message__svg :deep(.titleText) {
  fill: #172033 !important;
  color: #172033 !important;
}

.mermaid-message__svg :deep(.timeline) {
  background: #fff !important;
}

.mermaid-message__svg :deep(.timeline-section),
.mermaid-message__svg :deep(.timeline-vertical) {
  stroke: #53657d !important;
}

.mermaid-message__preview {
  position: relative;
  width: 100%;
  min-height: 120px;
  padding: 20px 16px;
  overflow: auto;
  background: #fff;
  isolation: isolate;
}

.mermaid-message__loading {
  display: flex;
  min-height: 90px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgb(var(--v-theme-primary));
  font-size: 0.8125rem;
  font-weight: 700;
}

.mermaid-message__expand-button {
  position: absolute;
  z-index: 1;
  top: 10px;
  left: 10px;
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  padding: 0;
  border: 1px solid rgba(95, 168, 88, 0.58);
  border-radius: 9px;
  background: rgba(185, 235, 179, 0.82);
  box-shadow: 0 3px 10px rgba(74, 133, 68, 0.22);
  color: #296a27;
  cursor: zoom-in;
}

.mermaid-message__expand-button:hover,
.mermaid-message__expand-button:focus-visible {
  background: #6fbe67;
  color: #fff;
}

.mermaid-message__expand-button:focus-visible {
  outline: 3px solid rgba(111, 190, 103, 0.4);
  outline-offset: 2px;
}

.mermaid-message__dialog {
  background: #fff;
}

.mermaid-message__dialog-close {
  position: absolute;
  z-index: 1;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 3px 10px rgba(19, 43, 79, 0.16);
}

.mermaid-message__dialog-content {
  max-height: min(78vh, 900px);
  padding: 28px;
  overflow: auto;
  background: #fff;
}

.mermaid-message__expanded-svg {
  min-width: 720px;
  padding: 24px;
  border: 1px solid rgba(var(--v-theme-primary), 0.14);
  border-radius: 16px;
  background: #fff;
}

.mermaid-message__expanded-svg :deep(svg) {
  display: block;
  width: 100%;
  height: auto;
  margin: 0 auto;
}

.mermaid-message__error {
  color: rgb(var(--v-theme-error));
  font-size: 0.8125rem;
}
</style>
