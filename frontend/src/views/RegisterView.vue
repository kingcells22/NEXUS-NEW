<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Estados de la búsqueda
const cedulaBusqueda = ref('');
const buscandoCedula = ref(false);
const empleadoEncontrado = ref(false);

// Visibilidad de contraseñas (El "Ojito")
const mostrarPassword = ref(false);
const mostrarConfirmar = ref(false);

const isSubmitting = ref(false);

// Modelo del formulario
const form = ref({
  cedula: '',
  nombres_apellidos: '',
  cargo: '',
  centro: '',
  correo: '',
  password: '',
  confirmar_password: '',
  pregunta_seguridad_1: '',
  respuesta_seguridad_1: '',
  pregunta_seguridad_2: '',
  respuesta_seguridad_2: '',
  validez_dias: 90 // Por defecto 90 días
});

// PASO 1: Buscar al empleado en la base de datos
const buscarEmpleado = async () => {
  if (!cedulaBusqueda.value) return;
  
  buscandoCedula.value = true;
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/empleados/buscar/${cedulaBusqueda.value}`);
    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Error al buscar la cédula.");
      empleadoEncontrado.value = false;
      return;
    }

    // Auto-llenar el formulario y bloquear la vista
    form.value.cedula = data.cedula;
    form.value.nombres_apellidos = data.nombres_apellidos;
    form.value.cargo = data.cargo;
    form.value.centro = data.centro;
    
    empleadoEncontrado.value = true;
    alert(`¡Empleado encontrado! Bienvenido/a ${data.nombres_apellidos}. Por favor, complete sus credenciales.`);

  } catch (error) {
    console.error("Error de conexión:", error);
    alert("Error de conexión con el servidor.");
  } finally {
    buscandoCedula.value = false;
  }
};

// PASO 2: Registrar la cuenta oficialmente
const procesarRegistro = async () => {
  if (form.value.password !== form.value.confirmar_password) {
    alert("Las contraseñas no coinciden. Por favor, verifica usando el ícono del ojo.");
    return;
  }

  isSubmitting.value = true;
  try {
    const response = await fetch('http://127.0.0.1:8000/api/usuarios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        correo: form.value.correo,
        password: form.value.password,
        cedula: form.value.cedula,
        nombres_apellidos: form.value.nombres_apellidos,
        cargo: form.value.cargo,
        centro: form.value.centro,
        pregunta_seguridad_1: form.value.pregunta_seguridad_1,
        respuesta_seguridad_1: form.value.respuesta_seguridad_1,
        pregunta_seguridad_2: form.value.pregunta_seguridad_2,
        respuesta_seguridad_2: form.value.respuesta_seguridad_2,
        validez_dias: form.value.validez_dias
      })
    });

    const data = await response.json();
    
    if (!response.ok) {
      alert(data.detail || "Ocurrió un error en el registro.");
      return;
    }

    alert("¡Cuenta registrada y rol asignado exitosamente! Ya puedes iniciar sesión.");
    router.push('/');

  } catch (error) {
    console.error(error);
    alert("Error de conexión con el servidor.");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4">
    <div class="max-w-2xl w-full bg-[#141414] border border-gray-800 rounded-lg shadow-2xl p-8">
      
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-white">NEXUS <span class="text-red-600">FIIIDT</span></h2>
        <p class="text-gray-400 mt-2">Activación de Cuenta Institucional</p>
      </div>

      <div v-if="!empleadoEncontrado" class="space-y-6">
        <div class="bg-blue-900/20 border border-blue-800 text-blue-300 p-4 rounded-md text-sm text-center">
          Para crear su usuario, primero debemos validar su información en la base de datos de Gestión Humana.
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-white mb-2">Ingrese su Cédula de Identidad</label>
          <div class="flex gap-4">
            <input 
              type="text" 
              v-model="cedulaBusqueda" 
              placeholder="V-12345678"
              class="flex-1 bg-[#0a0a0a] border border-gray-800 text-white rounded-md p-3 focus:ring-red-500 focus:border-red-500"
              @keyup.enter="buscarEmpleado"
            >
            <button 
              @click="buscarEmpleado" 
              :disabled="buscandoCedula || !cedulaBusqueda"
              class="bg-red-600 hover:bg-red-500 disabled:bg-gray-600 text-white font-bold py-3 px-6 rounded-md transition-colors"
            >
              {{ buscandoCedula ? 'Buscando...' : 'Validar' }}
            </button>
          </div>
        </div>
        
        <div class="text-center mt-4">
          <a href="/login" class="text-sm text-red-500 hover:text-red-400">¿Ya tienes cuenta? Inicia Sesión</a>
        </div>
      </div>

      <form v-else @submit.prevent="procesarRegistro" class="space-y-6">
        
        <div class="bg-[#0a0a0a] p-4 rounded-md border border-gray-800 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">Nombre Completo</label>
            <input type="text" v-model="form.nombres_apellidos" disabled class="w-full bg-transparent text-white font-semibold cursor-not-allowed">
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Cédula</label>
            <input type="text" v-model="form.cedula" disabled class="w-full bg-transparent text-white font-semibold cursor-not-allowed">
          </div>
          <div class="md:col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">Cargo</label>
            <input type="text" v-model="form.cargo" disabled class="w-full bg-transparent text-gray-300 cursor-not-allowed">
          </div>
          <div class="md:col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">Centro / Oficina</label>
            <input type="text" v-model="form.centro" disabled class="w-full bg-transparent text-gray-300 cursor-not-allowed">
          </div>
        </div>

        <hr class="border-gray-800">

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-white mb-2">Correo Electrónico Institucional</label>
            <input type="email" v-model="form.correo" placeholder="ejemplo@fii.gob.ve" required class="w-full bg-[#0a0a0a] border border-gray-800 text-white rounded-md p-3 focus:border-red-500">
          </div>

          <div class="relative">
            <label class="block text-sm font-semibold text-white mb-2">Contraseña</label>
            <div class="relative">
              <input :type="mostrarPassword ? 'text' : 'password'" v-model="form.password" required class="w-full bg-[#0a0a0a] border border-gray-800 text-white rounded-md p-3 pr-10 focus:border-red-500">
              <button type="button" @click="mostrarPassword = !mostrarPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-white">
                <svg v-if="!mostrarPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
              </button>
            </div>
          </div>

          <div class="relative">
            <label class="block text-sm font-semibold text-white mb-2">Confirmar Contraseña</label>
            <div class="relative">
              <input :type="mostrarConfirmar ? 'text' : 'password'" v-model="form.confirmar_password" required class="w-full bg-[#0a0a0a] border border-gray-800 text-white rounded-md p-3 pr-10 focus:border-red-500">
              <button type="button" @click="mostrarConfirmar = !mostrarConfirmar" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-white">
                <svg v-if="!mostrarConfirmar" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
              </button>
            </div>
          </div>
        </div>

        <hr class="border-gray-800">

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-semibold text-white mb-2">Pregunta de Seguridad 1</label>
            <select v-model="form.pregunta_seguridad_1" required class="w-full bg-[#0a0a0a] border border-gray-800 text-white text-sm rounded-md p-3 focus:border-red-500">
              <option value="" disabled>Seleccione una pregunta</option>
              <option value="¿Cuál es tu color favorito?">¿Cuál es tu color favorito?</option>
              <option value="¿Nombre de tu primera mascota?">¿Nombre de tu primera mascota?</option>
              <option value="¿Ciudad donde naciste?">¿Ciudad donde naciste?</option>
            </select>
            <input type="text" v-model="form.respuesta_seguridad_1" placeholder="Respuesta 1" required class="w-full bg-[#1a1a1a] border-t-0 border border-gray-800 text-white rounded-b-md p-3 focus:border-red-500 mt-1">
          </div>

          <div>
            <label class="block text-sm font-semibold text-white mb-2">Pregunta de Seguridad 2</label>
            <select v-model="form.pregunta_seguridad_2" required class="w-full bg-[#0a0a0a] border border-gray-800 text-white text-sm rounded-md p-3 focus:border-red-500">
              <option value="" disabled>Seleccione una pregunta</option>
              <option value="¿Cuál era el apodo de tu abuelo?">¿Cuál era el apodo de tu abuelo?</option>
              <option value="¿Nombre de tu mejor amigo de la infancia?">¿Nombre de tu mejor amigo de la infancia?</option>
              <option value="¿Marca de tu primer carro?">¿Marca de tu primer carro?</option>
            </select>
            <input type="text" v-model="form.respuesta_seguridad_2" placeholder="Respuesta 2" required class="w-full bg-[#1a1a1a] border-t-0 border border-gray-800 text-white rounded-b-md p-3 focus:border-red-500 mt-1">
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-white mb-2">Periodo de Validez de la Contraseña (Días)</label>
          <select v-model="form.validez_dias" class="w-full bg-[#0a0a0a] border border-gray-800 text-white rounded-md p-3 focus:border-red-500">
            <option :value="30">30 Días</option>
            <option :value="60">60 Días</option>
            <option :value="90">90 Días</option>
            <option :value="180">180 Días</option>
          </select>
        </div>

        <div class="flex gap-4 pt-4">
          <button 
            type="button" 
            @click="empleadoEncontrado = false" 
            class="w-1/3 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-md transition-colors"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="w-2/3 bg-red-600 hover:bg-red-500 disabled:bg-red-800 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-md transition-colors shadow-lg shadow-red-900/20"
          >
            {{ isSubmitting ? 'Creando cuenta...' : 'Finalizar Registro' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>