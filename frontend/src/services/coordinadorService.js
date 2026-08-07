/**
 * Coordinator Service - Endpoints under /api/coordinador
 */
import api from './api'

export const coordinadorService = {
  // Configuración institucional
  getConfig() {
    return api.get('/coordinador/institucion/config')
  },
  updateConfig(payload) {
    return api.patch('/coordinador/institucion/config', payload)
  },

  // Cursos
  listCursos() {
    return api.get('/coordinador/cursos')
  },
  getCurso(cursoId) {
    return api.get(`/coordinador/cursos/${cursoId}`)
  },
  createCurso(payload) {
    return api.post('/coordinador/cursos', payload)
  },
  updateCurso(cursoId, payload) {
    return api.put(`/coordinador/cursos/${cursoId}`, payload)
  },
  deleteCurso(cursoId) {
    return api.delete(`/coordinador/cursos/${cursoId}`)
  },
  importCursosExcel(file) {
    const form = new FormData()
    form.append('file', file)
    return api.post('/coordinador/cursos/importar/excel', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Estudiantes (global)
  listEstudiantes() {
    return api.get('/coordinador/estudiantes')
  },
  searchAlumnos(query) {
    return api.get('/coordinador/estudiantes', {
      params: { search: query }
    })
  },
  updateEstudiante(userId, payload) {
    return api.put(`/coordinador/estudiantes/${userId}`, payload)
  },
  deleteEstudiante(userId) {
    return api.delete(`/coordinador/estudiantes/${userId}`)
  },
  importAlumnosCursosExcel(file) {
    const form = new FormData()
    form.append('file', file)
    return api.post('/coordinador/estudiantes/importar/excel', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Estudiantes (por curso)
  listEstudiantesCurso(cursoId) {
    return api.get(`/coordinador/cursos/${cursoId}/estudiantes`)
  },
  addEstudianteCurso(cursoId, payload) {
    return api.post(`/coordinador/cursos/${cursoId}/estudiantes`, payload)
  },
  removeEstudianteCurso(cursoId, userId) {
    return api.delete(`/coordinador/cursos/${cursoId}/estudiantes/${userId}`)
  },
  importEstudiantesCursoExcel(cursoId, file) {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/coordinador/cursos/${cursoId}/estudiantes/importar/excel`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Agente IA (por curso)
  getAgenteCurso(cursoId) {
    return api.get(`/coordinador/cursos/${cursoId}/agente`)
  },
  updateAgenteCurso(cursoId, payload) {
    return api.put(`/coordinador/cursos/${cursoId}/agente`, payload)
  },

  // Material RAG / Multiple PDF upload (por curso)
  uploadMaterialCurso(cursoId, pdfFiles) {
    const form = new FormData()
    // pdfFiles puede ser FileList o Array de File objects
    for (const file of pdfFiles) {
      form.append('files', file)
    }
    return api.post(`/coordinador/cursos/${cursoId}/subir-materiales`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,  // 3 minutos para procesamiento
    })
  },
  getConocimientoCurso(cursoId) {
    return api.get(`/coordinador/cursos/${cursoId}/conocimiento`)
  },
  retryConocimientoCurso(cursoId, jobId) {
    return api.post(`/coordinador/cursos/${cursoId}/conocimiento/trabajos/${jobId}/reintentar`)
  },
  operarConocimientoCurso(cursoId, payload) {
    return api.post(`/coordinador/cursos/${cursoId}/conocimiento/operaciones`, payload)
  },

  // Analytics
  getConsumo(days = null, filters = {}) {
    const params = {}
    
    // Support custom date range
    if (filters.start_date && filters.end_date) {
      params.start_date = filters.start_date
      params.end_date = filters.end_date
    } else if (days) {
      params.days = days
    } else {
      params.days = 30  // Default
    }
    
    // Optional filters
    if (filters.tipo) params.tipo = filters.tipo
    if (filters.user) params.user = filters.user
    if (filters.cursoId) params.curso_id = filters.cursoId
    
    return api.get('/coordinador/analiticas/consumo', { params })
  },
  getConsumoDetalle(params = {}) {
    return api.get('/coordinador/analiticas/consumo/detalle', {
      params: {
        days: params.days || 30,
        tipo: params.tipo || undefined,
        user: params.user || undefined,
        limit: params.limit || 200,
      }
    })
  },

  // Perfil del usuario actual
  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(payload) {
    return api.patch('/auth/profile', payload)
  },
  updatePassword(payload) {
    return api.patch('/auth/profile/password', payload)
  }
}

export default coordinadorService

