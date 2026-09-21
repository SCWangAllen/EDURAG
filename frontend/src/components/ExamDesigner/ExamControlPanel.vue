<template>
  <div class="w-[400px] bg-gray-50 border-r border-gray-200 flex flex-col max-[1200px]:w-[350px] max-[900px]:w-full max-[900px]:h-[300px]">
    <div class="flex-1 overflow-y-auto">
      <!-- 考券標題設定 -->
      <div class="p-5 border-b border-gray-200">
        <div class="mb-4">
          <h3 class="text-base font-semibold text-gray-800">📝 {{ t('examDesigner.examDesign') }}</h3>
          <p class="text-[13px] text-gray-500 mt-1">{{ t('examDesigner.examDesignDescription') || '編輯考券標題和基本資訊' }}</p>
        </div>

        <div class="flex flex-col gap-3">
          <!-- 學校名稱 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_school_name') }}</label>
            <input
              type="text"
              :value="localHeader.schoolName"
              @input="updateHeader('schoolName', $event.target.value)"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white text-gray-700 transition-[border-color,box-shadow] duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] placeholder:text-gray-400"
              :placeholder="t('ui.ed_school_name_placeholder')"
            />
          </div>

          <!-- 考試標題 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_exam_title_label') }}</label>
            <input
              type="text"
              :value="localHeader.titlePrefix"
              @input="updateHeader('titlePrefix', $event.target.value)"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white text-gray-700 transition-[border-color,box-shadow] duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] placeholder:text-gray-400"
              :placeholder="t('ui.ed_exam_title_placeholder')"
            />
          </div>

          <!-- 副標題/範圍 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_subtitle_label') }}</label>
            <input
              type="text"
              :value="localHeader.subtitle"
              @input="updateHeader('subtitle', $event.target.value)"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white text-gray-700 transition-[border-color,box-shadow] duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] placeholder:text-gray-400"
              :placeholder="t('ui.ed_subtitle_placeholder')"
            />
          </div>
        </div>
      </div>

      <!-- 題型順序管理 -->
      <div class="p-5 border-b border-gray-200">
        <div class="mb-4">
          <h3 class="text-base font-semibold text-gray-800">📋 {{ t('examDesigner.questionTypeOrder') }}</h3>
          <p class="text-[13px] text-gray-500 mt-1">{{ t('examDesigner.questionTypeOrderDescription') }}</p>
        </div>

        <div class="mb-5">
          <div
            v-for="(typeInfo, index) in orderedTypes"
            :key="typeInfo.type"
            class="flex items-center p-3 mb-2 bg-white border border-gray-200 rounded-md transition-all duration-200 cursor-move hover:border-gray-400 hover:shadow-[0_2px_4px_rgba(0,0,0,0.05)]"
            :class="typeInfo.count > 0 ? 'border-l-4 border-l-emerald-500' : ''"
            draggable="true"
            @dragstart="onDragStart(index)"
            @dragover.prevent
            @drop="onDrop(index)"
          >
            <div class="text-gray-400 mr-3 text-sm cursor-grab active:cursor-grabbing">⋮⋮</div>

            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-base">{{ getTypeIcon(typeInfo.type) }}</span>
                <span class="font-medium text-gray-700">{{ getTypeName(typeInfo.type) }}</span>
                <span class="text-xs font-medium" :class="typeInfo.count === 0 ? 'text-gray-400' : 'text-emerald-500'">
                  {{ typeInfo.count }} {{ t('examDesigner.questions') }}
                </span>
              </div>

              <div v-if="typeInfo.count > 0" class="ml-6">
                <div class="flex items-center gap-0.5">
                  <span
                    v-for="n in Math.min(3, typeInfo.count)"
                    :key="n"
                    class="w-1 h-1 bg-emerald-500 rounded-full"
                  ></span>
                  <span v-if="typeInfo.count > 3" class="text-[10px] text-gray-500 ml-1">
                    +{{ typeInfo.count - 3 }}
                  </span>
                </div>
              </div>

              <div v-else class="ml-6 text-xs text-gray-400">
                {{ t('examDesigner.noQuestions') }}
              </div>
            </div>

            <div class="flex gap-1">
              <button
                @click="startEditQuestionType(typeInfo.type)"
                class="w-6 h-6 border border-gray-300 rounded bg-white text-gray-500 text-xs cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400 hover:text-gray-700"
                :title="t('ui.ed_edit_type_title')"
              >
                ✏️
              </button>
              <button
                v-if="index > 0"
                @click="$emit('move-up', index)"
                class="w-6 h-6 border border-gray-300 rounded bg-white text-gray-500 text-xs cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400 hover:text-gray-700"
                :title="t('examDesigner.moveUp')"
              >
                ↑
              </button>
              <button
                v-if="index < orderedTypes.length - 1"
                @click="$emit('move-down', index)"
                class="w-6 h-6 border border-gray-300 rounded bg-white text-gray-500 text-xs cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400 hover:text-gray-700"
                :title="t('examDesigner.moveDown')"
              >
                ↓
              </button>
            </div>

            <!-- 題型編輯表單（展開式） -->
            <div
              v-if="editingQuestionType === typeInfo.type"
              class="w-full mt-3 p-3 bg-gray-50 border border-gray-200 rounded-md"
              @click.stop
            >
              <div class="mb-2.5">
                <label class="block text-xs font-medium text-gray-700 mb-1">{{ t('ui.ed_type_name_label') }}</label>
                <input
                  v-model="questionTypeCustomizations[typeInfo.type].name"
                  type="text"
                  class="w-full px-2.5 py-2 text-[13px] border border-gray-300 rounded bg-white text-gray-700 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)]"
                  :placeholder="QUESTION_TYPE_MAPPING[typeInfo.type]?.name || typeInfo.type"
                />
              </div>
              <div class="mb-2.5">
                <label class="block text-xs font-medium text-gray-700 mb-1">{{ t('ui.ed_instruction_text_label') }}</label>
                <textarea
                  v-model="questionTypeCustomizations[typeInfo.type].instruction"
                  class="w-full px-2.5 py-2 text-[13px] border border-gray-300 rounded bg-white text-gray-700 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)] resize-y min-h-[50px]"
                  rows="2"
                  :placeholder="SECTION_INSTRUCTIONS[typeInfo.type] || ''"
                ></textarea>
              </div>
              <div class="flex justify-end gap-2 mt-2.5">
                <button @click="cancelEditQuestionType" class="px-3 py-1.5 text-xs rounded cursor-pointer transition-all duration-200 bg-white border border-gray-300 text-gray-500 hover:bg-gray-100">{{ t('cancel') }}</button>
                <button @click="saveQuestionTypeCustomization(typeInfo.type)" class="px-3 py-1.5 text-xs rounded cursor-pointer transition-all duration-200 bg-primary-500 border border-primary-500 text-white hover:bg-primary-600">{{ t('save') }}</button>
              </div>
            </div>
          </div>
        </div>

        <div class="p-4 bg-[#fef7f0] border border-orange-200 rounded-md">
          <div class="mb-2 text-[13px] text-orange-800">
            <strong>{{ t('examDesigner.examStructurePreview') }}：</strong>
          </div>
          <div class="flex flex-col gap-1">
            <div
              v-for="(typeInfo, index) in orderedTypes.filter(t => t.count > 0)"
              :key="typeInfo.type"
              class="flex items-center gap-1.5 text-xs text-orange-900"
            >
              <span class="font-semibold min-w-[20px]">{{ index + 1 }}.</span>
              <span class="font-medium">{{ getTypeName(typeInfo.type) }}</span>
              <span class="text-yellow-700">({{ typeInfo.count }} {{ t('examDesigner.questions') }})</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 樣式設定區塊 -->
      <div class="p-5 border-b border-gray-200">
        <div class="mb-4">
          <h3 class="text-base font-semibold text-gray-800">🎨 {{ t('ui.ed_style_settings') }}</h3>
          <p class="text-[13px] text-gray-500 mt-1">{{ t('ui.ed_style_settings_desc') }}</p>
        </div>

        <!-- 快速套用模板 -->
        <div class="mb-4">
          <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_quick_apply_template') }}</label>
          <select
            v-model="selectedTemplate"
            @change="applyStyleTemplate(selectedTemplate)"
            class="w-full px-2 py-1.5 text-[13px] border border-gray-300 rounded bg-white text-gray-700 cursor-pointer transition-colors duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)]"
          >
            <option value="">{{ t('ui.ed_select_grade_template_option') }}</option>
            <option v-for="(template, key) in styleTemplates" :key="key" :value="key">
              {{ template.name }}
            </option>
          </select>
          <p v-if="selectedTemplate && styleTemplates[selectedTemplate]" class="text-xs text-gray-500 mt-1">
            {{ styleTemplates[selectedTemplate].description }}
          </p>
        </div>

        <div class="grid grid-cols-3 gap-3 max-[1200px]:grid-cols-1 max-[1200px]:gap-[10px]">
          <!-- 字體大小 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_font_size_label') }}</label>
            <select
              :value="localTypography.fontSize"
              @change="updateTypography('fontSize', Number($event.target.value))"
              class="w-full px-2 py-1.5 text-[13px] border border-gray-300 rounded bg-white text-gray-700 cursor-pointer transition-colors duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)]"
            >
              <option :value="9">{{ t('ui.ed_font_size_9') }}</option>
              <option :value="10">10pt</option>
              <option :value="11">{{ t('ui.ed_font_size_11') }}</option>
              <option :value="12">12pt</option>
              <option :value="14">{{ t('ui.ed_font_size_14') }}</option>
            </select>
          </div>

          <!-- 行距 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_line_height_label') }}</label>
            <select
              :value="localTypography.lineHeight"
              @change="updateTypography('lineHeight', Number($event.target.value))"
              class="w-full px-2 py-1.5 text-[13px] border border-gray-300 rounded bg-white text-gray-700 cursor-pointer transition-colors duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)]"
            >
              <option :value="1.2">{{ t('ui.ed_line_height_1_2') }}</option>
              <option :value="1.4">{{ t('ui.ed_line_height_1_4') }}</option>
              <option :value="1.6">{{ t('ui.ed_line_height_1_6') }}</option>
              <option :value="1.8">{{ t('ui.ed_line_height_1_8') }}</option>
            </select>
          </div>

          <!-- 圖片大小 -->
          <div class="flex flex-col gap-1">
            <label class="text-xs text-gray-500 font-medium">{{ t('ui.ed_image_size_label') }}</label>
            <select
              :value="localTypography.imageSize"
              @change="updateTypography('imageSize', $event.target.value)"
              class="w-full px-2 py-1.5 text-[13px] border border-gray-300 rounded bg-white text-gray-700 cursor-pointer transition-colors duration-200 hover:border-gray-400 focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.1)]"
            >
              <option value="small">{{ t('ui.ed_image_size_small') }}</option>
              <option value="medium">{{ t('ui.ed_image_size_medium') }}</option>
              <option value="large">{{ t('ui.ed_image_size_large') }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 逐題圖片尺寸（只有考卷裡有圖片題才顯示） -->
      <div v-if="imageQuestions.length" class="p-5 border-b border-gray-200">
        <div class="text-xs text-gray-500 font-medium mb-1">{{ t('ui.ed_image_override_title') }}</div>
        <p class="text-[11px] text-gray-400 mb-2">{{ t('ui.ed_image_override_hint') }}</p>
        <div v-for="(q, idx) in imageQuestions" :key="q.id" class="flex items-start gap-2 py-1.5 border-t border-gray-100 first:border-t-0">
          <img
            v-if="q.question_image_url"
            :src="q.question_image_url"
            class="w-10 h-10 object-contain border border-gray-200 rounded bg-white flex-shrink-0"
            alt=""
          />
          <div class="flex-1 min-w-0">
            <div class="text-[12px] text-gray-700 truncate" :title="q.question_image || q.content">
              {{ idx + 1 }}. {{ q.question_image || q.content }}
            </div>
            <div class="flex items-center gap-1 mt-1">
              <input
                type="number" min="10" max="172" step="5"
                :value="imageOverrides[q.id]?.width ?? ''"
                :placeholder="t('ui.ed_image_override_width')"
                @input="updateImageOverride(q.id, 'width', $event.target.value)"
                class="w-16 px-1.5 py-1 text-[12px] border border-gray-300 rounded focus:outline-none focus:border-primary-500"
              />
              <span class="text-[11px] text-gray-400">×</span>
              <input
                type="number" min="10" max="240" step="5"
                :value="imageOverrides[q.id]?.height ?? ''"
                :placeholder="t('ui.ed_image_override_height')"
                @input="updateImageOverride(q.id, 'height', $event.target.value)"
                class="w-16 px-1.5 py-1 text-[12px] border border-gray-300 rounded focus:outline-none focus:border-primary-500"
              />
              <span class="text-[11px] text-gray-400">mm</span>
              <button
                v-if="imageOverrides[q.id]"
                type="button"
                @click="resetImageOverride(q.id)"
                class="ml-1 text-[11px] text-primary-600 hover:underline"
              >{{ t('ui.ed_image_override_reset') }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 進階字體設定區塊 -->
      <div class="p-5 border-b border-gray-200">
        <div
          class="mb-4 cursor-pointer select-none hover:bg-gray-100 hover:rounded hover:!-m-2 hover:p-2"
          @click="showAdvancedTypography = !showAdvancedTypography"
        >
          <h3 class="text-base font-semibold text-gray-800">
            <span class="text-[10px] mr-1.5 text-gray-500">{{ showAdvancedTypography ? '▼' : '▶' }}</span>
            🔤 {{ t('examDesigner.advancedTypography') || '進階字體設定' }}
          </h3>
          <p class="text-[13px] text-gray-500 mt-1">{{ t('examDesigner.advancedTypographyDescription') || '個別調整各元素的字體大小、粗體、對齊' }}</p>
        </div>

        <div v-show="showAdvancedTypography" class="mt-3">
          <div
            v-for="(style, key) in localTypography.elements"
            :key="key"
            class="flex items-center gap-2.5 py-2 border-b border-gray-100 [&:last-of-type]:border-b-0"
          >
            <span class="w-20 text-[13px] text-gray-700 font-medium flex-shrink-0">{{ elementLabels[key] || key }}</span>

            <!-- 字體大小 -->
            <select
              :value="style.fontSize"
              @change="updateElementStyle(key, 'fontSize', Number($event.target.value))"
              class="px-2 py-1 text-xs border border-gray-300 rounded bg-white cursor-pointer w-[70px]"
            >
              <option v-for="size in fontSizeOptions" :key="size" :value="size">
                {{ size }}pt
              </option>
            </select>

            <!-- 粗體勾選 -->
            <label class="flex items-center gap-1 text-xs text-gray-500 cursor-pointer whitespace-nowrap">
              <input
                type="checkbox"
                :checked="style.fontWeight === 'bold'"
                @change="updateElementStyle(key, 'fontWeight', $event.target.checked ? 'bold' : 'normal')"
                class="w-3.5 h-3.5 cursor-pointer"
              />
              {{ t('ui.ed_bold_label') }}
            </label>

            <!-- 置中勾選 -->
            <label class="flex items-center gap-1 text-xs text-gray-500 cursor-pointer whitespace-nowrap">
              <input
                type="checkbox"
                :checked="style.textAlign === 'center'"
                @change="updateElementStyle(key, 'textAlign', $event.target.checked ? 'center' : 'left')"
                class="w-3.5 h-3.5 cursor-pointer"
              />
              {{ t('ui.ed_center_label') }}
            </label>
          </div>

          <!-- 重置按鈕 -->
          <button
            @click="resetTypographyElements"
            class="mt-3 px-3 py-1.5 text-xs text-gray-500 bg-gray-100 border border-gray-300 rounded cursor-pointer transition-all duration-200 hover:bg-gray-200 hover:text-gray-700"
          >
            🔄 {{ t('examDesigner.resetToDefault') || '重置為預設值' }}
          </button>
        </div>
      </div>

      <!-- 顯示選項區塊 -->
      <div class="p-5 border-b border-gray-200">
        <div class="mb-4">
          <h3 class="text-base font-semibold text-gray-800">👁️ {{ t('examDesigner.displayOptions') || '顯示選項' }}</h3>
          <p class="text-[13px] text-gray-500 mt-1">{{ t('examDesigner.displayOptionsDescription') || '控制考券上顯示的區域' }}</p>
        </div>

        <div class="flex flex-col gap-3">
          <!-- 學生資訊開關 -->
          <label class="flex items-center gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              :checked="localStudentInfo.enabled"
              @change="updateStudentInfo('enabled', $event.target.checked)"
              class="w-4 h-4 cursor-pointer"
            />
            <span class="text-[13px] text-gray-700">{{ t('examDesigner.enableStudentInfo') || '啟用學生資訊欄位' }}</span>
          </label>

          <!-- 家長簽名開關 -->
          <label class="flex items-center gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              :checked="localParentSignature.enabled"
              @change="updateParentSignature('enabled', $event.target.checked)"
              class="w-4 h-4 cursor-pointer"
            />
            <span class="text-[13px] text-gray-700">{{ t('examDesigner.enableParentSignature') || '啟用家長簽名框（左上角）' }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 底部操作按鈕 -->
    <div class="flex-shrink-0 border-t border-gray-200">
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
  DEFAULT_EXAM_SUBTITLE,
  STYLE_TEMPLATES,
  QUESTION_TYPE_MAPPING,
  SECTION_INSTRUCTIONS
} from '@/constants/examDefaults.js'

const { t } = useLanguage()

// 進階設定展開狀態
const showAdvancedTypography = ref(false)

// 題型名稱和說明編輯狀態
const editingQuestionType = ref(null)
const questionTypeCustomizations = ref({})

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
  school: 'School',
  subject: 'Subject',
  range: 'Range',
  parentSignature: "Parent's Signature",
  studentInfo: 'Student Info',
  grade: 'Grade',
  questionType: 'Question Type',
  instructions: 'Instructions',
  questionContent: 'Question'
}

// 年級樣式模板選項
const styleTemplates = STYLE_TEMPLATES
const selectedTemplate = ref('')

// 套用樣式模板
const applyStyleTemplate = (templateKey) => {
  if (!templateKey || !styleTemplates[templateKey]) return

  const template = styleTemplates[templateKey]
  localTypography.value.fontSize = template.settings.fontSize
  localTypography.value.lineHeight = template.settings.lineHeight
  localTypography.value.imageSize = template.settings.imageSize

  emit('update-styles', {
    typography: { ...localTypography.value }
  })
}

// 取得題型的自定義名稱（優先使用自定義，否則使用預設）
const getCustomTypeName = (type) => {
  return questionTypeCustomizations.value[type]?.name ||
         QUESTION_TYPE_MAPPING[type]?.name ||
         type
}

// 取得題型的自定義說明（優先使用自定義，否則使用預設）
const getCustomTypeInstruction = (type) => {
  return questionTypeCustomizations.value[type]?.instruction ||
         SECTION_INSTRUCTIONS[type] ||
         ''
}

// 開始編輯題型
const startEditQuestionType = (type) => {
  editingQuestionType.value = type
  // 初始化自定義設定（如果沒有）
  if (!questionTypeCustomizations.value[type]) {
    questionTypeCustomizations.value[type] = {
      name: QUESTION_TYPE_MAPPING[type]?.name || type,
      instruction: SECTION_INSTRUCTIONS[type] || ''
    }
  }
}

// 取消編輯
const cancelEditQuestionType = () => {
  editingQuestionType.value = null
}

// 儲存題型自定義設定
const saveQuestionTypeCustomization = (type) => {
  editingQuestionType.value = null
  emit('update-styles', {
    questionTypeSettings: { ...questionTypeCustomizations.value }
  })
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
  },
  // 考卷裡的圖片題（逐題尺寸欄位用）
  imageQuestions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['move-up', 'move-down', 'export', 'export-answer-sheet', 'reorder', 'update-styles'])

// 逐題圖片尺寸覆寫（mm）：{ [questionId]: { width?, height? } }
const imageOverrides = ref({ ...(props.examStyles?.imageOverrides || {}) })
watch(() => props.examStyles?.imageOverrides, (v) => {
  imageOverrides.value = { ...(v || {}) }
})

const emitImageOverrides = (next) => {
  imageOverrides.value = next
  emit('update-styles', { imageOverrides: next })
}

const updateImageOverride = (id, field, value) => {
  const num = value === '' ? null : Number(value)
  const current = { ...(imageOverrides.value[id] || {}) }
  if (num === null || Number.isNaN(num) || num <= 0) delete current[field]
  else current[field] = num
  const next = { ...imageOverrides.value }
  if (Object.keys(current).length) next[id] = current
  else delete next[id]
  emitImageOverrides(next)
}

const resetImageOverride = (id) => {
  const next = { ...imageOverrides.value }
  delete next[id]
  emitImageOverrides(next)
}

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
