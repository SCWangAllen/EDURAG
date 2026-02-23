<template>
  <div class="question-selection-list">
    <!-- Loading 狀態 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>載入題目中...</p>
    </div>

    <!-- 題目列表 -->
    <div v-else-if="questions.length > 0" class="questions-section">
      <div class="section-header">
        <h3 class="section-title">
          📚 題目列表
          <span class="count-badge">{{ totalQuestions }} 題</span>
        </h3>
        <div class="select-all">
          <input
            type="checkbox"
            :checked="isAllSelected"
            @change="$emit('toggle-select-all')"
            id="select-all"
          >
          <label for="select-all">全選本頁</label>
        </div>
      </div>

      <div class="question-list">
        <div
          v-for="question in questions"
          :key="question.id"
          :class="['question-item', { 'selected': isSelected(question.id) }]"
        >
          <div class="question-checkbox">
            <input
              type="checkbox"
              :checked="isSelected(question.id)"
              @change="$emit('toggle-selection', question)"
            >
          </div>

          <div class="question-content">
            <div class="question-meta">
              <span class="meta-badge type">{{ t(`generate.${question.type}`) }}</span>
              <span v-if="question.subject" class="meta-badge subject">{{ t(`subjects.${question.subject.toLowerCase()}`) || question.subject }}</span>
              <span v-if="question.grade" class="meta-badge grade">{{ question.grade }}</span>
              <span v-if="question.difficulty" class="meta-badge difficulty">{{ question.difficulty }}</span>
              <span v-if="question.type === 'image_question' && question.images_verified" class="meta-badge verified">✓ 已驗證</span>
            </div>

            <!-- 圖片題目特殊渲染 -->
            <template v-if="question.type === 'image_question'">
              <div class="image-question-preview">
                <div class="image-thumbnail-container">
                  <img
                    v-if="question.question_image_url"
                    :src="question.question_image_url"
                    :alt="question.content || '問題圖片'"
                    class="image-thumbnail"
                    @error="handleImageError"
                  />
                  <div v-else class="image-placeholder">
                    🖼️ {{ question.question_image || '無圖片' }}
                  </div>
                </div>
                <div class="image-question-info">
                  <div class="question-prompt">{{ question.content || '圖片題' }}</div>
                  <div v-if="question.chapter" class="question-chapter">
                    <span class="chapter-label">章節：</span>{{ question.chapter }}
                  </div>
                  <div v-if="question.page" class="question-page">
                    <span class="page-label">頁碼：</span>{{ question.page }}
                  </div>
                  <div v-if="question.answer_image" class="has-answer-image">
                    ✓ 含答案圖片
                  </div>
                </div>
              </div>
            </template>

            <!-- 一般題目渲染 -->
            <template v-else>
              <div class="question-prompt">{{ question.content }}</div>

              <div v-if="question.options" class="question-options">
                <span
                  v-for="(opt, idx) in question.options"
                  :key="idx"
                  class="option-tag"
                >
                  {{ opt }}
                </span>
              </div>

              <div v-if="question.correct_answer" class="question-answer">
                <strong>答案：</strong>{{ formatAnswer(question.correct_answer) }}
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div class="pagination">
        <button
          @click="$emit('change-page', currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn-page"
        >
          ← 上一頁
        </button>

        <div class="page-numbers">
          <button
            v-for="page in pageNumbers"
            :key="page"
            @click="$emit('change-page', page)"
            :class="['btn-page-number', { 'active': page === currentPage }]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="$emit('change-page', currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn-page"
        >
          下一頁 →
        </button>

        <div class="page-info">
          第 {{ currentPage }} / {{ totalPages }} 頁
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📝</div>
      <p class="empty-title">沒有找到題目</p>
      <p class="empty-desc">請調整篩選條件或稍後再試</p>
    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  totalQuestions: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 0
  },
  pageNumbers: {
    type: Array,
    default: () => []
  },
  selectedIds: {
    type: Set,
    required: true
  },
  isAllSelected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-selection', 'toggle-select-all', 'change-page'])

const isSelected = (questionId) => {
  return props.selectedIds.has(questionId)
}

const formatAnswer = (answer) => {
  if (Array.isArray(answer)) {
    return answer.join(', ')
  }
  if (typeof answer === 'object') {
    return JSON.stringify(answer)
  }
  return String(answer).substring(0, 50) + (String(answer).length > 50 ? '...' : '')
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const placeholder = document.createElement('div')
  placeholder.className = 'image-placeholder'
  placeholder.textContent = '圖片載入失敗'
  event.target.parentNode.appendChild(placeholder)
}
</script>

<style scoped>
.questions-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: 0.5rem;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.select-all input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.select-all label {
  cursor: pointer;
  user-select: none;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.question-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
}

.question-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.question-checkbox {
  flex-shrink: 0;
  display: flex;
  align-items: start;
  padding-top: 0.25rem;
}

.question-checkbox input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.meta-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.meta-badge.type {
  background: #dbeafe;
  color: #1e40af;
}

.meta-badge.subject {
  background: #d1fae5;
  color: #065f46;
}

.meta-badge.grade {
  background: #fef3c7;
  color: #92400e;
}

.meta-badge.difficulty {
  background: #f3e8ff;
  color: #6b21a8;
}

.question-prompt {
  font-size: 0.875rem;
  color: #111827;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.option-tag {
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.question-answer {
  font-size: 0.75rem;
  color: #059669;
  padding: 0.25rem 0.5rem;
  background: #d1fae5;
  border-radius: 0.25rem;
  display: inline-block;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0;
}

.btn-page,
.btn-page-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled),
.btn-page-number:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-page-number.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-info {
  margin-left: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1rem;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-desc {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

/* 圖片題目樣式 */
.meta-badge.verified {
  background: #d1fae5;
  color: #065f46;
}

.image-question-preview {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.image-thumbnail-container {
  flex-shrink: 0;
  width: 120px;
  height: 80px;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
  background: #f9fafb;
}

.image-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
  padding: 0.5rem;
}

.image-question-info {
  flex: 1;
  min-width: 0;
}

.question-chapter,
.question-page {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.chapter-label,
.page-label {
  font-weight: 500;
  color: #374151;
}

.has-answer-image {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  padding: 0.125rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
