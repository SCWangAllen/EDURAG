<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 頁面標題 -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('generate.title') }}</h1>
        </div>
        <div>
          <button
            @click="resetForm"
            :disabled="generating"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            🔄 {{ t('generate.clearAllSettings') || '清空全部設定' }}
          </button>
        </div>
      </div>

      <!-- 考題生成區塊 - 垂直堆疊佈局 -->
      <div class="space-y-6">
        <!-- 選擇區域：模板 + 文件水平並排 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 模板選擇 -->
          <TemplateSelector
            :templates="templates"
            :filteredTemplates="filteredTemplates"
            :subjects="subjects"
            :subjectList="subjectList"
            :selectedSubject="selectedSubject"
            :selectedTemplate="selectedTemplate"
            :loadingTemplates="loadingTemplates"
            @update:selectedSubject="selectedSubject = $event"
            @select-template="selectTemplate"
            @fetch-templates="fetchTemplates"
          />

          <!-- 文件選擇 -->
          <DocumentSelector
            :documents="documents"
            :filteredDocuments="filteredDocuments"
            :selectedDocuments="selectedDocuments"
            :documentSubjects="documentSubjects"
            v-model:selectedDocumentSubject="selectedDocumentSubject"
            v-model:selectedDocumentGrade="selectedDocumentGrade"
            v-model:documentSearchQuery="documentSearchQuery"
            :gradeOptions="gradeOptions"
            :loadingDocuments="loadingDocuments"
            @select-document="selectDocument"
            @toggle-document="toggleDocumentSelection"
            @search-documents="searchDocuments"
          />
        </div>

        <!-- 生成設定區塊 -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex flex-wrap items-end gap-4">
            <!-- 生成數量 -->
            <div class="flex-1 min-w-[120px]">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('generate.questionCount') || '生成數量' }}
              </label>
              <input
                v-model.number="traditionalCount"
                type="number"
                min="1"
                max="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- 問題類型（唯讀） -->
            <div v-if="selectedTemplate" class="flex-1 min-w-[150px]">
              <label class="block text-sm font-medium text-gray-700 mb-2">問題類型</label>
              <div class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
                {{ getQuestionTypeLabel(selectedTemplate.question_type) }}
              </div>
            </div>

            <!-- 目標年級 -->
            <div v-if="availableGrades.length > 0" class="flex-1 min-w-[120px]">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('generate.targetGrade') || '目標年級' }}
              </label>
              <select
                v-model="targetGrade"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">-- {{ t('generate.selectGrade') || '請選擇' }} --</option>
                <option v-for="grade in availableGrades" :key="grade" :value="grade">
                  {{ grade }}
                </option>
              </select>
            </div>

            <!-- 生成按鈕 -->
            <div class="flex-shrink-0">
              <button
                @click="generateTraditionalQuestions"
                :disabled="!selectedTemplate || selectedDocuments.length === 0 || generating"
                class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center h-[42px]"
              >
                <svg v-if="generating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ generating ? t('generate.generating') || '生成中...' : t('generate.traditionalGenerate') || '生成題目' }}
              </button>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-3">
            {{ t('generate.traditionalGenerateDesc') || '基於選擇的模板和文件生成題目' }}
          </p>
        </div>

        <!-- 可折疊 Prompt 預覽 -->
        <div v-if="selectedTemplate" class="bg-white shadow rounded-lg overflow-hidden">
          <!-- 折疊標題列 -->
          <div
            @click="togglePreview"
            class="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50 border-b"
          >
            <div class="flex items-center space-x-2">
              <svg
                :class="['w-5 h-5 transition-transform duration-200', showPreview ? 'rotate-90' : '']"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
              <h2 class="text-lg font-medium text-gray-900">
                {{ t('generate.templatePreview') || 'Prompt 預覽' }}
              </h2>
            </div>
            <div class="text-sm text-gray-500">
              {{ selectedDocuments.length }} {{ t('generate.documentsSelected') }}
              · {{ previewContent.length }} {{ t('generate.characters') || '字符' }}
            </div>
          </div>

          <!-- 可折疊內容 -->
          <div v-show="showPreview" class="p-4 bg-gray-50 transition-all duration-300">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-medium text-gray-900">{{ selectedTemplate.name }}</h3>
            </div>
            <div class="max-h-[400px] overflow-y-auto border border-gray-200 bg-white p-3 rounded text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
              {{ previewContent }}
            </div>
            <div class="mt-3 text-xs text-gray-500 flex justify-between">
              <span>{{ t('generate.previewNote') }}</span>
              <span v-if="selectedDocuments.length > 0">
                已選文件: {{ selectedDocuments.map(d => d.title).join(', ') }}
              </span>
            </div>
          </div>
        </div>

        <!-- 生成結果 -->
        <GenerationResults
          :generatedQuestions="generatedQuestions"
          :saving="saving"
          @export="exportQuestions"
          @save="saveQuestions"
        />
      </div>
    </div>
  </div>

  <!-- 警告對話框 -->
  <div v-if="showWarningDialog" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showWarningDialog = false"></div>

      <!-- 警告對話框內容 -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <div class="sm:flex sm:items-start">
            <!-- 警告圖標 -->
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ currentWarning?.title || '警告' }}
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-600 whitespace-pre-line">
                  {{ currentWarning?.message }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            @click="showWarningDialog = false"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-yellow-600 text-base font-medium text-white hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            {{ t('close') || '關閉' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import templateService from '../api/templateService.js'
import subjectService from '../api/subjectService.js'
import documentService from '../api/documentService.js'
import { generateQuestionsByTemplateEnhanced, createQuestion } from '../api/questionService.js'
import { useLanguage } from '../composables/useLanguage.js'
import { getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'
import { useToast } from '../composables/useToast.js'
import GenerationResults from '../components/Generate/GenerationResults.vue'
import TemplateSelector from '../components/Generate/TemplateSelector.vue'
import DocumentSelector from '../components/Generate/DocumentSelector.vue'

export default {
  name: 'Generate',
  components: {
    GenerationResults,
    TemplateSelector,
    DocumentSelector
  },
  setup() {
    // 多語言支持
    const { t, isEnglish, currentLanguage } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    // 基本狀態
    const generating = ref(false)
    const saving = ref(false)
    const loadingTemplates = ref(false)
    const loadingDocuments = ref(false)

    // 預覽區域折疊狀態
    const showPreview = ref(true)

    const togglePreview = () => {
      showPreview.value = !showPreview.value
    }

    // 模板相關
    const templates = ref([])
    const subjects = ref([]) // 用於篩選器的科目名稱陣列
    const subjectList = ref([]) // 用於顏色顯示的完整科目資料
    const selectedSubject = ref('')
    const selectedTemplate = ref(null) // 保留用於預覽

    // 文件相關
    const documents = ref([])
    const selectedDocuments = ref([])  // 傳統生成用
    const documentSearchQuery = ref('')
    const selectedDocumentSubject = ref('')  // 文件科目篩選
    const selectedDocumentGrade = ref('')    // 文件年級篩選
    const documentSubjects = ref([])         // 文件科目清單
    const traditionalCount = ref(5)  // 傳統生成數量（預設 5 題）

    // 目標年級（生成時帶入）
    const targetGrade = ref('')

    // 動態年級選項（與科目連動）
    const gradeOptions = computed(() => {
      let filteredDocs = documents.value

      // 如果有選擇科目，只提取該科目的年級
      if (selectedDocumentSubject.value) {
        filteredDocs = filteredDocs.filter(doc => doc.subject === selectedDocumentSubject.value)
      }

      // 提取不重複的年級
      const grades = new Set()
      filteredDocs.forEach(doc => {
        if (doc.grade && doc.grade.trim()) {
          grades.add(doc.grade.trim())
        }
      })

      // 轉換為選項格式 { value, label }
      return Array.from(grades).sort().map(grade => ({
        value: grade,
        label: grade
      }))
    })

    // 目標年級選項（從模板和文件中提取）
    const availableGrades = computed(() => {
      const grades = new Set()

      // 從模板取得年級
      if (selectedTemplate.value?.grades && Array.isArray(selectedTemplate.value.grades)) {
        selectedTemplate.value.grades.forEach(g => {
          if (g && g.trim()) {
            grades.add(g.trim())
          }
        })
      }

      // 從選擇的文件取得年級
      selectedDocuments.value.forEach(doc => {
        if (doc.grade && doc.grade.trim()) {
          grades.add(doc.grade.trim())
        }
      })

      return Array.from(grades).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))
    })

    // 統一文件選擇功能
    const createDocumentSelector = (selectedDocs, searchQuery, subjectFilter = null, gradeFilter = null) => {
      const toggleSelection = (document) => {
        const index = selectedDocs.value.findIndex(d => d.id === document.id)
        if (index > -1) {
          selectedDocs.value.splice(index, 1)
        } else {
          selectedDocs.value.push(document)
        }
      }

      const filteredDocs = computed(() => {
        let filtered = documents.value

        // 科目篩選
        if (subjectFilter && subjectFilter.value) {
          filtered = filtered.filter(doc => doc.subject === subjectFilter.value)
        }

        // 年級篩選
        if (gradeFilter && gradeFilter.value) {
          filtered = filtered.filter(doc => doc.grade === gradeFilter.value)
        }

        // 文字搜尋
        if (searchQuery.value) {
          const query = searchQuery.value.toLowerCase()
          filtered = filtered.filter(doc =>
            doc.title.toLowerCase().includes(query) ||
            (doc.chapter && doc.chapter.toLowerCase().includes(query))
          )
        }

        return filtered
      })

      return { toggleSelection, filteredDocs }
    }

    // 統一題目儲存功能
    const saveQuestionsBatch = async (questionsArray, sourceInfo) => {
      const results = { success: [], failed: [] }
      for (const [index, question] of questionsArray.entries()) {
        try {
          const questionData = {
            type: question.type || 'single_choice',
            content: question.content || question.prompt || question.question || question.text || '',
            options: question.options || null,
            correct_answer: (Array.isArray(question.answer) || typeof question.answer === 'object')
              ? JSON.stringify(question.answer)
              : String(question.answer ?? ''),
            explanation: question.explanation || '',
            source_document_id: sourceInfo.documentId,
            source_content: sourceInfo.content,
            subject: sourceInfo.subject || 'General',
            chapter: sourceInfo.chapter,
            grade: sourceInfo.grade || null,
            difficulty: 'medium',
            question_data: question.question_data || null  // 配對題的 left_items/right_items
          }

          await createQuestion(questionData)
          results.success.push({ index: index + 1, question: question.prompt.substring(0, 50) + '...' })

        } catch (error) {
          results.failed.push({
            index: index + 1,
            question: question.prompt.substring(0, 50) + '...',
            error: error.response?.data?.detail || error.message
          })
        }
      }

      return results
    }

    // 生成結果
    const generatedQuestions = ref([])

    // 錯誤狀態管理
    const errors = ref({
      documents: null,
      templates: null,
      subjects: null,
      generation: null
    })

    const showErrorDialog = ref(false)
    const showWarningDialog = ref(false)
    const currentError = ref(null)
    const currentWarning = ref(null)

    // 錯誤處理方法
    const showError = (title, message, detail = null) => {
      currentError.value = { title, message, detail }
      showErrorDialog.value = true
    }

    // 警告通知方法
    const showWarning = (title, message) => {
      currentWarning.value = { title, message }
      showWarningDialog.value = true
    }

    const clearError = (errorType) => {
      if (errors.value[errorType]) {
        errors.value[errorType] = null
      }
    }

    // 計算屬性
    const filteredTemplates = computed(() => {
      if (!selectedSubject.value) return templates.value
      return templates.value.filter(template => template.subject === selectedSubject.value)
    })

    // 使用統一的文件選擇器
    const traditionalDocumentSelector = createDocumentSelector(
      selectedDocuments,
      documentSearchQuery,
      selectedDocumentSubject,
      selectedDocumentGrade
    )

    const filteredDocuments = traditionalDocumentSelector.filteredDocs

    const previewContent = computed(() => {
      if (!selectedTemplate.value?.content) return ''

      let contextContent = '範例文章內容...'

      if (selectedDocuments.value.length > 0) {
        // 顯示所有選中文件的完整內容
        contextContent = selectedDocuments.value.map(doc => {
          return `=== ${doc.title} ===\n${doc.chapter ? `章節: ${doc.chapter}\n` : ''}${doc.content}`
        }).join('\n\n')
      }

      return selectedTemplate.value.content
        .replace('{context}', contextContent)
        .replace('{count}', traditionalCount.value)
    })

    // 方法
    const fetchTemplates = async () => {
      loadingTemplates.value = true
      try {
        const params = selectedSubject.value ? { subject: selectedSubject.value } : {}
        const data = await templateService.getTemplates(params)
        templates.value = data.templates || []
      } catch (error) {
        errors.value.templates = {
          message: '無法載入模板清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        templates.value = []
        showError('模板載入失敗', '無法從伺服器取得模板清單，請檢查網路連線或聯絡系統管理員。', error.response?.data)
      } finally {
        loadingTemplates.value = false
      }
    }

    const refreshTemplates = async () => {
      const previousSelected = selectedTemplate.value
      await fetchTemplates()

      // 如果之前有選擇模板，重新設定選擇（獲取最新資料）
      if (previousSelected) {
        const updatedTemplate = templates.value.find(t => t.id === previousSelected.id)
        if (updatedTemplate) {
          selectedTemplate.value = updatedTemplate
        }
      }
    }

    // 取得篩選器用的科目名稱清單
    const fetchSubjects = async () => {
      try {
        const data = await templateService.getSubjects()
        subjects.value = data.subjects || []
      } catch (error) {
        errors.value.subjects = {
          message: '無法載入科目清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        subjects.value = []
        showError('科目載入失敗', '無法從伺服器取得科目清單，請檢查網路連線。', error.response?.data)
      }
    }

    // 取得完整的科目資料（包含顏色）
    const fetchSubjectList = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectList.value = data.subjects || []
      } catch (error) {
        subjectList.value = []
      }
    }

    const fetchDocuments = async () => {
      loadingDocuments.value = true
      try {
        // 請求最多 100 個文件（後端允許的最大值）
        const data = await documentService.getDocuments({ size: 100 })
        documents.value = data.documents || []

        // 提取文件的科目清單（去重）
        const subjects = new Set()
        documents.value.forEach(doc => {
          if (doc.subject) {
            subjects.add(doc.subject)
          }
        })
        documentSubjects.value = Array.from(subjects).sort()

      } catch (error) {
        errors.value.documents = {
          message: '無法載入文件清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        documents.value = []
        documentSubjects.value = []
        showError('文件載入失敗', '無法從伺服器取得文件清單，請檢查網路連線或確認已上傳文件。', error.response?.data)
      } finally {
        loadingDocuments.value = false
      }
    }

    const searchDocuments = () => {
      // 搜尋功能由 computed 屬性 filteredDocuments 處理
    }

    const selectTemplate = (template) => {
      selectedTemplate.value = template
    }

    const selectDocument = (document) => {
      toggleDocumentSelection(document)
    }

    const toggleDocumentSelection = traditionalDocumentSelector.toggleSelection

    // 傳統生成方法 - 使用完整模板資訊
    const generateTraditionalQuestions = async () => {
      if (!selectedTemplate.value || selectedDocuments.value.length === 0) return

      generating.value = true
      try {
        // 準備完整的模板資訊
        const templateData = {
          id: selectedTemplate.value.id,
          name: selectedTemplate.value.name,
          content: selectedTemplate.value.content,
          subject: selectedTemplate.value.subject,
          params: selectedTemplate.value.params || {},
          created_at: selectedTemplate.value.created_at,
          updated_at: selectedTemplate.value.updated_at
        }

        // 準備文件資訊
        const documentsData = selectedDocuments.value.map(doc => ({
          id: doc.id,
          title: doc.title,
          content: doc.content,
          chapter: doc.chapter,
          page: doc.page,
          subject: doc.subject
        }))

        // 使用新的 enhanced API
        const requestData = {
          template: templateData,
          documents: documentsData,
          count: traditionalCount.value,
          question_type: selectedTemplate.value.question_type || 'single_choice',
          target_grade: targetGrade.value || null,
          temperature: 0.7,
          max_tokens: 16384,
          model: 'claude-sonnet-4-20250514'
        }

        // 呼叫 Enhanced Template 驅動生成 API
        const response = await generateQuestionsByTemplateEnhanced(requestData)

        if (response.data && response.data.items) {
          generatedQuestions.value = response.data.items

          // 檢查是否有警告訊息
          if (response.data.warning) {
            showWarning('題目生成警告', response.data.warning)
          }

          // 如果是 fallback（完全失敗），顯示錯誤
          if (response.data.is_fallback) {
            showError('題目生成失敗', response.data.warning || '無法從所選文件生成有效題目')
          }
        } else {
          throw new Error('API 回應格式不正確')
        }

      } catch (error) {
        // 處理生成失敗
        errors.value.generation = {
          message: '題目生成失敗',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'ENHANCED_GENERATION_ERROR'
        }
        generatedQuestions.value = []

        // 顯示 Toast 錯誤通知
        toastError(
          `題目生成失敗：${error.response?.data?.detail || error.message}`,
          '考題生成',
          error
        )
      } finally {
        generating.value = false
      }
    }

    const exportQuestions = () => {
      const jsonContent = JSON.stringify(generatedQuestions.value, null, 2)
      const blob = new Blob([jsonContent], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `questions_${new Date().getTime()}.json`
      a.click()
      URL.revokeObjectURL(url)
    }

    const saveQuestions = async () => {
      if (generatedQuestions.value.length === 0) {
        toastError(isEnglish.value ? 'No questions to save!' : '沒有題目可儲存！', '儲存題目')
        return
      }

      saving.value = true
      try {
        // 獲取文件內容作為 source_content
        let sourceContent = '傳統生成'
        if (selectedDocuments.value.length > 0) {
          sourceContent = selectedDocuments.value.map(doc =>
            `Document: ${doc.title}\nContent: ${doc.content}`
          ).join('\n\n')
        }

        const sourceInfo = {
          documentId: selectedDocuments.value.length > 0 ? selectedDocuments.value[0].id : null,
          content: sourceContent,
          subject: selectedTemplate.value?.subject || 'General',
          chapter: selectedDocuments.value.length > 0 ? selectedDocuments.value[0].chapter : null,
          grade: targetGrade.value || null
        }

        const results = await saveQuestionsBatch(generatedQuestions.value, sourceInfo)
        const totalQuestions = generatedQuestions.value.length
        const successCount = results.success.length

        // 顯示結果
        if (successCount === totalQuestions) {
          showSuccess(isEnglish.value
              ? `Successfully saved all ${totalQuestions} questions!`
              : `成功儲存全部 ${totalQuestions} 道題目！`, '儲存題目')
        } else if (successCount > 0) {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.question} (${f.error})`).join('\n')
          toastError(isEnglish.value
              ? `Saved ${successCount}/${totalQuestions} questions.\n\nFailed questions:\n${failedDetails}`
              : `儲存了 ${successCount}/${totalQuestions} 道題目。\n\n失敗的題目：\n${failedDetails}`, '儲存題目')
        } else {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.error}`).join('\n')
          toastError(isEnglish.value
              ? `Failed to save any questions.\n\nErrors:\n${failedDetails}`
              : `所有題目儲存失敗。\n\n錯誤詳情：\n${failedDetails}`, '儲存題目')
        }

      } catch (error) {
        toastError(isEnglish.value
            ? 'An unexpected error occurred while saving questions.'
            : '儲存問題時發生未預期的錯誤。', '儲存題目', error)
      } finally {
        saving.value = false
      }
    }

    // 工具函數
    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || '未指定'
      return getQuestionTypeLabelUtil(type, t) || type
    }

    // 重置表單（清空全部設定）
    const resetForm = () => {
      // 模板相關
      selectedSubject.value = ''
      selectedTemplate.value = null

      // 文件相關
      selectedDocuments.value = []
      documentSearchQuery.value = ''
      selectedDocumentSubject.value = ''
      selectedDocumentGrade.value = ''

      // 生成相關
      generatedQuestions.value = []
      traditionalCount.value = 5
      targetGrade.value = ''

      // 清除錯誤狀態
      errors.value = {
        documents: null,
        templates: null,
        subjects: null,
        generation: null
      }
    }

    // 監聽科目變更，重置年級選擇
    watch(selectedDocumentSubject, () => {
      selectedDocumentGrade.value = ''
    })

    // 當模板或文件變更時，自動設定目標年級
    watch([selectedTemplate, selectedDocuments], ([template, docs]) => {
      // 優先使用模板的單一年級
      if (template?.grades?.length === 1) {
        targetGrade.value = template.grades[0]
        return
      }

      // 若模板無年級但文件只有單一年級，使用文件年級
      const docGrades = new Set()
      docs.forEach(doc => {
        if (doc.grade && doc.grade.trim()) {
          docGrades.add(doc.grade.trim())
        }
      })

      if (docGrades.size === 1) {
        targetGrade.value = Array.from(docGrades)[0]
        return
      }

      // 多個年級時，如果當前選擇不在可用選項中，重置
      const allGrades = new Set()
      if (template?.grades) {
        template.grades.forEach(g => allGrades.add(g))
      }
      docGrades.forEach(g => allGrades.add(g))

      if (targetGrade.value && !allGrades.has(targetGrade.value)) {
        targetGrade.value = ''
      }
    }, { deep: true })

    // 監聽語言變化
    watch(currentLanguage, async () => {
      await fetchTemplates()
    })

    // 生命週期
    onMounted(async () => {
      await fetchSubjects()
      await fetchSubjectList()
      await fetchTemplates()
      await fetchDocuments()
    })

    return {
      // 多語言
      t,
      isEnglish,
      currentLanguage,

      // 狀態
      generating,
      saving,
      loadingTemplates,
      loadingDocuments,
      templates,
      subjects,
      subjectList,
      selectedSubject,
      selectedTemplate,
      documents,
      selectedDocuments,
      documentSearchQuery,
      selectedDocumentSubject,
      selectedDocumentGrade,
      documentSubjects,
      traditionalCount,
      generatedQuestions,

      // 計算屬性
      filteredTemplates,
      filteredDocuments,
      previewContent,

      // 方法
      fetchTemplates,
      fetchSubjectList,
      refreshTemplates,
      searchDocuments,
      selectTemplate,
      selectDocument,
      toggleDocumentSelection,
      generateTraditionalQuestions,
      resetForm,
      exportQuestions,
      saveQuestions,
      getQuestionTypeLabel,

      // 錯誤處理
      errors,
      showErrorDialog,
      currentError,
      showError,
      clearError,

      // 警告處理
      showWarningDialog,
      currentWarning,
      showWarning,

      // 動態年級選項
      gradeOptions,

      // 目標年級
      targetGrade,
      availableGrades,

      // 預覽折疊
      showPreview,
      togglePreview
    }
  }
}
</script>

