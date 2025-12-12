<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Configuraciones del Sistema</h2>
      <p class="text-gray-600 mt-1">Administra los parámetros generales de la aplicación</p>
    </div>

    <!-- System Settings -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- General Settings -->
      <div class="bg-white shadow-lg rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Configuración General</h3>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Nombre de la Institución
            </label>
            <input
              v-model="settings.institution_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Universidad TutorIA"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email de Contacto
            </label>
            <input
              v-model="settings.contact_email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="contacto@tutoria.edu"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Teléfono de Contacto
            </label>
            <input
              v-model="settings.contact_phone"
              type="tel"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="+591 12345678"
            />
          </div>

          <button
            @click="saveGeneralSettings"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-4 focus:ring-purple-300"
          >
            Guardar Cambios
          </button>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="bg-white shadow-lg rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Seguridad</h3>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tiempo de Sesión (horas)
            </label>
            <input
              v-model.number="settings.session_timeout"
              type="number"
              min="1"
              max="72"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                v-model="settings.require_email_verification"
                type="checkbox"
                class="form-checkbox h-5 w-5 text-purple-600 rounded focus:ring-purple-500"
              />
              <span class="text-sm font-medium text-gray-700">
                Requerir verificación de email
              </span>
            </label>
          </div>

          <div>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                v-model="settings.enable_two_factor"
                type="checkbox"
                class="form-checkbox h-5 w-5 text-purple-600 rounded focus:ring-purple-500"
              />
              <span class="text-sm font-medium text-gray-700">
                Habilitar autenticación de dos factores
              </span>
            </label>
          </div>

          <button
            @click="saveSecuritySettings"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-4 focus:ring-purple-300"
          >
            Guardar Cambios
          </button>
        </div>
      </div>

      <!-- Academic Settings -->
      <div class="bg-white shadow-lg rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Configuración Académica</h3>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Año Académico Actual
            </label>
            <input
              v-model="settings.current_academic_year"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="2025"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Periodo Actual
            </label>
            <select
              v-model="settings.current_period"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="1">Primer Semestre</option>
              <option value="2">Segundo Semestre</option>
              <option value="3">Verano</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Máximo de Materias por Estudiante
            </label>
            <input
              v-model.number="settings.max_subjects_per_student"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <button
            @click="saveAcademicSettings"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-4 focus:ring-purple-300"
          >
            Guardar Cambios
          </button>
        </div>
      </div>

      <!-- System Information -->
      <div class="bg-white shadow-lg rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Información del Sistema</h3>
        </div>
        <div class="px-6 py-4 space-y-3">
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">Versión</span>
            <span class="text-sm font-medium text-gray-900">1.0.0</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">Base de Datos</span>
            <span class="text-sm font-medium text-gray-900">SQL Server</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">Última Actualización</span>
            <span class="text-sm font-medium text-gray-900">{{ getCurrentDate }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">Estado del Sistema</span>
            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
              Operativo
            </span>
          </div>
          <div class="flex justify-between items-center py-2">
            <span class="text-sm text-gray-600">Modo de Mantenimiento</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="settings.maintenance_mode"
                type="checkbox"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <transition name="fade">
      <div v-if="message" class="fixed bottom-6 right-6 z-50">
        <div
          :class="[
            'px-6 py-4 rounded-lg shadow-lg',
            message.type === 'success' ? 'bg-green-500' : 'bg-red-500'
          ]"
        >
          <p class="text-white font-medium">{{ message.text }}</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Settings state
const settings = ref({
  // General
  institution_name: 'Universidad TutorIA',
  contact_email: 'contacto@tutoria.edu',
  contact_phone: '+591 12345678',
  
  // Security
  session_timeout: 24,
  require_email_verification: false,
  enable_two_factor: false,
  
  // Academic
  current_academic_year: '2025',
  current_period: '2',
  max_subjects_per_student: 6,
  
  // System
  maintenance_mode: false
})

const message = ref(null)

const getCurrentDate = computed(() => {
  return new Date().toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Save functions
const saveGeneralSettings = () => {
  // TODO: Implement API call to save general settings
  showMessage('Configuración general guardada exitosamente', 'success')
}

const saveSecuritySettings = () => {
  // TODO: Implement API call to save security settings
  showMessage('Configuración de seguridad guardada exitosamente', 'success')
}

const saveAcademicSettings = () => {
  // TODO: Implement API call to save academic settings
  showMessage('Configuración académica guardada exitosamente', 'success')
}

const showMessage = (text, type = 'success') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = null
  }, 3000)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
