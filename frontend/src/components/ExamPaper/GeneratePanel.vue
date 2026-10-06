<template>
  <div>
    <!-- 題型 Tabs -->
    <QuestionTypeTabs
      v-model="activeType"
      :types="enabledTypes"
      :stats="generationStats"
    />

    <!-- 當前題型的生成介面 -->
    <div class="bg-white border-x border-b border-gray-200 rounded-b-lg p-6 min-h-[400px]">
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
        @scope-range="handleScopeRange"
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
import { generationUnitParams } from '@/utils/scoringUnits.js'

// 每個題型各有一個教材選擇器:記下各自選到的頁碼範圍,取聯集往上拋(由 ExamPaper 決定
// 要不要寫進副標),整張考卷的範圍才不會只反映最後點到的那個題型
const scopeRanges = {}
const handleScopeRange = ({ type, range }) => {
  if (range) scopeRanges[type] = range
  else delete scopeRanges[type]
  const ranges = Object.values(scopeRanges)
  if (ranges.length === 0) {
    emit('scope-range', null)
    return
  }
  emit('scope-range', {
    from: Math.min(...ranges.map(r => r.from)),
    to: Math.max(...ranges.map(r => r.to))
  })
}
import QuestionTypeTabs from './QuestionTypeTabs.vue'
import TypeGenerateSection from './TypeGenerateSection.vue'
import templateService from '../../api/templateService.js'
import { generateQuestionsByTemplateEnhanced, createQuestion } from '../../api/questionService.js'
import documentService from '../../api/documentService.js'
import { useToast } from '@/composables/useToast.js'

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

const emit = defineEmits(['generated', 'error', 'scope-range'])

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
        difficulty: 'medium',
        question_data: question.question_data || null  // 配對題的 left_items/right_items
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
    toastError(t('ui.ed_select_at_least_one_doc'), t('ui.ed_generate_questions_op'))
    return
  }

  isGenerating.value = true
  currentGeneratingType.value = type

  try {
    // 1️⃣ 獲取模板
    const useTemplate = template || findTemplateForType(type, props.examInfo.subject)

    if (!useTemplate) {
      throw new Error(t('ui.ed_no_suitable_template_error').replace('{type}', type))
    }


    // 2️⃣ 準備文件資料(教材清單只載摘要,沒有內文的這裡依 id 一次補抓)
    const missingIds = documents.filter(doc => !doc.content && !doc.slice_text).map(doc => doc.id)
    const contentById = {}
    // 後端一次最多 200 個 id;全選 2,000 多筆教材時分批抓
    for (let i = 0; i < missingIds.length; i += 200) {
      const full = await documentService.getDocumentsByIds(missingIds.slice(i, i + 200))
      ;(full.documents || []).forEach(doc => { contentById[doc.id] = doc.content || '' })
    }
    const documentsData = documents.map(doc => ({
      id: doc.id,
      title: doc.title,
      content: doc.content || doc.slice_text || contentById[doc.id] || '',
      chapter: doc.chapter,
      page: doc.page,
      subject: doc.subject,
      grade: doc.grade
    }))
    // 選了之後被刪掉、或本來就沒內文的教材不送給模型;全部沒內文就直接報錯
    const usableDocuments = documentsData.filter(doc => doc.content && doc.content.trim())
    if (usableDocuments.length === 0) {
      throw new Error(t('ui.ed_documents_missing_content'))
    }

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
      documents: usableDocuments,
      count: count,
      question_type: type,
      temperature: 0.7,
      max_tokens: 16384,  // Claude Sonnet 4 最大限制
      model: null,  // 送 null 由後端全域模型設定決定
      // Step 2 的「每題幾格」當生成條件(配對組數 / 填充空格數 / 辨識項目數),
      // 後端逐題檢核、不符就重生成,生成前算的分數才會等於實際分數
      ...generationUnitParams(type, props.questionTypeConfig?.[type])
    }


    const response = await generateQuestionsByTemplateEnhanced(requestData)

    if (!response.data?.items) {
      throw new Error(t('ui.ed_api_response_format_error'))
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
      toastError(
        t('ui.ed_generate_save_partial_fail')
          .replace('{generated}', generatedQuestions.length)
          .replace('{saved}', savedCount)
          .replace('{failed}', failedCount),
        `${t('ui.ed_generate_op_prefix')} ${t(`generate.${type}`)}`
      )
    } else {
      showSuccess(
        t('ui.ed_generate_save_success')
          .replace('{count}', savedCount)
          .replace('{typeName}', t(`generate.${type}`)),
        t('ui.ed_generate_questions_op')
      )
    }

  } catch (error) {
    toastError(error.message || t('ui.ed_question_generation_failed'), `${t('ui.ed_generate_op_prefix')} ${t(`generate.${type}`)}`)

    emit('error', {
      message: error.message || t('ui.ed_question_generation_failed'),
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


  showSuccess(
    t('ui.ed_cleared_unselected_questions')
      .replace('{count}', removedCount)
      .replace('{typeName}', t(`generate.${type}`)),
    t('ui.ed_clear_unselected')
  )

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
