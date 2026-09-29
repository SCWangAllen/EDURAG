<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Overlay -->
      <div class="absolute inset-0 bg-black/50" @click="closable && handleClose()" />

      <!-- Panel -->
      <div
        :class="[
          'relative bg-white rounded-lg shadow-modal w-full max-h-[90vh] flex flex-col',
          sizeClasses
        ]"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <slot name="header">
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
          </slot>
          <button
            v-if="closable"
            type="button"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
            @click="handleClose"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <slot />
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg', 'xl', '2xl'].includes(v)
  },
  closable: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'close'])

const sizeClasses = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  '2xl': 'max-w-6xl'
}[props.size]))

const handleClose = () => {
  emit('update:modelValue', false)
  emit('close')
}

// 用 document 層級監聽 Esc,而非掛在 modal 內的 div:Teleport 後的 modal 是 body 的
// 子節點而非觸發按鈕的祖先節點,若焦點還停在觸發按鈕上(常見情況),掛在內部 div 上的
// @keydown.esc 永遠收不到事件冒泡,導致「按 Esc 關閉」失效。
const handleKeydown = (event) => {
  if (event.key === 'Escape' && props.closable) {
    handleClose()
  }
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeydown)
    } else {
      document.removeEventListener('keydown', handleKeydown)
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
