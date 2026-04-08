<template>
  <div class="question-type-config">
    <!-- 自選模式提示 -->
    <div v-if="mode === 'select'" class="readonly-notice">
      <svg class="notice-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span class="notice-text">自選模式：可設定目標題型配置，選題時會顯示進度（已選/目標）</span>
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
          <QuestionTypeConfigRow
            :typeConfig="typeConfig"
            :index="index"
            :totalCount="orderedTypes.length"
            :mode="mode"
            @enabled-change="onEnabledChange"
            @config-change="onRowConfigChange"
            @move-up="moveUp"
            @move-down="moveDown"
          />
        </template>
      </draggable>
    </div>

    <QuestionTypeConfigFooter
      :enabledTypeCount="enabledTypeCount"
      :totalQuestions="totalQuestions"
      :totalPoints="totalPoints"
      :hasUnsavedChanges="hasUnsavedChanges"
      :mode="mode"
      @save="saveConfigManually"
      @apply-preset="applyPreset"
      @reset="resetAll"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import draggable from 'vuedraggable'
import QuestionTypeConfigRow from './QuestionTypeConfigRow.vue'
import QuestionTypeConfigFooter from './QuestionTypeConfigFooter.vue'

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

// 追蹤是否有未儲存的變更
const hasUnsavedChanges = ref(false)

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

// 拖拽結束事件
const onDragEnd = () => {
  orderedTypes.value.forEach((item, index) => {
    item.order = index + 1
  })
  syncToParent()
}

// 啟用狀態變更
const onEnabledChange = (typeConfig) => {
  typeConfig.enabled = !typeConfig.enabled

  if (!typeConfig.enabled) {
    typeConfig.count = 0
  } else {
    if (typeConfig.count === 0) {
      typeConfig.count = 5
    }
  }
  hasUnsavedChanges.value = true
}

// 子元件配置變更（count 或 points）
const onRowConfigChange = (typeConfig, field, value) => {
  typeConfig[field] = value
  hasUnsavedChanges.value = true
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

// 手動儲存設定
const saveConfigManually = () => {
  if (!hasUnsavedChanges.value) {
    syncToParent()
    return
  }
  syncToParent()
  hasUnsavedChanges.value = false
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
    hasUnsavedChanges.value = false
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
  hasUnsavedChanges.value = false
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
</style>
