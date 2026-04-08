<template>
  <div class="selected-summary">
    <div class="summary-stats">
      <div class="stat-item total">
        <span class="label">已選 / 應選</span>
        <span class="value" :class="{ 'text-green-600': selectedCount >= targetTotal, 'text-orange-500': selectedCount < targetTotal }">
          {{ selectedCount }} / {{ targetTotal }}
        </span>
      </div>
      <div
        v-for="(count, type) in typeStats"
        :key="type"
        class="stat-item"
      >
        <span class="label">{{ t(`generate.${type}`) }}</span>
        <span class="value" :class="getCountClass(type, count)">
          {{ count }} / {{ getTargetCount(type) }}
        </span>
      </div>
    </div>

    <div class="summary-actions">
      <button
        @click="$emit('clear')"
        class="btn btn-danger-sm"
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

<style scoped>
.selected-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #dbeafe;
  border: 1px solid #3b82f6;
  border-radius: 0.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.summary-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.stat-item .label {
  font-size: 0.75rem;
  color: #1e40af;
}

.stat-item .value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e3a8a;
}

.stat-item.total .value {
  font-size: 1.5rem;
  color: #1e40af;
}

.summary-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-danger-sm {
  padding: 0.5rem 0.75rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-danger-sm:hover:not(:disabled) {
  background: #dc2626;
}

.btn-danger-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
