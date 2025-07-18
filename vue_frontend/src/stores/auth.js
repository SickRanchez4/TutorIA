import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Mock user database - In production, this would be handled by your backend
  const mockUsers = [
    {
      id: 1,
      email: 'profesor@universidad.edu',
      password: 'profesor123',
      role: 'professor',
      name: 'Dr. Juan Pérez'
    },
    {
      id: 2,
      email: 'admin@universidad.edu', 
      password: 'admin123',
      role: 'admin',
      name: 'María González'
    }
  ]

  const login = async (credentials) => {
    isLoading.value = true
    error.value = ''

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Validate credentials
      const foundUser = mockUsers.find(
        u => u.email === credentials.email && u.password === credentials.password
      )

      if (!foundUser) {
        throw new Error('Credenciales inválidas')
      }

      // Generate mock JWT token
      const mockToken = btoa(JSON.stringify({
        userId: foundUser.id,
        role: foundUser.role,
        exp: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      }))

      // Set user and token
      user.value = {
        id: foundUser.id,
        email: foundUser.email,
        role: foundUser.role,
        name: foundUser.name
      }
      token.value = mockToken

      // Store in localStorage
      localStorage.setItem('auth_token', mockToken)
      localStorage.setItem('user_data', JSON.stringify(user.value))

      return { success: true, user: user.value }

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