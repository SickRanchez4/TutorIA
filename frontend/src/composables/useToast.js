import { reactive } from 'vue'

const DEFAULT_DURATION = 3500

export function errorMessage(error, fallback) {
  // Axios' own messages ("Network Error", "timeout of …") are English and technical.
  return error?.response?.data?.message || (error?.isAxiosError ? '' : error?.message) || fallback
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
    hideTimer = setTimeout(clear, DEFAULT_DURATION)
  }

  function notifyError(error, fallback) {
    notify(errorMessage(error, fallback), true)
  }

  return { state, notify, notifyError, clear }
}

export const coordinadorToast = createToast()
