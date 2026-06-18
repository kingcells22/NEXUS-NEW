<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';

// 1. Le decimos a TypeScript exactamente qué datos trae cada usuario
interface UsuarioListado {
  cedula: string;
  nombres_apellidos: string;
  fecha_ingreso: string;
  correo: string;
  estado: boolean;
  tiene_cuenta: boolean;
}

// 2. Aplicamos la interfaz al ref para que desaparezcan los errores rojos
const usuarios = ref<UsuarioListado[]>([]);
const busqueda = ref('');
const cargando = ref(true);
const miRol = ref(''); // <--- NUEVA VARIABLE

const obtenerUsuarios = async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    
    // Capturamos el rol de quien está viendo la tabla
    const meResponse = await fetch('http://127.0.0.1:8000/api/me', { headers: { 'Authorization': `Bearer ${token}` } });
    if(meResponse.ok) {
      const meData = await meResponse.json();
      miRol.value = meData.rol;
    }

    const response = await fetch('http://127.0.0.1:8000/api/admin/usuarios', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      usuarios.value = await response.json();
    } else {
      alert("Error al cargar la lista de usuarios. Verifica tus permisos.");
    }
  } catch (error) {
    console.error("Error de red:", error);
  } finally {
    cargando.value = false;
  }
};

const alternarEstadoUsuario = async (cedula: string) => {
  if (!confirm(`¿Estás seguro de que deseas modificar el estado del usuario con cédula ${cedula}?`)) return;

  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    const response = await fetch(`http://127.0.0.1:8000/api/admin/usuarios/${cedula}/deshabilitar`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      alert("Estado del usuario actualizado correctamente.");
      obtenerUsuarios(); // Recargamos la tabla
    } else {
      const errorData = await response.json();
      alert(errorData.detail || "Error al actualizar el usuario.");
    }
  } catch (error) {
    console.error(error);
    alert("Error de conexión.");
  }
};

onMounted(() => {
  obtenerUsuarios();
});

// Filtro de búsqueda en tiempo real (TS ya no se quejará aquí)
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u => 
    u.nombres_apellidos.toLowerCase().includes(busqueda.value.toLowerCase()) ||
    u.cedula.includes(busqueda.value)
  );
});
</script>

<template>
  <div class="h-full flex flex-col space-y-4">
    
    <div class="flex items-center justify-between">
      <router-link to="/dashboard" class="inline-flex items-center gap-2 text-gray-400 hover:text-red-500 transition-colors font-medium text-sm bg-[#141414] border border-gray-800 px-4 py-2 rounded-md hover:bg-gray-900">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Volver al Inicio
      </router-link>

      <div class="text-right">
        <h2 class="text-2xl font-bold text-white mb-1">Usuarios del sistema</h2>
        <p class="text-sm text-gray-500">Gestión de Accesos y Credenciales</p>
      </div>
    </div>

    <div class="bg-[#0a0a0a] border border-gray-800 rounded-lg shadow-xl flex-1 flex flex-col overflow-hidden">
      
      <div class="p-4 border-b border-gray-800">
        <input 
          type="text" 
          v-model="busqueda"
          placeholder="Buscar usuarios por nombre o cédula..." 
          class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
        >
      </div>

      <div class="flex-1 overflow-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-[#111] text-xs uppercase text-gray-500 sticky top-0 z-10">
            <tr>
              <th class="px-6 py-4 font-semibold border-b border-gray-800">Cédula ↓↑</th>
              <th class="px-6 py-4 font-semibold border-b border-gray-800">Nombres y Apellidos ↓↑</th>
              <th class="px-6 py-4 font-semibold border-b border-gray-800">Fecha de Ingreso ↓↑</th>
              <th class="px-6 py-4 font-semibold border-b border-gray-800">Correo ↓↑</th>
              <th class="px-6 py-4 font-semibold border-b border-gray-800 text-center">Acciones</th>
            </tr>
          </thead>
          
          <tbody class="text-sm divide-y divide-gray-800/50">
            <tr v-if="cargando">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">Cargando base de datos del personal...</td>
            </tr>
            <tr v-else-if="usuariosFiltrados.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">No se encontraron usuarios.</td>
            </tr>
            <tr 
              v-else 
              v-for="user in usuariosFiltrados" 
              :key="user.cedula"
              class="hover:bg-gray-900/50 transition-colors"
              :class="{'opacity-50': !user.estado && user.tiene_cuenta}"
            >
              <td class="px-6 py-4 text-gray-300">{{ user.cedula }}</td>
              <td class="px-6 py-4 text-gray-300 font-medium">{{ user.nombres_apellidos }}</td>
              <td class="px-6 py-4 text-gray-400">{{ user.fecha_ingreso }}</td>
              <td class="px-6 py-4 text-gray-400">{{ user.correo }}</td>
              <td class="px-6 py-4">
                
                <div v-if="['ADMIN USERS', 'ADMIN GLOBAL'].includes(miRol)" class="flex items-center justify-center gap-4">
                  <button 
                    v-if="user.tiene_cuenta"
                    @click="alternarEstadoUsuario(user.cedula)"
                    class="text-xs font-bold px-3 py-1.5 rounded transition-colors min-w-[90px]"
                    :class="user.estado ? 'bg-red-900/30 text-red-500 hover:bg-red-600 hover:text-white border border-red-900/50' : 'bg-green-900/30 text-green-500 hover:bg-green-600 hover:text-white border border-green-900/50'"
                  >
                    {{ user.estado ? 'Deshabilitar' : 'Habilitar' }}
                  </button>
                  <span v-else class="text-xs text-gray-600 italic border border-gray-800 px-3 py-1.5 rounded bg-gray-900/20">
                    Sin registrar
                  </span>

                  <button class="text-xs font-bold text-red-700 hover:text-red-500 transition-colors">
                    Eliminar
                  </button>
                </div>

                <div v-else class="flex items-center justify-center gap-4">
                  <span v-if="!user.tiene_cuenta" class="text-xs text-gray-600 italic border border-gray-800 px-3 py-1.5 rounded bg-gray-900/20">Sin registrar</span>
                  <span v-else-if="user.estado" class="text-xs text-green-500 font-bold bg-green-900/20 px-3 py-1.5 rounded border border-green-900/50">Activo</span>
                  <span v-else class="text-xs text-red-500 font-bold bg-red-900/20 px-3 py-1.5 rounded border border-red-900/50">Inactivo</span>
                </div>
                
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="p-4 border-t border-gray-800 flex items-center justify-between bg-[#111]">
        <button class="px-4 py-2 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-800 transition-colors">Anterior</button>
        <span class="text-sm text-gray-300 font-medium">Página 1 de 1</span>
        <button class="px-4 py-2 border border-gray-700 rounded text-sm text-gray-400 hover:bg-gray-800 transition-colors">Siguiente</button>
      </div>
    </div>
  </div>
</template>