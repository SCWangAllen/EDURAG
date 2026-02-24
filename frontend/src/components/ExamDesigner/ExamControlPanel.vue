<template>
  <div class="customization-panel">
    <div class="panel-content">
      <!-- 考券標題設定 -->
      <div class="customizer-section">
        <div class="section-header">
          <h3 class="section-title">📝 {{ t('examDesigner.examDesign') }}</h3>
          <p class="section-description">{{ t('examDesigner.examDesignDescription') || '編輯考券標題和基本資訊' }}</p>
        </div>

        <div class="header-fields">
          <!-- 學校名稱 -->
          <div class="field-group">
            <label class="field-label">學校名稱</label>
            <input
              type="text"
              :value="localHeader.schoolName"
              @input="updateHeader('schoolName', $event.target.value)"
              class="field-input"
              placeholder="輸入學校名稱"
            />
          </div>

          <!-- 考試標題 -->
          <div class="field-group">
            <label class="field-label">考試標題</label>
            <input
              type="text"
              :value="localHeader.titlePrefix"
              @input="updateHeader('titlePrefix', $event.target.value)"
              class="field-input"
              placeholder="例如：Science Quarterly Exam"
            />
          </div>

          <!-- 副標題/範圍 -->
          <div class="field-group">
            <label class="field-label">範圍/副標題</label>
            <input
              type="text"
              :value="localHeader.subtitle"
              @input="updateHeader('subtitle', $event.target.value)"
              class="field-input"
              placeholder="例如：Unit 1-3"
            />
          </div>
        </div>
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
                @click="$emit('move-up', index)"
                class="action-btn"
                :title="t('examDesigner.moveUp')"
              >
                ↑
              </button>
              <button
                v-if="index < orderedTypes.length - 1"
                @click="$emit('move-down', index)"
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

      <!-- 樣式設定區塊 -->
      <div class="customizer-section">
        <div class="section-header">
          <h3 class="section-title">🎨 樣式設定</h3>
          <p class="section-description">調整考券的字體、行距和圖片大小</p>
        </div>

        <div class="style-controls">
          <!-- 字體大小 -->
          <div class="control-group">
            <label class="control-label">字體大小</label>
            <select
              :value="localTypography.fontSize"
              @change="updateTypography('fontSize', Number($event.target.value))"
              class="control-select"
            >
              <option :value="9">9pt (小)</option>
              <option :value="10">10pt</option>
              <option :value="11">11pt (標準)</option>
              <option :value="12">12pt</option>
              <option :value="14">14pt (大)</option>
            </select>
          </div>

          <!-- 行距 -->
          <div class="control-group">
            <label class="control-label">行距</label>
            <select
              :value="localTypography.lineHeight"
              @change="updateTypography('lineHeight', Number($event.target.value))"
              class="control-select"
            >
              <option :value="1.2">緊湊 (1.2)</option>
              <option :value="1.4">標準 (1.4)</option>
              <option :value="1.6">寬鬆 (1.6)</option>
              <option :value="1.8">很寬 (1.8)</option>
            </select>
          </div>

          <!-- 圖片大小 -->
          <div class="control-group">
            <label class="control-label">圖片大小</label>
            <select
              :value="localTypography.imageSize"
              @change="updateTypography('imageSize', $event.target.value)"
              class="control-select"
            >
              <option value="small">小 (120px)</option>
              <option value="medium">中 (200px)</option>
              <option value="large">大 (300px)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 進階字體設定區塊 -->
      <div class="customizer-section">
        <div
          class="section-header collapsible"
          @click="showAdvancedTypography = !showAdvancedTypography"
        >
          <h3 class="section-title">
            <span class="collapse-icon">{{ showAdvancedTypography ? '▼' : '▶' }}</span>
            🔤 {{ t('examDesigner.advancedTypography') || '進階字體設定' }}
          </h3>
          <p class="section-description">{{ t('examDesigner.advancedTypographyDescription') || '個別調整各元素的字體大小、粗體、對齊' }}</p>
        </div>

        <div v-show="showAdvancedTypography" class="advanced-typography-settings">
          <div
            v-for="(style, key) in localTypography.elements"
            :key="key"
            class="element-style-row"
          >
            <span class="element-label">{{ elementLabels[key] || key }}</span>

            <!-- 字體大小 -->
            <select
              :value="style.fontSize"
              @change="updateElementStyle(key, 'fontSize', Number($event.target.value))"
              class="element-select font-size-select"
            >
              <option v-for="size in fontSizeOptions" :key="size" :value="size">
                {{ size }}pt
              </option>
            </select>

            <!-- 粗體勾選 -->
            <label class="checkbox-label">
              <input
                type="checkbox"
                :checked="style.fontWeight === 'bold'"
                @change="updateElementStyle(key, 'fontWeight', $event.target.checked ? 'bold' : 'normal')"
              />
              粗體
            </label>

            <!-- 置中勾選 -->
            <label class="checkbox-label">
              <input
                type="checkbox"
                :checked="style.textAlign === 'center'"
                @change="updateElementStyle(key, 'textAlign', $event.target.checked ? 'center' : 'left')"
              />
              置中
            </label>
          </div>

          <!-- 重置按鈕 -->
          <button
            @click="resetTypographyElements"
            class="reset-btn"
          >
            🔄 {{ t('examDesigner.resetToDefault') || '重置為預設值' }}
          </button>
        </div>
      </div>

      <!-- 顯示選項區塊 -->
      <div class="customizer-section">
        <div class="section-header">
          <h3 class="section-title">👁️ {{ t('examDesigner.displayOptions') || '顯示選項' }}</h3>
          <p class="section-description">{{ t('examDesigner.displayOptionsDescription') || '控制考券上顯示的區域' }}</p>
        </div>

        <div class="display-options">
          <!-- 學生資訊開關 -->
          <label class="toggle-option">
            <input
              type="checkbox"
              :checked="localStudentInfo.enabled"
              @change="updateStudentInfo('enabled', $event.target.checked)"
            />
            <span class="toggle-label">{{ t('examDesigner.enableStudentInfo') || '啟用學生資訊欄位' }}</span>
          </label>

          <!-- 家長簽名開關 -->
          <label class="toggle-option">
            <input
              type="checkbox"
              :checked="localParentSignature.enabled"
              @change="updateParentSignature('enabled', $event.target.checked)"
            />
            <span class="toggle-label">{{ t('examDesigner.enableParentSignature') || '啟用家長簽名框（左上角）' }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 底部操作按鈕 -->
    <div class="panel-footer">
      <div class="flex justify-end items-center gap-3 p-4 bg-gray-50 border-t">
        <button
          @click="$emit('export')"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
        >
          📤 {{ t('examDesigner.exportPDF') || '匯出試題卷' }}
        </button>
        <button
          @click="$emit('export-answer-sheet')"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          📝 {{ t('examDesigner.exportAnswerSheet') || '匯出答案卷' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import {
  DEFAULT_TYPOGRAPHY_ELEMENTS,
  DEFAULT_STUDENT_INFO,
  DEFAULT_PARENT_SIGNATURE,
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE
} from '@/constants/examDefaults.js'

const { t } = useLanguage()

// 進階設定展開狀態
const showAdvancedTypography = ref(false)

// 本地標題設定
const localHeader = ref({
  enabled: true,
  schoolName: DEFAULT_SCHOOL_NAME,
  titlePrefix: DEFAULT_EXAM_TITLE,
  subtitle: DEFAULT_EXAM_SUBTITLE
})

// 本地樣式狀態（用於雙向綁定）
const localTypography = ref({
  fontSize: 11,
  lineHeight: 1.4,
  imageSize: 'medium',
  elements: { ...DEFAULT_TYPOGRAPHY_ELEMENTS }
})

// 本地學生資訊設定
const localStudentInfo = ref({
  enabled: DEFAULT_STUDENT_INFO.enabled,
  topFields: [...DEFAULT_STUDENT_INFO.topFields],
  bottomField: { ...DEFAULT_STUDENT_INFO.bottomField }
})

// 本地家長簽名設定
const localParentSignature = ref({
  enabled: DEFAULT_PARENT_SIGNATURE.enabled,
  label: DEFAULT_PARENT_SIGNATURE.label,
  position: DEFAULT_PARENT_SIGNATURE.position,
  boxStyle: DEFAULT_PARENT_SIGNATURE.boxStyle
})

// 元素標籤對照表（英文）
const elementLabels = {
  schoolName: 'School Name',
  sectionTitle: 'Section Title',
  sectionInstruction: 'Instruction',
  studentInfo: 'Student Info',
  parentSignature: 'Parent Signature',
  questionContent: 'Question',
  examScope: 'Exam Scope'
}

// 字體大小選項
const fontSizeOptions = [8, 9, 10, 11, 12, 14, 16, 18, 20]

const props = defineProps({
  orderedTypes: {
    type: Array,
    required: true
  },
  examStyles: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['move-up', 'move-down', 'export', 'export-answer-sheet', 'reorder', 'update-styles'])

const draggedIndex = ref(-1)

const getTypeName = (type) => {
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

const onDragStart = (index) => {
  draggedIndex.value = index
}

const onDrop = (targetIndex) => {
  if (draggedIndex.value === -1 || draggedIndex.value === targetIndex) {
    return
  }
  emit('reorder', { from: draggedIndex.value, to: targetIndex })
  draggedIndex.value = -1
}

// 監聽 props 變化，同步到本地狀態
watch(() => props.examStyles?.header, (newHeader) => {
  if (newHeader) {
    localHeader.value = { ...localHeader.value, ...newHeader }
  }
}, { immediate: true, deep: true })

watch(() => props.examStyles?.typography, (newTypo) => {
  if (newTypo) {
    localTypography.value = {
      ...newTypo,
      elements: { ...DEFAULT_TYPOGRAPHY_ELEMENTS, ...(newTypo.elements || {}) }
    }
  }
}, { immediate: true, deep: true })

// 監聽 studentInfo 變化
watch(() => props.examStyles?.studentInfo, (newInfo) => {
  if (newInfo) {
    localStudentInfo.value = { ...newInfo }
  }
}, { immediate: true, deep: true })

// 監聽 parentSignature 變化
watch(() => props.examStyles?.parentSignature, (newSig) => {
  if (newSig) {
    localParentSignature.value = { ...newSig }
  }
}, { immediate: true, deep: true })

// 更新標題設定
const updateHeader = (field, value) => {
  localHeader.value[field] = value
  emit('update-styles', {
    header: { ...localHeader.value }
  })
}

// 樣式更新方法
const updateTypography = (field, value) => {
  localTypography.value[field] = value
  emit('update-styles', {
    typography: { ...localTypography.value }
  })
}

// 更新元素級別樣式
const updateElementStyle = (elementKey, styleKey, value) => {
  if (!localTypography.value.elements) {
    localTypography.value.elements = { ...DEFAULT_TYPOGRAPHY_ELEMENTS }
  }
  localTypography.value.elements[elementKey] = {
    ...localTypography.value.elements[elementKey],
    [styleKey]: value
  }
  emit('update-styles', {
    typography: { ...localTypography.value }
  })
}

// 重置元素樣式為預設值
const resetTypographyElements = () => {
  localTypography.value.elements = { ...DEFAULT_TYPOGRAPHY_ELEMENTS }
  emit('update-styles', {
    typography: { ...localTypography.value }
  })
}

// 更新學生資訊設定
const updateStudentInfo = (field, value) => {
  localStudentInfo.value[field] = value
  emit('update-styles', {
    studentInfo: { ...localStudentInfo.value }
  })
}

// 更新家長簽名設定
const updateParentSignature = (field, value) => {
  localParentSignature.value[field] = value
  emit('update-styles', {
    parentSignature: { ...localParentSignature.value }
  })
}
</script>

<style scoped>
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

@media (max-width: 1200px) {
  .customization-panel {
    width: 350px;
  }
}

@media (max-width: 900px) {
  .customization-panel {
    width: 100%;
    height: 300px;
  }
}

/* 樣式設定區塊 */
.style-controls {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.control-select {
  width: 100%;
  padding: 6px 8px;
  font-size: 13px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: border-color 0.2s;
}

.control-select:hover {
  border-color: #9ca3af;
}

.control-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

@media (max-width: 1200px) {
  .style-controls {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

/* 進階字體設定區塊 */
.section-header.collapsible {
  cursor: pointer;
  user-select: none;
}

.section-header.collapsible:hover {
  background: #f3f4f6;
  border-radius: 4px;
  margin: -8px;
  padding: 8px;
}

.collapse-icon {
  font-size: 10px;
  margin-right: 6px;
  color: #6b7280;
}

.advanced-typography-settings {
  margin-top: 12px;
}

.element-style-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.element-style-row:last-of-type {
  border-bottom: none;
}

.element-label {
  width: 80px;
  font-size: 13px;
  color: #374151;
  font-weight: 500;
  flex-shrink: 0;
}

.element-select {
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.font-size-select {
  width: 70px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  white-space: nowrap;
}

.checkbox-label input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.reset-btn {
  margin-top: 12px;
  padding: 6px 12px;
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

/* 顯示選項區塊 */
.display-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toggle-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.toggle-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.toggle-label {
  font-size: 13px;
  color: #374151;
}

/* 考券標題輸入欄位 */
.header-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.field-input {
  width: 100%;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field-input:hover {
  border-color: #9ca3af;
}

.field-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-input::placeholder {
  color: #9ca3af;
}
</style>
