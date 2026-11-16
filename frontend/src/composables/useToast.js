import { onScopeDispose, reactive } from 'vue'

const DEFAULT_DURATION = 3500

export function errorMessage(error, fallback) {
  if (error?.isAxiosError && !error.response && error.config?.method && !['get', 'head', 'options'].includes(error.config.method.toLowerCase())) return 'Resultado no confirmado. Consulta los datos antes de repetir la operación.'
  if (error?.code === 'ECONNABORTED' || error?.code === 'ETIMEDOUT') return 'Resultado no confirmado. Consulta los datos antes de repetir la operación.'
  if (error?.response?.status >= 500) return fallback || 'El servicio no está disponible. Inténtalo más tarde.'
  if (error?.response?.status === 403) return 'No tienes permiso para esta acción o el recurso no está disponible.'
  // Axios' own messages ("Network Error", "timeout of …") are English and technical.
  return error?.response?.data?.message || fallback || 'No se pudo completar la operación.'
}

/**
 * Toast state rendered by RoleLayout. Each dashboard owns one instance; the
 * coordinator views share the instance of their persistent layout.
 */
export function createToast() {
  const state = reactive({ message: '', isError: false })
  let hideTimer

  function clear() {
    clearTimeout(hideTimer)
    state.message = ''
  }

  function notify(text, isError = false) {
    clearTimeout(hideTimer)
    state.message = text
    state.isError = isError
    if (!isError) hideTimer = setTimeout(clear, DEFAULT_DURATION)
  }

  function notifyError(error, fallback) {
    notify(errorMessage(error, fallback), true)
  }

  return { state, notify, notifyError, clear }
}

export const coordinadorToast = createToast()

export function useCoordinadorToast() {
  let active = true
  onScopeDispose(() => { active = false })
  return {
    notify: (...args) => { if (active) coordinadorToast.notify(...args) },
    notifyError: (...args) => { if (active) coordinadorToast.notifyError(...args) },
  }
}
