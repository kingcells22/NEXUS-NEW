<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Estados del flujo
const paso = ref(1) // 1: Introducir correo, 2: Responder preguntas y cambiar clave
const correo = ref('')
const pregunta1 = ref('')
const pregunta2 = ref('')

const respuesta1 = ref('')
const respuesta2 = ref('')
const password = ref('')
const passwordConfirm = ref('')
const validezDias = ref(180) // Valor institucional por defecto

// Control de errores y animación
const errorMensaje = ref('')
const sacudir = ref(false)

// Paso 1: Buscar las preguntas de seguridad asociadas al correo
const buscarPreguntas = async () => {
  if (!correo.value) return

  try {
    // Nota: Este endpoint debe recibir el correo y retornar { pregunta_1, pregunta_2 }
    const response = await fetch(`http://127.0.0.1:8000/api/usuarios/preguntas?correo=${correo.value}`)
    
    if (response.ok) {
      const data = await response.json()
      pregunta1.value = data.pregunta_seguridad_1
      pregunta2.value = data.pregunta_seguridad_2
      errorMensaje.value = ''
      paso.value = 2
    } else {
      ejecutarSacudida('El correo electrónico no se encuentra registrado.')
    }
  } catch (error) {
    ejecutarSacudida('Error de conexión con el servidor de seguridad.')
  }
}

// Activa el efecto visual de error en la pantalla
const ejecutarSacudida = (mensaje: string) => {
  errorMensaje.value = mensaje
  sacudir.value = true
  setTimeout(() => {
    sacudir.value = false
  }, 500) // Duración de la animación
}

// Paso 2: Validar parámetros e intentar el cambio de clave
const procesarRecuperacion = async () => {
  errorMensaje.value = ''

  // 1. Validación de coincidencia exacta
  if (password.value !== passwordConfirm.value) {
    ejecutarSacudida('Las contraseñas introducidas no coinciden.')
    return
  }

  // 2. Validación de parámetros institucionales (Mínimo 8 caracteres, letras y números)
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/
  if (!passwordRegex.test(password.value)) {
    ejecutarSacudida('La contraseña debe tener al menos 8 caracteres, incluyendo letras y números.')
    return
  }

  // 3. Validación del periodo de validez
  if (validezDias.value <= 0) {
    ejecutarSacudida('El periodo de validez debe ser mayor a 0 días.')
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/usuarios/recuperar-clave', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        correo: correo.value,
        respuesta_seguridad_1: respuesta1.value,
        respuesta_seguridad_2: respuesta2.value,
        nueva_password: password.value,
        validez_dias: validezDias.value
      })
    })

    if (response.ok) {
      alert('Contraseña actualizada con éxito de acuerdo a las directrices del sistema.')
      router.push('/')
    } else {
      const errorData = await response.json()
      ejecutarSacudida(errorData.detail || 'Respuestas de seguridad incorrectas.')
    }
  } catch (error) {
    ejecutarSacudida('Error al procesar la actualización en la base de datos.')
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center p-4">
    <div 
      class="w-full max-w-md bg-[#141414] border border-gray-800 rounded-2xl p-8 shadow-2xl transition-transform"
      :class="{ 'animate-shake border-red-600': sacudir }"
    >
      <div class="text-center mb-6">
        <img src="/logo-fiidt.png" alt="Logo" class="h-12 mx-auto mb-3" />
        <h2 class="text-2xl font-bold text-white">Recuperación de Credenciales</h2>
        <p class="text-sm text-gray-400 mt-1">Módulo de Seguridad Nexus</p>
      </div>

      <div v-if="errorMensaje" class="mb-4 p-3 bg-red-900/40 border border-red-600 text-red-200 text-sm rounded-md text-center">
        {{ errorMensaje }}
      </div>

      <form v-if="paso === 1" @submit.prevent="buscarPreguntas" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">Correo Electrónico Institucional</label>
          <input 
            v-model="correo" 
            type="email" 
            required 
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
            placeholder="usuario@fii.gob.ve"
          />
        </div>
        <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-medium p-2.5 rounded-md transition-colors">
          Verificar Identidad
        </button>
      </form>

      <form v-if="paso === 2" @submit.prevent="procesarRecuperacion" class="space-y-4">
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Pregunta 1: {{ pregunta1 }}</label>
          <input 
            v-model="respuesta1" 
            type="text" 
            required 
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
            placeholder="Su respuesta..."
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Pregunta 2: {{ pregunta2 }}</label>
          <input 
            v-model="respuesta2" 
            type="text" 
            required 
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
            placeholder="Su respuesta..."
          />
        </div>

        <hr class="border-gray-800 my-4" />

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">Nueva Contraseña</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">Confirmar Nueva Contraseña</label>
          <input 
            v-model="passwordConfirm" 
            type="password" 
            required 
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">Periodo de Validez de la Clave (Días)</label>
          <input 
            v-model.number="validezDias" 
            type="number" 
            required 
            min="1"
            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md p-2.5 text-white focus:border-red-600 focus:outline-none"
          />
        </div>

        <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-medium p-2.5 rounded-md transition-colors pt-3">
          Actualizar Credenciales
        </button>
      </form>

      <div class="text-center mt-4">
        <button @click="router.push('/')" class="text-xs text-gray-500 hover:text-white transition-colors">
          Volver al Inicio de Sesión
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
  20%, 40%, 60%, 80% { transform: translateX(6px); }
}
.animate-shake {
  animation: shake 0.4s ease-in-out;
}
</style>