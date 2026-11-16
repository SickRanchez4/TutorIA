import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { useAuthStore } from './stores/auth'
import { connectAppearance } from './composables/useAppearance'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)
const disconnectAppearance = connectAppearance(vuetify)
app.onUnmount(() => {
  disconnectAppearance()
  window.tutoriaAppearance.dispose()
})

// Initialize authentication on app start
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')
