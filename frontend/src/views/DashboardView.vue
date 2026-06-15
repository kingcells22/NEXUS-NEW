<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth.store";

const router = useRouter();
const authStore = useAuthStore();

const logout = () => {
  authStore.logout();
  router.push("/");
};
</script>

<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white flex">
    <aside
      class="w-64 bg-[#141414] border-r border-gray-800 flex flex-col justify-between"
    >
      <div>
        <div class="p-6 flex items-center gap-3">
          <img src="/logo-fiidt-white.png" alt="Logo" class="h-8 w-auto" />
          <span class="text-xl font-bold text-red-600">Nexus</span>
        </div>

        <nav class="px-4 space-y-2 mt-4">
          <a
            href="#"
            class="flex items-center gap-3 bg-red-600 text-white px-4 py-2 rounded-md font-medium"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
              ></path>
            </svg>
            Panel Administrativo
          </a>

          <div class="pt-6 pb-2">
            <p
              class="text-xs font-semibold text-gray-500 uppercase tracking-wider"
            >
              Reportes
            </p>
          </div>

          <router-link
            to="/dashboard/redactar-memo"
            class="flex items-center justify-between text-gray-300 hover:text-white hover:bg-gray-800 px-4 py-2 rounded-md transition-colors"
          >
            <div class="flex items-center gap-3">
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              Memorandum
            </div>
          </router-link>

          <a
            href="#"
            class="flex items-center gap-3 text-gray-300 hover:text-white hover:bg-gray-800 px-4 py-2 rounded-md transition-colors"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            Oficio
          </a>
          <a
            href="#"
            class="flex items-center gap-3 text-gray-300 hover:text-white hover:bg-gray-800 px-4 py-2 rounded-md transition-colors"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            Punto de Informacion
          </a>
          <a
            href="#"
            class="flex items-center gap-3 text-gray-300 hover:text-white hover:bg-gray-800 px-4 py-2 rounded-md transition-colors"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            Punto de Cuenta
          </a>
        </nav>
      </div>

      <div class="p-4">
        <button
          @click="logout"
          class="flex items-center justify-center gap-2 w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            ></path>
          </svg>
          Cerrar sesión
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col h-screen overflow-hidden">
      <header
        class="h-16 border-b border-gray-800 flex items-center justify-between px-8 bg-[#0a0a0a]"
      >
        <div class="text-sm text-gray-400">
          Inicio <span class="mx-2">></span>
          <span class="text-white">Panel Administrativo</span>
        </div>
        <div class="flex items-center gap-4">
          <div
            class="w-8 h-8 rounded-full border border-gray-600 flex items-center justify-center text-xs"
          >
            J
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-auto p-8 relative">
        <router-view></router-view>
        <div
          v-if="$route.name === 'dashboard'"
          class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-50"
        >
          <img
            src="/Visionary.png"
            alt="Dashboard Illustration"
            class="max-w-2xl"
          />
        </div>
      </div>

      <footer
        class="p-4 text-xs text-gray-500 text-center border-t border-gray-800"
      >
        © 2026 | Nexus Gestión Documental | Desarrollado por el equipo del
        CSICE.
      </footer>
    </main>
  </div>
</template>
