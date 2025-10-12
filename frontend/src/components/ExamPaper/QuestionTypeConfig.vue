<template>
  <div class="question-type-config">
    <!-- 自選模式提示 -->
    <div v-if="mode === 'select'" class="readonly-notice">
      <svg class="notice-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span class="notice-text">自選模式：題目數量自動更新，但您可以調整每題配分</span>
    </div>

    <!-- 題型配置表格 -->
    <div class="config-table">
      <div class="table-header">
        <div class="col-order">#</div>
        <div class="col-type">題型</div>
        <div class="col-enabled">啟用</div>
        <div class="col-count">題目數量</div>
        <div class="col-points">每題配分</div>
        <div class="col-total">小計</div>
        <div class="col-actions">操作</div>
      </div>

      <draggable
        v-model="orderedTypes"
        item-key="type"
        handle=".drag-handle"
        @end="onDragEnd"
        class="table-body"
      >
        <template #item="{ element: typeConfig, index }">
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
              <span class="type-icon">{{ getTypeIcon(typeConfig.type) }}</span>
              <span class="type-name">{{ getTypeName(typeConfig.type) }}</span>
            </div>

            <!-- 啟用開關 -->
            <div class="col-enabled">
              <label class="toggle-switch">
                <input
                  type="checkbox"
                  v-model="typeConfig.enabled"
                  :disabled="mode === 'select'"
                  @change="onEnabledChange(typeConfig)"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <!-- 題目數量 -->
            <div class="col-count">
              <input
                v-model.number="typeConfig.count"
                type="number"
                min="0"
                max="50"
                :disabled="!typeConfig.enabled || mode === 'select'"
                :readonly="mode === 'select'"
                class="count-input"
                :class="{ 'readonly': mode === 'select' }"
                @input="onConfigChange"
              />
            </div>

            <!-- 每題配分 -->
            <div class="col-points">
              <input
                v-model.number="typeConfig.points"
                type="number"
                min="0"
                max="20"
                step="0.5"
                :disabled="!typeConfig.enabled"
                class="points-input"
                :class="{ 'editable-in-select': mode === 'select' && typeConfig.enabled }"
                @input="onConfigChange"
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
                @click="moveUp(index)"
                :disabled="index === 0"
                class="action-btn"
                title="向上移動"
              >
                ↑
              </button>
              <button
                @click="moveDown(index)"
                :disabled="index === orderedTypes.length - 1"
                class="action-btn"
                title="向下移動"
              >
                ↓
              </button>
            </div>
          </div>
        </template>
      </draggable>
    </div>

    <!-- 統計資訊 -->
    <div class="stats-panel">
      <div class="stat-card">
        <div class="stat-label">{{ mode === 'select' ? '已選題型' : '已啟用題型' }}</div>
        <div class="stat-value">{{ enabledTypeCount }} 種</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ mode === 'select' ? '已選題數' : '總題數' }}</div>
        <div class="stat-value">{{ totalQuestions }} 題</div>
      </div>
      <div class="stat-card highlight">
        <div class="stat-label">總分</div>
        <div class="stat-value">{{ totalPoints }} 分</div>
      </div>
    </div>

    <!-- 快速配置按鈕（AI生成模式才顯示） -->
    <div v-if="mode !== 'select'" class="quick-config">
      <p class="quick-config-title">💡 快速配置：</p>
      <div class="quick-config-buttons">
        <button @click="applyPreset('standard')" class="preset-btn">
          📋 標準考券 (41題)
        </button>
        <button @click="applyPreset('simple')" class="preset-btn">
          ✏️ 簡易考券 (20題)
        </button>
        <button @click="applyPreset('comprehensive')" class="preset-btn">
          📚 綜合考券 (50題)
        </button>
        <button @click="resetAll" class="preset-btn danger">
          🔄 全部重置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import draggable from 'vuedraggable'

const { t } = useLanguage()

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  mode: {
    type: String,
    default: 'generate'
  }
})

const emit = defineEmits(['update:modelValue'])

// 題型順序陣列（用於拖拽排序）
const orderedTypes = ref([])

// 初始化順序陣列
const initOrderedTypes = () => {
  orderedTypes.value = Object.entries(props.modelValue)
    .map(([type, config]) => ({
      type,
      ...config
    }))
    .sort((a, b) => a.order - b.order)
}

initOrderedTypes()

// 計算屬性
const enabledTypeCount = computed(() => {
  return orderedTypes.value.filter(t => t.enabled).length
})

const totalQuestions = computed(() => {
  return orderedTypes.value
    .filter(t => t.enabled)
    .reduce((sum, t) => sum + t.count, 0)
})

const totalPoints = computed(() => {
  return orderedTypes.value
    .filter(t => t.enabled)
    .reduce((sum, t) => sum + (t.count * t.points), 0)
})

// 題型圖標
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

// 題型名稱
const getTypeName = (type) => {
  return t(`generate.${type}`) || type
}

// 拖拽結束事件
const onDragEnd = () => {
  // 更新 order
  orderedTypes.value.forEach((item, index) => {
    item.order = index + 1
  })
  syncToParent()
}

// 啟用狀態變更
const onEnabledChange = (typeConfig) => {
  // 如果禁用，將數量設為 0
  if (!typeConfig.enabled) {
    typeConfig.count = 0
  }
  syncToParent()
}

// 配置變更
const onConfigChange = () => {
  syncToParent()
}

// 向上移動
const moveUp = (index) => {
  if (index > 0) {
    const temp = orderedTypes.value[index]
    orderedTypes.value[index] = orderedTypes.value[index - 1]
    orderedTypes.value[index - 1] = temp
    onDragEnd()
  }
}

// 向下移動
const moveDown = (index) => {
  if (index < orderedTypes.value.length - 1) {
    const temp = orderedTypes.value[index]
    orderedTypes.value[index] = orderedTypes.value[index + 1]
    orderedTypes.value[index + 1] = temp
    onDragEnd()
  }
}

// 同步到父組件
const syncToParent = () => {
  const newConfig = {}
  orderedTypes.value.forEach(item => {
    const { type, ...config } = item
    newConfig[type] = config
  })
  emit('update:modelValue', newConfig)
}

// 監聽 props 變化（雙向同步）
watch(() => props.modelValue, () => {
  initOrderedTypes()
}, { deep: true })

// 快速配置預設
const applyPreset = (preset) => {
  const presets = {
    standard: {
      single_choice: { count: 10, points: 1, enabled: true },
      cloze: { count: 13, points: 2, enabled: true },
      true_false: { count: 12, points: 1, enabled: true },
      short_answer: { count: 6, points: 4, enabled: true }
    },
    simple: {
      single_choice: { count: 10, points: 2, enabled: true },
      cloze: { count: 5, points: 2, enabled: true },
      short_answer: { count: 5, points: 4, enabled: true }
    },
    comprehensive: {
      single_choice: { count: 15, points: 1, enabled: true },
      cloze: { count: 15, points: 2, enabled: true },
      true_false: { count: 10, points: 1, enabled: true },
      short_answer: { count: 8, points: 3, enabled: true },
      matching: { count: 2, points: 5, enabled: true }
    }
  }

  const config = presets[preset]
  if (config) {
    orderedTypes.value.forEach(item => {
      if (config[item.type]) {
        Object.assign(item, config[item.type])
      } else {
        item.enabled = false
        item.count = 0
      }
    })
    syncToParent()
  }
}

// 全部重置
const resetAll = () => {
  orderedTypes.value.forEach(item => {
    item.enabled = false
    item.count = 0
    item.points = 2
  })
  syncToParent()
}
</script>

<style scoped>
.question-type-config {
  width: 100%;
}

/* 唯讀模式提示 */
.readonly-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background: #dbeafe;
  border: 1px solid #3b82f6;
  border-radius: 0.5rem;
  color: #1e40af;
}

.notice-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.notice-text {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 表格樣式 */
.config-table {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 1fr 80px 120px 120px 100px 100px;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.table-body {
  display: flex;
  flex-direction: column;
}

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

/* 統計面板 */
.stats-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.stat-card.highlight {
  background: #eff6ff;
  border-color: #3b82f6;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.stat-card.highlight .stat-value {
  color: #3b82f6;
}

/* 快速配置 */
.quick-config {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.quick-config-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
}

.quick-config-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preset-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.preset-btn.danger {
  color: #dc2626;
  border-color: #fca5a5;
}

.preset-btn.danger:hover {
  background: #fef2f2;
  border-color: #f87171;
}
</style>
