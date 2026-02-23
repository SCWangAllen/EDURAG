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
              {{ subject }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">年級</label>
          <select v-model="filters.grade" class="form-select-sm">
            <option value="">全部</option>
            <option v-for="grade in grades" :key="grade" :value="grade">{{ grade }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">題型</label>
          <select v-model="filters.questionType" class="form-select-sm">
            <option value="">全部</option>
            <option v-for="qt in selectableQuestionTypes" :key="qt.value" :value="qt.value">{{ t(qt.labelKey) }}</option>
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

    <!-- 題型分頁 Tabs -->
    <QuestionTypeTabs
      v-model="currentTab"
      :types="enabledTypes"
      :stats="tabStats"
      @update:modelValue="onTabChange"
      class="mb-4"
    />

    <!-- 已選摘要 -->
    <SelectedQuestionsSummary
      :selected-count="selectedQuestions.length"
      :type-stats="typeStats"
      @clear="clearSelection"
    />

    <!-- 題目列表（含 Loading、空狀態、分頁） -->
    <QuestionSelectionList
      :questions="questions"
      :loading="loading"
      :total-questions="totalQuestions"
      :current-page="currentPage"
      :total-pages="totalPages"
      :page-numbers="pageNumbers"
      :selected-ids="selectedIdSet"
      :is-all-selected="isAllCurrentPageSelected"
      @toggle-selection="toggleSelection"
      @toggle-select-all="toggleSelectAllCurrentPage"
      @change-page="changePage"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { getQuestions, getQuestionStats } from '@/api/questionService.js'
import { getImageQuestions, getQuestionImageUrl, getAnswerImageUrl } from '@/api/imageQuestionService.js'
import { useToast } from '@/composables/useToast.js'
import { QUESTION_TYPES } from '@/constants/index.js'
import QuestionTypeTabs from './QuestionTypeTabs.vue'
import SelectedQuestionsSummary from './SelectedQuestionsSummary.vue'
import QuestionSelectionList from './QuestionSelectionList.vue'

const { t } = useLanguage()
const { showSuccess, showError: toastError } = useToast()

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
const currentTab = ref('')  // 當前選中的題型 Tab（空字串表示「全部」）

const filters = ref({
  subject: '',
  grade: '',
  questionType: '',
  search: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const totalQuestions = ref(0)

// 動態載入的科目和年級
const subjects = ref([])
const grades = ref([])

// 篩選用的題型（排除 mixed/auto）
const selectableQuestionTypes = computed(() =>
  QUESTION_TYPES.filter(qt => qt.value !== 'mixed' && qt.value !== 'auto')
)

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

// 從父組件傳入的 questionTypeConfig 獲取已啟用的題型
const enabledTypes = computed(() => {
  return Object.keys(props.questionTypeConfig)
    .filter(type => props.questionTypeConfig[type].enabled)
    .map(type => ({
      type: type,
      count: props.questionTypeConfig[type].count
    }))
})

// 為 QuestionTypeTabs 準備統計資料
const tabStats = computed(() => {
  const stats = {}
  Object.keys(typeStats.value).forEach(type => {
    stats[type] = {
      selected: typeStats.value[type],  // 已選數量
      generated: 0,  // 自選模式不適用
    }
  })
  return stats
})

const selectedIdSet = computed(() => {
  return new Set(selectedQuestions.value.map(q => q.id))
})

const isAllCurrentPageSelected = computed(() => {
  if (questions.value.length === 0) return false
  return questions.value.every(q => selectedIdSet.value.has(q.id))
})

// ==================== 方法 ====================

// 從題目統計 API 載入科目和年級列表（只顯示有題目的）
const loadSubjectsAndGrades = async () => {
  try {
    const response = await getQuestionStats()
    const stats = response.data

    // 從題目統計中提取科目（只有實際有題目的科目）
    subjects.value = Object.keys(stats.by_subject || {}).filter(Boolean)

    // 從題目統計中提取年級
    grades.value = Object.keys(stats.by_grade || {}).filter(Boolean)
  } catch (error) {
    // 靜默失敗，使用空陣列
  }
}

const loadQuestions = async () => {
  try {
    loading.value = true

    const params = {
      page: currentPage.value,
      size: pageSize.value
    }

    // 優先使用 Tab 篩選（如果有選中特定題型）
    const activeFilter = currentTab.value || filters.value.questionType

    // 圖片題目使用獨立 API
    if (activeFilter === 'image_question') {
      await loadImageQuestions()
      return
    }

    if (activeFilter) params.question_type = activeFilter

    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.grade) params.grade = filters.value.grade
    if (filters.value.search) params.search = filters.value.search


    const response = await getQuestions(params)

    questions.value = response.data.questions || []
    totalQuestions.value = response.data.total || 0


  } catch (error) {
    toastError('載入題目失敗', '載入題目列表')
  } finally {
    loading.value = false
  }
}

// 載入圖片題目
const loadImageQuestions = async () => {
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      verified: true  // 只載入已驗證的圖片題目
    }

    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.grade) params.grade = filters.value.grade
    if (filters.value.search) params.search = filters.value.search

    const response = await getImageQuestions(params)
    const imageQuestionsData = response.data.questions || response.data.image_questions || []

    // 轉換 ImageQuestion 為與 Question 相容的格式
    questions.value = imageQuestionsData.map(iq => ({
      id: `img_${iq.id}`,  // 前綴區分
      _originalId: iq.id,
      type: 'image_question',
      content: iq.question_description || '圖片題',
      question_image: iq.question_image,
      question_image_ext: iq.question_image_ext,
      answer_image: iq.answer_image,
      answer_image_ext: iq.answer_image_ext,
      subject: iq.subject,
      grade: iq.grade,
      chapter: iq.chapter,
      page: iq.page,
      explanation: iq.question_description,
      images_verified: iq.images_verified,
      // 提供完整圖片 URL
      question_image_url: getQuestionImageUrl(
        iq.question_image + (iq.question_image_ext ? `.${iq.question_image_ext}` : '')
      ),
      answer_image_url: iq.answer_image ? getAnswerImageUrl(
        iq.answer_image + (iq.answer_image_ext ? `.${iq.answer_image_ext}` : '')
      ) : null
    }))

    totalQuestions.value = response.data.total || 0

  } catch (error) {
    toastError('載入圖片題目失敗', '載入圖片題目')
  } finally {
    loading.value = false
  }
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
      if (!selectedIdSet.value.has(q.id)) {
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

  showSuccess('已清空選擇', '清空題目')
}

// ✅ 自動同步配置到父組件
const autoSyncConfig = () => {
  emit('sync-config', { typeStats: typeStats.value })
}

// Tab 切換方法
const onTabChange = (questionType) => {
  currentTab.value = questionType
  currentPage.value = 1  // 重置到第一頁
  loadQuestions()
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

// ==================== 監聽 ====================

watch(filters, () => {
  currentPage.value = 1
  loadQuestions()
}, { deep: true })

// 監聯 examInfo 變化，同步更新篩選條件（批次更新避免多次觸發）
watch(() => props.examInfo, (newInfo) => {
  if (!newInfo) return

  const updates = {}
  if (newInfo.subject && newInfo.subject !== filters.value.subject) {
    updates.subject = newInfo.subject
  }
  if (newInfo.grade && newInfo.grade !== filters.value.grade) {
    updates.grade = newInfo.grade
  }

  // 一次性更新，只觸發一次 filters watch
  if (Object.keys(updates).length > 0) {
    filters.value = { ...filters.value, ...updates }
  }
}, { deep: true })

// ==================== 生命週期 ====================

onMounted(() => {
  // 動態載入科目和年級
  loadSubjectsAndGrades()

  // 不再自動從 examInfo 設定篩選器，讓使用者自行選擇「全部」或特定篩選條件
  // 篩選器預設值為空字串（全部）
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

/* Buttons (used by filters section) */
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
</style>
