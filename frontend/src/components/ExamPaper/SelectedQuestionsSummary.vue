<template>
  <div class="flex justify-between items-center p-4 bg-primary-100 border border-primary-500 rounded-lg flex-wrap gap-4">
    <div class="flex gap-4 flex-wrap">
      <div class="flex flex-col items-center min-w-[80px]">
        <span class="text-xs text-primary-800">已選 / 應選</span>
        <!-- 原 scoped .stat-item .value 以較高 specificity 壓過此動態色，故實際恆為 primary-800；以 !important 精確保留 -->
        <span class="text-2xl font-semibold !text-primary-800" :class="{ 'text-green-600': selectedCount >= targetTotal, 'text-orange-500': selectedCount < targetTotal }">
          {{ selectedCount }} / {{ targetTotal }}
        </span>
      </div>
      <div
        v-for="(count, type) in typeStats"
        :key="type"
        class="flex flex-col items-center min-w-[80px]"
      >
        <span class="text-xs text-primary-800">{{ t(`generate.${type}`) }}</span>
        <!-- 同上：原 scoped 樣式壓過 getCountClass 動態色，實際恆為 primary-900 -->
        <span class="text-xl font-semibold !text-primary-900" :class="getCountClass(type, count)">
          {{ count }} / {{ getTargetCount(type) }}
        </span>
      </div>
    </div>

    <div class="flex gap-2">
      <button
        @click="$emit('clear')"
        class="px-3 py-2 bg-danger-500 text-white rounded-md text-sm cursor-pointer enabled:hover:bg-danger-600 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="selectedCount === 0"
      >
        🗑️ 清空選擇
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
  selectedCount: {
    type: Number,
    required: true
  },
  typeStats: {
    type: Object,
    required: true
  },
  questionTypeConfig: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['clear'])

// 計算總應選數量
const targetTotal = computed(() => {
  return Object.values(props.questionTypeConfig)
    .filter(config => config.enabled)
    .reduce((sum, config) => sum + (config.count || 0), 0)
})

// 獲取特定題型的應選數量
const getTargetCount = (type) => {
  const config = props.questionTypeConfig[type]
  return config?.enabled ? (config.count || 0) : 0
}

// 根據已選/應選數量決定樣式
const getCountClass = (type, count) => {
  const target = getTargetCount(type)
  if (count >= target && target > 0) return 'text-green-600'
  if (count > 0 && count < target) return 'text-orange-500'
  return ''
}
</script>
