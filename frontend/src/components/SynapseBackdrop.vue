<template>
  <canvas ref="canvasEl" class="synapse-backdrop" aria-hidden="true"></canvas>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

/**
 * Red sináptica decorativa en canvas: nodos verdes conectados que
 * reaccionan sutilmente al cursor. Se dibuja sobre el elemento padre
 * (position: relative requerido en el contenedor).
 * Respeta prefers-reduced-motion (render estático) y pausa con la pestaña oculta.
 */
const props = defineProps({
  /** Área (px²) por nodo: valores mayores = menos nodos. */
  density: { type: Number, default: 22000 },
  minNodes: { type: Number, default: 36 },
  maxNodes: { type: Number, default: 110 },
})

const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const canvasEl = ref(null)
const pointer = { x: -9999, y: -9999, active: false }
let hostEl = null
let ctx = null
let rafId = 0
let nodes = []
let canvasW = 0
let canvasH = 0

const LINK_DIST = 130
const POINTER_DIST = 190

function buildNodes() {
  const area = canvasW * canvasH
  const count = Math.max(props.minNodes, Math.min(props.maxNodes, Math.round(area / props.density)))
  nodes = Array.from({ length: count }, () => ({
    x: Math.random() * canvasW,
    y: Math.random() * canvasH,
    vx: (Math.random() - 0.5) * 0.28,
    vy: (Math.random() - 0.5) * 0.28,
    r: 0.8 + Math.random() * 1.2
  }))
}

function resizeCanvas() {
  const canvas = canvasEl.value
  if (!canvas || !hostEl) return
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const rect = hostEl.getBoundingClientRect()
  canvasW = rect.width
  canvasH = rect.height
  canvas.width = Math.round(canvasW * dpr)
  canvas.height = Math.round(canvasH * dpr)
  ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  buildNodes()
  if (prefersReducedMotion) drawStaticSynapse()
}

function stepSynapse() {
  if (!ctx) return
  ctx.clearRect(0, 0, canvasW, canvasH)

  for (const n of nodes) {
    // Atracción muy sutil hacia el cursor
    if (pointer.active) {
      const dx = pointer.x - n.x
      const dy = pointer.y - n.y
      const dist = Math.hypot(dx, dy)
      if (dist < POINTER_DIST && dist > 0.001) {
        const force = ((POINTER_DIST - dist) / POINTER_DIST) * 0.012
        n.vx += (dx / dist) * force
        n.vy += (dy / dist) * force
      }
    }
    // Fricción + límite de velocidad
    n.vx *= 0.995
    n.vy *= 0.995
    const speed = Math.hypot(n.vx, n.vy)
    if (speed > 0.6) {
      n.vx = (n.vx / speed) * 0.6
      n.vy = (n.vy / speed) * 0.6
    }
    n.x += n.vx
    n.y += n.vy
    if (n.x < -20) n.x = canvasW + 20
    if (n.x > canvasW + 20) n.x = -20
    if (n.y < -20) n.y = canvasH + 20
    if (n.y > canvasH + 20) n.y = -20
  }

  // Conexiones entre nodos
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i]
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const dist = Math.hypot(dx, dy)
      if (dist < LINK_DIST) {
        const alpha = (1 - dist / LINK_DIST) * 0.16
        ctx.strokeStyle = `rgba(124, 197, 118, ${alpha})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.stroke()
      }
    }
  }

  // Sinapsis con el cursor: conexiones más brillantes
  if (pointer.active) {
    for (const n of nodes) {
      const dist = Math.hypot(pointer.x - n.x, pointer.y - n.y)
      if (dist < POINTER_DIST) {
        const alpha = (1 - dist / POINTER_DIST) * 0.4
        ctx.strokeStyle = `rgba(164, 233, 149, ${alpha})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(pointer.x, pointer.y)
        ctx.lineTo(n.x, n.y)
        ctx.stroke()
      }
    }
  }

  // Nodos
  for (const n of nodes) {
    const nearPointer =
      pointer.active && Math.hypot(pointer.x - n.x, pointer.y - n.y) < POINTER_DIST
    ctx.fillStyle = nearPointer
      ? 'rgba(182, 242, 170, 0.85)'
      : 'rgba(124, 197, 118, 0.45)'
    ctx.beginPath()
    ctx.arc(n.x, n.y, nearPointer ? n.r + 0.6 : n.r, 0, Math.PI * 2)
    ctx.fill()
  }

  rafId = requestAnimationFrame(stepSynapse)
}

function drawStaticSynapse() {
  if (!ctx) return
  ctx.clearRect(0, 0, canvasW, canvasH)
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i]
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j]
      const dist = Math.hypot(a.x - b.x, a.y - b.y)
      if (dist < LINK_DIST) {
        ctx.strokeStyle = `rgba(124, 197, 118, ${(1 - dist / LINK_DIST) * 0.14})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.stroke()
      }
    }
    ctx.fillStyle = 'rgba(124, 197, 118, 0.4)'
    ctx.beginPath()
    ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2)
    ctx.fill()
  }
}

function onHostPointerMove(event) {
  const rect = hostEl?.getBoundingClientRect()
  if (!rect) return
  pointer.x = event.clientX - rect.left
  pointer.y = event.clientY - rect.top
  pointer.active = true
}

function onHostPointerLeave() {
  pointer.active = false
  pointer.x = -9999
  pointer.y = -9999
}

function onVisibilityChange() {
  if (prefersReducedMotion) return
  if (document.hidden) {
    cancelAnimationFrame(rafId)
    rafId = 0
  } else if (!rafId) {
    rafId = requestAnimationFrame(stepSynapse)
  }
}

onMounted(() => {
  hostEl = canvasEl.value?.parentElement || null
  resizeCanvas()
  if (prefersReducedMotion) {
    drawStaticSynapse()
  } else {
    rafId = requestAnimationFrame(stepSynapse)
    hostEl?.addEventListener('pointermove', onHostPointerMove)
    hostEl?.addEventListener('pointerleave', onHostPointerLeave)
  }
  window.addEventListener('resize', resizeCanvas)
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  hostEl?.removeEventListener('pointermove', onHostPointerMove)
  hostEl?.removeEventListener('pointerleave', onHostPointerLeave)
  window.removeEventListener('resize', resizeCanvas)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.synapse-backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
