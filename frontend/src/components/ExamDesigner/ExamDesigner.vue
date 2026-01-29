<template>
  <div class="exam-designer">
    <!-- 設計器標題列 -->
    <div class="designer-header">
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
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="designer-content" :class="{ 'preview-only': isPreviewMode }">
      <!-- 左側：客製化控制面板 -->
      <div v-if="!isPreviewMode" class="customization-panel">
        <div class="panel-content">
          <!-- 考券基本設定 -->
          <div class="section-header">
            <h3 class="section-title">📝 {{ t('examDesigner.examDesign') }}</h3>
            <p class="section-description">{{ t('examDesigner.examDesignDescription') }}</p>
          </div>


          <!-- 題型順序管理 -->
          <div class="customizer-section">
            <div class="section-header">
              <h3 class="section-title">📋 {{ t('examDesigner.questionTypeOrder') }}</h3>
              <p class="section-description">{{ t('examDesigner.questionTypeOrderDescription') }}</p>
            </div>

            <div class="question-types-list">
              <div
                v-for="(typeInfo, index) in orderedTypes"
                :key="typeInfo.type"
                class="type-item"
                :class="{ 'has-questions': typeInfo.count > 0 }"
                draggable="true"
                @dragstart="onDragStart(index)"
                @dragover.prevent
                @drop="onDrop(index)"
              >
                <div class="type-drag-handle">⋮⋮</div>
                
                <div class="type-info">
                  <div class="type-header">
                    <span class="type-icon">{{ getTypeIcon(typeInfo.type) }}</span>
                    <span class="type-name">{{ getTypeName(typeInfo.type) }}</span>
                    <span class="type-count" :class="{ 'empty': typeInfo.count === 0 }">
                      {{ typeInfo.count }} {{ t('examDesigner.questions') }}
                    </span>
                  </div>
                  
                  <div v-if="typeInfo.count > 0" class="type-preview">
                    <div class="preview-questions">
                      <span 
                        v-for="n in Math.min(3, typeInfo.count)" 
                        :key="n"
                        class="preview-dot"
                      ></span>
                      <span v-if="typeInfo.count > 3" class="preview-more">
                        +{{ typeInfo.count - 3 }}
                      </span>
                    </div>
                  </div>
                  
                  <div v-else class="type-empty">
                    {{ t('examDesigner.noQuestions') }}
                  </div>
                </div>

                <div class="type-actions">
                  <button
                    v-if="index > 0"
                    @click="moveUp(index)"
                    class="action-btn"
                    :title="t('examDesigner.moveUp')"
                  >
                    ↑
                  </button>
                  <button
                    v-if="index < orderedTypes.length - 1"
                    @click="moveDown(index)"
                    class="action-btn"
                    :title="t('examDesigner.moveDown')"
                  >
                    ↓
                  </button>
                </div>
              </div>
            </div>

            <div class="order-info">
              <div class="info-item">
                <strong>{{ t('examDesigner.examStructurePreview') }}：</strong>
              </div>
              <div class="structure-preview">
                <div
                  v-for="(typeInfo, index) in orderedTypes.filter(t => t.count > 0)"
                  :key="typeInfo.type"
                  class="structure-item"
                >
                  <span class="structure-number">{{ index + 1 }}.</span>
                  <span class="structure-name">{{ getTypeName(typeInfo.type) }}</span>
                  <span class="structure-count">({{ typeInfo.count }} {{ t('examDesigner.questions') }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部操作按鈕 -->
        <div class="panel-footer">
          <div class="flex justify-end items-center p-4 bg-gray-50 border-t">
            <button
              @click="exportExam"
              class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
            >
              📤 {{ t('examDesigner.exportPDF') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 右側：即時預覽區域 -->
      <div class="preview-panel">
        <div class="preview-content">
          <!-- 預覽工具列 -->
          <div class="preview-toolbar">
            <div class="flex items-center justify-between p-3 bg-white border-b">
              <div class="text-sm font-medium text-gray-700">
                📄 {{ t('examDesigner.livePreview') }}
              </div>
              <div class="flex items-center space-x-2">
                <!-- 縮放控制 -->
                <button 
                  @click="adjustZoom(-0.1)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="縮小"
                >
                  🔍➖
                </button>
                <span class="text-xs text-gray-500 min-w-[40px] text-center">
                  {{ Math.round(zoomLevel * 100) }}%
                </span>
                <button 
                  @click="adjustZoom(0.1)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="放大"
                >
                  🔍➕
                </button>
                <div class="w-px h-4 bg-gray-300 mx-2"></div>
                <!-- 編輯模式切換 -->
                <button 
                  @click="toggleEditMode"
                  :class="[
                    'p-1 text-xs px-2 py-1 rounded',
                    editMode ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  ]"
                  title="編輯模式"
                >
                  {{ editMode ? '📝' : '✏️' }}
                </button>
                <div class="w-px h-4 bg-gray-300 mx-2"></div>
                <!-- 可拖拉預覽 -->
                <button 
                  @click="openDraggablePreview"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="可拖拉預覽"
                >
                  🪟
                </button>
                <!-- 全螢幕預覽 -->
                <button 
                  @click="openFullscreenPreview"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="全螢幕預覽"
                >
                  ⛶
                </button>
              </div>
            </div>
          </div>
          
          <!-- 預覽畫布 -->
          <div class="preview-canvas">
            <div class="preview-scaler" :style="{ transform: `scale(${zoomLevel})` }">
              <SimpleExamPreview
                :questions="selectedQuestions"
                :config="examStylesWithScore"
                :question-type-order="questionTypeOrder"
                :question-type-config="questionTypeConfig"
                :editable="editMode"
                @update-config="updateExamStyles"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 可拖拉預覽視窗 -->
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
          <span class="text-sm font-medium">🪟 完整考券預覽</span>
          <button 
            @click="closeDraggablePreview"
            class="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <!-- 預覽內容 -->
        <div class="overflow-auto" style="height: calc(100% - 50px);">
          <SimpleExamPreview
            :questions="selectedQuestions"
            :config="examStylesWithScore"
            :question-type-order="questionTypeOrder"
            :question-type-config="questionTypeConfig"
            :editable="true"
            @update-config="updateExamStyles"
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

// 子組件導入
import SimpleExamPreview from '../ExamPreview/SimpleExamPreview.vue'

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
const emit = defineEmits(['close', 'save', 'export'])

// 響應式數據
const isPreviewMode = ref(false)
const editMode = ref(false)
const zoomLevel = ref(0.8)
const questionTypeOrder = ref(['single_choice', 'cloze', 'short_answer', 'true_false', 'matching'])
const draggedIndex = ref(-1)
const showDraggableModal = ref(false)

// 基本考券配置 - Abraham Academy 標準格式
const examStyles = reactive({
  header: {
    enabled: true,
    schoolName: 'Abraham Academy',
    titlePrefix: '2024 Semester 2 G4 Science Midterm Exam',
    subtitle: '(Understanding God\'s World pp. 115-171)',
    duration: '90 minutes',
    totalScore: '100 points'
  },
  studentInfo: {
    enabled: false,  // 根據 exam_layout.html，預設關閉學生資訊
    fields: [
      { label: 'Class', width: '100px' },
      { label: 'Number', width: '80px' },
      { label: 'Name', width: '120px' },
      { label: 'Score', width: '80px' }
    ]
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

// 題型相關方法
const getTypeName = (type) => {
  // 使用 i18n 翻譯，從 generate 區塊取得題型名稱
  return t(`generate.${type}`) || type
}

const getTypeIcon = (type) => {
  const icons = {
    single_choice: '📝',
    multiple_choice: '☑️',
    cloze: '✏️',
    short_answer: '💬',
    true_false: '✓✗',
    matching: '🔗',
    sequence: '🔢',
    enumeration: '📋',
    symbol_identification: '🔍',
    mixed: '🎲',
    essay: '📄',
    auto: '🤖'
  }
  return icons[type] || '❓'
}

// 拖拽相關方法
const onDragStart = (index) => {
  draggedIndex.value = index
}

const onDrop = (targetIndex) => {
  if (draggedIndex.value === -1 || draggedIndex.value === targetIndex) {
    return
  }
  
  const draggedType = questionTypeOrder.value[draggedIndex.value]
  const newOrder = [...questionTypeOrder.value]
  
  // 移除拖拽的項目
  newOrder.splice(draggedIndex.value, 1)
  // 插入到新位置
  newOrder.splice(targetIndex, 0, draggedType)
  
  questionTypeOrder.value = newOrder
  examStyles.questionTypeOrder = newOrder
  draggedIndex.value = -1
  
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

const adjustZoom = (delta) => {
  const newZoom = zoomLevel.value + delta
  if (newZoom >= 0.3 && newZoom <= 2) {
    zoomLevel.value = newZoom
  }
}

// 編輯模式切換
const toggleEditMode = () => {
  editMode.value = !editMode.value
}

// 更新考券配置
const updateExamStyles = (newConfig) => {
  Object.assign(examStyles, newConfig)
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
  
  const filename = `exam_${Date.now()}.pdf`
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

// 初始化
</script>

<style scoped>
.exam-designer {
  height: 90vh;
  max-height: 900px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.designer-header {
  flex-shrink: 0;
  border-bottom: 1px solid #e5e7eb;
}

.designer-content {
  flex: 1;
  display: flex;
  min-height: 0;
}

.designer-content.preview-only {
  flex-direction: column;
}

.customization-panel {
  width: 400px;
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.panel-footer {
  flex-shrink: 0;
  border-top: 1px solid #e5e7eb;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;  /* 允許 flex 子元素正確計算滾動高度 */
}

.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
  min-height: 0;  /* 允許 flex 子元素正確計算滾動高度 */
}

.preview-toolbar {
  flex-shrink: 0;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.preview-canvas {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.preview-scaler {
  transform-origin: top left;
  transition: transform 0.2s ease;
  min-height: 100%;
}

/* 整合的客製化器樣式 */
.customizer-section {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.section-description {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.config-content {
  margin-top: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 12px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 4px;
}

.field-input {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px #3b82f6;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
}

.checkbox-item input {
  margin-right: 6px;
}


/* 題型順序管理樣式 */
.question-types-list {
  margin-bottom: 20px;
}

.type-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: move;
}

.type-item:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.type-item.has-questions {
  border-left: 4px solid #10b981;
}

.type-drag-handle {
  color: #9ca3af;
  margin-right: 12px;
  font-size: 14px;
  cursor: grab;
}

.type-drag-handle:active {
  cursor: grabbing;
}

.type-info {
  flex: 1;
}

.type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.type-icon {
  font-size: 16px;
}

.type-name {
  font-weight: 500;
  color: #374151;
}

.type-count {
  font-size: 12px;
  color: #10b981;
  font-weight: 500;
}

.type-count.empty {
  color: #9ca3af;
}

.type-preview {
  margin-left: 24px;
}

.preview-questions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.preview-dot {
  width: 4px;
  height: 4px;
  background: #10b981;
  border-radius: 50%;
}

.preview-more {
  font-size: 10px;
  color: #6b7280;
  margin-left: 4px;
}

.type-empty {
  margin-left: 24px;
  font-size: 12px;
  color: #9ca3af;
}

.type-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
  color: #374151;
}

.order-info {
  padding: 16px;
  background: #fef7f0;
  border: 1px solid #fed7aa;
  border-radius: 6px;
}

.info-item {
  margin-bottom: 8px;
  font-size: 13px;
  color: #9a3412;
}

.structure-preview {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.structure-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7c2d12;
}

.structure-number {
  font-weight: 600;
  min-width: 20px;
}

.structure-name {
  font-weight: 500;
}

.structure-count {
  color: #a16207;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .customization-panel {
    width: 350px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .designer-content:not(.preview-only) {
    flex-direction: column;
  }
  
  .customization-panel {
    width: 100%;
    height: 300px;
  }
  
  .preview-panel {
    flex: 1;
  }
}
</style>