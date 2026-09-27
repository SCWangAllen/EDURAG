<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 頁面標題 -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('generate.title') }}</h1>
        </div>
        <div>
          <BaseButton variant="secondary" :disabled="generating" @click="resetForm">
            🔄 {{ t('generate.clearAllSettings') || '清空全部設定' }}
          </BaseButton>
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
            @select-all-filtered="selectAllFilteredDocuments"
            @clear-selection="clearSelectedDocuments"
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
                max="20"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <!-- 配合題：每題配對組數 -->
            <div v-if="selectedTemplate && selectedTemplate.question_type === 'matching'" class="flex-1 min-w-[120px]">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('generate.matchingPairs') || '每題配對組數' }}
              </label>
              <input
                v-model.number="matchingPairs"
                type="number"
                min="2"
                max="20"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <!-- 問題類型（唯讀） -->
            <div v-if="selectedTemplate" class="flex-1 min-w-[150px]">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('ui.vw_question_type_label') }}</label>
              <div class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
                {{ getQuestionTypeLabel(selectedTemplate.question_type) }}
              </div>
            </div>

            <!-- 目標年級 -->
            <div v-if="availableGrades.length > 0" class="flex-1 min-w-[120px]">
              <FormSelect v-model="targetGrade" :label="t('generate.targetGrade') || '目標年級'">
                <option value="">-- {{ t('generate.selectGrade') || '請選擇' }} --</option>
                <option v-for="grade in availableGrades" :key="grade" :value="grade">
                  {{ grade }}
                </option>
              </FormSelect>
            </div>

            <!-- 生成按鈕 -->
            <div class="flex-shrink-0">
              <BaseButton
                variant="primary"
                class="px-8 h-[42px]"
                :disabled="!selectedTemplate || selectedDocuments.length === 0"
                :loading="generating"
                @click="generateTraditionalQuestions"
              >
                {{ generating ? t('generate.generating') || '生成中...' : t('generate.traditionalGenerate') || '生成題目' }}
              </BaseButton>
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
                {{ t('ui.vw_selected_docs_label') }} {{ selectedDocuments.map(d => d.title).join(', ') }}
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
  <BaseModal
    :model-value="showWarningDialog"
    size="md"
    :title="currentWarning?.title || t('ui.vw_warning_title')"
    @update:model-value="showWarningDialog = false"
  >
    <div class="sm:flex sm:items-start">
      <!-- 警告圖標 -->
      <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
        <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
        <div class="mt-2">
          <p class="text-sm text-gray-600 whitespace-pre-line">
            {{ currentWarning?.message }}
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        @click="showWarningDialog = false"
        class="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-yellow-600 text-base font-medium text-white hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 sm:text-sm"
      >
        {{ t('close') || '關閉' }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import templateService from '../api/templateService.js'
import documentService from '../api/documentService.js'
import { generateQuestionsByTemplateEnhanced, createQuestion } from '../api/questionService.js'
import { checkQuestion, checkLabel } from '../utils/questionChecks.js'
import { useLanguage } from '../composables/useLanguage.js'
import { useSubjects } from '../composables/useSubjects.js'
import { getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'
import { useToast } from '../composables/useToast.js'
import GenerationResults from '../components/Generate/GenerationResults.vue'
import TemplateSelector from '../components/Generate/TemplateSelector.vue'
import DocumentSelector from '../components/Generate/DocumentSelector.vue'
import BaseModal from '../components/Base/BaseModal.vue'
import BaseButton from '../components/Base/BaseButton.vue'
import FormSelect from '../components/Base/FormSelect.vue'

export default {
  name: 'Generate',
  components: {
    GenerationResults,
    TemplateSelector,
    DocumentSelector,
    BaseModal,
    BaseButton,
    FormSelect
  },
  setup() {
    // 多語言支持
    const { t, isEnglish, currentLanguage } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    // 科目資料唯一來源（取代寫死清單與從 documents/templates 去重）
    const { subjectNames, gradesFor, getGradeLabel, tree, ensureLoaded } = useSubjects()

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
    const subjects = subjectNames // 篩選器用的科目名稱（canonical key，單一來源）
    const subjectList = computed(() => tree.value.map(node => ({ name: node.name, color: node.color }))) // 顏色顯示用
    const selectedSubject = ref('')
    const selectedTemplate = ref(null) // 保留用於預覽

    // 文件相關
    const documents = ref([])
    const selectedDocuments = ref([])  // 傳統生成用
    const documentSearchQuery = ref('')
    const selectedDocumentSubject = ref('')  // 文件科目篩選
    const selectedDocumentGrade = ref('')    // 文件年級篩選
    const documentSubjects = subjectNames    // 文件科目清單（單一來源）
    const traditionalCount = ref(5)  // 傳統生成數量（預設 5 題）
    const matchingPairs = ref(10)  // 配合題每題配對組數（老師要求約 10 組）

    // 目標年級（生成時帶入）
    const targetGrade = ref('')

    // 動態年級選項（與科目連動，來源為 useSubjects 的科目→年級樹）
    const gradeOptions = computed(() =>
      gradesFor(selectedDocumentSubject.value).map(grade => ({
        value: grade,
        label: getGradeLabel(grade)
      }))
    )

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

        // 年級篩選（'ALL' 為全年級通用，任何年級選擇都命中）
        if (gradeFilter && gradeFilter.value) {
          filtered = filtered.filter(doc => doc.grade === gradeFilter.value || doc.grade === 'ALL')
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

    // 一次勾選目前篩選結果(已選的保留,不重複加入)
    const selectAllFilteredDocuments = () => {
      const existing = new Set(selectedDocuments.value.map(d => d.id))
      selectedDocuments.value = [
        ...selectedDocuments.value,
        ...filteredDocuments.value.filter(d => !existing.has(d.id))
      ]
    }
    const clearSelectedDocuments = () => {
      selectedDocuments.value = []
    }

    const previewContent = computed(() => {
      if (!selectedTemplate.value?.content) return ''

      let contextContent = t('ui.vw_sample_article_placeholder')

      if (selectedDocuments.value.length > 0) {
        // 顯示所有選中文件的完整內容
        contextContent = selectedDocuments.value.map(doc => {
          return `=== ${doc.title} ===\n${doc.chapter ? `${t('ui.vw_preview_chapter_label')}: ${doc.chapter}\n` : ''}${doc.content}`
        }).join('\n\n')
      }

      return selectedTemplate.value.content
        .replace(/\{context\}/g, contextContent)
        .replace(/\{count\}/g, traditionalCount.value)
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
          message: t('ui.vw_templates_load_error_msg'),
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        templates.value = []
        showError(t('ui.vw_templates_load_error_title'), t('ui.vw_templates_load_error_detail'), error.response?.data)
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

    const fetchDocuments = async () => {
      loadingDocuments.value = true
      try {
        // 不帶 size 參數時後端回傳全部文件（無數量限制）
        const data = await documentService.getDocuments()
        documents.value = data.documents || []

      } catch (error) {
        errors.value.documents = {
          message: t('ui.vw_documents_load_error_msg'),
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        documents.value = []
        showError(t('ui.vw_documents_load_error_title'), t('ui.vw_documents_load_error_detail'), error.response?.data)
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
          model: null,
          matching_pairs: Math.min(20, Math.max(2, Number(matchingPairs.value) || 10))
        }

        // 呼叫 Enhanced Template 驅動生成 API
        const response = await generateQuestionsByTemplateEnhanced(requestData)

        if (response.data && response.data.items) {
          generatedQuestions.value = response.data.items

          // 檢查是否有警告訊息
          if (response.data.warning) {
            showWarning(t('ui.vw_generation_warning_title'), response.data.warning)
          }

          // 如果是 fallback（完全失敗），顯示錯誤
          if (response.data.is_fallback) {
            showError(t('ui.vw_generation_failed_title'), response.data.warning || t('ui.vw_generation_no_valid_questions'))
          }
        } else {
          throw new Error(t('ui.vw_invalid_api_response'))
        }

      } catch (error) {
        // 處理生成失敗
        errors.value.generation = {
          message: t('ui.vw_generation_failed_title'),
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'ENHANCED_GENERATION_ERROR'
        }
        generatedQuestions.value = []

        // 顯示 Toast 錯誤通知
        toastError(
          t('ui.vw_generation_failed_toast').replace('{detail}', error.response?.data?.detail || error.message),
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
        toastError(t('ui.vw_no_questions_to_save'), '儲存題目')
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

        // 儲存前先做格式檢核:不合格的略過並提示(後端存檔時也會再檢一次)
        const problems = generatedQuestions.value.map(q => checkQuestion(q))
        const toSave = generatedQuestions.value.filter((_, i) => !problems[i])
        const skipped = problems.filter(Boolean)
        if (skipped.length > 0) {
          const summary = [...new Set(skipped)].map(k => checkLabel(k, t)).join('、')
          showWarning(
            t('ui.vw_generation_warning_title'),
            (t('generate.check_skipped') || '{count} 題格式有問題，已略過未儲存：{reasons}')
              .replace('{count}', skipped.length).replace('{reasons}', summary)
          )
        }
        if (toSave.length === 0) {
          toastError(t('generate.check_none_valid') || '所有題目都未通過格式檢核，沒有可儲存的題目', '儲存題目')
          return
        }

        const results = await saveQuestionsBatch(toSave, sourceInfo)
        const totalQuestions = toSave.length
        const successCount = results.success.length

        // 顯示結果
        if (successCount === totalQuestions) {
          showSuccess(t('ui.vw_save_all_success').replace('{count}', totalQuestions), '儲存題目')
        } else if (successCount > 0) {
          const failedDetails = results.failed.map(f =>
            t('ui.vw_failed_item_detail')
              .replace('{index}', f.index)
              .replace('{question}', f.question)
              .replace('{error}', f.error)
          ).join('\n')
          toastError(
            t('ui.vw_save_partial_result')
              .replace('{success}', successCount)
              .replace('{total}', totalQuestions)
              .replace('{details}', failedDetails),
            '儲存題目'
          )
        } else {
          const failedDetails = results.failed.map(f =>
            t('ui.vw_failed_item_detail_short')
              .replace('{index}', f.index)
              .replace('{error}', f.error)
          ).join('\n')
          toastError(
            t('ui.vw_save_all_failed').replace('{details}', failedDetails),
            '儲存題目'
          )
        }

      } catch (error) {
        toastError(t('ui.vw_save_unexpected_error'), '儲存題目', error)
      } finally {
        saving.value = false
      }
    }

    // 工具函數
    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || t('ui.vw_unspecified')
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

    // 換科目時:新科目底下還有該年級的文件就保留年級篩選,否則才清掉
    watch(selectedDocumentSubject, (subject) => {
      const grade = selectedDocumentGrade.value
      if (!grade) return
      const stillValid = documents.value.some(
        d => (!subject || d.subject === subject) && (d.grade === grade || d.grade === 'ALL')
      )
      if (!stillValid) selectedDocumentGrade.value = ''
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
      await ensureLoaded()
      await fetchTemplates()
      await fetchDocuments()
    })

    // 頁面被 keep-alive 快取後再次切回時,重新整理模板/文件清單(保留已選科目/文件等狀態)
    let isFirstActivation = true
    onActivated(() => {
      if (isFirstActivation) {
        isFirstActivation = false
        return
      }
      fetchTemplates()
      fetchDocuments()
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
      matchingPairs,
      generatedQuestions,

      // 計算屬性
      filteredTemplates,
      filteredDocuments,
      previewContent,

      // 方法
      fetchTemplates,
      refreshTemplates,
      searchDocuments,
      selectTemplate,
      selectDocument,
      selectAllFilteredDocuments,
      clearSelectedDocuments,
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

