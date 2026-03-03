<template>
  <div class="exam-paper-workspace max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- 頁面標題 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2 whitespace-pre-wrap">
        {{ t('examPaper.title') }}
      </h1>
    </div>

    <!-- Step 1: 選擇生成模式 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        📋 Step 1: {{ t('examPaper.selectMode') || '選擇生成模式' }}
      </h2>
      <ModeSelector v-model="generationMode" />

      <!-- Weekly Test 模式設定 -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <label class="inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="examInfo.isWeeklyTest"
            class="form-checkbox h-5 w-5 text-blue-600 rounded"
          />
          <span class="ml-2 text-sm font-medium text-gray-700">
            📝 Weekly Test 模式（多科目合併）
          </span>
        </label>
        <p class="mt-1 text-xs text-gray-500 ml-7">
          開啟後可選擇多個科目，考卷會按科目分區顯示
        </p>

        <!-- 多科目選擇（Weekly Test 模式下顯示） -->
        <div v-if="examInfo.isWeeklyTest" class="mt-4 ml-7">
          <label class="block text-sm font-medium text-gray-700 mb-2">選擇科目</label>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="sub in availableSubjects"
              :key="sub"
              class="inline-flex items-center px-3 py-2 rounded-lg border cursor-pointer transition-colors"
              :class="[
                examInfo.subjects?.includes(sub)
                  ? 'bg-blue-100 border-blue-500 text-blue-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
            >
              <input
                type="checkbox"
                :checked="examInfo.subjects?.includes(sub)"
                @change="toggleSubject(sub)"
                class="sr-only"
              />
              <span class="text-sm font-medium">{{ sub }}</span>
            </label>
          </div>
          <p v-if="examInfo.subjects?.length > 0" class="mt-2 text-sm text-blue-600">
            已選擇：{{ examInfo.subjects.join(', ') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Step 2: 題型配置 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        🎯 Step 2: {{ t('examPaper.questionTypeSettings') || '題型配置' }}
      </h2>
      <QuestionTypeConfig
        :modelValue="questionTypeConfig"
        @update:modelValue="handleQuestionTypeConfigUpdate"
        :mode="generationMode"
      />
    </div>

    <!-- Step 3: 題目來源（依模式顯示） -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        {{ generationMode === 'select' ? '📚 Step 3: 選擇題目' : '🤖 Step 3: 生成題目' }}
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

    <!-- Step 4: 操作按鈕 -->
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
            🎨 {{ t('examPaper.designExam') || '設計考券並匯出' }}
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
      @update-order="handleUpdateOrder"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '../composables/useToast.js'
import { DEFAULT_SCHOOL_NAME, DEFAULT_EXAM_TITLE, DEFAULT_EXAM_SUBTITLE } from '../constants/examDefaults.js'
import ModeSelector from '../components/ExamPaper/ModeSelector.vue'
import QuestionTypeConfig from '../components/ExamPaper/QuestionTypeConfig.vue'
import GeneratePanel from '../components/ExamPaper/GeneratePanel.vue'
import SelectPanel from '../components/ExamPaper/SelectPanel.vue'
import ExamDesigner from '../components/ExamDesigner/ExamDesigner.vue'
import { exportToPDF as exportPDFUtil } from '@/utils/pdfExporter.js'
import { getQuestionStats } from '@/api/questionService.js'

export default {
  name: 'ExamPaper',
  components: {
    ModeSelector,
    QuestionTypeConfig,
    GeneratePanel,
    SelectPanel,
    ExamDesigner
  },
  setup() {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    const route = useRoute()

    // ==================== 狀態管理 ====================

    // 生成模式：'select' 從題庫選題 | 'generate' AI 自動生成
    const generationMode = ref('select')

    // 考券基本資訊
    const examInfo = reactive({
      schoolName: DEFAULT_SCHOOL_NAME,
      title: '',
      subtitle: '',
      subject: '',  // 不預設科目，讓使用者自行選擇
      grade: '',  // 不預設年級，讓使用者自行選擇
      duration: '90',
      totalScore: '100',
      isWeeklyTest: false,  // Weekly Test 模式
      subjects: []  // 多科目選擇
    })

    // 可選科目列表（從 API 動態載入）
    const availableSubjects = ref([])

    // 載入科目列表
    const loadAvailableSubjects = async () => {
      try {
        const response = await getQuestionStats()
        const stats = response.data
        // 從題目統計中提取科目（只有實際有題目的科目）
        availableSubjects.value = Object.keys(stats.by_subject || {}).filter(Boolean)
      } catch (error) {
        // 靜默失敗，使用空陣列
        availableSubjects.value = []
      }
    }

    // 切換科目選擇（多選模式）
    const toggleSubject = (subject) => {
      if (!examInfo.subjects) examInfo.subjects = []
      const idx = examInfo.subjects.indexOf(subject)
      if (idx === -1) {
        examInfo.subjects.push(subject)
      } else {
        examInfo.subjects.splice(idx, 1)
      }
    }

    // 題型配置（8 種實際題型，排除 symbol_identification/mixed/auto）
    const questionTypeConfig = reactive({
      single_choice: { count: 10, points: 1, enabled: true, order: 1 },
      cloze: { count: 13, points: 2, enabled: true, order: 2 },
      true_false: { count: 12, points: 1, enabled: true, order: 3 },
      short_answer: { count: 6, points: 4, enabled: true, order: 4 },
      matching: { count: 0, points: 2, enabled: false, order: 5 },
      sequence: { count: 0, points: 2, enabled: false, order: 6 },
      enumeration: { count: 0, points: 3, enabled: false, order: 7 },
      image_question: { count: 0, points: 5, enabled: false, order: 8 }
    })

    // 題目資料
    const selectedQuestions = ref([])  // 從題庫選擇的題目
    const generatedQuestions = ref([]) // AI 生成的題目

    // 設計器狀態
    const showDesigner = ref(false)
    const customQuestionTypeOrder = ref([])  // 用戶在 ExamDesigner 調整的順序
    const examStyles = reactive({
      header: {
        enabled: true,
        schoolName: DEFAULT_SCHOOL_NAME,
        titlePrefix: DEFAULT_EXAM_TITLE,
        subtitle: DEFAULT_EXAM_SUBTITLE
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

    // 處理 QuestionTypeConfig 的更新（保持 reactive 響應性）
    const handleQuestionTypeConfigUpdate = (newConfig) => {

      // 清空現有配置
      Object.keys(questionTypeConfig).forEach(key => {
        delete questionTypeConfig[key]
      })

      // 使用 Object.assign 來保持 reactive 響應性
      Object.assign(questionTypeConfig, newConfig)
    }

    // 開啟考券設計器
    const openExamDesigner = () => {
      if (!canDesign.value) {
        toastError('請先配置題目數量', '開啟考券設計器')
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

    // 處理從設計器同步的題型順序
    const handleUpdateOrder = (newOrder) => {
      if (newOrder && newOrder.length > 0) {
        customQuestionTypeOrder.value = [...newOrder]
        examStyles.questionTypeOrder = [...newOrder]
      }
    }

    // 處理從設計器匯出
    const handleExportFromDesigner = async (exportData) => {
      showSuccess('考券已匯出', '匯出 PDF')
    }

    // 🔄 處理 AI 生成的題目（Phase 5 - 增強版）
    // 注意：不覆蓋 count（目標數量），只處理自動啟用邏輯
    const handleQuestionsGenerated = ({ questions, total, errors }) => {

      // 更新生成的題目列表
      generatedQuestions.value = questions

      // 統計各題型實際生成的數量
      const typeStats = {}
      questions.forEach(q => {
        const type = q._meta?.type || q.type
        if (type) {
          typeStats[type] = (typeStats[type] || 0) + 1
        }
      })

      // 如果有生成某個題型的題目，且該題型原本未啟用，則自動啟用
      // ⚠️ 重要：不覆蓋 count（目標數量），保持使用者設定的目標不變
      Object.keys(questionTypeConfig).forEach(type => {
        if (typeStats[type] && typeStats[type] > 0) {
          if (!questionTypeConfig[type].enabled) {
            questionTypeConfig[type].enabled = true
            // 如果原本沒設定數量，設為已生成數量作為初始值
            if (!questionTypeConfig[type].count) {
              questionTypeConfig[type].count = typeStats[type]
            }
          }
        }
      })

      // 🆕 自動儲存草稿（確保題目同步）
      if (questions.length > 0) {
        saveDraft()
      }

      // 顯示成功訊息
      showSuccess(`成功生成 ${total} 題`, 'AI 生成題目')

      // 如果有部分失敗，顯示警告
      if (errors && errors.length > 0) {
        const failedTypes = errors.map(e => e.type).join(', ')
        toastError(`部分題型生成失敗: ${failedTypes}`, 'AI 生成題目')
      }
    }

    // 處理生成錯誤
    const handleGenerationError = ({ message, errors }) => {

      toastError(message || '題目生成失敗', 'AI 生成題目')
    }

    // 處理題目載入（從題庫選題）
    const handleQuestionsLoaded = ({ questions, total }) => {

      selectedQuestions.value = questions

      showSuccess(`已載入 ${total} 題`, '載入選中題目')
    }

    // 處理題目更新
    const handleQuestionsUpdated = ({ questions }) => {

      selectedQuestions.value = questions

      // 🆕 自動儲存草稿（確保題目同步）
      if (questions.length > 0) {
        saveDraft()
      }
    }

    // 處理同步配置（自動同步，靜默更新）
    // 注意：不修改 count（目標數量），只處理自動啟用邏輯
    const handleSyncConfig = ({ typeStats }) => {
      // 如果有選中某個題型的題目，且該題型原本未啟用，則自動啟用
      Object.keys(questionTypeConfig).forEach(type => {
        if (typeStats[type] && typeStats[type] > 0) {
          if (!questionTypeConfig[type].enabled) {
            questionTypeConfig[type].enabled = true
            // 如果原本沒設定數量，設為已選數量作為初始值
            if (!questionTypeConfig[type].count) {
              questionTypeConfig[type].count = typeStats[type]
            }
          }
        }
      })

      // ✅ 移除成功訊息（自動同步，不需要每次通知）
    }

    // 直接匯出 PDF (試題卷)
    const exportToPDF = async () => {
      if (!canExport.value) {
        toastError('請先生成或選擇題目', '匯出試題卷')
        return
      }

      try {
        updateExamStyles()

        const examData = {
          questions: currentQuestions.value,
          config: examStyles,
          questionTypeOrder: getQuestionTypeOrder()
        }

        const filename = `${examInfo.title || 'Exam'}_試題卷.pdf`
        const result = await exportPDFUtil(examData, filename)

        if (result.success) {
          showSuccess('試題卷 PDF 已匯出', '匯出試題卷')
        }
      } catch (error) {
        toastError('匯出失敗: ' + error.message, '匯出試題卷')
      }
    }

    // 匯出答案卷（增強版，支援答案圖片和解釋）
    const exportAnswerSheet = async () => {
      if (!canExport.value) {
        toastError('請先生成或選擇題目', '匯出答案卷')
        return
      }

      try {
        updateExamStyles()

        const examData = {
          questions: currentQuestions.value,
          config: {
            ...examStyles,
            isAnswerSheet: true,
            showAnswerImages: true,      // 顯示答案圖片
            showExplanations: true,      // 顯示解釋說明
            forTeacher: true             // 老師用完整版
          },
          questionTypeOrder: getQuestionTypeOrder(),
          questionTypeConfig: questionTypeConfig
        }

        const filename = `${examInfo.title || 'Exam'}_答案券.pdf`
        const result = await exportPDFUtil(examData, filename)

        if (result.success) {
          showSuccess('答案券 PDF 已匯出', '匯出答案券')
        }
      } catch (error) {
        toastError('匯出失敗: ' + error.message, '匯出答案券')
      }
    }

    // 儲存草稿
    const saveDraft = () => {
      if (!canSaveDraft.value) return

      // 儲存前先更新考券樣式
      updateExamStyles()

      const draft = {
        generationMode: generationMode.value,
        examInfo: { ...examInfo },
        questionTypeConfig: { ...questionTypeConfig },
        examStyles: JSON.parse(JSON.stringify(examStyles)),  // 深拷貝 reactive 物件
        selectedQuestions: selectedQuestions.value,
        generatedQuestions: generatedQuestions.value,
        savedAt: new Date().toISOString()
      }

      localStorage.setItem('examPaperDraft', JSON.stringify(draft))

      showSuccess('草稿已儲存', '儲存草稿')
    }

    // 載入草稿
    const loadDraft = () => {
      try {
        const draft = localStorage.getItem('examPaperDraft')
        if (draft) {
          const data = JSON.parse(draft)
          generationMode.value = data.generationMode || 'select'
          Object.assign(examInfo, data.examInfo)
          Object.assign(questionTypeConfig, data.questionTypeConfig)

          // 載入考券樣式（如果有）
          if (data.examStyles) {
            if (data.examStyles.header) {
              Object.assign(examStyles.header, data.examStyles.header)
            }
            if (data.examStyles.questionStyles) {
              examStyles.questionStyles = data.examStyles.questionStyles
            }
            if (data.examStyles.questionTypeOrder && data.examStyles.questionTypeOrder.length > 0) {
              examStyles.questionTypeOrder = data.examStyles.questionTypeOrder
              // 同步到 customQuestionTypeOrder 以便直接匯出時使用
              customQuestionTypeOrder.value = [...data.examStyles.questionTypeOrder]
            }
          }

          selectedQuestions.value = data.selectedQuestions || []
          generatedQuestions.value = data.generatedQuestions || []

        }
      } catch (error) {
      }
    }

    // 更新考券樣式（傳遞給設計器）
    const updateExamStyles = () => {
      examStyles.header.schoolName = examInfo.schoolName
      examStyles.header.titlePrefix = examInfo.title || `${examInfo.grade} ${examInfo.subject} Exam`
      examStyles.header.subtitle = examInfo.subtitle
      examStyles.questionTypeOrder = getQuestionTypeOrder()

      // Weekly Test 模式設定
      examStyles.isWeeklyTest = examInfo.isWeeklyTest || false
      examStyles.subjects = examInfo.subjects || []
      examStyles.grade = examInfo.grade || ''
    }

    // 取得題型順序（優先使用用戶在 ExamDesigner 調整的順序）
    const getQuestionTypeOrder = () => {
      // 如果用戶有在 ExamDesigner 調整過順序，使用調整後的順序
      if (customQuestionTypeOrder.value.length > 0) {
        // 過濾掉已停用或數量為 0 的題型
        return customQuestionTypeOrder.value.filter(type => {
          const config = questionTypeConfig[type]
          return config && config.enabled && config.count > 0
        })
      }

      // 否則使用預設順序（根據 questionTypeConfig 的 order 排序）
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

    // ==================== 監聽器 ====================

    // 監聽 examInfo 變化，即時同步到 examStyles（確保預覽和匯出使用最新資訊）
    watch(examInfo, () => {
      updateExamStyles()
    }, { deep: true })

    // ==================== 生命週期 ====================

    onMounted(() => {
      // 載入草稿（如果有）
      loadDraft()

      // 載入可用科目列表
      loadAvailableSubjects()

      // 檢查路由參數，自動切換模式
      const mode = route.query.mode
      if (mode === 'select') {
        generationMode.value = 'select'
      }

      // 不再自動設定預設考試標題，讓使用者自行輸入
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
      availableSubjects,

      // 計算屬性
      currentQuestions,
      totalSelectedQuestions,
      totalScore,
      canSaveDraft,
      canDesign,
      canExport,

      // 方法
      handleQuestionTypeConfigUpdate,
      openExamDesigner,
      closeExamDesigner,
      handleUpdateOrder,
      handleExportFromDesigner,
      handleQuestionsGenerated,
      handleGenerationError,
      handleQuestionsLoaded,
      handleQuestionsUpdated,
      handleSyncConfig,
      saveDraft,
      loadDraft,
      toggleSubject
    }
  }
}
</script>

<style scoped>
.exam-paper-workspace {
  min-height: calc(100vh - 64px);
}
</style>
