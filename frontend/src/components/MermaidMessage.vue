<template>
  <div ref="messageRoot" class="mermaid-message">
    <template v-for="(part, index) in parts" :key="index">
      <!-- eslint-disable-next-line vue/no-v-html -- Markdown sin HTML crudo y sanitizado en renderRichText() -->
      <div v-if="part.type === 'text'" class="mermaid-message__text rich-text" v-html="part.html"></div>
      <div v-else class="mermaid-message__diagram" :data-diagram-index="index" role="figure" :aria-label="DIAGRAM_LABEL">
        <div class="mermaid-message__preview">
          <button
            v-if="renderedSvgs[index]"
            type="button"
            class="mermaid-message__expand-button"
            :aria-label="`Ampliar ${DIAGRAM_LABEL.toLowerCase()}`"
            title="Ampliar diagrama"
            @click="expandDiagram(index, $event.currentTarget)"
          >
            <v-icon icon="mdi-magnify-plus-outline" size="20"></v-icon>
          </button>
          <div v-if="renderErrors[index]" class="mermaid-message__error" role="alert">
            <p class="mb-2">No se pudo dibujar este diagrama. Usa un tipo del catálogo de Recursos; se muestra el código como referencia:</p>
            <pre>{{ part.value }}</pre>
          </div>
          <div v-else-if="!renderedSvgs[index]" class="mermaid-message__loading">
            <v-progress-circular indeterminate color="primary" size="24" width="3"></v-progress-circular>
            Generando diagrama...
          </div>
          <!-- eslint-disable-next-line vue/no-v-html -- SVG sanitizado en prepareSvg() -->
          <div v-else class="mermaid-message__svg" v-html="renderedSvgs[index]"></div>
        </div>
      </div>
    </template>

    <v-dialog v-model="expanded" width="calc(100% - 24px)" max-width="1200" scrollable @after-leave="restoreDiagramFocus">
      <v-card class="mermaid-message__dialog position-relative" rounded="xl">
        <v-card-title class="pr-14">
          Diagrama
          <v-btn icon="mdi-minus" size="small" aria-label="Reducir diagrama" :disabled="zoom <= 0.5" @click="zoom -= 0.25" />
          <v-btn icon="mdi-plus" size="small" aria-label="Ampliar tamaño del diagrama" :disabled="zoom >= 2" @click="zoom += 0.25" />
        </v-card-title>
        <v-btn
          icon="mdi-close"
          class="mermaid-message__dialog-close"
          size="small"
          aria-label="Cerrar diagrama ampliado"
          @click="expanded = false"
        ></v-btn>
        <v-card-text class="mermaid-message__dialog-content">
          <!-- eslint-disable-next-line vue/no-v-html -- SVG sanitizado en prepareSvg() -->
          <div class="mermaid-message__expanded-svg" tabindex="0" role="region" aria-label="Diagrama ampliado; usa las flechas para desplazarte" :style="{ width: `${expandedWidth * zoom}px` }" v-html="expandedSvg"></div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
let renderQueue = Promise.resolve()
let mermaid
let nextDiagramId = 0
</script>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import DOMPurify from 'dompurify'
import 'katex/dist/katex.min.css'
import { useAppearance } from '../composables/useAppearance'
import { getSupportedMermaidType, normalizeMermaidSource } from '../utils/mermaidCatalog'
import { renderRichText } from '../utils/richText'

const props = defineProps({
  active: { type: Boolean, default: true },
  content: {
    type: String,
    default: '',
  },
})

const renderedSvgs = ref({})
const messageRoot = ref(null)
const renderErrors = ref({})
const expanded = ref(false)
const expandedSvg = ref('')
const expandedIndex = ref(null)
const expandedWidth = ref(720)
const diagramWidths = ref({})
const zoom = ref(1)
const { appearance } = useAppearance()
let renderSequence = 0
let renderedContent = ''
let diagramTrigger = null
let focusFallback = null
const DIAGRAM_LABEL = 'Diagrama generado para el recurso de estudio'

const parts = computed(() => {
  const result = []
  const matcher = /```mermaid\s*\r?\n([\s\S]*?)```/gi
  let lastIndex = 0
  let match

  while ((match = matcher.exec(props.content)) !== null) {
    const text = props.content.slice(lastIndex, match.index).trim()
    if (text) result.push({ type: 'text', value: text })
    result.push({ type: 'diagram', value: match[1].trim() })
    lastIndex = matcher.lastIndex
  }

  const trailingText = props.content.slice(lastIndex).trim()
  if (trailingText) result.push({ type: 'text', value: trailingText })
  if (!result.length) result.push({ type: 'text', value: props.content })
  return result.map(part => (part.type === 'text' ? { ...part, html: renderRichText(part.value) } : part))
})

function prepareSvg(svg) {
  const fragment = DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true }, RETURN_DOM_FRAGMENT: true })
  const graphic = fragment.querySelector('svg')
  if (!graphic) throw new Error('El recurso no contiene un SVG válido.')
  Object.assign(graphic.style, { background: 'var(--tutoria-surface)', color: 'var(--tutoria-text)', display: 'block', height: 'auto', margin: '0 auto', maxWidth: 'none' })
  return graphic.outerHTML
}

function expandDiagram(index, trigger) {
  const svg = renderedSvgs.value[index]
  if (!svg) return
  expandedSvg.value = svg
  expandedIndex.value = index
  expandedWidth.value = diagramWidths.value[index] || 720
  zoom.value = 1
  diagramTrigger = trigger
  focusFallback = trigger.closest('[tabindex="0"]')
  expanded.value = true
}
function restoreDiagramFocus() {
  if (diagramTrigger?.isConnected) diagramTrigger.focus()
  else if (focusFallback?.isConnected) focusFallback.focus()
}

async function ensureMermaid() {
  if (!mermaid) {
    const module = await import('mermaid')
    mermaid = module.default
  }

  const css = getComputedStyle(document.documentElement)
  const token = key => css.getPropertyValue(`--tutoria-${key}`).trim()
  mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'strict',
      suppressErrorRendering: true,
      // HTML labels live in <foreignObject>, which the SVG sanitizer removes;
      // plain SVG text keeps labels visible after sanitizing.
      htmlLabels: false,
      flowchart: { htmlLabels: false, nodeSpacing: 64, rankSpacing: 72, diagramPadding: 24 },
      sequence: { actorMargin: 72, messageMargin: 42, noteMargin: 18, boxMargin: 12, boxTextMargin: 8, diagramMarginX: 40, diagramMarginY: 30 },
      state: { nodeSpacing: 60, rankSpacing: 72, padding: 18 },
      class: { nodeSpacing: 60, rankSpacing: 72, padding: 16, diagramPadding: 20 },
      er: { layoutDirection: 'LR', nodeSpacing: 60, rankSpacing: 72, entityPadding: 16, minEntityWidth: 160, minEntityHeight: 80, diagramPadding: 20 },
      mindmap: { padding: 24, maxNodeWidth: 220 },
      journey: { diagramMarginX: 36, diagramMarginY: 30, leftMargin: 160, maxLabelWidth: 200, width: 180, height: 52, taskMargin: 24 },
      gantt: { barHeight: 26, barGap: 10, topPadding: 48, leftPadding: 120, gridLineStartPadding: 35, fontSize: 14, sectionFontSize: 14 },
      c4: { diagramMarginX: 48, diagramMarginY: 40, c4ShapeMargin: 64, c4ShapePadding: 18, c4ShapeInRow: 3, width: 200, height: 120, boxMargin: 12 },
      themeVariables: {
        background: token('surface'),
        primaryColor: token('nav-active-bg'),
        primaryTextColor: token('text'),
        primaryBorderColor: token('control-border'),
        secondaryColor: token('surface'),
        secondaryTextColor: token('text'),
        secondaryBorderColor: token('control-border'),
        tertiaryColor: token('surface-raised'),
        tertiaryTextColor: token('text'),
        tertiaryBorderColor: token('control-border'),
        lineColor: token('text-muted'),
        textColor: token('text'),
        mainBkg: token('nav-active-bg'),
        nodeBorder: token('control-border'),
        clusterBkg: token('surface'),
        clusterBorder: token('control-border'),
        titleColor: token('text'),
        edgeLabelBackground: token('surface'),
        timelineSectionBkgColor: token('nav-active-bg'),
        timelineSectionBkgColor2: token('surface'),
        timelineTaskBkgColor: token('nav-active-bg'),
        timelineTaskTextColor: token('text'),
        timelineTaskBorderColor: token('control-border'),
      },
  })
}

async function renderDiagrams() {
  const sequence = ++renderSequence
  if (renderedContent !== props.content) {
    renderedSvgs.value = {}
    diagramWidths.value = {}
    renderedContent = props.content
  }
  renderErrors.value = {}

  if (!parts.value.some((part) => part.type === 'diagram')) return

  for (const [index, part] of parts.value.entries()) {
    if (part.type !== 'diagram') continue

    const renderId = `tutoria-mermaid-${Date.now()}-${++nextDiagramId}-${index}`
    try {
      if (!getSupportedMermaidType(part.value)) {
        throw new Error('Tipo de diagrama fuera del catálogo compatible.')
      }

      const render = async () => {
        await ensureMermaid()
        return mermaid.render(renderId, normalizeMermaidSource(part.value))
      }
      const pending = renderQueue.then(render)
      renderQueue = pending.then(() => undefined, () => undefined)
      const { svg } = await pending
      if (sequence === renderSequence) {
        renderedSvgs.value = { ...renderedSvgs.value, [index]: prepareSvg(svg) }
        await nextTick()
        if (sequence !== renderSequence) return
        const graphic = messageRoot.value.querySelector(`[data-diagram-index="${index}"] .mermaid-message__svg svg`)
        const bounds = graphic.getBBox()
        if (bounds.width && bounds.height) {
          // Measure after insertion: the renderer's staging viewBox can clip translated nodes.
          const width = bounds.width + 16
          const height = bounds.height + 16
          graphic.setAttribute('viewBox', `${bounds.x - 8} ${bounds.y - 8} ${width} ${height}`)
          graphic.setAttribute('width', String(width))
          graphic.setAttribute('height', String(height))
          graphic.style.width = `${width}px`
          graphic.style.maxWidth = 'none'
          diagramWidths.value = { ...diagramWidths.value, [index]: width }
          renderedSvgs.value = { ...renderedSvgs.value, [index]: prepareSvg(graphic.outerHTML) }
        }
        if (expandedIndex.value === index) expandedSvg.value = renderedSvgs.value[index]
      }
    } catch (error) {
      console.error('No se pudo renderizar el diagrama Mermaid.', error)
      if (sequence === renderSequence) {
        renderErrors.value = { ...renderErrors.value, [index]: true }
      }
    }
  }
}

onMounted(() => { if (props.active) renderDiagrams() })

watch([() => props.content, () => appearance.value.resolved, () => props.active], () => {
  if (props.active) renderDiagrams()
  else renderSequence++
})
onUnmounted(() => { renderSequence += 1 })
</script>

<style scoped>
.mermaid-message {
  width: 100%;
}

.mermaid-message__text {
  margin: 0 0 12px;
  overflow-wrap: anywhere;
}

.mermaid-message__text:last-child {
  margin-bottom: 0;
}

.rich-text :deep(> :first-child) { margin-top: 0; }
.rich-text :deep(> :last-child) { margin-bottom: 0; }
.rich-text :deep(p),
.rich-text :deep(ul),
.rich-text :deep(ol),
.rich-text :deep(blockquote),
.rich-text :deep(pre),
.rich-text :deep(table) { margin: 0 0 10px; }
.rich-text :deep(h1),
.rich-text :deep(h2),
.rich-text :deep(h3),
.rich-text :deep(h4) { margin: 16px 0 8px; font-weight: 800; line-height: 1.3; }
.rich-text :deep(h1) { font-size: 1.2rem; }
.rich-text :deep(h2) { font-size: 1.1rem; }
.rich-text :deep(h3),
.rich-text :deep(h4) { font-size: 1rem; }
.rich-text :deep(ul),
.rich-text :deep(ol) { padding-left: 1.4em; }
.rich-text :deep(li) { margin: 2px 0; }
.rich-text :deep(strong) { font-weight: 800; }
.rich-text :deep(a) { color: inherit; text-decoration: underline; }
.rich-text :deep(hr) { margin: 14px 0; border: 0; border-top: 1px solid var(--tutoria-border); }
.rich-text :deep(blockquote) { padding: 6px 12px; border-left: 3px solid var(--tutoria-control-border); color: var(--tutoria-text-muted); }
.rich-text :deep(code) { padding: 1px 5px; border-radius: 6px; background: var(--tutoria-surface-raised); font-size: 0.9em; }
.rich-text :deep(pre) { overflow-x: auto; padding: 10px 12px; border: 1px solid var(--tutoria-border); border-radius: 10px; background: var(--tutoria-surface-raised); }
.rich-text :deep(pre code) { padding: 0; background: none; }
.rich-text :deep(table) { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
.rich-text :deep(th),
.rich-text :deep(td) { padding: 6px 10px; border: 1px solid var(--tutoria-border); text-align: left; }
.rich-text :deep(th) { background: var(--tutoria-surface-raised); font-weight: 800; }
.rich-text :deep(.katex) { font-size: 1.08em; color: inherit; }
.rich-text :deep(.katex-display) {
  overflow-x: auto;
  overflow-y: hidden;
  margin: 10px 0;
  padding: 10px 12px;
  border: 1px solid var(--tutoria-border);
  border-radius: 10px;
  background: var(--tutoria-surface);
}

.mermaid-message__diagram {
  margin: 12px 0;
  overflow: hidden;
  border: 1px solid var(--tutoria-border);
  border-radius: 16px;
  background: var(--tutoria-surface);
  box-shadow: 0 6px 18px rgba(37, 35, 27, 0.12);
}

.mermaid-message__diagram:last-child {
  margin-bottom: 0;
}

.mermaid-message__svg :deep(svg) {
  display: block;
  max-width: none;
  height: auto;
  margin: 0 auto;
  background: var(--tutoria-surface) !important;
  color: var(--tutoria-text) !important;
}

.mermaid-message__svg :deep(text),
.mermaid-message__svg :deep(tspan),
.mermaid-message__svg :deep(.label),
.mermaid-message__svg :deep(.titleText) {
  fill: var(--tutoria-text) !important;
  color: var(--tutoria-text) !important;
}

.mermaid-message__svg :deep(.timeline) {
  background: var(--tutoria-surface) !important;
}

.mermaid-message__svg :deep(.timeline-section),
.mermaid-message__svg :deep(.timeline-vertical) {
  stroke: var(--tutoria-text-muted) !important;
}

.mermaid-message__preview {
  position: relative;
  width: 100%;
  min-height: 120px;
  padding: 20px 16px;
  overflow: auto;
  background: var(--tutoria-surface);
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
  border: 1px solid var(--tutoria-border);
  border-radius: 9px;
  background: var(--tutoria-green);
  box-shadow: 0 3px 10px rgba(37, 35, 27, 0.16);
  color: var(--tutoria-on-primary);
  cursor: zoom-in;
}

.mermaid-message__expand-button:hover,
.mermaid-message__expand-button:focus-visible {
  background: var(--tutoria-green);
  color: var(--tutoria-on-primary);
}

.mermaid-message__expand-button:focus-visible {
  outline: 3px solid rgba(var(--tutoria-green-rgb), 0.4);
  outline-offset: 2px;
}

.mermaid-message__dialog {
  background: var(--tutoria-surface);
}

.mermaid-message__dialog-close {
  position: absolute;
  z-index: 1;
  top: 12px;
  right: 12px;
  background: var(--tutoria-nav-active-bg);
  color: var(--tutoria-text);
  box-shadow: 0 3px 10px rgba(37, 35, 27, 0.16);
}

.mermaid-message__dialog-content {
  max-height: min(78vh, 900px);
  padding: 28px;
  overflow: auto;
  background: var(--tutoria-surface);
}

.mermaid-message__expanded-svg {
  box-sizing: content-box;
  padding: 24px;
  border: 1px solid var(--tutoria-border);
  border-radius: 16px;
  background: var(--tutoria-surface);
}

.mermaid-message__expanded-svg :deep(svg) {
  display: block;
  width: 100% !important;
  max-width: none !important;
  height: auto;
  margin: 0 auto;
}

.mermaid-message__error {
  color: rgb(var(--v-theme-error));
  font-size: 0.8125rem;
}

.mermaid-message__error pre {
  max-height: 220px;
  margin: 0;
  padding: 10px;
  overflow: auto;
  border-radius: 8px;
  color: var(--tutoria-text);
  background: var(--tutoria-nav-active-bg);
  font-size: 0.75rem;
  white-space: pre-wrap;
}

.mermaid-message__source { overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; }

@media (max-width: 599px) {
  .mermaid-message__diagram { border-radius: 12px; }
  .mermaid-message__preview { min-height: 100px; padding: 16px 10px; }
  .mermaid-message__dialog-content { padding: 48px 12px 16px; }
  .mermaid-message__expanded-svg { min-width: 640px; padding: 14px; }
}
</style>
