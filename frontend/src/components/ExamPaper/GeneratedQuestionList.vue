<template>
  <div class="generated-question-list">
    <!-- 摘要統計 -->
    <div class="summary-header">
      <div class="summary-stats">
        <div class="stat-item generated">
          <span class="label">已生成</span>
          <span class="value">{{ questions.length }}</span>
        </div>
        <div class="stat-item selected-target">
          <span class="label">已選 / 應選</span>
          <span class="value" :class="countStatusClass">{{ selectedCount }} / {{ targetCount }}</span>
        </div>
      </div>

      <div class="summary-actions">
        <button
          v-if="unselectedQuestions.length > 0"
          @click="clearUnselected"
          class="btn-secondary-sm"
          title="刪除所有未勾選的題目"
        >
          🗑️ 清空未選用 ({{ unselectedQuestions.length }})
        </button>
        <button
          v-if="questions.length > 0"
          @click="toggleSelectAll"
          class="btn-primary-sm"
        >
          {{ isAllSelected ? '取消全選' : '全選' }}
        </button>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-if="questions.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p class="empty-text">尚未生成題目</p>
      <p class="empty-hint">點擊上方「生成題目」按鈕開始生成</p>
    </div>

    <!-- 題目列表 -->
    <div v-else class="question-list">
      <div
        v-for="(question, index) in questions"
        :key="question.id || index"
        :class="['question-item', { 'selected': question.selected, 'unselected': !question.selected }]"
      >
        <!-- 勾選框 -->
        <div class="question-checkbox">
          <input
            type="checkbox"
            :checked="question.selected"
            @change="toggleSelection(question)"
          />
        </div>

        <!-- 序號 -->
        <div class="question-number">{{ index + 1 }}</div>

        <!-- 題目內容 -->
        <div class="question-content">
          <!-- 題目文字 -->
          <div class="question-prompt">
            {{ question.content || question.prompt }}
          </div>

          <!-- 選項（如果有） -->
          <div v-if="question.options && question.options.length > 0" class="question-options">
            <span v-for="(opt, idx) in question.options" :key="idx" class="option-tag">
              {{ opt }}
            </span>
          </div>

          <!-- 元數據 -->
          <div class="question-meta">
            <span v-if="question._meta?.templateName" class="meta-badge template">
              📋 {{ question._meta.templateName }}
            </span>
            <span v-if="question._meta?.documentNames" class="meta-badge docs" :title="question._meta.documentNames">
              📚 {{ truncateText(question._meta.documentNames, 30) }}
            </span>
            <span v-if="question.saved" class="meta-badge saved">
              ✓ 已儲存
            </span>
            <span v-else-if="question.save_error" class="meta-badge error" :title="question.save_error">
              ✗ 儲存失敗
            </span>
          </div>
        </div>

        <!-- 操作按鈕 -->
        <div class="question-actions">
          <button
            @click="removeQuestion(question)"
            class="btn-remove"
            title="刪除此題"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  targetCount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['toggle-selection', 'remove-question', 'clear-unselected'])

const selectedCount = computed(() => {
  return props.questions.filter(q => q.selected).length
})

// 計算已選/應選的狀態 class
const countStatusClass = computed(() => {
  if (selectedCount.value === 0) return 'status-empty'
  if (selectedCount.value < props.targetCount) return 'status-partial'
  if (selectedCount.value === props.targetCount) return 'status-complete'
  return 'status-over' // 超過目標
})

const unselectedQuestions = computed(() => {
  return props.questions.filter(q => !q.selected)
})

const isAllSelected = computed(() => {
  if (props.questions.length === 0) return false
  return props.questions.every(q => q.selected)
})

const toggleSelection = (question) => {
  emit('toggle-selection', question)
}

const removeQuestion = (question) => {
  if (confirm('確定要刪除此題目嗎？')) {
    emit('remove-question', question)
  }
}

const clearUnselected = () => {
  if (confirm(`確定要清空 ${unselectedQuestions.value.length} 道未勾選的題目嗎？`)) {
    emit('clear-unselected')
  }
}

const toggleSelectAll = () => {
  const newState = !isAllSelected.value
  props.questions.forEach(q => {
    if (q.selected !== newState) {
      emit('toggle-selection', q)
    }
  })
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.generated-question-list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.summary-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item .label {
  font-size: 0.75rem;
  color: #6b7280;
}

.stat-item .value {
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-item.generated .value {
  color: #3b82f6;
}

.stat-item.selected-target .value {
  font-weight: 700;
}

.stat-item.selected-target .value.status-empty {
  color: #9ca3af;
}

.stat-item.selected-target .value.status-partial {
  color: #f59e0b;
}

.stat-item.selected-target .value.status-complete {
  color: #059669;
}

.stat-item.selected-target .value.status-over {
  color: #dc2626;
}

.summary-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary-sm,
.btn-secondary-sm {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary-sm {
  background: #3b82f6;
  color: white;
}

.btn-primary-sm:hover {
  background: #2563eb;
}

.btn-secondary-sm {
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-secondary-sm:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.875rem;
  color: #9ca3af;
}

.question-list {
  display: flex;
  flex-direction: column;
}

.question-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.question-item:last-child {
  border-bottom: none;
}

.question-item:hover {
  background: #f9fafb;
}

.question-item.selected {
  background: #eff6ff;
}

.question-item.unselected {
  opacity: 0.6;
}

.question-checkbox input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.question-number {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 600;
}

.question-item.unselected .question-number {
  background: #9ca3af;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-prompt {
  font-size: 0.9375rem;
  color: #111827;
  line-height: 1.6;
  margin-bottom: 0.75rem;
  word-wrap: break-word;
}

.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.option-tag {
  padding: 0.375rem 0.75rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #374151;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.meta-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.meta-badge.template {
  background: #dbeafe;
  color: #1e40af;
}

.meta-badge.docs {
  background: #fef3c7;
  color: #92400e;
}

.meta-badge.saved {
  background: #d1fae5;
  color: #065f46;
}

.meta-badge.error {
  background: #fee2e2;
  color: #991b1b;
  cursor: help;
}

.question-actions {
  flex-shrink: 0;
}

.btn-remove {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #fecaca;
  border-color: #f87171;
  transform: scale(1.05);
}
</style>
