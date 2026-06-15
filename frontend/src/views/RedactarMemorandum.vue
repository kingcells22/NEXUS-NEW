<template>
  <div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md mt-10">
    <div class="flex items-center justify-between mb-6 border-b pb-4">
      <h2 class="text-2xl font-bold text-gray-800">
        Redactar Memorándum Oficial
      </h2>
      <span
        class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full"
      >
        NUEVO
      </span>
    </div>

    <div v-if="cargandoEmpleados" class="text-center py-4 text-gray-500">
      Cargando lista de personal...
    </div>

    <form v-else @submit.prevent="generarDocumento" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700">Asunto</label>
        <input
          v-model="form.asunto"
          type="text"
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-gray-50"
          placeholder="Ej: Solicitud de revisión de equipos..."
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700"
            >De (Remitente)</label
          >
          <select
            v-model="form.emisor_id"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-gray-50"
          >
            <option value="" disabled>Seleccione un remitente...</option>
            <option v-for="emp in listaEmpleados" :key="emp.id" :value="emp.id">
              {{ emp.nombre }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700"
            >Para (Destinatario)</label
          >
          <select
            v-model="form.receptor_id"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-gray-50"
          >
            <option value="" disabled>Seleccione un destinatario...</option>
            <option v-for="emp in listaEmpleados" :key="emp.id" :value="emp.id">
              {{ emp.nombre }}
            </option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700"
          >Cuerpo del Memorándum</label
        >
        <textarea
          v-model="form.descripcion"
          rows="8"
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-gray-50"
          placeholder="Redacte el contenido oficial aquí..."
        ></textarea>
      </div>

      <div class="flex items-center">
        <input
          v-model="form.anexos"
          type="checkbox"
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label class="ml-2 block text-sm text-gray-900 font-medium">
          Este documento incluye anexos físicos/digitales
        </label>
      </div>

      <div class="flex justify-end space-x-3 pt-6 border-t mt-6">
        <button
          type="button"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm"
        >
          Cancelar
        </button>
        <button
          type="submit"
          :disabled="guardando"
          class="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-800 hover:bg-blue-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-800 disabled:bg-gray-400"
        >
          {{ guardando ? "Procesando..." : "Generar Documento" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const form = ref({
  asunto: "",
  descripcion: "",
  fecha: new Date().toISOString(),
  emisor_id: "",
  receptor_id: "",
  anexos: false,
  centro: "Sede Principal",
});

const listaEmpleados = ref([]);
const cargandoEmpleados = ref(true);
const guardando = ref(false);

onMounted(async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/empleados");
    if (response.ok) {
      listaEmpleados.value = await response.json();
    }
  } catch (error) {
    console.error("Error cargando empleados:", error);
  } finally {
    cargandoEmpleados.value = false;
  }
});

const generarDocumento = async () => {
  guardando.value = true;
  try {
    const response = await fetch("http://127.0.0.1:8000/api/memorandums", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form.value),
    });

    if (response.ok) {
      const data = await response.json();
      alert(
        `¡Documento Generado Exitosamente!\nCorrelativo Oficial: ${data.numero_documento}\nEstatus: ${data.status}`,
      );

      // Limpiamos el formulario
      form.value.asunto = "";
      form.value.descripcion = "";
      form.value.emisor_id = "";
      form.value.receptor_id = "";
      form.value.anexos = false;
    } else {
      const errorData = await response.json();
      alert("Error en el servidor: " + JSON.stringify(errorData));
    }
  } catch (error) {
    console.error("Error de red:", error);
    alert("No se pudo conectar con el servidor.");
  } finally {
    guardando.value = false;
  }
};
</script>
