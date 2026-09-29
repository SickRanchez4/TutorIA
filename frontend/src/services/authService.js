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
  }
}
