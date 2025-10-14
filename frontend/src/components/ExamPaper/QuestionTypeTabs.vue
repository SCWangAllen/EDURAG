<template>
  <div class="question-type-tabs">
    <div class="tabs-container">
      <button
        v-for="typeInfo in types"
        :key="typeInfo.type"
        @click="selectType(typeInfo.type)"
        :class="['tab-button', { 'active': modelValue === typeInfo.type }]"
      >
        <span class="tab-icon">{{ getTypeIcon(typeInfo.type) }}</span>
        <span class="tab-label">{{ getTypeName(typeInfo.type) }}</span>
        <span v-if="stats[typeInfo.type]" class="tab-stats">
          <span class="generated-count">{{ stats[typeInfo.type].generated }}</span>
          <span class="separator">/</span>
          <span class="selected-count">{{ stats[typeInfo.type].selected }}</span>
          <span class="target-count">/ {{ typeInfo.count }}</span>
        </span>
        <span v-else class="tab-stats empty">
          <span class="target-count">0 / {{ typeInfo.count }}</span>
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
    symbol_identification: '🔍',
    mixed: '🎲',
    auto: '🤖'
  }
  return icons[type] || '❓'
}
</script>

<style scoped>
.question-type-tabs {
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs-container {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.tabs-container::-webkit-scrollbar {
  height: 4px;
}

.tabs-container::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 2px;
}

.tabs-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.tabs-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.tab-button {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-bottom: none;
  border-radius: 0.5rem 0.5rem 0 0;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  position: relative;
}

.tab-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-button.active {
  background: #ffffff;
  color: #111827;
  border-color: #3b82f6;
  border-bottom: 2px solid #ffffff;
  margin-bottom: -2px;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.tab-icon {
  font-size: 1.125rem;
}

.tab-label {
  font-weight: 600;
}

.tab-stats {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
}

.tab-button.active .tab-stats {
  background: #dbeafe;
}

.tab-stats.empty {
  background: #f3f4f6;
  color: #9ca3af;
}

.generated-count {
  color: #3b82f6;
  font-weight: 600;
}

.selected-count {
  color: #059669;
  font-weight: 700;
}

.separator {
  color: #9ca3af;
}

.target-count {
  color: #6b7280;
}
</style>
