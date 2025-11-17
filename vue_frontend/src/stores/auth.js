import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Mock user database - In production, this would be handled by your backend
  // const mockUsers = [
  //   {
  //     id: 1,
  //     email: 'profesor@universidad.edu',
  //     password: 'profesor123',
  //     role: 'professor',
  //     name: 'Dr. Juan Pérez'
  //   },
  //   {
  //     id: 2,
  //     email: 'admin@universidad.edu', 
  //     password: 'admin123',
  //     role: 'admin',
  //     name: 'María González'
  //   }
  // ]

  const login = async (credentials) => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })
  
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Error de autenticación')
      }
  
      const data = await response.json()
      
      // Guardar token y datos del usuario
      user.value = data.user
      token.value = data.token
      
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('user_data', JSON.stringify(data.user))
  
      return { success: true, user: data.user }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    error.value = ''
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
  }

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user_data')

    if (storedToken && storedUser) {
      try {
        // Verify token hasn't expired
        const tokenData = JSON.parse(atob(storedToken))
        if (tokenData.exp && tokenData.exp > Date.now()) {
          token.value = storedToken
          user.value = JSON.parse(storedUser)
        } else {
          // Token expired, clear storage
          logout()
        }
      } catch (err) {
        // Invalid token, clear storage
        logout()
      }
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    login,
    logout,
    initializeAuth
  }
})