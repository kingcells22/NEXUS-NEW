<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { Loader2, AlertCircle } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth.store' // Importamos el cerebro

const router = useRouter()
const authStore = useAuthStore() // Activamos el cerebro

const formData = reactive({ correo: '', password: '' })
const formErrors = reactive({ correo: '', password: '' })
const isLoading = ref(false)
const errorMessage = ref('')

const validateForm = () => {
  let isValid = true
  formErrors.correo = ''
  formErrors.password = ''

  if (!formData.correo || !/^\S+@\S+\.\S+$/.test(formData.correo)) {
    formErrors.correo = 'El correo electrónico no es válido (ejemplo@fii.gob.ve)'
    isValid = false
  }
  if (!formData.password || formData.password.length < 6) {
    formErrors.password = 'La contraseña debe tener mínimo seis (6) caracteres'
    isValid = false
  }
  return isValid
}

const onSubmit = async () => {
  if (!validateForm()) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    // LLAMADA REAL AL BACKEND DE PYTHON
    await authStore.loginUser(formData.correo, formData.password)
    
    // Si la contraseña es correcta, te avisa por consola (luego configuraremos el Router para ir al Dashboard)
    console.log("¡SESIÓN INICIADA CORRECTAMENTE! Token guardado.")
    alert("¡Inicio de sesión exitoso! (Mira la consola)")
    
  } catch (error: any) {
    // Si la clave es incorrecta, FastAPI devuelve el error y lo pintamos de rojo
    errorMessage.value = error.response?.data?.detail || 'Correo/Contraseña incorrecta. Por favor, verifica tus credenciales.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="grid gap-6">
    <form @submit.prevent="onSubmit" class="space-y-8" novalidate>
      
      <div class="space-y-2 text-left">
        <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Correo Electrónico
        </label>
        <input 
          v-model="formData.correo"
          type="email" 
          placeholder="ejemplo@fii.gob.ve" 
          class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
        />
        <p v-if="formErrors.correo" class="text-[0.8rem] font-medium text-destructive">
          {{ formErrors.correo }}
        </p>
      </div>

      <div class="space-y-2 text-left">
        <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Contraseña
        </label>
        <input 
          v-model="formData.password"
          type="password" 
          placeholder="*********" 
          class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
        />
        <p v-if="formErrors.password" class="text-[0.8rem] font-medium text-destructive">
          {{ formErrors.password }}
        </p>
      </div>

      <button 
        type="submit" 
        :disabled="isLoading"
        class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 w-full"
      >
        <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
        Ingresar
      </button>

      <div class="mt-4 text-center text-sm">
        ¿No tienes cuenta administrativa? 
        <RouterLink to="/registro" class="text-primary font-medium hover:underline">
          Regístrate aquí
        </RouterLink>
      </div>
      
    </form>

    <div v-if="errorMessage" class="relative w-full rounded-lg border border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive p-4 flex gap-3 text-left">
      <AlertCircle class="h-4 w-4 mt-0.5" />
      <div class="flex flex-col">
        <h5 class="mb-1 font-medium leading-none tracking-tight">Error</h5>
        <div class="text-sm [&_p]:leading-relaxed">{{ errorMessage }}</div>
      </div>
    </div>
    
  </div>
</template>