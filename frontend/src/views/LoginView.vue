<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserAuthForm from '../components/UserAuthForm.vue' // Importamos el componente recién creado

const router = useRouter()

onMounted(() => {
  // Lógica futura de protección de rutas
})
</script>

<template>
  <div class="container relative flex h-screen flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
    
    <div class="relative hidden h-full flex-col p-10 text-white lg:flex ml-5">
      <div class="absolute inset-0 rounded-3xl bg-primary my-5 mx-2"></div>
      <div class="relative z-20 flex items-center text-lg font-medium gap-4">
        <img src="/logo-fiidt-white.png" alt="Logo FIIDT" class="w-auto h-auto" style="width: 3vw;" />
        Nexus
      </div>
      <div class="relative z-20 mt-auto w-full p-10 flex justify-center">
        <img src="/folder.svg" alt="Ilustración Documentos" class="max-w-full h-auto" />
      </div>
      <div class="relative z-20 mt-auto">
        <blockquote class="space-y-2">
          <p class="text-lg">
            &ldquo;La capacidad de aprender y cambiar es lo que nos hace humanos.&rdquo;
          </p>
          <footer class="text-sm">- Alan Turing</footer>
        </blockquote>
      </div>
    </div>

    <div class="lg:p-8">
      <div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div class="flex flex-col space-y-2 text-center">
          <div class="flex justify-center">
            <img src="/logo-fiidt.png" alt="Logo FIIIDT" class="w-auto h-auto text-center" style="width: 40vw; max-width: 200px;" />
          </div>
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-primary">Nexus</h1>
            <p class="text-md text-muted-foreground">Iniciar sesión</p>
          </div>
        </div>
        
        <UserAuthForm />
        
      </div>
    </div>
  </div>
</template>