<template>
  <div class="generate-panel-tabbed">
    <!-- 題型 Tabs -->
    <QuestionTypeTabs
      v-model="activeType"
      :types="enabledTypes"
      :stats="generationStats"
    />

    <!-- 當前題型的生成介面 -->
    <div class="tab-content">
      <TypeGenerateSection
        v-for="typeInfo in enabledTypes"
        :key="typeInfo.type"
        v-show="activeType === typeInfo.type"
        :type="typeInfo.type"
        :count="typeInfo.count"
        :exam-info="examInfo"
        :templates="templates"
        :questions="getQuestionsByType(typeInfo.type)"
        :is-generating="isGenerating && currentGeneratingType === typeInfo.type"
        @generate="handleGenerate"
        @toggle-selection="handleToggleSelection"
        @remove-question="handleRemoveQuestion"
        @clear-unselected="handleClearUnselected"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import QuestionTypeTabs from './QuestionTypeTabs.vue'
import TypeGenerateSection from './TypeGenerateSection.vue'
import templateService from '../../api/templateService.js'
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
const loadingTemplates = ref(false)

// 當前活動的題型 Tab
const activeType = ref(null)

// 生成狀態
const isGenerating = ref(false)
const currentGeneratingType = ref(null)

// 按題型儲存已生成的題目
const generatedQuestionsByType = ref({})

// ==================== 計算屬性 ====================

const enabledTypes = computed(() => {
  const types = Object.entries(props.questionTypeConfig)
    .filter(([_, config]) => config.enabled && config.count > 0)
    .map(([type, config]) => ({
      type,
      count: config.count,
      points: config.points,
      order: config.order
    }))
    .sort((a, b) => a.order - b.order)

  return types
})

// 生成統計（用於 Tabs 顯示）
const generationStats = computed(() => {
  const stats = {}
  Object.keys(generatedQuestionsByType.value).forEach(type => {
    const questions = generatedQuestionsByType.value[type] || []
    stats[type] = {
      generated: questions.length,
      selected: questions.filter(q => q.selected).length
    }
  })
  return stats
})

// ==================== 方法 ====================

// 獲取該題型的題目
const getQuestionsByType = (type) => {
  return generatedQuestionsByType.value[type] || []
}

// 自動匹配模板
const findTemplateForType = (type, preferredSubject = null) => {
  // 優先找同科目 + 題型的模板
  if (preferredSubject) {
    const matched = templates.value.find(t =>
      t.question_type === type && t.subject === preferredSubject
    )
    if (matched) {
      return matched
    }
  }

  // Fallback 到任何匹配題型的模板
  const fallback = templates.value.find(t => t.question_type === type)
  if (fallback) {
  }
  return fallback
}

// 儲存題目到資料庫
const saveQuestionsToDatabase = async (questions, questionType) => {
  const results = []


  for (const question of questions) {
    try {
      const questionData = {
        type: questionType,
        content: question.content || question.prompt,
        options: question.options || null,
        correct_answer: typeof question.answer === 'object'
          ? JSON.stringify(question.answer)
          : String(question.answer),
        explanation: question.explanation || '',
        subject: props.examInfo.subject,
        grade: props.examInfo.grade,
        difficulty: 'medium'
      }

      const response = await createQuestion(questionData)

      results.push({
        id: response.data.id,
        success: true,
        originalData: question
      })


    } catch (error) {
      results.push({
        id: null,
        success: false,
        error: error.response?.data?.detail || error.message,
        originalData: question
      })
    }
  }

  return results
}

// 處理生成請求
const handleGenerate = async ({ type, count, documents, template }) => {

  if (documents.length === 0) {
    eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
      message: '請至少選擇一個文件',
      operation: '生成題目'
    })
    return
  }

  isGenerating.value = true
  currentGeneratingType.value = type

  try {
    // 1️⃣ 獲取模板
    const useTemplate = template || findTemplateForType(type, props.examInfo.subject)

    if (!useTemplate) {
      throw new Error(`找不到適合 ${type} 的模板`)
    }


    // 2️⃣ 準備文件資料
    const documentsData = documents.map(doc => ({
      id: doc.id,
      title: doc.title,
      content: doc.content || doc.slice_text || '',
      chapter: doc.chapter,
      page: doc.page,
      subject: doc.subject,
      grade: doc.grade
    }))

    // 3️⃣ 調用 Enhanced API 生成
    const requestData = {
      template: {
        id: useTemplate.id,
        name: useTemplate.name,
        content: useTemplate.content,
        subject: useTemplate.subject,
        params: useTemplate.params || {},
        question_type: useTemplate.question_type
      },
      documents: documentsData,
      count: count,
      question_type: type,
      temperature: 0.7,
      max_tokens: 16384,  // Claude 3.7 Sonnet 最大限制
      model: 'claude-3-7-sonnet-20250219'
    }


    const response = await generateQuestionsByTemplateEnhanced(requestData)

    if (!response.data?.items) {
      throw new Error('API 回應格式錯誤')
    }

    const generatedQuestions = response.data.items

    // 4️⃣ 加上 _meta
    const questionsWithMeta = generatedQuestions.map(q => ({
      ...q,
      _meta: {
        type,
        templateId: useTemplate.id,
        templateName: useTemplate.name,
        documentIds: documents.map(d => d.id),
        documentNames: documents.map(d => d.title).join(', ')
      }
    }))

    // 5️⃣ 儲存到資料庫
    const saveResults = await saveQuestionsToDatabase(questionsWithMeta, type)

    // 6️⃣ 合併資料庫 ID 並預設勾選
    const savedQuestions = questionsWithMeta.map((q, idx) => ({
      ...q,
      id: saveResults[idx]?.id || null,
      saved: saveResults[idx]?.success || false,
      save_error: saveResults[idx]?.error || null,
      selected: true  // 🆕 預設勾選
    }))

    const savedCount = saveResults.filter(r => r.success).length
    const failedCount = saveResults.filter(r => !r.success).length


    // 7️⃣ 加入到該題型的列表
    if (!generatedQuestionsByType.value[type]) {
      generatedQuestionsByType.value[type] = []
    }
    generatedQuestionsByType.value[type].push(...savedQuestions)

    // 8️⃣ 發送更新事件
    emitSelectionChange()

    // 9️⃣ 顯示成功訊息
    if (failedCount > 0) {
      eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
        message: `生成 ${generatedQuestions.length} 題，儲存 ${savedCount} 題成功，${failedCount} 題失敗`,
        operation: `生成 ${t(`generate.${type}`)}`
      })
    } else {
      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: `成功生成並儲存 ${savedCount} 題 ${t(`generate.${type}`)}`,
        operation: '生成題目'
      })
    }

  } catch (error) {
    eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
      message: error.message || '題目生成失敗',
      operation: `生成 ${t(`generate.${type}`)}`
    })

    emit('error', {
      message: error.message || '題目生成失敗',
      type
    })

  } finally {
    isGenerating.value = false
    currentGeneratingType.value = null
  }
}

// 處理題目勾選/取消
const handleToggleSelection = ({ type, question }) => {
  const questions = generatedQuestionsByType.value[type]
  const target = questions.find(q => q.id === question.id)
  if (target) {
    target.selected = !target.selected
    emitSelectionChange()
  }
}

// 處理題目刪除
const handleRemoveQuestion = ({ type, question }) => {
  const questions = generatedQuestionsByType.value[type]
  const index = questions.findIndex(q => q.id === question.id)
  if (index > -1) {
    questions.splice(index, 1)
    emitSelectionChange()
  }
}

// 清空未選用的題目
const handleClearUnselected = (type) => {
  const questions = generatedQuestionsByType.value[type]
  const beforeCount = questions.length
  generatedQuestionsByType.value[type] = questions.filter(q => q.selected)
  const afterCount = generatedQuestionsByType.value[type].length
  const removedCount = beforeCount - afterCount


  eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
    message: `已清空 ${removedCount} 題未選用的 ${t(`generate.${type}`)}`,
    operation: '清空未選用'
  })

  emitSelectionChange()
}

// 發送選擇變化事件（同步到 ExamPaper）
const emitSelectionChange = () => {
  // 收集所有被勾選的題目
  const selectedQuestions = []
  const typeStats = {}

  Object.keys(generatedQuestionsByType.value).forEach(type => {
    const questions = generatedQuestionsByType.value[type] || []
    const selected = questions.filter(q => q.selected)
    selectedQuestions.push(...selected)

    if (selected.length > 0) {
      typeStats[type] = selected.length
    }
  })


  // 發送給 ExamPaper
  emit('generated', {
    questions: selectedQuestions,
    total: selectedQuestions.length,
    typeStats: typeStats
  })
}

// 載入模板
const loadTemplates = async () => {
  loadingTemplates.value = true
  try {
    const data = await templateService.getTemplates()
    templates.value = data.templates || []
  } catch (error) {
    templates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// ==================== 監聽器 ====================

// 監聯 activeType 變化
watch(activeType, () => {
})

// 監聽 enabledTypes 變化，自動更新 activeType
watch(enabledTypes, (newTypes) => {
  if (newTypes.length > 0) {
    const currentTypeExists = newTypes.some(t => t.type === activeType.value)
    if (!currentTypeExists || !activeType.value) {
      activeType.value = newTypes[0].type
    }
  } else {
    activeType.value = null
  }
}, { deep: true })

// ==================== 生命週期 ====================

onMounted(() => {
  loadTemplates()

  // 初始化題型列表
  Object.keys(props.questionTypeConfig).forEach(type => {
    if (!generatedQuestionsByType.value[type]) {
      generatedQuestionsByType.value[type] = []
    }
  })

  // 設定預設的 active tab
  if (enabledTypes.value.length > 0) {
    activeType.value = enabledTypes.value[0].type
  }
})
</script>

<style scoped>
.generate-panel-tabbed {
  /* Tab-based 佈局容器 */
}

.tab-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  padding: 1.5rem;
  min-height: 400px;
}
</style>
