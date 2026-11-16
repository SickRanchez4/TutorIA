import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services'
import { discardPrivateDrafts } from '../composables/useUnsavedChanges'
import { clearListStates } from '../composables/usePagination'
import { coordinadorToast } from '../composables/useToast'
import { resolveConfirmation } from '../composables/useConfirm'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'user_data'

function withAuthStorage(action) {
  try {
    return action(localStorage)
  } catch (error) {
    console.warn('El almacenamiento de sesión no está disponible; se usará solo memoria.', error.name)
    return null
  }
}

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
    withAuthStorage(storage => storage.setItem(USER_KEY, JSON.stringify(user.value)))
  }

  async function login(credentials) {
    if (isLoading.value) return { success: false }
    isLoading.value = true
    error.value = ''
    try {
      const data = await authService.login(credentials)
      token.value = data.token
      withAuthStorage(storage => storage.setItem(TOKEN_KEY, data.token))
      persistUser(data.user)
      return { success: true, user: user.value }
    } catch {
      error.value = 'No se pudo iniciar sesión. Revisa tus credenciales y la conexión.'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    resolveConfirmation(false)
    discardPrivateDrafts()
    clearListStates()
    coordinadorToast.clear()
    user.value = null
    token.value = null
    error.value = ''
    withAuthStorage(storage => { storage.removeItem(TOKEN_KEY); storage.removeItem(USER_KEY) })
  }

  function initializeAuth() {
    const stored = withAuthStorage(storage => ({ token: storage.getItem(TOKEN_KEY), user: storage.getItem(USER_KEY) }))
    const storedToken = stored?.token
    const storedUser = stored?.user
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
