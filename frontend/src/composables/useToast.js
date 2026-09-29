import { ref } from 'vue'

const DEFAULT_DURATION = 3500

/**
 * Creates isolated toast state for a view, or shared state when the same
 * instance is consumed by a parent layout and its child views.
 */
export function createToast() {
  const message = ref('')
  const isError = ref(false)
  let hideTimer

  function notify(text, error = false) {
    message.value = text
    isError.value = error
    clearTimeout(hideTimer)
    hideTimer = setTimeout(() => {
      message.value = ''
    }, DEFAULT_DURATION)
  }

  function notifyError(error, fallback) {
    notify(error?.response?.data?.message || error?.message || fallback, true)
  }

  return { message, isError, notify, notifyError }
}

// Coordinador has one persistent layout, so its nested views intentionally
// share a single toast instance rendered by that layout.
export const coordinadorToast = createToast()
