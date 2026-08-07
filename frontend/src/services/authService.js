/**
 * Authentication Service
 */
import api from './api'

export const authService = {
  async login(credentials) {
    try {
      return await api.post('/auth/login', credentials)
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  },

  async register(userData) {
    try {
      return await api.post('/auth/register', userData)
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  },

  async getProfile() {
    try {
      return await api.get('/auth/profile')
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  },

  async getProfessors() {
    try {
      return await api.get('/auth/professors')
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  },

  async toggleProfessorStatus(professorId) {
    try {
      return await api.patch(`/auth/professors/${professorId}/toggle-status`)
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  },

  async deleteProfessor(professorId) {
    try {
      return await api.delete(`/auth/professors/${professorId}`)
    } catch (error) {
      throw error.response?.data || { message: 'Error de conexión' }
    }
  }
}
