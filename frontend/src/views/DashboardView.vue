<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground p-10 flex flex-col items-center justify-center">
    <h1 class="text-4xl font-bold text-primary mb-4">¡Bienvenido a NEXUS!</h1>
    <p class="text-lg text-muted-foreground mb-8">Has iniciado sesión correctamente como Administrador.</p>
    
    <button @click="logout" class="bg-destructive text-destructive-foreground px-4 py-2 rounded-md hover:bg-destructive/90 transition-colors">
      Cerrar Sesión
    </button>
  </div>
</template>