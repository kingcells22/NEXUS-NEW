<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import EditorTipTap from '../components/EditorTipTap.vue'; 

const router = useRouter();

const receptorId = ref('');
const emisorId = ref<number | null>(null); 
const asunto = ref('');
const fecha = ref(new Date().toISOString().split('T')[0]); 
const descripcion = ref('');
const adjuntarArchivos = ref(false);

// NUEVO: Estado para guardar el archivo que elija el usuario
const archivoSeleccionado = ref<File | null>(null);

const isSubmitting = ref(false);
const listaEmpleados = ref<Array<{id: number, nombre: string, cedula: string}>>([]);

onMounted(async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    
    const responseEmpleados = await fetch('http://127.0.0.1:8000/api/empleados', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (responseEmpleados.ok) listaEmpleados.value = await responseEmpleados.json();

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

// NUEVO: Función para capturar el archivo cuando el usuario lo selecciona
const manejarArchivo = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    archivoSeleccionado.value = target.files[0];
  }
};

const procesarFormulario = async () => {
    if (!emisorId.value) {
      alert("Error: No se pudo identificar tu perfil de usuario. Recarga la página.");
      return;
    }
    if (!descripcion.value || descripcion.value === '<p></p>') {
      alert("Por favor, redacte el contenido del documento.");
      return;
    }
    if (adjuntarArchivos.value && !archivoSeleccionado.value) {
      alert("Marcaste la casilla de anexos, por favor selecciona un archivo.");
      return;
    }

    isSubmitting.value = true;
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');

    try {
      const formData = new FormData();
      formData.append('emisor_id', String(emisorId.value));
      formData.append('receptor_id', String(receptorId.value));
      formData.append('asunto', asunto.value);
      formData.append('fecha', fecha.value);
      formData.append('descripcion', descripcion.value);
      formData.append('anexos', adjuntarArchivos.value ? "Sí" : "No");
      
      if (adjuntarArchivos.value && archivoSeleccionado.value) {
        formData.append('archivo', archivoSeleccionado.value);
      }

      const memoResponse = await fetch('http://127.0.0.1:8000/api/memorandums', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      // === AQUÍ SE CORRIGE ===
      if (!memoResponse.ok) {
        const errorData = await memoResponse.json();
        alert("Error de validación FastAPI: " + JSON.stringify(errorData.detail));
        throw new Error("El servidor rechazó el documento.");
      }
      // =======================
      
      const memoGenerado = await memoResponse.json();
      const correlativo = memoGenerado.numero_documento;
      
      alert(`¡Memorándum ${correlativo} guardado exitosamente!`);
      router.push('/dashboard/emitidos');

    } catch (error: any) {
      console.error(error);
      alert("Ocurrió un error de conexión con el servidor o validación.");
    } finally {
      isSubmitting.value = false;
    }
};
</script>

<template>
  <div class="max-w-3xl text-gray-200 pb-10">
    <h2 class="text-xl font-bold text-white mb-6">Nuevo Memorándum</h2>

    <form @submit.prevent="procesarFormulario" class="space-y-6">
      
      <div>
        <label class="block text-sm font-semibold text-white mb-2">Seleccionar Receptor</label>
        <select v-model="receptorId" class="w-full bg-[#141414] border border-red-600 text-white text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3 appearance-none" required>
          <option value="" disabled selected>Selecciona un usuario</option>
          <option v-for="emp in listaEmpleados" :key="emp.id" :value="emp.id">
            {{ emp.nombre }} - {{ emp.cedula }}
          </option>
        </select>
      </div>

      <div>
        <input type="text" v-model="asunto" placeholder="Asunto" class="w-full bg-[#0a0a0a] border border-gray-800 text-white text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3" required>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-500 mb-2">Fecha del Documento</label>
        <input type="date" v-model="fecha" class="w-full bg-white text-black text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3" required>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-500 mb-2">Descripción del Memorándum</label>
        <EditorTipTap v-model="descripcion" />
      </div>

      <div class="flex items-center">
        <input type="checkbox" v-model="adjuntarArchivos" id="adjuntos" class="w-4 h-4 text-red-600 bg-[#141414] border-gray-600 rounded focus:ring-red-500 focus:ring-2">
        <label for="adjuntos" class="ml-2 text-sm font-medium text-white">¿Desea adjuntar archivos de soporte?</label>
      </div>

      <div v-if="adjuntarArchivos" class="mt-3 p-4 bg-[#1a1a1a] border border-gray-700 rounded-md transition-all">
        <label class="block text-sm font-medium text-gray-400 mb-2">Seleccione el archivo a adjuntar (PDF, JPG, PNG...)</label>
        <input
          type="file"
          @change="manejarArchivo"
          class="block w-full text-sm text-gray-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-red-600 file:text-white hover:file:bg-red-700 transition-colors cursor-pointer"
          required
        >
      </div>

      <div class="pt-4">
        <button type="submit" :disabled="isSubmitting" class="w-full sm:w-auto bg-[#e52323] hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2.5 px-8 rounded-md transition-colors shadow-lg">
          {{ isSubmitting ? 'Procesando...' : 'Crear Memorándum' }}
        </button>
      </div>

    </form>
  </div>
</template>