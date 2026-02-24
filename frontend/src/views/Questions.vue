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
            <button
              @click="exportSelectedQuestions"
              :disabled="exporting"
              class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
            >
              <svg v-if="exporting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
              </svg>
              JSON ({{ selectedQuestions.length }})
            </button>
            
            <div class="relative inline-block">
              <button
                @click="showSelectedExportMenu = !showSelectedExportMenu"
                :disabled="exporting || selectedQuestions.length === 0"
                class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
📝 {{ t('questions.examPaper') }} ({{ selectedQuestions.length }})
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              
              <!-- Selected Questions Export Options Dropdown -->
              <div v-if="showSelectedExportMenu" class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div class="py-2">
                  <button
                    @click="openExamDesigner"
                    class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"></path>
                    </svg>
🎨 {{ t('questions.customExamEditor') }}
                  </button>
                </div>
              </div>
              
              <!-- Click Outside to Close Dropdown -->
              <div v-if="showSelectedExportMenu" @click="showSelectedExportMenu = false" class="fixed inset-0 z-40"></div>
            </div>

            <!-- Batch Delete Button -->
            <button
              @click="handleBatchDelete"
              :disabled="deleting"
              class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
            >
              <svg v-if="deleting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
              {{ t('questions.batchDelete') }} ({{ selectedQuestions.length }})
            </button>
          </div>

          <!-- Removed old export feature, now using custom exam editor -->
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6" v-if="stats">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.totalQuestions') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.total_questions }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h2m-2 0v4a2 2 0 002 2h2a2 2 0 002-2v-4m0 0V9a2 2 0 00-2-2h-2m2 4h4"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.byType') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_type || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.bySubject') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_subject || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.byDifficulty') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_difficulty || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter -->
      <QuestionFilters
        v-model:searchQuery="searchQuery"
        v-model:selectedType="selectedType"
        v-model:selectedSubject="selectedSubject"
        v-model:selectedGrade="selectedGrade"
        v-model:selectedDifficulty="selectedDifficulty"
        :subjects="subjects"
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

  <!-- Selected Questions Style Editor Modal -->
  <QuestionExportStyleModal
    :visible="showSelectedExportStyleModal"
    :selected-questions="selectedQuestions"
    :exporting="exporting"
    :exam-styles="examStyles"
    @close="closeSelectedExportStyleModal"
    @export="exportSelectedWithCustomStyle"
    @open-designer="openExamDesigner"
    @preview="previewSelectedExamStyle"
  />

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


  <!-- ExamDesigner Modal -->
  <div v-if="showExamDesigner" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="w-full max-w-7xl max-h-[95vh] overflow-hidden">
      <ExamDesigner
        :visible="showExamDesigner"
        :selected-questions="selectedQuestions"
        :initial-exam-styles="examStyles"
        @close="closeExamDesigner"
        @save="handleExamDesignerSave"
        @export="handleExamDesignerExport"
      />
    </div>
  </div>

</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { getQuestions, deleteQuestion as deleteQuestionAPI, getQuestionStats, batchDeleteQuestions } from '../api/questionService.js'
import { useToast } from '@/composables/useToast.js'
import ExamDesigner from '@/components/ExamDesigner/ExamDesigner.vue'
import QuestionFilters from '@/components/Questions/QuestionFilters.vue'
import QuestionDetailModal from '@/components/Questions/QuestionDetailModal.vue'
import QuestionEditModal from '@/components/Questions/QuestionEditModal.vue'
import QuestionListSection from '@/components/Questions/QuestionListSection.vue'
import QuestionExportStyleModal from '@/components/Questions/QuestionExportStyleModal.vue'
import { exportQuestionsAsJson, generateFilename } from '@/utils/markdownExporter.js'
import { QUESTION_TYPES } from '@/constants/index.js'
import { generateCustomMarkdown } from '@/utils/examMarkdownGenerator.js'

export default {
  name: 'Questions',
  components: {
    QuestionFilters,
    QuestionDetailModal,
    QuestionEditModal,
    QuestionListSection,
    QuestionExportStyleModal,
    ExamDesigner
  },
  setup() {
    const { t, isEnglish } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    // Reactive data
    const loading = ref(false)
    const questions = ref([])
    const stats = ref(null)
    const subjects = ref([])
    const grades = ref([])  // 動態年級列表
    
    // Search and filter
    const searchQuery = ref('')
    const selectedType = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')
    const selectedDifficulty = ref('')
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
    const exporting = ref(false)
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

    // Exam style editor related
    const showSelectedExportStyleModal = ref(false)
    const showSelectedExportMenu = ref(false)
    const showExamDesigner = ref(false)

    const closeSelectedExportStyleModal = () => {
      showSelectedExportStyleModal.value = false
    }

    const previewSelectedExamStyle = () => {
      const examTitle = generateExamTitle(selectedQuestions.value)
      const markdown = generateCustomMarkdown(examTitle, selectedQuestions.value, examStyles)
      showInlinePreview(markdown)
    }
    
    // New layout system
    const examStyles = reactive({
      
      header: {
        enabled: true,
        titlePrefix: 'Examination',
        subtitle: '',
        duration: '90 minutes',
        totalScore: '100 points',
        schoolName: '○○學校'
      },
      sections: {
        singleChoice: {
          enabled: true,
          title: 'Multiple Choice Questions',
          instruction: 'Choose the best answer for each question.',
          pointsPerQuestion: 2
        },
        cloze: {
          enabled: true,
          title: 'Fill-in-the-Blank Questions',
          instruction: 'Complete the sentences with appropriate words.',
          pointsPerQuestion: 3
        },
        shortAnswer: {
          enabled: true,
          title: 'Short Answer Questions',
          instruction: 'Provide brief answers to the following questions.',
          pointsPerQuestion: 5
        },
        auto: {
          enabled: true,
          title: 'Auto-Generated Questions',
          instruction: 'Answer the following questions based on the provided information.',
          pointsPerQuestion: 4
        }
      },
      content: {
        includeQuestions: true,
        includeInstructions: true
      },
      answerSheet: {
        enabled: true,
        title: 'Answer Sheet',
        studentInfo: 'Name: ________________　Student ID: ________________　Class: ________________',
        format: 'table',
        includeExplanation: true
      },
      exportOptions: {
        questionsOnly: false,
        answerSheetOnly: false,
        completeExam: true
      }
    })

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

    // 動態年級選項
    const gradeOptions = computed(() => {
      return grades.value.sort().map(grade => ({
        value: grade,
        label: grade
      }))
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

        // Extract subject list
        if (stats.value && stats.value.by_subject) {
          subjects.value = Object.keys(stats.value.by_subject).filter(Boolean)
        }

        // Extract grade list
        if (stats.value && stats.value.by_grade) {
          grades.value = Object.keys(stats.value.by_grade).filter(Boolean)
        }

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
        toastError('請先選擇要刪除的題目', '批量刪除')
        return
      }

      const count = selectedQuestions.value.length
      const confirmMsg = `確定要刪除選中的 ${count} 道題目嗎？此操作無法撤銷。`
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
            `成功刪除 ${result.success_count} 道題目，${result.failed_count} 道刪除失敗`,
            '批量刪除'
          )
        } else {
          showSuccess(`成功刪除 ${result.success_count} 道題目`, '批量刪除')
        }
      } catch (error) {
        toastError('批量刪除失敗：' + (error.response?.data?.detail || error.message), '批量刪除', error)
      } finally {
        deleting.value = false
      }
    }

    const exportSelectedQuestions = async () => {
      if (selectedQuestions.value.length === 0) {
        toastError("請先選擇要匯出的問題", "匯出選中問題")
        return
      }

      try {
        exporting.value = true
        
        // 使用新的匯出工具函數
        const filename = generateFilename("selected_questions")
        exportQuestionsAsJson(selectedQuestions.value, filename)

        // Clear selection and localStorage
        const count = selectedQuestions.value.length
        selectedQuestions.value = []
        clearSelectedQuestions()
        
        showSuccess(`已匯出 ${count} 道選中的題目`, "匯出選中問題")
      } catch (error) {
        toastError("匯出失敗: " + error.message, "匯出選中問題", error)
      } finally {
        exporting.value = false
      }
    }
    // 生成考券標題
    const generateExamTitle = (questions, customTitle = null) => {
      if (customTitle) {
        return customTitle
      }
      
      const subjects = [...new Set(questions.map(q => q.subject).filter(Boolean))]
      const subjectText = subjects.length > 0 ? subjects.join(' & ') : 'General'
      const today = new Date()
      const dateStr = today.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
      })
      return `${subjectText} Examination - ${dateStr}`
    }



    // ExamDesigner 相關方法
    const openExamDesigner = () => {
      if (selectedQuestions.value.length === 0) {
        toastError("請先選擇要設計的題目", "開啟考券設計器")
        return
      }

      showExamDesigner.value = true
      closeSelectedExportStyleModal() // 關閉樣式編輯器
    }

    const closeExamDesigner = () => {
      showExamDesigner.value = false
    }

    const handleExamDesignerSave = (templateData) => {
      // 儲存自訂樣式到 localStorage
      const savedTemplates = JSON.parse(localStorage.getItem('customExamTemplates') || '[]')
      savedTemplates.push(templateData)
      localStorage.setItem('customExamTemplates', JSON.stringify(savedTemplates))
      
      showSuccess('考券樣式已儲存', '儲存樣式')
      
    }

    const handleExamDesignerExport = (exportData) => {
      // 使用考券設計器的匯出功能
      const { title, questions, examStyles: designerStyles, markdown } = exportData
      
      // 更新目前的 examStyles
      Object.assign(examStyles, designerStyles)
      
      // 觸發匯出
      exportSelectedWithCustomStyle()
      
    }




    // 在當前頁面顯示預覽的備用方案
    const showInlinePreview = (markdown) => {
      showSuccess('預覽內容已輸出到瀏覽器控制台，請按F12查看', '預覽考券')

      if (markdown.length < 1000) {
        alert(`考券預覽：\n\n${markdown.substring(0, 800)}${markdown.length > 800 ? '...' : ''}`)
      }
    }

    const exportSelectedWithCustomStyle = async () => {
      if (selectedQuestions.value.length === 0) {
        toastError('請先選擇要匯出的問題', '匯出選中問題')
        return
      }

      try {
        exporting.value = true
        
        // 生成考券標題
        const examTitle = generateExamTitle(selectedQuestions.value)
        
        // 直接使用 PDF 導出
        const examData = {
          questions: selectedQuestions.value,
          config: examStyles,
          questionTypeOrder: examStyles.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
        }
        
        // 動態導入 PDF 導出器
        const { exportToPDF } = await import('@/utils/pdfExporter.js')
        const result = await exportToPDF(examData, `${examTitle.replace(/[^a-zA-Z0-9\-_\s]/g, '_')}.pdf`)
        
        // 關閉 Modal
        showSelectedExportStyleModal.value = false
        
        if (result.success) {
          showSuccess(`成功匯出 ${selectedQuestions.value.length} 道選中題目為 PDF`, '匯出 PDF 考券')
        } else {
          throw new Error(result.message)
        }
        
      } catch (error) {
        toastError('匯出考券失敗：' + (error.message || '未知錯誤'), '匯出自定義考券', error)
      } finally {
        exporting.value = false
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
        loadStats()
      ])
    })

    return {
      // 語言
      t,
      isEnglish,
      
      // 資料
      loading,
      questions,
      stats,
      subjects,
      
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
      showExamDesigner,
      selectedQuestion,
      editingQuestion,
      
      // 匯出
      exporting,
      
      // 考券樣式編輯器
      showSelectedExportStyleModal,
      showSelectedExportMenu,
      examStyles,
      
      
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
      exportSelectedQuestions,
      handleBatchDelete,
      deleting,
      
      // 樣式管理方法
      closeSelectedExportStyleModal,
      previewSelectedExamStyle,
      
      
      // 匯出方法
      exportSelectedWithCustomStyle,

      // ExamDesigner 相關方法
      openExamDesigner,
      closeExamDesigner,
      handleExamDesignerSave,
      handleExamDesignerExport,
      
      // 常數
      questionTypes: QUESTION_TYPES,

      // 動態年級選項
      gradeOptions
    }
  }
}
</script>