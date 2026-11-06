/**
 * Authentication and current-user profile endpoints under /api/auth
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

  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(payload) {
    return api.patch('/auth/profile', payload)
  },
  updatePassword(payload) {
    return api.patch('/auth/profile/password', payload)
  },
}
