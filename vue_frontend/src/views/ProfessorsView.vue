<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Lista de Profesores</h2>
        <p class="text-gray-600 mt-1">Administra los profesores del sistema</p>
      </div>
      <button
        @click="showModal = true"
        class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Añadir Profesor
      </button>
    </div>

    <!-- Modal for Add/Edit Professor -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <h3 class="text-lg font-medium text-gray-900">
            {{ editingProfessor ? 'Editar Profesor' : 'Nuevo Profesor' }}
          </h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="px-6 py-6">
          <!-- Tabs for Form / Excel -->
          <div class="flex border-b border-gray-200 mb-6">
            <button
              @click="activeTab = 'form'"
              :class="[
                'px-4 py-2 font-medium text-sm border-b-2 transition-colors',
                activeTab === 'form'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Formulario Manual
            </button>
            <button
              @click="activeTab = 'excel'"
              :class="[
                'px-4 py-2 font-medium text-sm border-b-2 transition-colors',
                activeTab === 'excel'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Cargar desde Excel
            </button>
          </div>

          <!-- Form Tab -->
          <div v-show="activeTab === 'form'">
            <form @submit.prevent="handleSubmit" class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- First Name -->
                <div>
                  <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">
                    Nombre <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="first_name"
                    v-model="formData.first_name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ej: Juan"
                  />
                </div>

                <!-- Last Name -->
                <div>
                  <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">
                    Apellido <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="last_name"
                    v-model="formData.last_name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ej: Pérez"
                  />
                </div>

                <!-- Email -->
                <div>
                  <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                    Email <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="email"
                    v-model="formData.email"
                    type="email"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="profesor@tutoria.edu"
                  />
                </div>

                <!-- Phone -->
                <div>
                  <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="phone"
                    v-model="formData.phone"
                    type="tel"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ej: 76543210"
                  />
                </div>

                <!-- Password (only when creating new) -->
                <div v-if="!editingProfessor">
                  <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                    Contraseña <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="password"
                    v-model="formData.password"
                    type="password"
                    :required="!editingProfessor"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Mínimo 6 caracteres"
                  />
                  <p class="text-xs text-gray-500 mt-1">
                    Debe incluir mayúsculas, minúsculas y números
                  </p>
                </div>

                <!-- Confirm Password (only when creating new) -->
                <div v-if="!editingProfessor">
                  <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-1">
                    Confirmar Contraseña <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="confirm_password"
                    v-model="formData.confirm_password"
                    type="password"
                    :required="!editingProfessor"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Repetir contraseña"
                  />
                </div>
              </div>

              <!-- Error/Success Messages -->
              <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-700">{{ errorMessage }}</p>
              </div>
              <div v-if="successMessage" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-700">{{ successMessage }}</p>
              </div>

              <!-- Submit Button -->
              <div class="flex justify-end gap-3">
                <button
                  type="button"
                  @click="closeModal"
                  class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  :disabled="isLoading"
                  class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-4 focus:ring-purple-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <svg v-if="isLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{{ editingProfessor ? 'Actualizar Profesor' : 'Registrar Profesor' }}</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Excel Tab -->
          <div v-show="activeTab === 'excel'" class="space-y-4">
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                ref="fileInput"
                type="file"
                accept=".xlsx,.xls"
                @change="handleFileUpload"
                class="hidden"
              />
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-2 text-sm text-gray-600">
                <button
                  type="button"
                  @click="$refs.fileInput.click()"
                  class="text-purple-600 hover:text-purple-700 font-medium"
                >
                  Selecciona un archivo Excel
                </button>
                o arrastra y suelta aquí
              </p>
              <p class="mt-1 text-xs text-gray-500">Formatos: XLSX, XLS</p>
            </div>

            <div v-if="selectedFile" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
                    <p class="text-xs text-gray-500">{{ (selectedFile.size / 1024).toFixed(2) }} KB</p>
                  </div>
                </div>
                <button
                  @click="selectedFile = null"
                  class="text-red-600 hover:text-red-800"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div class="flex">
                <svg class="h-5 w-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h4 class="text-sm font-medium text-yellow-800">Formato del Excel</h4>
                  <p class="text-xs text-yellow-700 mt-1">
                    El archivo debe contener las columnas: <strong>Nombre, Apellido, Email, Teléfono, Contraseña</strong>
                  </p>
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-3">
              <button
                type="button"
                @click="closeModal"
                class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                @click="uploadExcel"
                :disabled="!selectedFile || isLoading"
                class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-4 focus:ring-purple-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg v-if="isLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Cargar Profesores</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Professors List Table -->
    <div class="bg-white shadow-lg rounded-lg">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre Completo
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Teléfono
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="professors.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                No hay profesores registrados
              </td>
            </tr>
            <tr v-for="professor in professors" :key="professor.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <span class="text-purple-600 font-medium">
                      {{ professor.first_name.charAt(0) }}{{ professor.last_name.charAt(0) }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ professor.first_name }} {{ professor.last_name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ professor.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ professor.phone }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="[
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    professor.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ professor.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="editProfessor(professor)"
                  class="text-purple-600 hover:text-purple-900 mr-3"
                  title="Editar"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click="toggleProfessorStatus(professor)"
                  :class="[
                    'mr-3',
                    professor.is_active ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'
                  ]"
                  :title="professor.is_active ? 'Desactivar' : 'Activar'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                </button>
                <button
                  @click="deleteProfessor(professor)"
                  class="text-red-600 hover:text-red-900"
                  title="Eliminar"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// Form data
const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: ''
})

// State
const professors = ref([])
const editingProfessor = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showModal = ref(false)
const activeTab = ref('form')
const selectedFile = ref(null)
const fileInput = ref(null)

// Load professors on mount
onMounted(() => {
  loadProfessors()
})

// Load professors list (mock data for now)
const loadProfessors = async () => {
  try {
    const token = localStorage.getItem('auth_token')
    const response = await fetch('http://localhost:5000/api/auth/professors', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Error al cargar profesores')
    }

    const data = await response.json()
    professors.value = data.professors || []
  } catch (error) {
    console.error('Error loading professors:', error)
    errorMessage.value = 'Error al cargar la lista de profesores'
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
  }
}

// Handle form submission
const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  // Validate passwords match (only for new professors)
  if (!editingProfessor.value && formData.value.password !== formData.value.confirm_password) {
    errorMessage.value = 'Las contraseñas no coinciden'
    return
  }

  isLoading.value = true

  try {
    if (editingProfessor.value) {
      // Update existing professor
      await updateProfessor()
    } else {
      // Create new professor
      await createProfessor()
    }
  } catch (error) {
    errorMessage.value = error.message || 'Error al procesar la solicitud'
  } finally {
    isLoading.value = false
  }
}

// Create new professor
const createProfessor = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: formData.value.email,
        password: formData.value.password,
        first_name: formData.value.first_name,
        last_name: formData.value.last_name,
        phone: formData.value.phone
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Error al registrar profesor')
    }

    successMessage.value = 'Profesor registrado exitosamente'
    resetForm()
    loadProfessors()

    // Close modal after success
    setTimeout(() => {
      closeModal()
    }, 1500)
  } catch (error) {
    throw error
  }
}

// Update existing professor
const updateProfessor = async () => {
  // TODO: Implement API call to update professor
  successMessage.value = 'Profesor actualizado exitosamente'
  resetForm()
  loadProfessors()

  setTimeout(() => {
    closeModal()
  }, 1500)
}

// Edit professor
const editProfessor = (professor) => {
  editingProfessor.value = professor
  formData.value = {
    first_name: professor.first_name,
    last_name: professor.last_name,
    email: professor.email,
    phone: professor.phone,
    password: '',
    confirm_password: ''
  }
  showModal.value = true
  activeTab.value = 'form'
}

// Cancel edit
const cancelEdit = () => {
  editingProfessor.value = null
  resetForm()
}

// Toggle professor status
const toggleProfessorStatus = async (professor) => {
  const action = professor.is_active ? 'desactivar' : 'activar'
  if (confirm(`¿Está seguro de ${action} a ${professor.first_name} ${professor.last_name}?`)) {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`http://localhost:5000/api/auth/professors/${professor.id}/toggle-status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Error al cambiar el estado del profesor')
      }

      const data = await response.json()
      
      // Update local state with the response data
      professor.is_active = data.professor.is_active
      
      successMessage.value = data.message
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } catch (error) {
      console.error('Error toggling professor status:', error)
      errorMessage.value = 'Error al cambiar el estado del profesor'
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
    }
  }
}

// Delete professor
const deleteProfessor = async (professor) => {
  if (confirm(`¿Está seguro de eliminar a ${professor.first_name} ${professor.last_name}? Esta acción no se puede deshacer.`)) {
    // TODO: Implement API call to delete professor
    professors.value = professors.value.filter(p => p.id !== professor.id)
    successMessage.value = 'Profesor eliminado exitosamente'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
}

// Reset form
const resetForm = () => {
  formData.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: ''
  }
  editingProfessor.value = null
  errorMessage.value = ''
  successMessage.value = ''
}

// Close modal
const closeModal = () => {
  showModal.value = false
  activeTab.value = 'form'
  selectedFile.value = null
  resetForm()
}

// Handle file upload
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

// Upload Excel file
const uploadExcel = async () => {
  if (!selectedFile.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const token = localStorage.getItem('auth_token')
    const response = await fetch('http://localhost:5000/api/auth/professors/bulk-upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Error al cargar el archivo')
    }

    successMessage.value = `${data.count || 0} profesores cargados exitosamente`
    selectedFile.value = null
    loadProfessors()
    
    setTimeout(() => {
      closeModal()
    }, 2000)
  } catch (error) {
    console.error('Error uploading Excel:', error)
    errorMessage.value = error.message || 'Error al cargar el archivo Excel'
  } finally {
    isLoading.value = false
  }
}
</script>
