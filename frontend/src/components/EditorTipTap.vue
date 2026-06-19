<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
  ],
  editorProps: {
    attributes: {
      // Estilos para el área de escritura
      class: 'focus:outline-none min-h-[250px] p-4 text-gray-300',
    },
  },
  onUpdate: () => {
    // Cada vez que el usuario escribe, enviamos el HTML al componente padre
    emit('update:modelValue', editor.value?.getHTML())
  },
})

// Sincronizar cambios si el valor viene de afuera (ej. limpiar formulario)
watch(() => props.modelValue, (value) => {
  const isSame = editor.value?.getHTML() === value
  if (editor.value && !isSame) {
    editor.value.commands.setContent(value, false)
  }
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<template>
  <div class="border border-gray-700 rounded-md overflow-hidden bg-[#141414] focus-within:border-red-500 transition-colors shadow-inner">
    
    <div v-if="editor" class="bg-[#0a0a0a] border-b border-gray-800 p-2 flex items-center gap-1 flex-wrap">
      
      <button @click.prevent="editor.chain().focus().toggleBold().run()" :class="{ 'bg-gray-700 text-white': editor.isActive('bold'), 'text-gray-400 hover:bg-gray-800 hover:text-white': !editor.isActive('bold') }" class="p-2 rounded transition-colors" title="Negrita">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 11h4.5a2.5 2.5 0 1 0 0-5H8v5Zm0 2v5h5.25a2.75 2.75 0 1 0 0-5.5H8Zm-2-9h8.25a4.5 4.5 0 0 1 2.227 8.39A4.75 4.75 0 0 1 13.25 20H6V4Z"></path></svg>
      </button>

      <button @click.prevent="editor.chain().focus().toggleItalic().run()" :class="{ 'bg-gray-700 text-white': editor.isActive('italic'), 'text-gray-400 hover:bg-gray-800 hover:text-white': !editor.isActive('italic') }" class="p-2 rounded transition-colors" title="Cursiva">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M15 4h5v2h-2.866l-4.667 12H15v2H5v-2h2.866l4.667-12H10V4h5Z"></path></svg>
      </button>

      <div class="w-px h-6 bg-gray-700 mx-2"></div>

      <button @click.prevent="editor.chain().focus().toggleBulletList().run()" :class="{ 'bg-gray-700 text-white': editor.isActive('bulletList'), 'text-gray-400 hover:bg-gray-800 hover:text-white': !editor.isActive('bulletList') }" class="p-2 rounded transition-colors" title="Viñetas">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 6h11v2H8V6Zm0 5h11v2H8v-2Zm0 5h11v2H8v-2ZM5 7a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm0 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm0 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>
      </button>

      <button @click.prevent="editor.chain().focus().toggleOrderedList().run()" :class="{ 'bg-gray-700 text-white': editor.isActive('orderedList'), 'text-gray-400 hover:bg-gray-800 hover:text-white': !editor.isActive('orderedList') }" class="p-2 rounded transition-colors" title="Lista Numerada">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M10 6h9v2h-9V6Zm0 5h9v2h-9v-2Zm0 5h9v2h-9v-2Zm-3-1v2H5v-2h2Zm0-5v2H5v-2h2Zm0-5v2H5V6h2Z"></path></svg>
      </button>

    </div>

    <editor-content :editor="editor" class="ProseMirror-wrapper" />
    
  </div>
</template>

<style>
/* Pequeño ajuste para que las listas se vean bien y el placeholder desaparezca */
.ProseMirror ul { list-style-type: disc; padding-left: 1.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }
.ProseMirror ol { list-style-type: decimal; padding-left: 1.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }
.ProseMirror p { margin-bottom: 0.5rem; }
.ProseMirror strong { font-weight: bold; color: white; }
</style>