import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

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

      // Normalize user object: ensure `name` exists for UI components
      const userObj = data.user || {}
      if (!userObj.name) {
        if (userObj.full_name) userObj.name = userObj.full_name
        else if (userObj.first_name || userObj.last_name) userObj.name = `${userObj.first_name || ''}${userObj.first_name && userObj.last_name ? ' ' : ''}${userObj.last_name || ''}`.trim()
      }

      // Guardar token y datos del usuario
      user.value = userObj
      token.value = data.token

      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('user_data', JSON.stringify(userObj))
  
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
          // NOTE: JWT parsing here is best-effort. We only use it to check expiry if present.
          let tokenValid = true
          try {
            const payload = JSON.parse(atob(storedToken.split('.')[1] || ''))
            if (payload && payload.exp && payload.exp * 1000 < Date.now()) tokenValid = false
          } catch (e) {
            // ignore parse errors; assume token is valid
          }

          if (tokenValid) {
            token.value = storedToken
            // ensure stored user has `name` field
            const parsedUser = JSON.parse(storedUser)
            if (!parsedUser.name) {
              parsedUser.name = parsedUser.full_name || `${parsedUser.first_name || ''}${parsedUser.first_name && parsedUser.last_name ? ' ' : ''}${parsedUser.last_name || ''}`.trim()
            }
            user.value = parsedUser
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