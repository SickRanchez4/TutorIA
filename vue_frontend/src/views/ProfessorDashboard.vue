<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
    <!-- Sidebar Component -->
    <Sidebar 
      ref="sidebarRef" 
      user-role="professor"
      :on-logout="handleLogout" 
    />
    
    <!-- Main Content with dynamic margin -->
    <div
      :class="[
        'transition-all duration-300',
        sidebarRef?.isOpen ? 'ml-64' : 'ml-0'
      ]"
    >
      <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center ml-4">
            <h1 class="text-xl font-semibold text-gray-900">
              Portal del Profesor
            </h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">
              Bienvenido, {{ authStore.user?.name }}
            </span>
          </div>
        </div>
      </div>
    </nav>

    <!-- Selected Materia Panel -->
    <div v-if="sidebarRef?.selectedMateria" class="h-screen">
      <MateriaPanel :materia="sidebarRef.selectedMateria" />
    </div>
    
    <!-- Default Dashboard Content (when no materia is selected) -->
    <main v-else class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Welcome Section -->
        <div class="bg-white overflow-hidden shadow-lg rounded-lg mb-8">
          <div class="px-6 py-8">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-6">
                <h2 class="text-2xl font-bold text-gray-900">
                  ¡Bienvenido, {{ authStore.user?.name }}!
                </h2>
                <p class="text-gray-600 mt-1">
                  Has ingresado exitosamente al portal de profesores. Aquí puedes gestionar tus clases, calificaciones y materiales académicos.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div class="bg-white overflow-hidden shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Mis Clases</h3>
                  <p class="text-sm text-gray-500">Gestionar cursos y estudiantes</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Calificaciones</h3>
                  <p class="text-sm text-gray-500">Registrar y revisar notas</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Materiales</h3>
                  <p class="text-sm text-gray-500">Subir y organizar recursos</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white shadow-lg rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Actividad Reciente</h3>
          </div>
          <div class="px-6 py-4">
            <div class="space-y-4">
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <p class="text-sm text-gray-600">Sistema iniciado correctamente</p>
                <span class="text-xs text-gray-400">{{ getCurrentTime }}</span>
              </div>
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                <p class="text-sm text-gray-600">Acceso autorizado para {{ authStore.user?.name }}</p>
                <span class="text-xs text-gray-400">{{ getCurrentTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../components/Sidebar.vue'
import MateriaPanel from '../components/MateriaPanel.vue'

const router = useRouter()
const sidebarRef = ref(null)
const authStore = useAuthStore()

const getCurrentTime = computed(() => {
  return new Date().toLocaleTimeString('es-ES')
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>