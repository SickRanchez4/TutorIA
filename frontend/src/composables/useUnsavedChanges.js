import { computed, onScopeDispose, reactive, ref, watchEffect } from 'vue'
import { confirmAction } from './useConfirm'

const entries = reactive(new Map())
const beforeUnload = event => {
  event.preventDefault()
  event.returnValue = ''
}
watchEffect(() => {
  if ([...entries.values()].some(entry => entry.dirty() || entry.pending())) window.addEventListener('beforeunload', beforeUnload)
  else window.removeEventListener('beforeunload', beforeUnload)
})

export async function confirmNavigation() {
  if ([...entries.values()].some(entry => entry.pending())) {
    await confirmAction({ title: 'Operación en curso', message: 'Espera a conocer el resultado antes de salir o repetir la operación.', confirmText: 'Entendido' })
    return false
  }
  const changed = [...entries.values()].filter(entry => entry.dirty())
  if (!changed.length) return true
  if (!await confirmAction({ title: 'Cambios sin guardar', message: 'Hay cambios o un borrador sin guardar. ¿Descartarlos y continuar?', confirmText: 'Descartar y continuar' })) return false
  changed.forEach(entry => entry.discard())
  return true
}

export function discardPrivateDrafts() {
  entries.forEach(entry => entry.discard())
}

export function useUnsavedChanges(dirty, discard, pending = () => false) {
  const key = Symbol()
  entries.set(key, { dirty, discard, pending })
  onScopeDispose(() => entries.delete(key))
}

export function useFormDraft(source, enabled = () => true, pending = () => false) {
  const saved = ref(JSON.stringify(source()))
  const dirty = computed(() => enabled() && JSON.stringify(source()) !== saved.value)
  const accept = () => { saved.value = JSON.stringify(source()) }
  const discard = () => { Object.assign(source(), JSON.parse(saved.value)) }
  useUnsavedChanges(() => dirty.value, discard, pending)
  async function canClose() {
    if (!dirty.value) return true
    if (!await confirmAction({ title: 'Cambios sin guardar', message: '¿Descartar los cambios de este formulario?', confirmText: 'Descartar cambios' })) return false
    discard()
    return true
  }
  return { dirty, accept, discard, canClose }
}

export function useGuardedDialog(open, draft, pending = () => false) {
  return computed({
    get: () => open.value,
    async set(value) {
      if (value) open.value = true
      else if (!pending() && await draft.canClose()) open.value = false
    },
  })
}
