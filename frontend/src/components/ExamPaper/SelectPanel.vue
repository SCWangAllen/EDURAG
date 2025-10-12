<template>
  <div class="select-panel-embedded">
    <!-- 篩選器區域 -->
    <div class="filters-section">
      <h3 class="section-title">🔍 篩選條件</h3>

      <div class="filters">
        <div class="filter-group">
          <label class="filter-label">科目</label>
          <select v-model="filters.subject" class="form-select-sm">
            <option value="">全部</option>
            <option v-for="subject in subjects" :key="subject" :value="subject">
              {{ t(`subjects.${subject.toLowerCase()}`) || subject }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">年級</label>
          <select v-model="filters.grade" class="form-select-sm">
            <option value="">全部</option>
            <option value="G1">G1</option>
            <option value="G2">G2</option>
            <option value="G3">G3</option>
            <option value="G4">G4</option>
            <option value="G5">G5</option>
            <option value="G6">G6</option>
            <option value="ALL">ALL</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">題型</label>
          <select v-model="filters.questionType" class="form-select-sm">
            <option value="">全部</option>
            <option value="single_choice">{{ t('generate.single_choice') }}</option>
            <option value="cloze">{{ t('generate.cloze') }}</option>
            <option value="true_false">{{ t('generate.true_false') }}</option>
            <option value="short_answer">{{ t('generate.short_answer') }}</option>
            <option value="matching">{{ t('generate.matching') }}</option>
            <option value="sequence">{{ t('generate.sequence') }}</option>
            <option value="enumeration">{{ t('generate.enumeration') }}</option>
            <option value="symbol_identification">{{ t('generate.symbol_identification') }}</option>
          </select>
        </div>

        <div class="filter-group flex-grow">
          <label class="filter-label">搜尋</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="搜尋題目內容..."
            class="form-input-sm"
          >
        </div>

        <div class="filter-group">
          <label class="filter-label">&nbsp;</label>
          <button @click="resetFilters" class="btn btn-secondary-sm">
            🔄 重置
          </button>
        </div>
      </div>
    </div>

    <!-- 已選摘要 -->
    <div class="selected-summary">
      <div class="summary-stats">
        <div class="stat-item total">
          <span class="label">已選題數</span>
          <span class="value">{{ selectedQuestions.length }}</span>
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
          @click="clearSelection"
          class="btn btn-danger-sm"
          :disabled="selectedQuestions.length === 0"
        >
          🗑️ 清空選擇
        </button>
      </div>
    </div>

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
            :checked="isAllCurrentPageSelected"
            @change="toggleSelectAllCurrentPage"
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
              @change="toggleSelection(question)"
            >
          </div>

          <div class="question-content">
            <div class="question-meta">
              <span class="meta-badge type">{{ t(`generate.${question.type}`) }}</span>
              <span v-if="question.subject" class="meta-badge subject">{{ question.subject }}</span>
              <span v-if="question.grade" class="meta-badge grade">{{ question.grade }}</span>
              <span v-if="question.difficulty" class="meta-badge difficulty">{{ question.difficulty }}</span>
            </div>

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
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div class="pagination">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn-page"
        >
          ← 上一頁
        </button>

        <div class="page-numbers">
          <button
            v-for="page in pageNumbers"
            :key="page"
            @click="changePage(page)"
            :class="['btn-page-number', { 'active': page === currentPage }]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="changePage(currentPage + 1)"
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
import { ref, computed, watch, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { getQuestions } from '@/api/questionService.js'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'

const { t } = useLanguage()

const props = defineProps({
  examInfo: {
    type: Object,
    required: true
  },
  questionTypeConfig: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['questions-loaded', 'questions-updated', 'sync-config'])

// ==================== 狀態 ====================

const questions = ref([])
const selectedQuestions = ref([])
const loading = ref(false)

const filters = ref({
  subject: '',
  grade: '',
  questionType: '',
  search: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const totalQuestions = ref(0)

const subjects = ref(['Health', 'Math', 'Science', 'English', 'Chinese', 'Social'])

// ==================== 計算屬性 ====================

const totalPages = computed(() => {
  return Math.ceil(totalQuestions.value / pageSize.value)
})

const pageNumbers = computed(() => {
  const pages = []
  const maxVisible = 5
  const total = totalPages.value

  if (total <= maxVisible) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      for (let i = 1; i <= maxVisible; i++) {
        pages.push(i)
      }
    } else if (currentPage.value >= total - 2) {
      for (let i = total - maxVisible + 1; i <= total; i++) {
        pages.push(i)
      }
    } else {
      for (let i = currentPage.value - 2; i <= currentPage.value + 2; i++) {
        pages.push(i)
      }
    }
  }

  return pages
})

const typeStats = computed(() => {
  const stats = {}
  selectedQuestions.value.forEach(q => {
    const type = q.type  // ✅ 統一使用 'type' 欄位（後端回傳的欄位名）
    if (type) {
      stats[type] = (stats[type] || 0) + 1
    }
  })
  return stats
})

const isAllCurrentPageSelected = computed(() => {
  if (questions.value.length === 0) return false
  return questions.value.every(q => isSelected(q.id))
})

// ==================== 方法 ====================

const loadQuestions = async () => {
  try {
    loading.value = true

    const params = {
      page: currentPage.value,
      size: pageSize.value
    }

    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.grade) params.grade = filters.value.grade
    if (filters.value.questionType) params.question_type = filters.value.questionType
    if (filters.value.search) params.search = filters.value.search

    console.log('📂 載入題目列表:', params)

    const response = await getQuestions(params)

    questions.value = response.data.questions || []
    totalQuestions.value = response.data.total || 0

    console.log(`✅ 載入 ${questions.value.length} 題，總計 ${totalQuestions.value} 題`)

  } catch (error) {
    console.error('❌ 載入題目失敗:', error)
    eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
      message: '載入題目失敗',
      operation: '載入題目列表'
    })
  } finally {
    loading.value = false
  }
}

const isSelected = (questionId) => {
  return selectedQuestions.value.some(q => q.id === questionId)
}

const toggleSelection = (question) => {
  const index = selectedQuestions.value.findIndex(q => q.id === question.id)

  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(question)
  }

  emit('questions-updated', { questions: selectedQuestions.value })

  // ✅ 自動同步配置
  autoSyncConfig()
}

const toggleSelectAllCurrentPage = () => {
  if (isAllCurrentPageSelected.value) {
    // 取消選擇本頁所有題目
    questions.value.forEach(q => {
      const index = selectedQuestions.value.findIndex(sq => sq.id === q.id)
      if (index > -1) {
        selectedQuestions.value.splice(index, 1)
      }
    })
  } else {
    // 選擇本頁所有題目
    questions.value.forEach(q => {
      if (!isSelected(q.id)) {
        selectedQuestions.value.push(q)
      }
    })
  }

  emit('questions-updated', { questions: selectedQuestions.value })

  // ✅ 自動同步配置
  autoSyncConfig()
}

const clearSelection = () => {
  selectedQuestions.value = []
  emit('questions-updated', { questions: [] })

  // ✅ 自動同步配置
  autoSyncConfig()

  eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
    message: '已清空選擇',
    operation: '清空題目'
  })
}

// ✅ 自動同步配置到父組件
const autoSyncConfig = () => {
  console.log('🔄 自動同步題型配置:', typeStats.value)
  emit('sync-config', { typeStats: typeStats.value })
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadQuestions()
}

const resetFilters = () => {
  filters.value = {
    subject: '',
    grade: '',
    questionType: '',
    search: ''
  }
  currentPage.value = 1
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

// ==================== 監聽 ====================

watch(filters, () => {
  currentPage.value = 1
  loadQuestions()
}, { deep: true })

// ==================== 生命週期 ====================

onMounted(() => {
  // 初始化時根據 examInfo 設定預設篩選
  if (props.examInfo.subject) {
    filters.value.subject = props.examInfo.subject
  }
  if (props.examInfo.grade) {
    filters.value.grade = props.examInfo.grade
  }

  loadQuestions()
})
</script>

<style scoped>
.select-panel-embedded {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Filters Section */
.filters-section {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 150px;
}

.filter-group.flex-grow {
  flex: 1;
  min-width: 200px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
}

.form-select-sm,
.form-input-sm {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.form-select-sm:focus,
.form-input-sm:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Selected Summary */
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

/* Questions Section */
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

/* Question List */
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

/* Pagination */
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

/* Buttons */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary-sm {
  padding: 0.5rem 0.75rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-secondary-sm:hover {
  background: #4b5563;
}

.btn-success-sm {
  padding: 0.5rem 0.75rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-success-sm:hover:not(:disabled) {
  background: #059669;
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

/* Loading State */
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

/* Empty State */
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
</style>
