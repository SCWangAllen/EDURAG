<template>
  <div class="mb-6 border-b-2 border-gray-200">
    <div class="flex gap-2 overflow-x-auto pb-2 [&::-webkit-scrollbar]:h-1 [&::-webkit-scrollbar-track]:bg-gray-100 [&::-webkit-scrollbar-track]:rounded-sm [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-thumb]:rounded-sm [&::-webkit-scrollbar-thumb:hover]:bg-gray-400">
      <button
        v-for="typeInfo in types"
        :key="typeInfo.type"
        @click="selectType(typeInfo.type)"
        class="shrink-0 flex items-center gap-2 px-5 py-3 border-x border-t rounded-t-lg cursor-pointer transition-all duration-200 text-sm font-medium relative"
        :class="modelValue === typeInfo.type
          ? 'bg-white text-gray-900 border-x-primary-500 border-t-primary-500 border-b-2 border-b-white -mb-0.5 shadow-[0_-2px_4px_rgba(0,0,0,0.05)]'
          : 'bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-700'"
      >
        <span class="text-lg">{{ getTypeIcon(typeInfo.type) }}</span>
        <span class="font-semibold">{{ getTypeName(typeInfo.type) }}</span>
        <span
          v-if="stats[typeInfo.type]"
          class="flex items-center gap-1 text-xs ml-2 px-2 py-1 rounded"
          :class="modelValue === typeInfo.type ? 'bg-primary-100' : 'bg-gray-200'"
        >
          <!-- 自選模式：只顯示 已選/目標 -->
          <span class="text-emerald-600 font-bold">{{ stats[typeInfo.type].selected }}</span>
          <span class="text-gray-500">/ {{ typeInfo.count }}</span>
        </span>
        <span
          v-else
          class="flex items-center gap-1 text-xs ml-2 px-2 py-1 rounded text-gray-400"
          :class="modelValue === typeInfo.type ? 'bg-primary-100' : 'bg-gray-100'"
        >
          <span class="text-gray-500">0 / {{ typeInfo.count }}</span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '../../composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  types: {
    type: Array,
    required: true
  },
  stats: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const selectType = (type) => {
  emit('update:modelValue', type)
}

const getTypeName = (type) => {
  return t(`generate.${type}`) || type
}

const getTypeIcon = (type) => {
  const icons = {
    single_choice: '📝',
    cloze: '✏️',
    true_false: '✓✗',
    short_answer: '💬',
    matching: '🔗',
    sequence: '🔢',
    enumeration: '📋',
    diagram_question: '🖼️'
  }
  return icons[type] || '❓'
}
</script>
