/* components/Drawer.vue */
<template>
  <div v-if="open" class="fixed inset-0 bg-black/50 flex items-center justify-end">
    <div class="bg-white w-full max-w-lg h-full p-6 overflow-y-auto">
      <button class="mb-4 text-gray-600" @click="$emit('close')">✕ Close</button>
      <h2 class="text-lg font-semibold mb-4">Relative Context</h2>
      <pre class="whitespace-pre-wrap text-sm">{{ context }}</pre>
    </div>
  </div>
</template>

<script>
import { useEscapeToClose } from '@/composables/useEscapeToClose.js'

export default {
  name: 'Drawer',
  props: {
    open: { type: Boolean, required: true },
    context: { type: String, default: '' }
  },
  emits: ['close'],
  setup(props, { emit }) {
    useEscapeToClose(() => props.open, () => emit('close'))  // Esc 關閉
  }
}
</script>