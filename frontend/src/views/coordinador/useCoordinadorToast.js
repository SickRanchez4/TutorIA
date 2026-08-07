/**
 * Shared toast notification state for the Coordinador section.
 * The layout renders the toast; child views call notify()/notifyError() to trigger it.
 */
import { ref } from 'vue'

const toast = ref('')
const toastError = ref(false)
let hideTimer = null

function notify(msg, isError = false) {
  toast.value = msg
  toastError.value = isError
  if (hideTimer) clearTimeout(hideTimer)
  hideTimer = setTimeout(() => { toast.value = '' }, 3500)
}

function notifyError(err, fallback) {
  notify(err?.response?.data?.message || fallback, true)
}

export function useCoordinadorToast() {
  return { toast, toastError, notify, notifyError }
}
