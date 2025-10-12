<template>
  <div class="generate-panel">
    <!-- 模板選擇 -->
    <div class="section">
      <h3 class="section-title">📋 選擇模板</h3>
      <p class="section-desc">選擇一個生成模板，或使用預設模板</p>

      <div class="template-selector">
        <select v-model="selectedTemplateId" class="form-select">
          <option :value="null">{{ t('generate.noTemplatesAvailable') || '無可用模板（將使用預設）' }}</option>
          <option v-for="template in filteredTemplates" :key="template.id" :value="template.id">
            {{ template.name }} ({{ template.question_type }})
          </option>
        </select>

        <div v-if="selectedTemplate" class="template-info">
          <div class="info-row">
            <span class="label">科目：</span>
            <span class="value">{{ selectedTemplate.subject }}</span>
          </div>
          <div class="info-row">
            <span class="label">題型：</span>
            <span class="value">{{ t(`generate.${selectedTemplate.question_type}`) }}</span>
          </div>
        </div>

        <!-- 模板匹配提示 -->
        <div v-if="filteredTemplates.length === 0" class="template-hint warning">
          ⚠️ 目前沒有 {{ props.examInfo.subject }} 科目的專用模板，系統將使用通用模板生成
        </div>
        <div v-else-if="!selectedTemplate" class="template-hint info">
          💡 未選擇模板時，系統會自動為每個題型匹配最合適的模板
        </div>
      </div>
    </div>

    <!-- 文件選擇 -->
    <div class="section">
      <h3 class="section-title">📚 選擇文件</h3>
      <p class="section-desc">選擇一個或多個文件作為生成來源</p>

      <!-- 文件篩選 -->
      <div class="filters">
        <div class="filter-group">
          <label class="filter-label">科目</label>
          <select v-model="documentFilters.subject" class="form-select-sm">
            <option value="">全部</option>
            <option v-for="subject in documentSubjects" :key="subject" :value="subject">
              {{ subject }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">年級</label>
          <select v-model="documentFilters.grade" class="form-select-sm">
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

        <div class="filter-group flex-grow">
          <label class="filter-label">搜尋</label>
          <input
            v-model="documentFilters.search"
            type="text"
            placeholder="搜尋文件..."
            class="form-input-sm"
          />
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="document-list">
        <div v-if="loadingDocuments" class="loading-state">
          <div class="spinner"></div>
          <p>載入文件中...</p>
        </div>

        <div v-else-if="filteredDocuments.length === 0" class="empty-state">
          <p>沒有符合條件的文件</p>
        </div>

        <div v-else class="document-items">
          <div
            v-for="doc in filteredDocuments"
            :key="doc.id"
            @click="toggleDocument(doc)"
            :class="['document-item', { selected: isDocumentSelected(doc.id) }]"
          >
            <div class="doc-checkbox">
              <input type="checkbox" :checked="isDocumentSelected(doc.id)" />
            </div>
            <div class="doc-info">
              <div class="doc-title">{{ doc.title }}</div>
              <div class="doc-meta">
                <span v-if="doc.subject" class="meta-badge subject">{{ doc.subject }}</span>
                <span v-if="doc.grade" class="meta-badge grade">{{ doc.grade }}</span>
                <span v-if="doc.chapter" class="meta-text">{{ doc.chapter }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="selection-summary">
        已選擇 <strong>{{ selectedDocuments.length }}</strong> 個文件
      </div>
    </div>

    <!-- 生成按鈕 -->
    <div class="generate-actions">
      <button
        @click="handleGenerate"
        :disabled="!canGenerate || isGenerating"
        class="btn-generate"
      >
        <span v-if="isGenerating" class="spinner-sm"></span>
        <span v-else>🤖</span>
        {{ isGenerating ? t('generate.generating') : t('generate.generateQuestions') }}
      </button>

      <div v-if="!canGenerate" class="validation-hint">
        <span v-if="selectedDocuments.length === 0">⚠️ 請至少選擇一個文件</span>
        <span v-else-if="totalQuestions === 0">⚠️ 請在題型配置中設定題目數量</span>
      </div>
    </div>

    <!-- 生成進度 -->
    <div v-if="isGenerating" class="progress-panel">
      <div class="progress-header">
        <h4>生成進度</h4>
        <span>{{ completedTypes.length }} / {{ enabledTypes.length }}</span>
      </div>

      <div class="progress-list">
        <div
          v-for="typeInfo in enabledTypes"
          :key="typeInfo.type"
          :class="['progress-item', {
            'completed': isTypeCompleted(typeInfo.type),
            'generating': isTypeGenerating(typeInfo.type),
            'pending': !isTypeCompleted(typeInfo.type) && !isTypeGenerating(typeInfo.type)
          }]"
        >
          <div class="progress-icon">
            <span v-if="isTypeCompleted(typeInfo.type)">✓</span>
            <span v-else-if="isTypeGenerating(typeInfo.type)" class="spinner-sm"></span>
            <span v-else>⏳</span>
          </div>
          <div class="progress-text">
            {{ getTypeName(typeInfo.type) }} - {{ typeInfo.count }} 題
          </div>
        </div>
      </div>

      <!-- 儲存進度 -->
      <div v-if="savingStatus.isSaving || savingStatus.total > 0" class="saving-status">
        <div class="saving-header">
          <span>💾 儲存進度</span>
          <span v-if="savingStatus.isSaving" class="spinner-sm"></span>
        </div>
        <div class="saving-stats">
          <span class="stat-success">✓ 成功: {{ savingStatus.saved }}</span>
          <span v-if="savingStatus.failed > 0" class="stat-failed">✗ 失敗: {{ savingStatus.failed }}</span>
          <span class="stat-total">總計: {{ savingStatus.total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import templateService from '../../api/templateService.js'
import documentService from '../../api/documentService.js'
import { generateQuestionsByTemplateEnhanced, createQuestion } from '../../api/questionService.js'
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

const emit = defineEmits(['generated', 'error'])

// ==================== 狀態 ====================

const templates = ref([])
const selectedTemplateId = ref(null)
const loadingTemplates = ref(false)

const documents = ref([])
const selectedDocuments = ref([])
const loadingDocuments = ref(false)

const documentSubjects = ref([])
const documentFilters = ref({
  subject: '',
  grade: '',
  search: ''
})

const isGenerating = ref(false)
const currentGeneratingType = ref(null)
const completedTypes = ref([])

// 儲存狀態追蹤
const savingStatus = ref({
  total: 0,
  saved: 0,
  failed: 0,
  isSaving: false
})

// ==================== 計算屬性 ====================

const selectedTemplate = computed(() => {
  if (!selectedTemplateId.value) return null
  return templates.value.find(t => t.id === selectedTemplateId.value)
})

const filteredTemplates = computed(() => {
  if (!props.examInfo.subject) return templates.value
  return templates.value.filter(t => t.subject === props.examInfo.subject)
})

const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 科目篩選
  if (documentFilters.value.subject) {
    filtered = filtered.filter(doc => doc.subject === documentFilters.value.subject)
  }

  // 年級篩選
  if (documentFilters.value.grade) {
    filtered = filtered.filter(doc => doc.grade === documentFilters.value.grade)
  }

  // 搜尋篩選
  if (documentFilters.value.search) {
    const query = documentFilters.value.search.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(query) ||
      (doc.chapter && doc.chapter.toLowerCase().includes(query))
    )
  }

  return filtered
})

const enabledTypes = computed(() => {
  return Object.entries(props.questionTypeConfig)
    .filter(([_, config]) => config.enabled && config.count > 0)
    .map(([type, config]) => ({
      type,
      count: config.count,
      points: config.points,
      order: config.order
    }))
    .sort((a, b) => a.order - b.order)
})

const totalQuestions = computed(() => {
  return enabledTypes.value.reduce((sum, t) => sum + t.count, 0)
})

const canGenerate = computed(() => {
  return selectedDocuments.value.length > 0 && totalQuestions.value > 0
})

// ==================== 方法 ====================

const isDocumentSelected = (docId) => {
  return selectedDocuments.value.some(d => d.id === docId)
}

const toggleDocument = (doc) => {
  const index = selectedDocuments.value.findIndex(d => d.id === doc.id)
  if (index > -1) {
    selectedDocuments.value.splice(index, 1)
  } else {
    selectedDocuments.value.push(doc)
  }
}

const isTypeCompleted = (type) => {
  return completedTypes.value.includes(type)
}

const isTypeGenerating = (type) => {
  return currentGeneratingType.value === type
}

const getTypeName = (type) => {
  return t(`generate.${type}`) || type
}

// 批次儲存題目到資料庫
const saveQuestionsToDatabase = async (questions, questionType) => {
  const results = []

  console.log(`💾 開始儲存 ${questions.length} 題 ${questionType} 到資料庫...`)

  for (const question of questions) {
    try {
      // 使用後端 API 要求的欄位名稱
      const questionData = {
        type: questionType,  // ✅ 使用 'type' (對應 QuestionCreate.type)
        content: question.prompt,  // ✅ 使用 'content' (對應 QuestionCreate.content)
        options: question.options || null,
        correct_answer: typeof question.answer === 'object'
          ? JSON.stringify(question.answer)
          : String(question.answer),  // ✅ 使用 'correct_answer'
        explanation: question.explanation || '',
        subject: props.examInfo.subject,
        grade: props.examInfo.grade,
        difficulty: 'medium'
        // 移除 tags 和 metadata（QuestionCreate Schema 不支援）
      }

      const response = await createQuestion(questionData)

      results.push({
        id: response.data.id,
        success: true,
        originalData: question
      })

      savingStatus.value.saved++
      console.log(`✅ 儲存成功: ${question.prompt.substring(0, 30)}... (ID: ${response.data.id})`)

    } catch (error) {
      console.error(`❌ 儲存失敗: ${question.prompt.substring(0, 30)}...`, error)
      results.push({
        id: null,
        success: false,
        error: error.response?.data?.detail || error.message,
        originalData: question
      })

      savingStatus.value.failed++
    }
  }

  return results
}

const handleGenerate = async () => {
  if (!canGenerate.value) return

  isGenerating.value = true
  completedTypes.value = []
  currentGeneratingType.value = null

  // 重置儲存狀態
  savingStatus.value = {
    total: 0,
    saved: 0,
    failed: 0,
    isSaving: false
  }

  const allQuestions = []
  const errors = []

  try {
    // 逐個題型生成
    for (const typeInfo of enabledTypes.value) {
      currentGeneratingType.value = typeInfo.type

      try {
        // 找到該題型的模板（如果有）
        let template = selectedTemplate.value

        // 如果沒選模板或模板題型不符，嘗試找合適的
        if (!template || template.question_type !== typeInfo.type) {
          // 先嘗試找同科目的模板
          template = templates.value.find(t =>
            t.question_type === typeInfo.type &&
            t.subject === props.examInfo.subject
          )

          // 如果找不到，使用任何匹配題型的模板作為通用模板
          if (!template) {
            template = templates.value.find(t => t.question_type === typeInfo.type)
            if (template) {
              console.log(`⚠️ 使用通用模板 (${template.subject}) 生成 ${typeInfo.type}`)
            }
          }
        }

        // 準備文件資料
        const documentsData = selectedDocuments.value.map(doc => ({
          id: doc.id,
          title: doc.title,
          content: doc.content || doc.slice_text || '',
          chapter: doc.chapter,
          page: doc.page,
          subject: doc.subject,
          grade: doc.grade
        }))

        // 如果還是沒有模板，跳過此題型
        if (!template) {
          console.warn(`❌ 找不到任何 ${typeInfo.type} 的模板，跳過此題型`)
          errors.push({
            type: typeInfo.type,
            message: `找不到對應的模板`
          })
          completedTypes.value.push(typeInfo.type)
          continue
        }

        // 調用 API 生成題目
        const requestData = {
          template: {
            id: template.id,
            name: template.name,
            content: template.content,
            subject: template.subject,
            params: template.params || {},
            question_type: template.question_type
          },
          documents: documentsData,
          count: typeInfo.count,
          question_type: typeInfo.type,
          temperature: 0.7,
          max_tokens: 2000,
          model: 'claude-3-5-sonnet-20241022'
        }

        console.log(`🤖 生成 ${typeInfo.type} - ${typeInfo.count} 題`)

        const response = await generateQuestionsByTemplateEnhanced(requestData)

        if (response.data && response.data.items) {
          const generatedQuestions = response.data.items
          console.log(`✅ ${typeInfo.type} 完成，生成 ${generatedQuestions.length} 題`)

          // 🆕 儲存到資料庫
          savingStatus.value.total += generatedQuestions.length
          savingStatus.value.isSaving = true

          const saveResults = await saveQuestionsToDatabase(generatedQuestions, typeInfo.type)

          // 將資料庫 ID 合併到題目資料
          const questionsWithIds = generatedQuestions.map((q, idx) => ({
            ...q,
            id: saveResults[idx]?.id || null,
            saved: saveResults[idx]?.success || false,
            save_error: saveResults[idx]?.error || null
          }))

          allQuestions.push(...questionsWithIds)

          // 檢查警告
          if (response.data.warning) {
            console.warn(`⚠️ ${typeInfo.type} 警告:`, response.data.warning)
          }
        }

        completedTypes.value.push(typeInfo.type)

      } catch (error) {
        console.error(`❌ ${typeInfo.type} 生成失敗:`, error)
        errors.push({
          type: typeInfo.type,
          message: error.response?.data?.detail || error.message
        })
        // 繼續生成其他題型
        completedTypes.value.push(typeInfo.type)
      }

      // 短暫延遲避免 API 過載
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    savingStatus.value.isSaving = false

    // 生成完成
    if (allQuestions.length > 0) {
      // 顯示儲存摘要
      const saveMessage = `生成 ${allQuestions.length} 題，儲存 ${savingStatus.value.saved} 題成功`

      if (savingStatus.value.failed > 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: `${saveMessage}，${savingStatus.value.failed} 題儲存失敗`,
          operation: 'AI 生成並儲存'
        })
      } else {
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: saveMessage,
          operation: 'AI 生成並儲存'
        })
      }

      emit('generated', {
        questions: allQuestions,
        total: allQuestions.length,
        saved: savingStatus.value.saved,
        failed: savingStatus.value.failed,
        errors: errors.length > 0 ? errors : null
      })
    } else {
      emit('error', {
        message: '所有題型生成均失敗',
        errors
      })
    }

  } catch (error) {
    console.error('生成過程發生錯誤:', error)
    emit('error', {
      message: '生成過程發生錯誤: ' + error.message
    })
  } finally {
    isGenerating.value = false
    currentGeneratingType.value = null
    savingStatus.value.isSaving = false
  }
}

// 載入模板
const loadTemplates = async () => {
  loadingTemplates.value = true
  try {
    const data = await templateService.getTemplates()
    templates.value = data.templates || []
    console.log('載入模板:', templates.value.length)
  } catch (error) {
    console.error('載入模板失敗:', error)
    templates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// 載入文件
const loadDocuments = async () => {
  loadingDocuments.value = true
  try {
    const data = await documentService.getDocuments({ size: 100 })
    documents.value = data.documents || []

    // 提取科目列表
    const subjects = new Set()
    documents.value.forEach(doc => {
      if (doc.subject) subjects.add(doc.subject)
    })
    documentSubjects.value = Array.from(subjects).sort()

    console.log('載入文件:', documents.value.length)
  } catch (error) {
    console.error('載入文件失敗:', error)
    documents.value = []
  } finally {
    loadingDocuments.value = false
  }
}

// 根據考券資訊自動篩選
watch(() => props.examInfo.subject, (newSubject) => {
  documentFilters.value.subject = newSubject
})

watch(() => props.examInfo.grade, (newGrade) => {
  documentFilters.value.grade = newGrade
})

// ==================== 生命週期 ====================

onMounted(() => {
  loadTemplates()
  loadDocuments()

  // 自動設定篩選
  if (props.examInfo.subject) {
    documentFilters.value.subject = props.examInfo.subject
  }
  if (props.examInfo.grade) {
    documentFilters.value.grade = props.examInfo.grade
  }
})
</script>

<style scoped>
.generate-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Section */
.section {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.section-desc {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

/* Template Selector */
.template-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.template-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.template-hint {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  line-height: 1.5;
}

.template-hint.warning {
  background: #fef3c7;
  border: 1px solid #fbbf24;
  color: #92400e;
}

.template-hint.info {
  background: #dbeafe;
  border: 1px solid #3b82f6;
  color: #1e40af;
}

.info-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  color: #6b7280;
  font-weight: 500;
}

.info-row .value {
  color: #111827;
}

/* Filters */
.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group.flex-grow {
  flex: 1;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
}

/* Form Elements */
.form-select,
.form-select-sm,
.form-input-sm {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.form-select-sm,
.form-input-sm {
  padding: 0.375rem 0.5rem;
  font-size: 0.8125rem;
}

.form-select:focus,
.form-select-sm:focus,
.form-input-sm:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Document List */
.document-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background: white;
}

.loading-state,
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.document-items {
  display: flex;
  flex-direction: column;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.document-item:hover {
  background-color: #f9fafb;
}

.document-item.selected {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.doc-checkbox input {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.doc-info {
  flex: 1;
}

.doc-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.meta-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.meta-badge.subject {
  background: #dbeafe;
  color: #1e40af;
}

.meta-badge.grade {
  background: #e9d5ff;
  color: #7c3aed;
}

.meta-text {
  font-size: 0.75rem;
  color: #6b7280;
}

.selection-summary {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: #eff6ff;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1e40af;
  text-align: center;
}

/* Generate Actions */
.generate-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.btn-generate {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 200px;
}

.btn-generate:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.btn-generate:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.validation-hint {
  font-size: 0.875rem;
  color: #dc2626;
}

/* Progress Panel */
.progress-panel {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.progress-header h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.progress-item.completed {
  border-color: #10b981;
  background: #f0fdf4;
}

.progress-item.generating {
  border-color: #3b82f6;
  background: #eff6ff;
}

.progress-item.pending {
  opacity: 0.6;
}

.progress-icon {
  font-size: 1.25rem;
}

.progress-text {
  font-size: 0.875rem;
  color: #374151;
}

/* Spinner */
.spinner,
.spinner-sm {
  border: 2px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner {
  width: 2rem;
  height: 2rem;
}

.spinner-sm {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Saving Status */
.saving-status {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
}

.saving-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e40af;
}

.saving-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.875rem;
}

.stat-success {
  color: #059669;
  font-weight: 500;
}

.stat-failed {
  color: #dc2626;
  font-weight: 500;
}

.stat-total {
  color: #6b7280;
  font-weight: 500;
}
</style>
