<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth.store";

const router = useRouter();
const authStore = useAuthStore();

// Estados para los menús y la interfaz
const memoDesplegable = ref(false);
const perfilDesplegable = ref(false);
const isSidebarOpen = ref(true); // <--- Nuevo estado para ocultar el panel

// Estado para el Tema (Modo Oscuro / Claro)
const isDarkMode = ref(true);

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
};

// Estado reactivo para la data del usuario
const usuarioActual = ref({
  nombres_apellidos: "Cargando...",
  correo: "Buscando datos...",
  inicial: "?",
  rol: "USER NORMAL" // <--- Agregamos el rol para poder leerlo
});

onMounted(async () => {
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    
    if (token) {
      const response = await fetch('http://127.0.0.1:8000/api/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        usuarioActual.value.nombres_apellidos = data.nombres_apellidos;
        usuarioActual.value.correo = data.correo;
        usuarioActual.value.inicial = data.nombres_apellidos.charAt(0).toUpperCase();
        
        // ¡CAPTURAMOS EL ROL DEL BACKEND!
        usuarioActual.value.rol = data.rol;
      } else {
        console.error("Error de autorización. Token inválido o expirado.");
        usuarioActual.value.nombres_apellidos = "Sesión Expirada";
        usuarioActual.value.inicial = "X";
      }
    } else {
      console.warn("No se encontró ningún token en el LocalStorage.");
      usuarioActual.value.nombres_apellidos = "Usuario Desconocido";
      usuarioActual.value.correo = "Falta Token de Sesión";
    }
  } catch (error) {
    console.error("Error de conexión al cargar perfil:", error);
    usuarioActual.value.nombres_apellidos = "Error de Conexión";
  }
});

const logout = () => {
  authStore.logout();
  router.push("/");
};
</script>

<template>
  <div 
    class="min-h-screen flex transition-colors duration-300"
    :class="isDarkMode ? 'bg-[#0a0a0a] text-white' : 'bg-gray-50 text-gray-900'"
  >
    <aside 
      v-show="isSidebarOpen"
      class="w-64 border-r flex flex-col justify-between transition-all duration-300 overflow-y-auto"
      :class="isDarkMode ? 'bg-[#0a0a0a] border-gray-800' : 'bg-white border-gray-200'"
    >
      <div>
        <div class="p-6 pb-2 flex items-center gap-4">
          <img src="/logo-fiidt.png" alt="Logo FIIIDT" class="h-24 w-auto" />
          <span class="text-2xl font-bold text-red-600 mt-2">Nexus</span>
        </div>

        <nav class="px-4 space-y-2 mt-6">
          <router-link to="/dashboard" class="flex items-center gap-3 bg-red-600 text-white px-4 py-2 rounded-md font-medium shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
            Panel Administrativo
          </router-link>

          <div class="pt-6 pb-2">
            <p class="text-xs font-semibold uppercase tracking-wider" :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">Reportes</p>
          </div>

          <div>
            <button 
              @click="memoDesplegable = !memoDesplegable" 
              class="w-full flex items-center justify-between px-4 py-2 rounded-md transition-colors"
              :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                Memorandum
              </div>
              <span class="text-[10px] transition-transform" :class="memoDesplegable ? 'rotate-180' : ''">▲</span>
            </button>
            <div 
              v-if="memoDesplegable" 
              class="mt-1 py-1 pl-12 text-sm space-y-3"
            >
              <router-link to="/dashboard/emitidos" class="block font-bold transition-colors" :class="isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-red-600'">
                <span class="mr-1 text-gray-500">•</span> Emitidos
              </router-link>
              <a href="#" class="block font-bold transition-colors" :class="isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-red-600'">
                <span class="mr-1 text-gray-500">•</span> Recibidos
              </a>
            </div>
          </div>

          <a href="#" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Oficio
          </a>
          <a href="#" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Punto de Informacion
          </a>
          <a href="#" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Punto de Cuenta
          </a>

          <div v-if="['ADMIN USERS', 'ADMIN GRAL', 'ADMIN GLOBAL'].includes(usuarioActual.rol)">
            <div class="pt-6 pb-2">
              <p class="text-xs font-semibold uppercase tracking-wider" :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">Administrador</p>
            </div>
            
            <router-link to="/dashboard/usuarios" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
              Ver Usuarios
            </router-link>

            <a href="#" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
              Activar Usuarios
            </a>

            <a href="#" class="flex items-center gap-3 px-4 py-2 rounded-md transition-colors" :class="isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
              Crear Usuarios
            </a>
          </div>
          </nav>
      </div>

      <div class="p-4">
        <button @click="logout" class="flex items-center justify-center gap-2 w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors shadow-sm">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          Cerrar sesión
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col h-screen overflow-hidden relative" :class="isDarkMode ? 'bg-[#0a0a0a]' : 'bg-gray-50'">
      
      <header 
        class="h-16 border-b flex items-center justify-between px-6 relative transition-colors duration-300 z-10"
        :class="isDarkMode ? 'bg-[#0a0a0a] border-gray-800' : 'bg-white border-gray-200'"
      >
        <div class="flex items-center gap-4">
          <button 
            @click="isSidebarOpen = !isSidebarOpen" 
            class="p-1.5 rounded-md transition-colors border"
            :class="isDarkMode ? 'border-gray-700 bg-[#141414] text-gray-400 hover:text-white hover:bg-gray-800' : 'border-gray-300 bg-gray-50 text-gray-600 hover:bg-gray-200'"
          >
            <svg v-if="isSidebarOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
          <h1 class="text-xl font-bold" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
            Panel Administrativo
          </h1>
        </div>
        
        <div class="flex items-center gap-5">
          <button @click="toggleTheme" class="focus:outline-none transition-colors p-1 rounded-md" :class="isDarkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'" title="Cambiar tema">
            <svg v-if="isDarkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
          </button>

          <div class="relative">
            <button 
              @click="perfilDesplegable = !perfilDesplegable"
              class="w-9 h-9 rounded-full border flex items-center justify-center text-sm font-bold focus:outline-none transition-colors select-none shadow-sm"
              :class="isDarkMode ? 'border-gray-600 text-white hover:border-gray-400 bg-gray-800' : 'border-gray-300 text-red-600 bg-gray-100 hover:bg-gray-200'"
            >
              {{ usuarioActual.inicial }}
            </button>

            <div 
              v-if="perfilDesplegable" 
              class="absolute right-0 mt-3 w-64 border rounded-md shadow-2xl z-50 overflow-hidden transition-colors"
              :class="isDarkMode ? 'bg-[#141414] border-gray-800' : 'bg-white border-gray-200'"
            >
              <div class="px-4 py-3 border-b" :class="isDarkMode ? 'border-gray-800 bg-[#1a1a1a]' : 'border-gray-100 bg-gray-50'">
                <p class="text-sm font-bold uppercase tracking-wide truncate" :class="isDarkMode ? 'text-white' : 'text-gray-800'">
                  {{ usuarioActual.nombres_apellidos }}
                </p>
                <p class="text-xs truncate mt-0.5" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                  {{ usuarioActual.correo }}
                </p>
              </div>
              <div class="py-1">
                <button @click="router.push('/recuperar-password')" class="w-full text-left px-4 py-2.5 text-sm flex items-center gap-3 transition-colors" :class="isDarkMode ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'">
                  <svg class="w-4 h-4" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                  Cambiar contraseña
                </button>
                <button 
                  @click="logout" 
                  class="w-full text-left px-4 py-2.5 text-sm flex items-center gap-3 transition-colors"
                  :class="isDarkMode ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-red-600 hover:bg-red-50 hover:text-red-700'"
                >
                  <svg class="w-4 h-4" :class="isDarkMode ? 'text-gray-400' : 'text-red-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-auto relative z-0 flex flex-col">
        
        <div class="px-8 pt-6 pb-2 text-sm font-medium" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
          Inicio <span class="mx-2">></span>
          <span :class="isDarkMode ? 'text-white' : 'text-gray-900'">Panel Administrativo</span>
        </div>

        <div class="p-8 pt-4 flex-1 relative">
          <router-view></router-view>
          
          <div v-if="$route.name === 'dashboard'" class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-50">
            <img src="/placeholder.png" alt="Dashboard Illustration" class="max-w-2xl" />
          </div>
        </div>

        <footer class="p-4 text-xs text-center border-t transition-colors mt-auto" :class="isDarkMode ? 'text-gray-600 border-gray-800 bg-[#0a0a0a]' : 'text-gray-500 border-gray-200 bg-gray-50'">
          © 2026 | Nexus Gestión Documental | Desarrollado por el equipo del CSICE.
        </footer>
      </div>

    </main>
  </div>
</template>