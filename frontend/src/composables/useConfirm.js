import { reactive } from 'vue'

export const confirmation = reactive({ open: false, title: '', message: '', confirmText: '', destructive: false })
let resolveDecision

export function confirmAction({ title = '¿Continuar?', message, confirmText = 'Confirmar', destructive = false }) {
  if (resolveDecision) {
    console.warn('A confirmation is already open; ignoring repeated action.')
    return Promise.resolve(false)
  }
  Object.assign(confirmation, { open: true, title, message, confirmText, destructive })
  return new Promise(resolve => { resolveDecision = resolve })
}

export function resolveConfirmation(confirmed) {
  confirmation.open = false
  const resolve = resolveDecision
  resolveDecision = null
  Object.assign(confirmation, { title: '', message: '', confirmText: '', destructive: false })
  resolve?.(confirmed)
}
