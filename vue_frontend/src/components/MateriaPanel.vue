<template>
  <div v-if="materia" class="h-full flex flex-col">
    <!-- Materia Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="px-6 py-4">
        <h2 class="text-2xl font-bold text-gray-900">{{ materia.name }}</h2>
      </div>
      
      <!-- Navigation Tabs -->
      <div class="border-t border-gray-200">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <div class="flex items-center gap-2">
              <component :is="tab.icon" class="w-5 h-5" />
              <span>{{ tab.label }}</span>
            </div>
          </button>
        </nav>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50 p-6">
      <!-- Actividades Tab -->
      <div v-if="activeTab === 'actividades'" class="space-y-4">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Actividades</h3>
          <p class="text-gray-600">Gestiona las actividades y tareas de esta materia.</p>
          <!-- Add more content here -->
        </div>
      </div>

      <!-- Calendario Tab -->
      <div v-if="activeTab === 'calendario'" class="space-y-4">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Calendario</h3>
          <p class="text-gray-600">Visualiza el calendario de clases y eventos.</p>
          <!-- Add more content here -->
        </div>
      </div>

      <!-- Conocimiento Tab -->
      <div v-if="activeTab === 'conocimiento'" class="space-y-4">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Conocimiento</h3>
          <p class="text-gray-600">Base de conocimientos y materiales de la materia.</p>
          <!-- Add more content here -->
        </div>
      </div>

      <!-- Configuración Tab -->
      <div v-if="activeTab === 'configuracion'" class="space-y-4">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Configuración</h3>
          <p class="text-gray-600">Configura los ajustes de esta materia.</p>
          <!-- Add more content here -->
        </div>
      </div>
    </div>
  </div>
  
  <!-- Empty State -->
  <div v-else class="h-full flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <svg class="w-24 h-24 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
      </svg>
      <h3 class="text-xl font-medium text-gray-900 mb-2">No hay materia seleccionada</h3>
      <p class="text-gray-500">Selecciona una materia del menú lateral para comenzar</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'

const props = defineProps({
  materia: {
    type: Object,
    default: null
  }
})

const activeTab = ref('actividades')

const tabs = [
  {
    id: 'actividades',
    label: 'Actividades',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
      `
    }
  },
  {
    id: 'calendario',
    label: 'Calendario',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      `
    }
  },
  {
    id: 'conocimiento',
    label: 'Conocimiento',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
        </svg>
      `
    }
  },
  {
    id: 'configuracion',
    label: 'Configuración',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
      `
    }
  }
]
</script>

<style scoped>
/* Custom scrollbar for content area */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
