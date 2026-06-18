<script setup lang="ts">
import { ref } from 'vue';

const isSubmitting = ref(false);

const form = ref({
  cedula: '',
  nombres_apellidos: '',
  fecha_ingreso: '',
  cargo: '',
  centro: '',
  tipo_nomina: '',
  genero: '', // <--- NUEVO
  titulo: ''  // <--- NUEVO
});

const guardarEmpleado = async () => {
  isSubmitting.value = true;
  try {
    const token = localStorage.getItem('nexus_token') || localStorage.getItem('token');
    
    const response = await fetch('http://127.0.0.1:8000/api/admin/empleados', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form.value)
    });

    const data = await response.json();

    if (response.ok) {
      alert("¡Trabajador agregado a la nómina exitosamente!");
      form.value = { cedula: '', nombres_apellidos: '', fecha_ingreso: '', cargo: '', centro: '', tipo_nomina: '', genero: '', titulo: '' };
    } else {
      alert(data.detail || "Error al registrar al trabajador.");
    }
  } catch (error) {
    console.error("Error de conexión:", error);
    alert("Error de conexión con el servidor.");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-4">
    
    <router-link to="/dashboard" class="inline-flex items-center gap-2 text-gray-400 hover:text-red-500 transition-colors font-medium text-sm bg-[#141414] border border-gray-800 px-4 py-2 rounded-md hover:bg-gray-900 w-fit">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      Volver al Inicio
    </router-link>

    <div class="bg-[#0a0a0a] border border-gray-800 rounded-lg shadow-xl p-8">
      <div class="mb-8 border-b border-gray-800 pb-4">
        <h2 class="text-2xl font-bold text-white">Ingreso a Nómina</h2>
        <p class="text-gray-400 mt-1">Registre los datos del nuevo trabajador y su tratamiento profesional para la redacción de documentos.</p>
      </div>

      <form @submit.prevent="guardarEmpleado" class="space-y-6">
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <div class="lg:col-span-1">
            <label class="block text-sm font-semibold text-white mb-2">Cédula de Identidad</label>
            <input type="text" v-model="form.cedula" placeholder="Ej: 20123456" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500">
          </div>
          
          <div class="lg:col-span-2">
            <label class="block text-sm font-semibold text-white mb-2">Nombres y Apellidos</label>
            <input type="text" v-model="form.nombres_apellidos" placeholder="Ej: PÉREZ RODRÍGUEZ, JUAN CARLOS" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500 uppercase">
          </div>

          <div>
            <label class="block text-sm font-semibold text-white mb-2">Género</label>
            <select v-model="form.genero" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500">
              <option value="" disabled>Seleccione...</option>
              <option value="M">Masculino (M)</option>
              <option value="F">Femenino (F)</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold text-white mb-2">Título / Tratamiento</label>
            <select v-model="form.titulo" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500">
              <option value="" disabled>Seleccione...</option>
              <option value="SR.">Señor (Sr.) / Señora (Sra.)</option>
              <option value="CIUDADANO">Ciudadano / Ciudadana</option>
              <option value="ING.">Ingeniero / Ingeniera (Ing.)</option>
              <option value="DR.">Doctor (Dr.) / Doctora (Dra.)</option>
              <option value="LIC.">Licenciado / Licenciada (Lic.)</option>
              <option value="ABG.">Abogado / Abogada (Abg.)</option>
              <option value="TSU.">Técnico Superior (TSU.)</option>
              <option value="MINISTRO">Ministro / Ministra</option>
              <option value="VICEMINISTRO">Viceministro / Viceministra</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold text-white mb-2">Fecha de Ingreso</label>
            <input type="date" v-model="form.fecha_ingreso" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500 [color-scheme:dark]">
          </div>

          <div class="lg:col-span-3">
            <label class="block text-sm font-semibold text-white mb-2">Centro / Oficina de Adscripción</label>
            <input type="text" v-model="form.centro" placeholder="Ej: Centro de Ingeniería Eléctrica y Sistemas" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500 uppercase">
          </div>

          <div class="lg:col-span-2">
            <label class="block text-sm font-semibold text-white mb-2">Cargo</label>
            <input type="text" v-model="form.cargo" placeholder="Ej: INVESTIGADOR" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500 uppercase">
          </div>

          <div>
            <label class="block text-sm font-semibold text-white mb-2">Tipo de Nómina</label>
            <select v-model="form.tipo_nomina" required class="w-full bg-[#141414] border border-gray-700 text-white rounded-md p-3 focus:border-red-500">
              <option value="" disabled>Seleccione...</option>
              <option value="FIJO">Fijo</option>
              <option value="CONTRATADO">Contratado</option>
              <option value="COMISIÓN DE SERVICIO">Comisión de Servicio</option>
              <option value="AD HONOREM">Ad Honorem</option>
              <option value="ALTO NIVEL">Alto Nivel</option>
            </select>
          </div>
        </div>

        <div class="pt-6 border-t border-gray-800 flex justify-end gap-4 mt-8">
          <button type="button" @click="form = { cedula: '', nombres_apellidos: '', fecha_ingreso: '', cargo: '', centro: '', tipo_nomina: '', genero: '', titulo: '' }" class="px-6 py-3 border border-gray-700 text-gray-300 rounded-md hover:bg-gray-800 transition-colors">
            Limpiar
          </button>
          <button type="submit" :disabled="isSubmitting" class="px-6 py-3 bg-red-600 hover:bg-red-500 disabled:bg-red-800 text-white font-bold rounded-md transition-colors shadow-lg">
            {{ isSubmitting ? 'Guardando...' : 'Registrar Trabajador' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>