import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'user_data'

const DASHBOARD_ROUTES = {
  super_admin: '/super-admin',
  coordinador: '/coordinador',
  estudiante: '/estudiante',
}

function normalizeUser(userObj) {
  const user = { ...(userObj || {}) }
  if (!user.name) {
    user.name = user.full_name || [user.first_name, user.last_name].filter(Boolean).join(' ')
  }
  return user
}

function isTokenUsable(storedToken) {
  try {
    const encodedPayload = storedToken.split('.')[1]
    if (!encodedPayload) return false
    const payload = JSON.parse(atob(encodedPayload.replace(/-/g, '+').replace(/_/g, '/')))
    return !payload?.exp || payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const dashboardRoute = computed(() => DASHBOARD_ROUTES[user.value?.role] || '/login')
  const displayName = computed(() => user.value?.name || user.value?.email || '')

  function persistUser(userObj) {
    user.value = normalizeUser(userObj)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
  }

  async function login(credentials) {
    isLoading.value = true
    error.value = ''
    try {
      const data = await authService.login(credentials)
      token.value = data.token
      localStorage.setItem(TOKEN_KEY, data.token)
      persistUser(data.user)
      return { success: true, user: user.value }
    } catch (err) {
      error.value = err.message || 'Error de autenticación'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    error.value = ''
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function initializeAuth() {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_KEY)
    if (!storedToken || !storedUser) return
    try {
      if (!isTokenUsable(storedToken)) return logout()
      token.value = storedToken
      user.value = normalizeUser(JSON.parse(storedUser))
    } catch {
      logout()
    }
  }

  /** Merges profile changes so fields missing from a response (e.g. role) are kept. */
  function setUserData(userData) {
    persistUser({ ...user.value, ...(userData || {}), name: undefined })
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    dashboardRoute,
    displayName,
    login,
    logout,
    initializeAuth,
    setUserData,
  }
})
