<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Estados del formulario
const receptorId = ref('');
const emisorId = ref<number | null>(null); 
const asunto = ref('');
const fecha = ref(new Date().toISOString().split('T')[0]); 
const descripcion = ref('');
const adjuntarArchivos = ref(false);

const isSubmitting = ref(false);

// Lista de empleados desde la BD
const listaEmpleados = ref<Array<{id: number, nombre: string, cedula: string}>>([]);

// Consultamos al backend al cargar la página
onMounted(async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    
    // 1. Buscar la lista de receptores
    const responseEmpleados = await fetch('http://127.0.0.1:8000/api/empleados', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (responseEmpleados.ok) {
      listaEmpleados.value = await responseEmpleados.json();
    }

    // 2. Buscar quién es el usuario actual (Emisor)
    const responseMe = await fetch('http://127.0.0.1:8000/api/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (responseMe.ok) {
      const meData = await responseMe.json();
      emisorId.value = meData.empleado_id;
    }
  } catch (error) {
    console.error("Error cargando datos iniciales:", error);
  }
});

const procesarFormulario = async () => {
    if (!emisorId.value) {
      alert("Error: No se pudo identificar tu perfil de usuario. Recarga la página.");
      return;
    }

    isSubmitting.value = true;
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');

    try {
      // AJUSTE MAESTRO: Forzamos a que todo sea texto (String) para complacer a Pydantic
      const payload = {
        emisor_id: String(emisorId.value),
        receptor_id: String(receptorId.value),
        asunto: asunto.value,
        fecha: fecha.value,
        descripcion: descripcion.value,
        anexos: adjuntarArchivos.value ? "Sí" : "No"
      };

      const memoResponse = await fetch('http://127.0.0.1:8000/api/memorandums', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!memoResponse.ok) {
        const errorData = await memoResponse.json();
        console.error("Detalle del Error 422:", errorData);
        alert("FastAPI rechazó los datos (422). Detalle: " + JSON.stringify(errorData.detail));
        throw new Error("Error 422 de Validación Pydantic");
      }
      
      const memoGenerado = await memoResponse.json();
      const correlativo = memoGenerado.numero_documento;
      
      alert(`¡Memorándum ${correlativo} guardado exitosamente con estatus CREADO!`);
      router.push('/dashboard/emitidos');

    } catch (error: any) {
      console.error(error);
      if (error.message !== "Error 422 de Validación Pydantic") {
        alert("Ocurrió un error de conexión con el servidor.");
      }
    } finally {
      isSubmitting.value = false;
    }
};
</script>

<template>
  <div class="max-w-3xl text-gray-200">
    <h2 class="text-xl font-bold text-white mb-6">Nuevo Memorándum</h2>

    <form @submit.prevent="procesarFormulario" class="space-y-6">
      
      <div>
        <label class="block text-sm font-semibold text-white mb-2">Seleccionar Receptor</label>
        <select 
          v-model="receptorId"
          class="w-full bg-[#141414] border border-red-600 text-white text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3 appearance-none"
          required
        >
          <option value="" disabled selected>Selecciona un usuario</option>
          <option 
            v-for="emp in listaEmpleados" 
            :key="emp.id" 
            :value="emp.id"
          >
            {{ emp.nombre }} - {{ emp.cedula }}
          </option>
        </select>
      </div>

      <div>
        <input 
          type="text" 
          v-model="asunto"
          placeholder="Asunto"
          class="w-full bg-[#0a0a0a] border border-gray-800 text-white text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3"
          required
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-500 mb-2">Fecha del Documento</label>
        <input 
          type="date" 
          v-model="fecha"
          class="w-full bg-white text-black text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3"
          required
        >
      </div>

      <div>
        <textarea 
          v-model="descripcion"
          placeholder="Descripción del memorándum..."
          rows="6"
          class="w-full bg-[#2a2a2a] border border-gray-600 text-gray-300 text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3 resize-none"
          required
        ></textarea>
      </div>

      <div class="flex items-center">
        <input 
          type="checkbox" 
          v-model="adjuntarArchivos"
          id="adjuntos"
          class="w-4 h-4 text-red-600 bg-[#141414] border-gray-600 rounded focus:ring-red-500 focus:ring-2"
        >
        <label for="adjuntos" class="ml-2 text-sm font-medium text-white">¿Desea adjuntar archivos?</label>
      </div>

      <div class="pt-2">
        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="bg-[#e52323] hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2.5 px-6 rounded-md transition-colors"
        >
          {{ isSubmitting ? 'Procesando...' : 'Crear Memorándum' }}
        </button>
      </div>

    </form>
  </div>
</template>