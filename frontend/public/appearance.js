;(function () {
  const key = 'tutoria.appearance'
  const valid = value => ['light', 'dark', 'system'].includes(value)
  const media = typeof window.matchMedia === 'function' ? window.matchMedia('(prefers-color-scheme: dark)') : null
  const listeners = new Set()
  let selection = 'system'
  try {
    const stored = localStorage.getItem(key)
    if (valid(stored)) selection = stored
  } catch (error) {
    console.warn('Appearance storage cannot be read; using system preference.', error.name)
  }
  let state
  function apply() {
    const resolved = selection === 'system' ? (media?.matches ? 'dark' : 'light') : selection
    state = Object.freeze({ selection, resolved })
    document.documentElement.dataset.theme = resolved
    document.documentElement.style.colorScheme = resolved
    listeners.forEach(listener => listener(state))
  }
  function systemChanged() {
    if (selection === 'system') apply()
  }
  function storageChanged(event) {
    if (event.key !== key && event.key !== null) return
    selection = valid(event.newValue) ? event.newValue : 'system'
    apply()
  }
  media?.addEventListener?.('change', systemChanged)
  window.addEventListener('storage', storageChanged)
  apply()
  window.tutoriaAppearance = {
    getState: () => state,
    setSelection(value) {
      if (!valid(value)) throw new RangeError('Invalid appearance preference')
      selection = value
      try {
        localStorage.setItem(key, value)
      } catch (error) {
        console.warn('Appearance storage cannot be written; keeping preference in memory.', error.name)
      }
      apply()
    },
    subscribe(listener) {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    dispose() {
      media?.removeEventListener?.('change', systemChanged)
      window.removeEventListener('storage', storageChanged)
      listeners.clear()
    },
  }
})()
