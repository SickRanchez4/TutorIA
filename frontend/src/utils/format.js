const LOCALE = 'es-BO'

function toDate(value) {
  if (!value) return null
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(value, options = { day: '2-digit', month: 'short', year: 'numeric' }, fallback = '—') {
  const date = toDate(value)
  return date ? date.toLocaleDateString(LOCALE, options) : fallback
}

export function formatDateTime(value, options = { dateStyle: 'medium', timeStyle: 'short' }, fallback = '—') {
  const date = toDate(value)
  return date ? date.toLocaleString(LOCALE, options) : fallback
}

/** Value for `<input type="date">` (yyyy-mm-dd). */
export function toDateInput(value) {
  const date = toDate(value)
  return date ? date.toISOString().slice(0, 10) : ''
}

export function formatNumber(value) {
  return Number(value || 0).toLocaleString(LOCALE)
}

export function formatFileSize(bytes) {
  if (!bytes) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / (1024 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`
}

/** v-file-input yields a File in single mode and File[] with `multiple`. */
export function firstFile(value) {
  return (Array.isArray(value) ? value[0] : value) || null
}
