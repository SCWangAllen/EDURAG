<template>
  <div
    class="grid grid-cols-[80px_1fr_80px_120px_120px_100px_100px] gap-4 p-4 border-b border-gray-100 items-center transition-colors duration-200"
    :class="typeConfig.enabled ? 'bg-white' : 'bg-neutral-50 opacity-60'"
  >
    <!-- 順序 / 拖拽手柄 -->
    <div class="flex items-center gap-2">
      <span class="drag-handle cursor-grab text-xl text-gray-400 select-none active:cursor-grabbing" :title="t('ui.ed_drag_reorder_title')">
        ⋮⋮
      </span>
      <span class="font-semibold text-gray-500">{{ index + 1 }}</span>
    </div>

    <!-- 題型名稱 -->
    <div class="flex items-center gap-2">
      <span class="text-xl">{{ typeIcon }}</span>
      <span class="font-medium text-gray-900">{{ typeName }}</span>
    </div>

    <!-- 啟用開關 -->
    <div>
      <label class="relative inline-block w-11 h-6">
        <input
          type="checkbox"
          :checked="typeConfig.enabled"
          @change="$emit('enabled-change', typeConfig)"
          class="peer opacity-0 w-0 h-0"
        />
        <span class="absolute cursor-pointer inset-0 bg-gray-300 rounded-full transition-all duration-300 peer-checked:bg-primary-500 before:content-[''] before:absolute before:h-[18px] before:w-[18px] before:left-[3px] before:bottom-[3px] before:bg-white before:rounded-full before:transition-all before:duration-300 peer-checked:before:translate-x-[20px]"></span>
      </label>
    </div>

    <!-- 題目數量 -->
    <div>
      <input
        :value="typeConfig.count"
        type="number"
        min="0"
        max="50"
        :disabled="!typeConfig.enabled"
        class="w-full p-2 border border-gray-300 rounded-md text-sm text-center disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]"
        @input="$emit('config-change', typeConfig, 'count', Number($event.target.value))"
      />
    </div>

    <!-- 每題配分 -->
    <div>
      <input
        :value="typeConfig.points"
        type="number"
        min="0"
        max="20"
        step="0.5"
        :disabled="!typeConfig.enabled"
        class="w-full p-2 border rounded-md text-sm text-center disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed focus:outline-none"
        :class="mode === 'select' && typeConfig.enabled
          ? 'bg-warning-100 border-amber-400 font-medium focus:bg-[#fef9e7] focus:border-warning-500 focus:shadow-[0_0_0_3px_rgba(251,191,36,0.1)]'
          : 'border-gray-300 focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]'"
        @input="$emit('config-change', typeConfig, 'points', Number($event.target.value))"
      />
    </div>

    <!-- 小計分數 -->
    <div>
      <span class="font-semibold" :class="typeConfig.enabled ? 'text-emerald-600' : 'text-gray-400'">
        {{ typeConfig.enabled ? (typeConfig.count * typeConfig.points) : 0 }} {{ t('ui.ed_points_unit') }}
      </span>
    </div>

    <!-- 操作按鈕 -->
    <div class="flex gap-1">
      <button
        @click="$emit('move-up', index)"
        :disabled="index === 0"
        class="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-gray-500 text-sm cursor-pointer transition-all duration-200 enabled:hover:bg-gray-200 enabled:hover:text-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
        :title="t('ui.ed_move_up_title')"
      >
        ↑
      </button>
      <button
        @click="$emit('move-down', index)"
        :disabled="index === totalCount - 1"
        class="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-gray-500 text-sm cursor-pointer transition-all duration-200 enabled:hover:bg-gray-200 enabled:hover:text-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
        :title="t('ui.ed_move_down_title')"
      >
        ↓
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
  typeConfig: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  totalCount: {
    type: Number,
    required: true
  },
  mode: {
    type: String,
    default: 'generate'
  }
})

defineEmits(['enabled-change', 'config-change', 'move-up', 'move-down'])

const TYPE_ICONS = {
  single_choice: '📝',
  cloze: '✏️',
  true_false: '✓✗',
  short_answer: '💬',
  matching: '🔗',
  sequence: '🔢',
  enumeration: '📋',
  symbol_identification: '🔍',
  mixed: '🎲',
  auto: '🤖'
}

const typeIcon = computed(() => TYPE_ICONS[props.typeConfig.type] || '❓')
const typeName = computed(() => t(`generate.${props.typeConfig.type}`) || props.typeConfig.type)
</script>
