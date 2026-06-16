<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const documentos = ref<any[]>([]);
const busqueda = ref('');

// Cargar los documentos al montar la vista
onMounted(async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    const response = await fetch('http://127.0.0.1:8000/api/memorandums/emitidos', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      documentos.value = await response.json();
    }
  } catch (error) {
    console.error("Error al cargar la bandeja:", error);
  }
});

// Función para abrir el PDF en una pestaña nueva
const verDocumento = (id: number) => {
  const urlPdf = `http://127.0.0.1:8000/api/memorandums/${id}/pdf`;
  window.open(urlPdf, '_blank');
};

// Filtro simple de búsqueda por Asunto o Correlativo
const documentosFiltrados = computed(() => {
  if (!busqueda.value) return documentos.value;
  return documentos.value.filter(doc => 
    doc.asunto.toLowerCase().includes(busqueda.value.toLowerCase()) || 
    doc.correlativo.toLowerCase().includes(busqueda.value.toLowerCase())
  );
});
</script>

<template>
  <div class="text-gray-200 h-full flex flex-col relative z-10">
    <div class="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
      <div>
        <h2 class="text-2xl font-bold text-white">Memorándums Emitidos</h2>
        <p class="text-sm text-gray-500 mt-1">Bandeja de documentos generados y enviados</p>
      </div>
      
      <button 
        @click="router.push('/dashboard/redactar-memo')" 
        class="bg-[#e52323] hover:bg-red-700 text-white font-bold py-2.5 px-6 rounded-md transition-colors shadow-lg flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        Crear Memorándum
      </button>
    </div>

    <div class="bg-[#141414] border border-gray-800 rounded-lg p-6 flex-1 flex flex-col shadow-2xl overflow-hidden">
      
      <div class="mb-6">
        <input 
          type="text" 
          v-model="busqueda"
          placeholder="Buscar por asunto o número de documento..." 
          class="w-full bg-[#0a0a0a] border border-gray-800 text-white text-sm rounded-md focus:ring-red-500 focus:border-red-500 block p-3"
        >
      </div>

      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left text-sm text-gray-400">
          <thead class="text-xs text-gray-500 uppercase bg-[#1a1a1a] border-b border-gray-800">
            <tr>
              <th scope="col" class="px-4 py-3 font-medium">CORRELATIVO</th>
              <th scope="col" class="px-4 py-3 font-medium">PRESENTADOR</th>
              <th scope="col" class="px-4 py-3 font-medium">CARGO PRESENTADOR</th>
              <th scope="col" class="px-4 py-3 font-medium">ASUNTO</th>
              <th scope="col" class="px-4 py-3 font-medium">DECISIÓN</th>
              <th scope="col" class="px-4 py-3 font-medium">FECHA</th>
              <th scope="col" class="px-4 py-3 font-medium">ANEXOS</th>
              <th scope="col" class="px-4 py-3 font-medium text-center">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="documentosFiltrados.length === 0">
              <td colspan="8" class="px-4 py-8 text-center text-gray-500 bg-[#0a0a0a]">
                No hay documentos registrados en esta bandeja.
              </td>
            </tr>
            
            <tr 
              v-for="doc in documentosFiltrados" 
              :key="doc.id"
              class="border-b border-gray-800 bg-[#0a0a0a] hover:bg-[#1a1a1a] transition-colors"
            >
              <td class="px-4 py-4 font-bold text-white">{{ doc.correlativo }}</td>
              <td class="px-4 py-4">{{ doc.presentador }}</td>
              <td class="px-4 py-4">{{ doc.cargo_presentador }}</td>
              <td class="px-4 py-4 max-w-xs truncate" :title="doc.asunto">{{ doc.asunto }}</td>
              <td class="px-4 py-4">
                <span 
                  class="px-2 py-1 rounded text-xs font-semibold"
                  :class="{
                    'bg-gray-800 text-gray-300': doc.decision === 'CREADO',
                    'bg-yellow-900/50 text-yellow-500': doc.decision === 'REVISIÓN',
                    'bg-green-900/50 text-green-500': doc.decision === 'APROBADO',
                    'bg-red-900/50 text-red-500': doc.decision === 'RECHAZADO'
                  }"
                >
                  {{ doc.decision }}
                </span>
              </td>
              <td class="px-4 py-4">{{ doc.fecha }}</td>
              <td class="px-4 py-4 text-center">{{ doc.anexos }}</td>
              <td class="px-4 py-4">
                <div class="flex items-center justify-center gap-2">
                  <button 
                    @click="verDocumento(doc.id)"
                    class="bg-red-600 hover:bg-red-500 text-white text-xs font-bold py-1.5 px-3 rounded transition-colors"
                  >
                    Ver
                  </button>
                  <button class="bg-[#5c1616] hover:bg-red-900 text-white text-xs font-bold py-1.5 px-3 rounded transition-colors border border-red-900">
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex justify-between items-center mt-4 pt-4 border-t border-gray-800">
        <button class="bg-[#1a1a1a] border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 py-1.5 px-4 rounded text-sm transition-colors">
          Anterior
        </button>
        <span class="text-sm text-gray-500">Página 1 de 1</span>
        <button class="bg-[#1a1a1a] border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 py-1.5 px-4 rounded text-sm transition-colors">
          Siguiente
        </button>
      </div>

    </div>
  </div>
</template>