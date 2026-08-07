import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const dashboardRoute = computed(() => {
    const role = user.value?.role
    if (role === 'super_admin') return '/super-admin'
    if (role === 'coordinador') return '/coordinador'
    if (role === 'estudiante') return '/estudiante'
    return '/login'
  })

  const normalizeUserName = (userObj) => {
    if (!userObj.name) {
      if (userObj.full_name) userObj.name = userObj.full_name
      else if (userObj.first_name || userObj.last_name) {
        userObj.name = `${userObj.first_name || ''}${userObj.first_name && userObj.last_name ? ' ' : ''}${userObj.last_name || ''}`.trim()
      }
    }
    return userObj
  }

  const login = async (credentials) => {
    isLoading.value = true
    error.value = ''

    try {
      const data = await authService.login(credentials)
      const userObj = normalizeUserName(data.user || {})

      user.value = userObj
      token.value = data.token

      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('user_data', JSON.stringify(userObj))
  
      return { success: true, user: userObj }

    } catch (err) {
      error.value = err.message || 'Error de autenticación'
      return { success: false, error: err.message || 'Error de autenticación' }
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
        let tokenValid = true
        try {
          const payload = JSON.parse(atob(storedToken.split('.')[1] || ''))
          if (payload?.exp && payload.exp * 1000 < Date.now()) tokenValid = false
        } catch (e) {
          // Ignore parse errors; assume token is valid
        }

        if (tokenValid) {
          token.value = storedToken
          const parsedUser = normalizeUserName(JSON.parse(storedUser))
          user.value = parsedUser
        } else {
          logout()
        }
      } catch (err) {
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
    dashboardRoute,
    login,
    logout,
    initializeAuth,
    setUserData: (userData) => {
      const normalized = normalizeUserName(userData || {})
      user.value = normalized
      localStorage.setItem('user_data', JSON.stringify(normalized))
    }
  }
})