<template>
  <div class="selected-summary">
    <div class="summary-stats">
      <div class="stat-item total">
        <span class="label">已選題數</span>
        <span class="value">{{ selectedCount }}</span>
      </div>
      <div
        v-for="(count, type) in typeStats"
        :key="type"
        class="stat-item"
      >
        <span class="label">{{ t(`generate.${type}`) }}</span>
        <span class="value">{{ count }}</span>
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
import { useLanguage } from '@/composables/useLanguage.js'

const { t } = useLanguage()

defineProps({
  selectedCount: {
    type: Number,
    required: true
  },
  typeStats: {
    type: Object,
    required: true
  }
})

defineEmits(['clear'])
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
