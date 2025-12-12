<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
    <Sidebar 
      ref="sidebarRef" 
      user-role="admin"
      :on-logout="handleLogout"
      @navigate="handleNavigation"
    />
    <div :class="['transition-all duration-300', sidebarRef?.isOpen ? 'ml-64' : 'ml-0']">
      <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center ml-4">
              <h1 class="text-xl font-semibold text-gray-900">
                Panel de Administración
                <span class="text-purple-600">
                  / {{ activeView === 'professors' ? 'Profesores' : 'Configuraciones' }}
                </span>
              </h1>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-700">
                Administrador: {{ authStore.user?.name }}
              </span>
            </div>
          </div>
        </div>
      </nav>
      <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <ProfessorsView v-if="activeView === 'professors'" />
        <ConfigurationsView v-else-if="activeView === 'configurations'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../components/Sidebar.vue'
import ProfessorsView from './ProfessorsView.vue'
import ConfigurationsView from './ConfigurationsView.vue'

const router = useRouter()
const sidebarRef = ref(null)
const authStore = useAuthStore()
const activeView = ref('professors')

const handleNavigation = (section) => {
  activeView.value = section
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
