<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Loader2, CheckCircle2 } from 'lucide-vue-next'
import axios from 'axios'

const router = useRouter()
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const isShaking = ref(false) // Para activar la animación

const triggerShake = () => {
  isShaking.value = true
  setTimeout(() => isShaking.value = false, 500)
}

// Lista estándar de preguntas de seguridad
const preguntasEstandar = [
  '¿Cuál fue el nombre de tu primera mascota?',
  '¿En qué ciudad naciste?',
  '¿Cuál es el segundo nombre de tu madre?',
  '¿Cuál fue tu primera escuela primaria?',
  '¿Cuál es el nombre de tu mejor amigo de la infancia?',
  '¿Marca de tu primer vehículo?'
]

const formData = reactive({
  correo: '',
  password: '',
  confirmPassword: '', // Nuevo campo
  cedula: '',
  nombres_apellidos: '',
  cargo: '',
  centro: '',
  pregunta_seguridad_1: '', // Inicia vacío para obligar a seleccionar
  respuesta_seguridad_1: '',
  pregunta_seguridad_2: '',
  respuesta_seguridad_2: '',
  validez_dias: 90 
})

const onSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (formData.password !== formData.confirmPassword) {
    errorMessage.value = 'Las contraseñas no coinciden.'
    triggerShake()
    return
  }

  // Validación: No pueden elegir la misma pregunta dos veces
  if (formData.pregunta_seguridad_1 !== '' && formData.pregunta_seguridad_1 === formData.pregunta_seguridad_2) {
    errorMessage.value = 'Debes seleccionar dos preguntas de seguridad diferentes.'
    triggerShake()
    return
  }

  isLoading.value = true

  try {
    // Usamos la variable de entorno que configuraste (con respaldo local por si acaso)
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
    await axios.post(`${apiUrl}/usuarios`, formData)
    
    successMessage.value = '¡Usuario administrador creado exitosamente!'
    
    // Esperamos 2 segundos y lo mandamos al login
    setTimeout(() => {
      router.push('/')
    }, 2000)

  } catch (error: any) {
    // Si Axios tiene respuesta, mostramos el detalle técnico real
    if (error.response) {
      errorMessage.value = JSON.stringify(error.response.data.detail || error.response.data);
    } else {
      errorMessage.value = 'No hubo conexión con el servidor. Verifica que FastAPI esté corriendo.'
    }
    triggerShake()
  } finally {
    isLoading.value = false
  }
}

const goToLogin = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background p-4">
    <div :class="['w-full max-w-3xl bg-card border-border border rounded-xl shadow-lg p-8', { 'animate-shake': isShaking }]">
      
      <div class="flex flex-col space-y-2 text-center mb-8">
        <h1 class="text-3xl font-semibold tracking-tight text-primary">NEXUS</h1>
        <p class="text-muted-foreground">Registro de Usuario Administrador</p>
      </div>

      <form @submit.prevent="onSubmit" class="space-y-4" novalidate>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="text-sm font-medium">Cédula de Identidad</label>
            <input v-model="formData.cedula" type="text" placeholder="Ej. 12345678" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Nombres y Apellidos</label>
            <input v-model="formData.nombres_apellidos" type="text" placeholder="Ej. Juan Pérez" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Correo Electrónico Institucional</label>
            <input v-model="formData.correo" type="email" placeholder="ejemplo@fii.gob.ve" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Días de Validez de Clave</label>
            <select v-model="formData.validez_dias" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm">
              <option value="30">30 días</option>
              <option value="60">60 días</option>
              <option value="90">90 días</option>
              <option value="180">180 días</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Contraseña de Acceso</label>
            <input v-model="formData.password" type="password" placeholder="********" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Confirmar Contraseña</label>
            <input v-model="formData.confirmPassword" type="password" placeholder="********" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Cargo Oficial</label>
            <input v-model="formData.cargo" type="text" placeholder="Ej. Analista de Sistemas" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Centro de Adscripción</label>
            <input v-model="formData.centro" type="text" placeholder="Ej. Centro de Sistemas (CSICE)" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
          </div>
        </div>

        <div class="border-t border-border mt-6 pt-6">
          <p class="text-sm font-semibold text-foreground mb-4">Configuración de Seguridad</p>
          
          <div class="grid grid-cols-1 gap-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
              <div class="space-y-2 flex-1">
                <label class="text-sm font-medium">Pregunta de Seguridad 1</label>
                <select v-model="formData.pregunta_seguridad_1" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                  <option value="" disabled>Seleccione una pregunta...</option>
                  <option v-for="pregunta in preguntasEstandar" :key="pregunta" :value="pregunta">
                    {{ pregunta }}
                  </option>
                </select>
              </div>
              <div class="space-y-2 flex-1">
                <label class="text-sm font-medium">Respuesta 1</label>
                <input v-model="formData.respuesta_seguridad_1" type="password" placeholder="Tu respuesta secreta" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
              <div class="space-y-2 flex-1">
                <label class="text-sm font-medium">Pregunta de Seguridad 2</label>
                <select v-model="formData.pregunta_seguridad_2" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                  <option value="" disabled>Seleccione una pregunta...</option>
                  <option v-for="pregunta in preguntasEstandar" :key="pregunta" :value="pregunta">
                    {{ pregunta }}
                  </option>
                </select>
              </div>
              <div class="space-y-2 flex-1">
                <label class="text-sm font-medium">Respuesta 2</label>
                <input v-model="formData.respuesta_seguridad_2" type="password" placeholder="Tu respuesta secreta" required class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
              </div>
            </div>
          </div>
        </div>

        <button type="submit" :disabled="isLoading" class="mt-8 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 w-full">
          <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
          Registrar Usuario
        </button>

      </form>

      <div v-if="successMessage" class="mt-6 p-4 rounded-lg bg-green-500/10 border border-green-500/50 text-green-500 flex items-center gap-3">
        <CheckCircle2 class="h-5 w-5" />
        <p class="text-sm font-medium">{{ successMessage }}</p>
      </div>

      <div v-if="errorMessage" class="mt-6 p-4 rounded-lg bg-destructive/10 border border-destructive/50 text-destructive text-sm font-medium">
        {{ errorMessage }}
      </div>

      <div class="mt-6 text-center">
        <button @click="goToLogin" class="text-sm text-muted-foreground hover:text-primary transition-colors hover:underline">
          Volver al Inicio de Sesión
        </button>
      </div>
    </div>
  </div>
</template>