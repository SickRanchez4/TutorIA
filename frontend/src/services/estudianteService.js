/**
 * Student Service - Endpoints under /api/estudiante
 */
import api from './api'

export const estudianteService = {
  // Grupos inscritos
  listGrupos() {
    return api.get('/estudiante/cursos')
  },

  // Chat
  listSesiones() {
    return api.get('/estudiante/chat/sesiones')
  },
  createSesion(payload) {
    return api.post('/estudiante/chat/sesiones', payload)
  },
  updateSesion(sesionId, payload) {
    return api.patch(`/estudiante/chat/sesiones/${sesionId}`, payload)
  },
  deleteSesion(sesionId) {
    return api.delete(`/estudiante/chat/sesiones/${sesionId}`)
  },
  getMensajes(sesionId) {
    return api.get(`/estudiante/chat/sesiones/${sesionId}/mensajes`)
  },
  getSesionContexto(sesionId) {
    return api.get(`/estudiante/chat/sesiones/${sesionId}/contexto`)
  },
  sendMensaje(sesionId, payload) {
    return api.post(`/estudiante/chat/sesiones/${sesionId}/mensaje`, payload)
  },

  // Recurso sintético
  recursoSintetico(sesionId, payload) {
    return api.post(`/estudiante/chat/sesiones/${sesionId}/recurso-sintetico`, payload)
  },

  // Modo práctica
  practicar(sesionId, payload) {
    return api.post(`/estudiante/chat/sesiones/${sesionId}/practicar`, payload)
  },

  // Agenda
  getAgenda(grupoMateriaId = null) {
    const params = {}
    if (grupoMateriaId) params.grupo_materia_id = grupoMateriaId
    return api.get('/estudiante/agenda', { params })
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

export default estudianteService
