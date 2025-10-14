<template>
  <div class="exam-paper-workspace max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- 頁面標題 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        {{ t('examPaper.title') }}
      </h1>
      <p class="text-gray-600">
        {{ t('examPaper.subtitle') }}
      </p>
    </div>

    <!-- Step 1: 選擇生成模式 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        📋 Step 1: {{ t('examPaper.selectMode') || '選擇生成模式' }}
      </h2>
      <ModeSelector v-model="generationMode" />
    </div>

    <!-- Step 2: 考券基本資訊 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        📝 Step 2: {{ t('examPaper.basicInfo') }}
      </h2>
      <ExamInfoForm v-model="examInfo" />
    </div>

    <!-- Step 3: 題型配置 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        🎯 Step 3: {{ t('examPaper.questionTypeSettings') || '題型配置' }}
      </h2>
      <QuestionTypeConfig
        v-model="questionTypeConfig"
        :mode="generationMode"
      />
    </div>

    <!-- Step 4: 題目來源（依模式顯示） -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        {{ generationMode === 'select' ? '📚 Step 4: 選擇題目' : '🤖 Step 4: 生成題目' }}
      </h2>

      <!-- 選題模式 -->
      <div v-if="generationMode === 'select'">
        <SelectPanel
          :exam-info="examInfo"
          :question-type-config="questionTypeConfig"
          @questions-loaded="handleQuestionsLoaded"
          @questions-updated="handleQuestionsUpdated"
          @sync-config="handleSyncConfig"
        />
      </div>

      <!-- AI 生成模式 -->
      <div v-else-if="generationMode === 'generate'">
        <GeneratePanel
          :exam-info="examInfo"
          :question-type-config="questionTypeConfig"
          @generated="handleQuestionsGenerated"
          @error="handleGenerationError"
        />
      </div>
    </div>

    <!-- Step 5: 操作按鈕 -->
    <div class="bg-gray-50 rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-600">
          <p>已選題目: <span class="font-semibold text-gray-900">{{ totalSelectedQuestions }}</span> 題</p>
          <p>預計總分: <span class="font-semibold text-gray-900">{{ totalScore }}</span> 分</p>
        </div>

        <div class="flex space-x-3">
          <button
            @click="saveDraft"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm font-medium"
            :disabled="!canSaveDraft"
          >
            💾 {{ t('examPaper.saveDraft') || '儲存草稿' }}
          </button>

          <button
            @click="openExamDesigner"
            class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm font-medium"
            :disabled="!canDesign"
          >
            🎨 {{ t('examPaper.designExam') || '設計考券' }}
          </button>

          <button
            @click="exportToPDF"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium"
            :disabled="!canExport"
          >
            📤 {{ t('examPaper.exportPDF') || '匯出 PDF' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 考券設計器 Modal -->
    <ExamDesigner
      v-if="showDesigner"
      :visible="showDesigner"
      :selected-questions="currentQuestions"
      :initial-exam-styles="examStyles"
      :question-type-config="questionTypeConfig"
      @close="closeExamDesigner"
      @export="handleExportFromDesigner"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLanguage } from '../composables/useLanguage.js'
import ModeSelector from '../components/ExamPaper/ModeSelector.vue'
import ExamInfoForm from '../components/ExamPaper/ExamInfoForm.vue'
import QuestionTypeConfig from '../components/ExamPaper/QuestionTypeConfig.vue'
import GeneratePanel from '../components/ExamPaper/GeneratePanel.vue'
import SelectPanel from '../components/ExamPaper/SelectPanel.vue'
import ExamDesigner from '../components/ExamDesigner/ExamDesigner.vue'
import { exportToPDF as exportPDFUtil } from '@/utils/pdfExporter.js'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'

export default {
  name: 'ExamPaper',
  components: {
    ModeSelector,
    ExamInfoForm,
    QuestionTypeConfig,
    GeneratePanel,
    SelectPanel,
    ExamDesigner
  },
  setup() {
    const { t } = useLanguage()
    const route = useRoute()

    // ==================== 狀態管理 ====================

    // 生成模式：'select' 從題庫選題 | 'generate' AI 自動生成
    const generationMode = ref('generate')

    // 考券基本資訊
    const examInfo = reactive({
      schoolName: 'Abraham Academy',
      title: '',
      subtitle: '',
      subject: 'Health',
      grade: '',  // 不預設年級，讓使用者自行選擇
      duration: '90',
      totalScore: '100'
    })

    // 題型配置（支援所有 10 種題型）
    const questionTypeConfig = reactive({
      single_choice: { count: 10, points: 1, enabled: true, order: 1 },
      cloze: { count: 13, points: 2, enabled: true, order: 2 },
      true_false: { count: 12, points: 1, enabled: true, order: 3 },
      short_answer: { count: 6, points: 4, enabled: true, order: 4 },
      matching: { count: 0, points: 2, enabled: false, order: 5 },
      sequence: { count: 0, points: 2, enabled: false, order: 6 },
      enumeration: { count: 0, points: 3, enabled: false, order: 7 },
      symbol_identification: { count: 0, points: 2, enabled: false, order: 8 },
      mixed: { count: 0, points: 3, enabled: false, order: 9 },
      auto: { count: 0, points: 2, enabled: false, order: 10 }
    })

    // 題目資料
    const selectedQuestions = ref([])  // 從題庫選擇的題目
    const generatedQuestions = ref([]) // AI 生成的題目

    // 設計器狀態
    const showDesigner = ref(false)
    const examStyles = reactive({
      header: {
        enabled: true,
        schoolName: 'Abraham Academy',
        titlePrefix: '2024 Semester 2 G4 Health Midterm Exam',
        subtitle: '(Understanding God\'s World pp. 115-171)'
      },
      questionStyles: {},
      questionTypeOrder: []
    })

    // ==================== 計算屬性 ====================

    // 當前使用的題目列表
    const currentQuestions = computed(() => {
      return generationMode.value === 'select'
        ? selectedQuestions.value
        : generatedQuestions.value
    })

    // 總題數
    const totalSelectedQuestions = computed(() => {
      return Object.values(questionTypeConfig)
        .filter(config => config.enabled)
        .reduce((sum, config) => sum + config.count, 0)
    })

    // 總分
    const totalScore = computed(() => {
      return Object.values(questionTypeConfig)
        .filter(config => config.enabled)
        .reduce((sum, config) => sum + (config.count * config.points), 0)
    })

    // 是否可以儲存草稿
    const canSaveDraft = computed(() => {
      return examInfo.title && totalSelectedQuestions.value > 0
    })

    // 是否可以設計考券
    const canDesign = computed(() => {
      return totalSelectedQuestions.value > 0
    })

    // 是否可以匯出
    const canExport = computed(() => {
      return currentQuestions.value.length > 0
    })

    // ==================== 方法 ====================

    // 開啟考券設計器
    const openExamDesigner = () => {
      if (!canDesign.value) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '請先配置題目數量',
          operation: '開啟考券設計器'
        })
        return
      }

      // 如果還沒有實際題目，創建模擬題目用於預覽
      if (currentQuestions.value.length === 0) {
        generatedQuestions.value = generateMockQuestions()
      }

      // 更新考券標題
      updateExamStyles()

      showDesigner.value = true
    }

    // 關閉考券設計器
    const closeExamDesigner = () => {
      showDesigner.value = false
    }

    // 處理從設計器匯出
    const handleExportFromDesigner = async (exportData) => {
      console.log('從設計器匯出:', exportData)
      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: '考券已匯出',
        operation: '匯出 PDF'
      })
    }

    // 🔄 處理 AI 生成的題目（Phase 5 - 增強版）
    const handleQuestionsGenerated = ({ questions, total, errors }) => {
      console.log('=== AI 生成完成 ===')
      console.log('生成題數:', total)
      console.log('題目:', questions)

      // 更新生成的題目列表
      generatedQuestions.value = questions

      // 🆕 自動同步題型配置到實際生成的題目數量
      const typeStats = {}
      questions.forEach(q => {
        const type = q._meta?.type || q.type
        if (type) {
          typeStats[type] = (typeStats[type] || 0) + 1
        }
      })

      console.log('📊 題型統計:', typeStats)

      // 更新題型配置
      Object.keys(questionTypeConfig).forEach(type => {
        if (typeStats[type] !== undefined) {
          questionTypeConfig[type].count = typeStats[type]
          questionTypeConfig[type].enabled = typeStats[type] > 0
        }
      })

      // 顯示成功訊息
      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: `成功生成 ${total} 題`,
        operation: 'AI 生成題目'
      })

      // 如果有部分失敗，顯示警告
      if (errors && errors.length > 0) {
        console.warn('部分題型生成失敗:', errors)
        const failedTypes = errors.map(e => e.type).join(', ')
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: `部分題型生成失敗: ${failedTypes}`,
          operation: 'AI 生成題目'
        })
      }
    }

    // 處理生成錯誤
    const handleGenerationError = ({ message, errors }) => {
      console.error('=== AI 生成失敗 ===')
      console.error('錯誤訊息:', message)
      console.error('詳細錯誤:', errors)

      eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
        message: message || '題目生成失敗',
        operation: 'AI 生成題目'
      })
    }

    // 處理題目載入（從題庫選題）
    const handleQuestionsLoaded = ({ questions, total }) => {
      console.log('=== 題目載入完成 ===')
      console.log('載入題數:', total)
      console.log('題目:', questions)

      selectedQuestions.value = questions

      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: `已載入 ${total} 題`,
        operation: '載入選中題目'
      })
    }

    // 處理題目更新
    const handleQuestionsUpdated = ({ questions }) => {
      console.log('=== 題目更新 ===')
      console.log('更新後題數:', questions.length)

      selectedQuestions.value = questions
    }

    // 處理同步配置（自動同步，靜默更新）
    const handleSyncConfig = ({ typeStats }) => {
      console.log('=== 自動同步題型配置 ===')
      console.log('題型統計:', typeStats)

      // 根據選中題目的題型統計更新配置
      Object.keys(questionTypeConfig).forEach(type => {
        if (typeStats[type]) {
          questionTypeConfig[type].count = typeStats[type]
          questionTypeConfig[type].enabled = true
        } else {
          questionTypeConfig[type].count = 0
          questionTypeConfig[type].enabled = false
        }
      })

      // ✅ 移除成功訊息（自動同步，不需要每次通知）
    }

    // 直接匯出 PDF
    const exportToPDF = async () => {
      if (!canExport.value) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '請先生成或選擇題目',
          operation: '匯出 PDF'
        })
        return
      }

      try {
        updateExamStyles()

        const examData = {
          questions: currentQuestions.value,
          config: examStyles,
          questionTypeOrder: getQuestionTypeOrder()
        }

        const filename = `${examInfo.title || 'Exam'}.pdf`
        const result = await exportPDFUtil(examData, filename)

        if (result.success) {
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: '考券 PDF 已匯出',
            operation: '匯出 PDF'
          })
        }
      } catch (error) {
        console.error('匯出失敗:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '匯出失敗: ' + error.message,
          operation: '匯出 PDF'
        })
      }
    }

    // 儲存草稿
    const saveDraft = () => {
      if (!canSaveDraft.value) return

      const draft = {
        generationMode: generationMode.value,
        examInfo: { ...examInfo },
        questionTypeConfig: { ...questionTypeConfig },
        selectedQuestions: selectedQuestions.value,
        generatedQuestions: generatedQuestions.value,
        savedAt: new Date().toISOString()
      }

      localStorage.setItem('examPaperDraft', JSON.stringify(draft))

      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: '草稿已儲存',
        operation: '儲存草稿'
      })
    }

    // 載入草稿
    const loadDraft = () => {
      try {
        const draft = localStorage.getItem('examPaperDraft')
        if (draft) {
          const data = JSON.parse(draft)
          generationMode.value = data.generationMode || 'generate'
          Object.assign(examInfo, data.examInfo)
          Object.assign(questionTypeConfig, data.questionTypeConfig)
          selectedQuestions.value = data.selectedQuestions || []
          generatedQuestions.value = data.generatedQuestions || []

          console.log('草稿已載入:', data.savedAt)
        }
      } catch (error) {
        console.error('載入草稿失敗:', error)
      }
    }

    // 更新考券樣式（傳遞給設計器）
    const updateExamStyles = () => {
      examStyles.header.schoolName = examInfo.schoolName
      examStyles.header.titlePrefix = examInfo.title || `${examInfo.grade} ${examInfo.subject} Exam`
      examStyles.header.subtitle = examInfo.subtitle
      examStyles.questionTypeOrder = getQuestionTypeOrder()
    }

    // 取得題型順序
    const getQuestionTypeOrder = () => {
      return Object.entries(questionTypeConfig)
        .filter(([_, config]) => config.enabled && config.count > 0)
        .sort(([_, a], [__, b]) => a.order - b.order)
        .map(([type, _]) => type)
    }

    // 生成模擬題目（用於預覽）
    const generateMockQuestions = () => {
      const mockQuestions = []

      Object.entries(questionTypeConfig).forEach(([type, config]) => {
        if (config.enabled && config.count > 0) {
          for (let i = 0; i < config.count; i++) {
            mockQuestions.push(createMockQuestion(type, i + 1))
          }
        }
      })

      return mockQuestions
    }

    // 創建單個模擬題目
    const createMockQuestion = (type, number) => {
      const baseQuestion = {
        type: type,
        subject: examInfo.subject,
        grade: examInfo.grade,
        source: { document_id: 1, chunk_id: 1, chunk_text: 'Mock source' }
      }

      switch (type) {
        case 'single_choice':
          return {
            ...baseQuestion,
            prompt: `Sample multiple choice question ${number}`,
            content: `Sample multiple choice question ${number}`,
            options: ['a. Option A', 'b. Option B', 'c. Option C', 'd. Option D'],
            answer: 'a',
            explanation: 'This is a sample explanation.'
          }

        case 'cloze':
          return {
            ...baseQuestion,
            prompt: `The heart pumps ______ throughout the body.`,
            content: `The heart pumps ______ throughout the body.`,
            answer: 'blood',
            explanation: 'The heart is responsible for pumping blood.'
          }

        case 'true_false':
          return {
            ...baseQuestion,
            prompt: `Sample true/false statement ${number}`,
            content: `Sample true/false statement ${number}`,
            answer: 'true',
            explanation: 'This is a sample explanation.'
          }

        case 'short_answer':
          return {
            ...baseQuestion,
            prompt: `Sample short answer question ${number}`,
            content: `Sample short answer question ${number}`,
            answer: 'Sample answer',
            explanation: 'This is a sample explanation.'
          }

        default:
          return {
            ...baseQuestion,
            prompt: `Sample ${type} question ${number}`,
            content: `Sample ${type} question ${number}`,
            answer: 'Sample answer',
            explanation: 'This is a sample explanation.'
          }
      }
    }

    // ==================== 生命週期 ====================

    onMounted(() => {
      // 載入草稿（如果有）
      loadDraft()

      // 檢查路由參數，自動切換模式
      const mode = route.query.mode
      if (mode === 'select') {
        generationMode.value = 'select'
        console.log('📍 從路由切換到選題模式')
      }

      // 設定預設考試標題
      if (!examInfo.title) {
        examInfo.title = `2024 Semester 2 ${examInfo.grade} ${examInfo.subject} Midterm Exam`
      }
    })

    // ==================== 返回 ====================

    return {
      // i18n
      t,

      // 狀態
      generationMode,
      examInfo,
      questionTypeConfig,
      selectedQuestions,
      generatedQuestions,
      showDesigner,
      examStyles,

      // 計算屬性
      currentQuestions,
      totalSelectedQuestions,
      totalScore,
      canSaveDraft,
      canDesign,
      canExport,

      // 方法
      openExamDesigner,
      closeExamDesigner,
      handleExportFromDesigner,
      handleQuestionsGenerated,
      handleGenerationError,
      handleQuestionsLoaded,
      handleQuestionsUpdated,
      handleSyncConfig,
      exportToPDF,
      saveDraft,
      loadDraft
    }
  }
}
</script>

<style scoped>
.exam-paper-workspace {
  min-height: calc(100vh - 64px);
}
</style>
