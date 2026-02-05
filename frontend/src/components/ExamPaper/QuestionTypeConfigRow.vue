<template>
  <div
    class="table-row"
    :class="{
      'row-enabled': typeConfig.enabled,
      'row-disabled': !typeConfig.enabled
    }"
  >
    <!-- 順序 / 拖拽手柄 -->
    <div class="col-order">
      <span class="drag-handle" title="拖拽調整順序">
        ⋮⋮
      </span>
      <span class="order-number">{{ index + 1 }}</span>
    </div>

    <!-- 題型名稱 -->
    <div class="col-type">
      <span class="type-icon">{{ typeIcon }}</span>
      <span class="type-name">{{ typeName }}</span>
    </div>

    <!-- 啟用開關 -->
    <div class="col-enabled">
      <label class="toggle-switch">
        <input
          type="checkbox"
          :checked="typeConfig.enabled"
          @change="$emit('enabled-change', typeConfig)"
        />
        <span class="toggle-slider"></span>
      </label>
    </div>

    <!-- 題目數量 -->
    <div class="col-count">
      <input
        :value="typeConfig.count"
        type="number"
        min="0"
        max="50"
        :disabled="!typeConfig.enabled"
        class="count-input"
        @input="$emit('config-change', typeConfig, 'count', Number($event.target.value))"
      />
    </div>

    <!-- 每題配分 -->
    <div class="col-points">
      <input
        :value="typeConfig.points"
        type="number"
        min="0"
        max="20"
        step="0.5"
        :disabled="!typeConfig.enabled"
        class="points-input"
        :class="{ 'editable-in-select': mode === 'select' && typeConfig.enabled }"
        @input="$emit('config-change', typeConfig, 'points', Number($event.target.value))"
      />
    </div>

    <!-- 小計分數 -->
    <div class="col-total">
      <span class="subtotal" :class="{ 'text-gray-400': !typeConfig.enabled }">
        {{ typeConfig.enabled ? (typeConfig.count * typeConfig.points) : 0 }} 分
      </span>
    </div>

    <!-- 操作按鈕 -->
    <div class="col-actions">
      <button
        @click="$emit('move-up', index)"
        :disabled="index === 0"
        class="action-btn"
        title="向上移動"
      >
        ↑
      </button>
      <button
        @click="$emit('move-down', index)"
        :disabled="index === totalCount - 1"
        class="action-btn"
        title="向下移動"
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

<style scoped>
.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 80px 120px 120px 100px 100px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f9fafb;
}

.table-row.row-enabled {
  background-color: white;
}

.table-row.row-disabled {
  background-color: #fafafa;
  opacity: 0.6;
}

/* 列樣式 */
.col-order {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.drag-handle {
  cursor: grab;
  font-size: 1.25rem;
  color: #9ca3af;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.order-number {
  font-weight: 600;
  color: #6b7280;
}

.col-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.type-icon {
  font-size: 1.25rem;
}

.type-name {
  font-weight: 500;
  color: #111827;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #d1d5db;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #3b82f6;
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* Input 樣式 */
.count-input,
.points-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  text-align: center;
}

.count-input:disabled,
.points-input:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.count-input:focus,
.points-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.count-input.readonly,
.points-input.readonly {
  background-color: #f9fafb;
  color: #374151;
  cursor: default;
}

.points-input.editable-in-select {
  background-color: #fef3c7;
  border-color: #fbbf24;
  font-weight: 500;
}

.points-input.editable-in-select:focus {
  background-color: #fef9e7;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1);
}

.subtotal {
  font-weight: 600;
  color: #059669;
}

/* Action Buttons */
.col-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #e5e7eb;
  color: #374151;
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
