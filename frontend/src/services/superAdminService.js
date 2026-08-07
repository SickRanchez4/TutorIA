/**
 * Super Admin Service - Endpoints under /api/admin
 */
import api from './api'

export const superAdminService = {
  // Instituciones
  listInstituciones() {
    return api.get('/admin/instituciones')
  },
  createInstitucion(payload) {
    return api.post('/admin/instituciones', payload)
  },
  getInstitucion(id) {
    return api.get(`/admin/instituciones/${id}`)
  },
  updateInstitucion(id, payload) {
    return api.patch(`/admin/instituciones/${id}`, payload)
  },
  deleteInstitucion(id) {
    return api.delete(`/admin/instituciones/${id}`)
  },
  toggleActive(id) {
    return api.patch(`/admin/instituciones/${id}/toggle-active`)
  },

  // Planes y suscripciones
  listPlanes() {
    return api.get('/admin/planes')
  },
  createPlan(payload) {
    return api.post('/admin/planes', payload)
  },
  updatePlan(id, payload) {
    return api.patch(`/admin/planes/${id}`, payload)
  },
  deletePlan(id) {
    return api.delete(`/admin/planes/${id}`)
  },
  listSuscripciones() {
    return api.get('/admin/suscripciones')
  },
  getSuscripcion(institucionId) {
    return api.get(`/admin/instituciones/${institucionId}/suscripcion`)
  },
  assignSuscripcion(institucionId, payload) {
    return api.post(`/admin/instituciones/${institucionId}/suscripcion`, payload)
  },
  updateSuscripcion(institucionId, payload) {
    return api.patch(`/admin/instituciones/${institucionId}/suscripcion`, payload)
  },
  deleteSuscripcion(institucionId) {
    return api.delete(`/admin/instituciones/${institucionId}/suscripcion`)
  },

  // Coordinadores por institución
  listCoordinadores(institucionId) {
    return api.get(`/admin/instituciones/${institucionId}/coordinadores`)
  },
  createCoordinador(institucionId, payload) {
    return api.post(`/admin/instituciones/${institucionId}/coordinadores`, payload)
  },
  updateCoordinador(institucionId, userId, payload) {
    return api.patch(`/admin/instituciones/${institucionId}/coordinadores/${userId}`, payload)
  },
  deleteCoordinador(institucionId, userId) {
    return api.delete(`/admin/instituciones/${institucionId}/coordinadores/${userId}`)
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

export default superAdminService
