export function importSummary(result) {
  return {
    created: result.created || 0,
    enrolled: result.enrolled || 0,
    issues: (result.skipped || []).map(item => {
      const reason = String(item.reason || '')
      if (/missing/i.test(reason)) return 'Faltan campos requeridos.'
      if (/duplicad/i.test(reason)) return 'El código ya existe.'
      if (/password|contrase/i.test(reason)) return 'La contraseña no cumple los requisitos.'
      if (/course code not found/i.test(reason)) return 'No se encontró el curso indicado.'
      return 'No se pudo importar. Revisa los datos y permisos antes de reintentar.'
    }),
  }
}
