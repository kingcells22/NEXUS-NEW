<script setup lang="ts">
import { ref, onMounted } from 'vue';

// Estado para guardar los documentos y el loader
const documentos = ref<Array<any>>([]);
const cargando = ref(true);

// Consultar la nueva ruta de recibidos en el backend
const cargarBandeja = async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    const response = await fetch('http://127.0.0.1:8000/api/memorandums/recibidos', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      documentos.value = await response.json();
    } else {
      console.error("Error al obtener la bandeja de recibidos");
    }
  } catch (error) {
    console.error("Error de conexión:", error);
  } finally {
    cargando.value = false;
  }
};

// Función para descargar el PDF
// Función para descargar el PDF
const descargarPDF = async (id: number, correlativo: string) => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    const response = await fetch(`http://127.0.0.1:8000/api/memorandums/${id}/pdf`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error("Error al generar el PDF");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${correlativo}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    // ELIMINAMOS EL ALERT() MOLESTO
    // Solo dejamos un aviso silencioso en la consola por si acaso
    console.warn("Aviso de descarga del navegador:", error);
  }
};

onMounted(() => {
  cargarBandeja();
});
</script>

<template>
  <div class="max-w-6xl mx-auto text-gray-200">
    <h2 class="text-2xl font-bold text-white mb-6 border-b border-gray-700 pb-2">Bandeja de Recibidos</h2>

    <div v-if="cargando" class="text-center py-10 text-gray-400">
      Cargando documentos...
    </div>

    <div v-else-if="documentos.length === 0" class="bg-[#141414] border border-gray-800 rounded-md p-8 text-center text-gray-500">
      No tienes ningún documento en tu bandeja de entrada.
    </div>

    <div v-else class="overflow-x-auto rounded-md border border-gray-700 shadow-lg">
      <table class="w-full text-sm text-left text-gray-300">
        <thead class="text-xs text-white uppercase bg-[#0a0a0a] border-b border-gray-700">
          <tr>
            <th scope="col" class="px-6 py-3">Correlativo</th>
            <th scope="col" class="px-6 py-3">Remitente</th>
            <th scope="col" class="px-6 py-3">Asunto</th>
            <th scope="col" class="px-6 py-3">Fecha</th>
            <th scope="col" class="px-6 py-3 text-center">Estatus</th>
            <th scope="col" class="px-6 py-3 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documentos" :key="doc.id" class="bg-[#141414] border-b border-gray-800 hover:bg-[#1a1a1a] transition-colors">
            <td class="px-6 py-4 font-bold text-white whitespace-nowrap">{{ doc.correlativo }}</td>
            <td class="px-6 py-4">
              <div class="font-medium text-white">{{ doc.remitente }}</div>
              <div class="text-xs text-gray-500">{{ doc.cargo_remitente }}</div>
            </td>
            <td class="px-6 py-4">{{ doc.asunto }}</td>
            <td class="px-6 py-4">{{ doc.fecha }}</td>
            <td class="px-6 py-4 text-center">
              <span class="bg-gray-800 text-gray-300 text-xs font-medium px-2.5 py-0.5 rounded border border-gray-600">
                {{ doc.decision }}
              </span>
            </td>
            <td class="px-6 py-4 text-center">
              <button 
                @click="descargarPDF(doc.id, doc.correlativo)"
                class="text-red-500 hover:text-white border border-red-500 hover:bg-red-600 focus:ring-4 focus:outline-none focus:ring-red-900 font-medium rounded-lg text-xs px-3 py-1.5 text-center transition-colors"
              >
                Ver PDF
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>