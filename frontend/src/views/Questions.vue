<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- Title and Action Buttons -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('questions.title') }}</h1>
        </div>
        <div class="flex space-x-3">
          <div v-if="selectedQuestions.length > 0" class="flex space-x-2">
            <!-- Batch Delete Button -->
            <BaseButton
              variant="danger"
              :loading="deleting"
              @click="handleBatchDelete"
            >
              <svg v-if="!deleting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
              {{ t('questions.batchDelete') }} ({{ selectedQuestions.length }})
            </BaseButton>
          </div>

          <!-- Removed old export feature, now using custom exam editor -->
        </div>
      </div>

      <!-- 統計一行摘要,可展開 -->
      <StatsStrip storage-key="edurag:questionStatsCollapsed" :items="statItems" />


      <!-- Search and Filter -->
      <QuestionFilters
        v-model:searchQuery="searchQuery"
        v-model:selectedType="selectedType"
        v-model:selectedSubject="selectedSubject"
        v-model:selectedGrade="selectedGrade"
        v-model:selectedDifficulty="selectedDifficulty"
        :subjects="facetSubjectNames"
        :questionTypes="questionTypes"
        :gradeOptions="gradeOptions"
        @search="searchQuestions"
      />


      <!-- Question List -->
      <QuestionListSection
        :questions="questions"
        :loading="loading"
        :selected-questions="selectedQuestions"
        :total-questions="totalQuestions"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-numbers="pageNumbers"
        :page-size="pageSize"
        :is-all-selected="isAllSelected"
        @select="selectQuestion"
        @edit="editQuestion"
        @delete="deleteQuestion"
        @toggle-select="toggleQuestionSelection"
        @toggle-select-all="toggleSelectAll"
        @change-page="changePage"
      />
    </div>
  </div>

  <!-- Question Detail Modal -->
  <QuestionDetailModal
    :visible="showDetailModal"
    :question="selectedQuestion"
    @close="closeDetailModal"
  />

  <!-- Edit Question Modal -->
  <QuestionEditModal
    :visible="showEditModal"
    :question="editingQuestion"
    @close="closeEditModal"
    @save="saveQuestion"
  />
</template>

<script>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import StatsStrip from '../components/Base/StatsStrip.vue'
import { getQuestions, deleteQuestion as deleteQuestionAPI, getQuestionStats, batchDeleteQuestions, getQuestionFacets } from '../api/questionService.js'
import { useToast } from '@/composables/useToast.js'
import QuestionFilters from '@/components/Questions/QuestionFilters.vue'
import QuestionDetailModal from '@/components/Questions/QuestionDetailModal.vue'
import QuestionEditModal from '@/components/Questions/QuestionEditModal.vue'
import QuestionListSection from '@/components/Questions/QuestionListSection.vue'
import { useSubjects } from '@/composables/useSubjects.js'
import { QUESTION_TYPES, GRADE_OPTIONS } from '@/constants/index.js'
import BaseButton from '@/components/Base/BaseButton.vue'

export default {
  name: 'Questions',
  components: {
    StatsStrip,
    QuestionFilters,
    QuestionDetailModal,
    QuestionEditModal,
    QuestionListSection,
    BaseButton
  },
  setup() {
    const { t, isEnglish } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目唯一來源
    const { subjectNames, ensureLoaded } = useSubjects()

    // Reactive data
    const loading = ref(false)
    const questions = ref([])
    const stats = ref(null)
    // 統計一行摘要(StatsStrip)
    const statItems = computed(() => stats.value ? [
      { label: t('questions.totalQuestions'), value: stats.value.total_questions ?? 0 },
      { label: t('questions.byType'), value: Object.keys(stats.value.by_type || {}).length },
      { label: t('questions.bySubject'), value: Object.keys(stats.value.by_subject || {}).length },
      { label: t('questions.byDifficulty'), value: Object.keys(stats.value.by_difficulty || {}).length }
    ] : [])

    // Search and filter
    const searchQuery = ref('')
    const selectedType = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')

    // 逐層限制(facets):科目 / 年級 / 題型清單只列目前其他條件下實際有題目的
    const qFacets = ref({ subjects: [], grades: [], question_types: [] })
    const facetSubjectNames = computed(() => qFacets.value.subjects.length ? qFacets.value.subjects.map(f => f.value) : subjectNames.value)
    const facetGradeOptions = computed(() => qFacets.value.grades.length ? qFacets.value.grades.map(f => ({ value: f.value })) : GRADE_OPTIONS)
    const facetQuestionTypes = computed(() => {
      if (!qFacets.value.question_types.length) return QUESTION_TYPES
      const allowed = new Set(qFacets.value.question_types.map(f => f.value))
      return QUESTION_TYPES.filter(qt => allowed.has(qt.value))
    })
    let qFacetsSeq = 0
    const loadQuestionFacets = async () => {
      const seq = ++qFacetsSeq
      try {
        const params = {}
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedGrade.value) params.grade = selectedGrade.value
        if (selectedType.value) params.question_type = selectedType.value
        if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value
        const { data } = await getQuestionFacets(params)
        if (seq !== qFacetsSeq) return
        qFacets.value = { subjects: data.subjects || [], grades: data.grades || [], question_types: data.question_types || [] }
        if (selectedSubject.value && !facetSubjectNames.value.includes(selectedSubject.value)) selectedSubject.value = ''
        if (selectedGrade.value && !facetGradeOptions.value.some(g => g.value === selectedGrade.value)) selectedGrade.value = ''
        if (selectedType.value && !facetQuestionTypes.value.some(q => q.value === selectedType.value)) selectedType.value = ''
      } catch (error) {
        qFacets.value = { subjects: [], grades: [], question_types: [] }
      }
    }
    const selectedDifficulty = ref('')
    // 放在 selectedDifficulty 宣告之後:immediate watch 在 setup 當下就執行,const 還沒宣告會炸 TDZ
    watch([selectedSubject, selectedGrade, selectedType, selectedDifficulty], loadQuestionFacets, { immediate: true })
    const pageSize = ref(20)
    
    // 分頁
    const currentPage = ref(1)
    const totalQuestions = ref(0)
    const totalPages = ref(0)
    
    // Modal 控制
    const showDetailModal = ref(false)
    const showEditModal = ref(false)
    const selectedQuestion = ref(null)
    
    // Batch selection related
    const selectedQuestions = ref([])
    const deleting = ref(false)
    
    // Cross-page persistence for selected questions using localStorage
    const SELECTED_QUESTIONS_KEY = 'edurag_selected_questions'
    
    // localStorage helper functions
    const saveSelectedQuestions = () => {
      try {
        const selectedIds = selectedQuestions.value.map(q => q.id)
        localStorage.setItem(SELECTED_QUESTIONS_KEY, JSON.stringify(selectedIds))
      } catch (error) {
      }
    }
    
    const loadSelectedQuestions = () => {
      try {
        const savedIds = localStorage.getItem(SELECTED_QUESTIONS_KEY)
        if (savedIds) {
          const ids = JSON.parse(savedIds)
          return ids
        }
      } catch (error) {
      }
      return []
    }
    
    const clearSelectedQuestions = () => {
      try {
        localStorage.removeItem(SELECTED_QUESTIONS_KEY)
      } catch (error) {
      }
    }
    
    const restoreSelectedQuestions = () => {
      const savedIds = loadSelectedQuestions()
      if (savedIds.length > 0) {
        // Find questions in current page that match saved IDs
        const matchingQuestions = questions.value.filter(q => savedIds.includes(q.id))
        
        // Add matching questions to selectedQuestions if they're not already there
        matchingQuestions.forEach(question => {
          if (!selectedQuestions.value.some(q => q.id === question.id)) {
            selectedQuestions.value.push(question)
          }
        })
        
      }
    }
    
    // Editing related
    const editingQuestion = ref(null)

    // Computed properties
    const pageNumbers = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    const isAllSelected = computed(() => {
      return questions.value.length > 0 && selectedQuestions.value.length === questions.value.length
    })

    // 方法
    const loadQuestions = async () => {
      try {
        loading.value = true
        
        const params = {
          page: currentPage.value,
          size: pageSize.value
        }
        
        if (searchQuery.value) params.search = searchQuery.value
        if (selectedType.value) params.question_type = selectedType.value
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedGrade.value) params.grade = selectedGrade.value
        if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value

        
        const response = await getQuestions(params)
        
        questions.value = response.data.questions || []
        totalQuestions.value = response.data.total || 0
        totalPages.value = response.data.pages || 0
        
        
        // Restore previously selected questions from localStorage
        restoreSelectedQuestions()
      } catch (error) {
        if (error.response) {
        } else if (error.request) {
          toastError('Network connection error: Unable to connect to backend service, please check if backend is running.', 'Load questions')
        } else {
        }
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        const response = await getQuestionStats()

        stats.value = response.data
      } catch (error) {
        if (error.response) {
        } else if (error.request) {
        }
      }
    }

    const searchQuestions = () => {
      currentPage.value = 1
      loadQuestions()
    }

    const changePage = (page) => {
      currentPage.value = page
      loadQuestions()
    }

    // 問題操作相關
    const selectQuestion = (question) => {
      selectedQuestion.value = question
      showDetailModal.value = true
    }

    const editQuestion = (question) => {
      editingQuestion.value = { ...question }
      showEditModal.value = true
    }

    const deleteQuestion = async (question) => {
      if (!confirm(t('questions.deleteConfirm'))) return
      
      try {
        await deleteQuestionAPI(question.id)
        await loadQuestions()
        await loadStats()
        showSuccess(t('questions.deleteSuccess'), '刪除問題')
      } catch (error) {
        toastError(t('questions.deleteError') + (error.response?.data?.detail || error.message), '刪除問題', error)
      }
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedQuestion.value = null
    }

    const closeEditModal = () => {
      showEditModal.value = false
      editingQuestion.value = null
    }

    const saveQuestion = async (formData) => {
      try {
        if (!formData.content.trim()) {
          toastError(t('questions.contentRequired'), '編輯問題')
          return
        }
        if (!formData.correct_answer.trim()) {
          toastError(t('questions.answerRequired'), '編輯問題')
          return
        }

        if (formData.type === 'single_choice') {
          const validOptions = formData.options.filter(opt => opt.trim())
          if (validOptions.length < 2) {
            toastError(t('questions.optionsRequired'), '編輯問題')
            return
          }
          formData.options = validOptions
        }

        const { updateQuestion } = await import('../api/questionService.js')
        await updateQuestion(editingQuestion.value.id, formData)

        closeEditModal()
        await loadQuestions()
        await loadStats()
        showSuccess(t('questions.updateSuccess'), '更新問題')
      } catch (error) {
        toastError(t('questions.updateError') + (error.response?.data?.detail || error.message), '更新問題', error)
      }
    }

    // Batch selection related方法
    const toggleQuestionSelection = (question) => {
      const index = selectedQuestions.value.findIndex(q => q.id === question.id)
      if (index > -1) {
        selectedQuestions.value.splice(index, 1)
      } else {
        selectedQuestions.value.push(question)
      }
    }

    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedQuestions.value = []
        clearSelectedQuestions()
      } else {
        selectedQuestions.value = [...questions.value]
        // saveSelectedQuestions() will be called automatically by the watcher
      }
    }

    const handleBatchDelete = async () => {
      if (selectedQuestions.value.length === 0) {
        toastError(t('ui.vw_select_questions_to_delete'), '批量刪除')
        return
      }

      const count = selectedQuestions.value.length
      const confirmMsg = t('ui.vw_batch_delete_confirm').replace('{count}', count)
      if (!confirm(confirmMsg)) return

      try {
        deleting.value = true
        const ids = selectedQuestions.value.map(q => q.id)
        const response = await batchDeleteQuestions(ids)
        const result = response.data

        // Clear selection and localStorage
        selectedQuestions.value = []
        clearSelectedQuestions()

        // Reload data
        await loadQuestions()
        await loadStats()

        if (result.failed_count > 0) {
          showSuccess(
            t('ui.vw_batch_delete_partial_success')
              .replace('{success}', result.success_count)
              .replace('{failed}', result.failed_count),
            '批量刪除'
          )
        } else {
          showSuccess(t('ui.vw_batch_delete_success').replace('{count}', result.success_count), '批量刪除')
        }
      } catch (error) {
        toastError(t('ui.vw_batch_delete_failed').replace('{detail}', error.response?.data?.detail || error.message), '批量刪除', error)
      } finally {
        deleting.value = false
      }
    }

    // Debounced search function
    let searchTimeout = null
    const debouncedSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadQuestions()
      }, 300) // 300ms debounce
    }

    // Watchers
    watch(searchQuery, () => {
      debouncedSearch()
    })
    
    watch([selectedType, selectedSubject, selectedGrade, selectedDifficulty], () => {
      currentPage.value = 1
      loadQuestions()
    })
    
    // Watch for changes in selected questions and save to localStorage
    watch(selectedQuestions, (newValue) => {
      saveSelectedQuestions()
    }, { deep: true })

    // Load data
    onMounted(async () => {
      await Promise.all([
        loadQuestions(),
        loadStats(),
        ensureLoaded()
      ])
    })

    // 頁面被 keep-alive 快取後再次切回時,重新整理清單/統計(保留篩選/分頁/選取狀態)
    let isFirstActivation = true
    onActivated(() => {
      if (isFirstActivation) {
        isFirstActivation = false
        return
      }
      loadQuestions()
      loadStats()
    })

    return {
      // 語言
      t,
      isEnglish,
      
      // 資料
      loading,
      questions,
      stats,
      statItems,
      subjectNames,
      facetSubjectNames,

      // Search and filter
      searchQuery,
      selectedType,
      selectedSubject,
      selectedGrade,
      selectedDifficulty,
      pageSize,
      
      // 分頁
      currentPage,
      totalQuestions,
      totalPages,
      pageNumbers,
      
      // Modal
      showDetailModal,
      showEditModal,
      selectedQuestion,
      editingQuestion,

      // 方法
      searchQuestions,
      changePage,
      selectQuestion,
      editQuestion,
      deleteQuestion,
      closeDetailModal,
      closeEditModal,
      saveQuestion,

      // 批次選擇
      selectedQuestions,
      isAllSelected,
      toggleQuestionSelection,
      toggleSelectAll,
      handleBatchDelete,
      deleting,

      // 常數
      questionTypes: facetQuestionTypes,
      gradeOptions: facetGradeOptions
    }
  }
}
</script>