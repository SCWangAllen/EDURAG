<template>
  <div class="h-[90vh] max-h-[900px] flex flex-col bg-white rounded-lg shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1)] overflow-hidden">
    <!-- 設計器標題列 -->
    <div class="shrink-0 border-b border-gray-200">
      <div class="flex items-center justify-between p-4 bg-gray-50 border-b">
        <div class="flex items-center space-x-4">
          <h2 class="text-lg font-semibold text-gray-900">🎨 {{ t('examDesigner.title') }}</h2>
          <div class="text-sm text-gray-500">
            {{ selectedQuestions.length }} {{ t('examDesigner.questionsSelected') }}
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <!-- 預覽模式切換 -->
          <button
            @click="togglePreviewMode"
            :class="[
              'px-3 py-1 text-sm rounded transition-colors',
              isPreviewMode
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            ]"
          >
            {{ isPreviewMode ? `📝 ${t('examDesigner.editMode')}` : `👀 ${t('examDesigner.previewMode')}` }}
          </button>
          
          <!-- 關閉按鈕 -->
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="flex-1 flex min-h-0" :class="isPreviewMode ? 'flex-col' : 'max-[900px]:flex-col'">
      <!-- 左側：客製化控制面板 -->
      <ExamControlPanel
        v-if="!isPreviewMode"
        :ordered-types="orderedTypes"
        :exam-styles="examStyles"
        @move-up="moveUp"
        @move-down="moveDown"
        @export="exportExam"
        @export-answer-sheet="exportAnswerSheet"
        @reorder="handleReorder"
        @update-styles="updateExamStyles"
      />

      <!-- 右側：即時 PDF 預覽區域 -->
      <div class="flex-1 flex flex-col min-w-0 min-h-0">
        <div class="flex-1 flex flex-col bg-gray-100 min-h-0">
          <!-- 預覽工具列（簡化版 - PDF 查看器內建縮放功能） -->
          <div class="shrink-0 bg-white border-b border-gray-200">
            <div class="flex items-center justify-between p-3 bg-white border-b">
              <div class="text-sm font-medium text-gray-700">
                📄 {{ t('examDesigner.livePreview') }}
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500">
                  PDF 預覽（所見即所得）
                </span>
                <div class="w-px h-4 bg-gray-300 mx-2"></div>
                <!-- 可拖拉預覽 -->
                <button
                  @click="openDraggablePreview"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="可拖拉預覽"
                >
                  🪟
                </button>
              </div>
            </div>
          </div>

          <!-- PDF 預覽畫布（iframe，無需 scaler） -->
          <div class="flex-1 overflow-auto p-5">
            <SimpleExamPreview
              :questions="selectedQuestions"
              :config="examStylesWithScore"
              :question-type-order="questionTypeOrder"
              :question-type-config="questionTypeConfig"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 可拖拉 PDF 預覽視窗 -->
    <div v-if="showDraggableModal" class="fixed inset-0 z-50 pointer-events-none">
      <div
        class="draggable-preview pointer-events-auto"
        :style="{
          position: 'fixed',
          top: dragPosition.y + 'px',
          left: dragPosition.x + 'px',
          width: '800px',
          height: '600px',
          backgroundColor: 'white',
          border: '1px solid #ccc',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          zIndex: 1000
        }"
      >
        <!-- 拖拉標題列 -->
        <div
          class="drag-header cursor-move bg-gray-100 p-3 border-b flex justify-between items-center rounded-t-lg"
          @mousedown="startDrag"
        >
          <span class="text-sm font-medium">🪟 完整考券預覽（PDF）</span>
          <button
            @click="closeDraggablePreview"
            class="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <!-- PDF 預覽內容 -->
        <div class="h-[calc(100%-50px)] overflow-hidden">
          <SimpleExamPreview
            :questions="selectedQuestions"
            :config="examStylesWithScore"
            :question-type-order="questionTypeOrder"
            :question-type-config="questionTypeConfig"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import { exportToPDF } from '@/utils/pdfExporter.js'
import {
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE,
  DEFAULT_TYPOGRAPHY_ELEMENTS,
  DEFAULT_STUDENT_INFO,
  DEFAULT_PARENT_SIGNATURE
} from '@/constants/examDefaults.js'

// 子組件導入
import SimpleExamPreview from '../ExamPreview/SimpleExamPreview.vue'
import ExamControlPanel from './ExamControlPanel.vue'

const { t } = useLanguage()

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedQuestions: {
    type: Array,
    required: true
  },
  initialExamStyles: {
    type: Object,
    default: () => ({})
  },
  questionTypeConfig: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['close', 'save', 'export', 'update-order'])

// 響應式數據
const isPreviewMode = ref(false)
const questionTypeOrder = ref(['single_choice', 'cloze', 'short_answer', 'true_false', 'matching'])
const showDraggableModal = ref(false)

// 基本考券配置 - 標準格式
const examStyles = reactive({
  header: {
    enabled: true,
    schoolName: DEFAULT_SCHOOL_NAME,
    titlePrefix: DEFAULT_EXAM_TITLE,
    subtitle: DEFAULT_EXAM_SUBTITLE,
    duration: '90 minutes',
    totalScore: '100 points'
  },
  // 學生資訊區配置
  studentInfo: {
    enabled: DEFAULT_STUDENT_INFO.enabled,
    topFields: [...DEFAULT_STUDENT_INFO.topFields],
    bottomField: { ...DEFAULT_STUDENT_INFO.bottomField }
  },
  // 家長簽名區配置
  parentSignature: {
    enabled: DEFAULT_PARENT_SIGNATURE.enabled,
    label: DEFAULT_PARENT_SIGNATURE.label,
    position: DEFAULT_PARENT_SIGNATURE.position,
    boxStyle: DEFAULT_PARENT_SIGNATURE.boxStyle
  },
  // 排版樣式設定
  typography: {
    fontSize: 11,        // pt (9, 10, 11, 12, 14)
    lineHeight: 1.4,     // (1.2, 1.4, 1.6, 1.8)
    imageSize: 'medium', // 'small', 'medium', 'large'
    // 元素級別字體設定
    elements: { ...DEFAULT_TYPOGRAPHY_ELEMENTS }
  }
})

// 計算屬性
const examTitle = computed(() => {
  return examStyles.header?.titlePrefix || 'Examination'
})

// 題型統計和順序相關的計算屬性
const typeStats = computed(() => {
  const stats = {}
  
  // 初始化所有題型
  questionTypeOrder.value.forEach(type => {
    stats[type] = 0
  })
  
  // 計算實際數量
  props.selectedQuestions.forEach(q => {
    if (stats.hasOwnProperty(q.type)) {
      stats[q.type]++
    } else {
      // 如果有新的題型，加入到順序中
      stats[q.type] = 1
      if (!questionTypeOrder.value.includes(q.type)) {
        questionTypeOrder.value.push(q.type)
      }
    }
  })
  
  return stats
})

const orderedTypes = computed(() => {
  return questionTypeOrder.value.map(type => ({
    type,
    count: typeStats.value[type] || 0
  }))
})

// 計算總分
const totalScore = computed(() => {
  let total = 0

  // 從 questionTypeConfig 計算總分
  Object.entries(typeStats.value).forEach(([type, count]) => {
    if (count > 0 && props.questionTypeConfig[type]) {
      const points = props.questionTypeConfig[type].points || 0
      total += count * points
    }
  })

  return total
})

// 考券標題總分
const examTotalScore = computed(() => {
  // 優先使用計算值，否則使用手動設定值
  return totalScore.value > 0 ? totalScore.value : (examStyles.header?.totalScore || '100')
})

// 動態注入總分的考券配置
const examStylesWithScore = computed(() => {
  return {
    ...examStyles,
    header: {
      ...examStyles.header,
      totalScore: `${examTotalScore.value} points`
    }
  }
})

// 方法

// 拖拽相關方法（由子元件 ExamControlPanel 觸發）
const handleReorder = ({ from, to }) => {
  const draggedType = questionTypeOrder.value[from]
  const newOrder = [...questionTypeOrder.value]
  newOrder.splice(from, 1)
  newOrder.splice(to, 0, draggedType)
  questionTypeOrder.value = newOrder
  examStyles.questionTypeOrder = newOrder
}

// 按鈕移動
const moveUp = (index) => {
  if (index > 0) {
    const newOrder = [...questionTypeOrder.value]
    const temp = newOrder[index]
    newOrder[index] = newOrder[index - 1]
    newOrder[index - 1] = temp
    questionTypeOrder.value = newOrder
    examStyles.questionTypeOrder = newOrder
    
  }
}

const moveDown = (index) => {
  if (index < questionTypeOrder.value.length - 1) {
    const newOrder = [...questionTypeOrder.value]
    const temp = newOrder[index]
    newOrder[index] = newOrder[index + 1]
    newOrder[index + 1] = temp
    questionTypeOrder.value = newOrder
    examStyles.questionTypeOrder = newOrder
    
  }
}

const togglePreviewMode = () => {
  isPreviewMode.value = !isPreviewMode.value
}

// 更新考券配置
const updateExamStyles = (newConfig) => {
  Object.assign(examStyles, newConfig)
}

// 關閉設計器並同步順序
const handleClose = () => {
  // 將調整後的順序同步回父元件
  emit('update-order', questionTypeOrder.value)
  emit('close')
}

// 可拖拉預覽
const openDraggablePreview = () => {
  showDraggableModal.value = true
}

const closeDraggablePreview = () => {
  showDraggableModal.value = false
}

// 拖拉功能
const dragPosition = ref({ x: 50, y: 50 })
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const startDrag = (event) => {
  isDragging.value = true
  const rect = event.target.closest('.draggable-preview').getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (event) => {
  if (!isDragging.value) return
  
  dragPosition.value = {
    x: event.clientX - dragOffset.value.x,
    y: event.clientY - dragOffset.value.y
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}


const exportExam = async () => {
  const exportData = {
    questions: props.selectedQuestions,
    config: examStyles,
    questionTypeOrder: questionTypeOrder.value
  }

  // 使用考券標題作為檔名，去除不合法字元
  const examTitle = examStyles.header?.titlePrefix || 'Exam'
  const safeTitle = examTitle.replace(/[<>:"/\\|?*]/g, '_').substring(0, 100)
  const filename = `${safeTitle}_試題卷.pdf`
  const result = await exportToPDF(exportData, filename)

  if (result.success) {
  } else {
    alert(result.message)
  }
}

const exportAnswerSheet = async () => {
  const exportData = {
    questions: props.selectedQuestions,
    config: {
      ...examStyles,
      isAnswerSheet: true,
      showAnswerImages: true,
      showExplanations: true,
      forTeacher: true
    },
    questionTypeOrder: questionTypeOrder.value,
    questionTypeConfig: props.questionTypeConfig
  }

  // 使用考券標題作為檔名
  const examTitle = examStyles.header?.titlePrefix || 'Exam'
  const safeTitle = examTitle.replace(/[<>:"/\\|?*]/g, '_').substring(0, 100)
  const filename = `${safeTitle}_答案卷.pdf`
  const result = await exportToPDF(exportData, filename)

  if (result.success) {
  } else {
    alert(result.message)
  }
}

// ==================== 初始化 questionTypeOrder ====================

// 從 props.questionTypeConfig 初始化題型順序
const initializeQuestionTypeOrder = () => {
  if (!props.questionTypeConfig || Object.keys(props.questionTypeConfig).length === 0) {
    return
  }

  // 從 questionTypeConfig 提取已啟用且 count > 0 的題型，按 order 排序
  const enabledTypes = Object.entries(props.questionTypeConfig)
    .filter(([_, config]) => config.enabled && config.count > 0)
    .sort(([_, a], [__, b]) => (a.order || 0) - (b.order || 0))
    .map(([type, _]) => type)

  if (enabledTypes.length > 0) {
    questionTypeOrder.value = enabledTypes
  } else {
  }
}

// 監聽 questionTypeConfig 變化
watch(() => props.questionTypeConfig, (newConfig) => {
  initializeQuestionTypeOrder()
}, { deep: true, immediate: true })

// 監聽 initialExamStyles 變化，同步到內部 examStyles
watch(() => props.initialExamStyles, (newStyles) => {
  if (newStyles && Object.keys(newStyles).length > 0) {
    // 同步 header 設定
    if (newStyles.header) {
      Object.assign(examStyles.header, newStyles.header)
    }
    // 同步 studentInfo 設定
    if (newStyles.studentInfo) {
      Object.assign(examStyles.studentInfo, newStyles.studentInfo)
    }
    // 同步 parentSignature 設定
    if (newStyles.parentSignature) {
      Object.assign(examStyles.parentSignature, newStyles.parentSignature)
    }
    // 同步題型順序
    if (newStyles.questionTypeOrder && newStyles.questionTypeOrder.length > 0) {
      questionTypeOrder.value = [...newStyles.questionTypeOrder]
    }
    // 同步 typography 設定（包括 elements）
    if (newStyles.typography) {
      Object.assign(examStyles.typography, newStyles.typography)
      if (newStyles.typography.elements) {
        examStyles.typography.elements = { ...DEFAULT_TYPOGRAPHY_ELEMENTS, ...newStyles.typography.elements }
      }
    }
    // 同步 Weekly Test 設定
    examStyles.isWeeklyTest = newStyles.isWeeklyTest || false
    examStyles.subjects = newStyles.subjects || []
    examStyles.grade = newStyles.grade || ''
    examStyles.weeklyTestMixMode = newStyles.weeklyTestMixMode || 'separate'
    examStyles.weeklyTestSubjectCounts = newStyles.weeklyTestSubjectCounts || {}
  }
}, { deep: true, immediate: true })

// 初始化
</script>