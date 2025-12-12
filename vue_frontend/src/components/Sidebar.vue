<template>
  <div>
    <!-- Sidebar -->
    <div
      :class="[
        'fixed left-0 top-0 h-full bg-white shadow-xl z-40 flex flex-col transition-all duration-300',
        isOpen ? 'w-56' : 'w-0'
      ]"
    >
      <div v-show="isOpen" class="flex flex-col h-full">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">
            {{ userRole === 'admin' ? 'Administración' : 'Materias' }}
          </h2>
        </div>

        <!-- Admin Menu -->
        <div v-if="userRole === 'admin'" class="flex-1 overflow-y-auto">
          <!-- Professors Option -->
          <button
            @click="navigateToSection('professors')"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 transition-colors border-b border-gray-100',
              activeSection === 'professors' ? 'bg-purple-50 text-purple-700' : 'hover:bg-gray-50 text-gray-700'
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <span class="font-medium">Profesores</span>
          </button>

          <!-- Configurations Option (above logout) -->
          <button
            @click="navigateToSection('configurations')"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 transition-colors border-b border-gray-100',
              activeSection === 'configurations' ? 'bg-purple-50 text-purple-700' : 'hover:bg-gray-50 text-gray-700'
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span class="font-medium">Configuraciones</span>
          </button>
        </div>

        <!-- Professor Menu -->
        <div v-else class="flex-1 flex flex-col">
          <!-- Add button -->
          <div class="p-4 border-b border-gray-200">
            <button
              @click="handleAddMateria"
              class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              <span class="font-medium">Agregar Materia</span>
            </button>
          </div>

          <!-- Materias list -->
          <div class="flex-1 overflow-y-auto p-4">
            <div v-if="materias.length === 0" class="text-center text-gray-500 py-8">
              <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
              <p class="text-sm">No hay materias agregadas</p>
              <p class="text-xs mt-1">Haz clic en el botón de arriba para agregar</p>
            </div>
            <ul v-else class="space-y-2">
              <li
                v-for="materia in materias"
                :key="materia.id"
                @click="selectMateria(materia)"
                :class="[
                  'p-3 rounded-lg cursor-pointer transition-colors border',
                  selectedMateria?.id === materia.id
                    ? 'bg-blue-100 border-blue-300'
                    : 'bg-gray-50 hover:bg-gray-100 border-gray-200'
                ]"
              >
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-gray-800">{{ materia.name }}</span>
                  <button
                    @click.stop="handleDeleteMateria(materia.id)"
                    class="p-1 hover:bg-red-100 rounded transition-colors"
                    aria-label="Eliminar materia"
                  >
                    <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
        
        <!-- Logout Button at bottom -->
        <div class="p-4 border-t border-gray-200 mt-auto">
          <button
            v-if="onLogout"
            @click="onLogout"
            class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors shadow-sm text-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            <span class="font-medium">Cerrar Sesión</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Toggle Button (sticks to edge of sidebar) -->
    <button
      @click="toggleSidebar"
      :class="[
        'fixed top-4 z-50 p-2 text-white rounded-r-lg shadow-lg transition-all duration-300',
        userRole === 'admin' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-blue-600 hover:bg-blue-700',
        isOpen ? 'left-56' : 'left-0'
      ]"
      :aria-label="isOpen ? 'Cerrar menú' : 'Abrir menú'"
    >
      <svg class="w-6 h-6 transition-transform duration-300" :class="{ 'rotate-180': isOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
      </svg>
    </button>

    <!-- Overlay (darkens background when sidebar is open on mobile) -->
    <transition name="fade">
      <div
        v-if="isOpen"
        @click="toggleSidebar"
        class="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
      ></div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  userRole: {
    type: String,
    default: 'professor',
    validator: (value) => ['admin', 'professor'].includes(value)
  },
  onLogout: {
    type: Function,
    default: null
  }
})

// Emits
const emit = defineEmits(['navigate'])

const isOpen = ref(true)
const materias = ref([])
const selectedMateria = ref(null)
const activeSection = ref('professors')

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const navigateToSection = (section) => {
  activeSection.value = section
  emit('navigate', section)
}

const handleAddMateria = () => {
  const materiaName = prompt('Ingrese el nombre de la materia:')
  if (materiaName && materiaName.trim()) {
    const newMateria = {
      id: Date.now(),
      name: materiaName.trim()
    }
    materias.value.push(newMateria)
    // Auto-select the newly added materia
    selectMateria(newMateria)
  }
}

const handleDeleteMateria = (id) => {
  if (confirm('¿Está seguro de eliminar esta materia?')) {
    materias.value = materias.value.filter(m => m.id !== id)
    // Clear selection if deleted materia was selected
    if (selectedMateria.value?.id === id) {
      selectedMateria.value = null
    }
  }
}

const selectMateria = (materia) => {
  selectedMateria.value = materia
}

// Expose properties for parent components
defineExpose({
  isOpen,
  selectedMateria,
  activeSection
})

</script>

<style scoped>
/* Fade animation for overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
