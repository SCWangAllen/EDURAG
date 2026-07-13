<template>
  <div class="py-6">
    <!-- 文件範圍選擇 -->
    <DocumentRangeSelector
      v-model="selectedDocuments"
      :exam-info="examInfo"
    />

    <!-- 模板選擇（可選） -->
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
      <h4 class="text-base font-semibold text-gray-900 mb-4">📋 模板選擇 (可選)</h4>
      <div class="flex gap-6 mb-4">
        <label class="flex items-center gap-2 cursor-pointer text-sm font-medium">
          <input type="radio" v-model="templateMode" value="auto" class="cursor-pointer" />
          <span>🤖 自動匹配模板</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer text-sm font-medium">
          <input type="radio" v-model="templateMode" value="manual" class="cursor-pointer" />
          <span>✋ 手動選擇模板</span>
        </label>
      </div>

      <select
        v-if="templateMode === 'manual'"
        v-model="selectedTemplateId"
        class="w-full p-3 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500"
      >
        <option :value="null">請選擇模板...</option>
        <option v-for="template in availableTemplates" :key="template.id" :value="template.id">
          {{ template.name }} ({{ template.subject }})
        </option>
      </select>

      <div v-if="templateMode === 'auto'" class="p-3 bg-sky-100 border border-sky-200 rounded-md text-sm text-sky-800">
        💡 系統會自動為此題型找最合適的模板
      </div>
    </div>

    <!-- 生成按鈕 -->
    <div class="flex items-center gap-4 mb-6 flex-wrap">
      <button
        @click="handleGenerate(count)"
        :disabled="!canGenerate || isGenerating"
        class="px-6 py-3 rounded-lg text-base font-semibold cursor-pointer transition-all duration-200 flex items-center gap-2 bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-[0_4px_6px_rgba(59,130,246,0.3)] enabled:hover:from-primary-600 enabled:hover:to-primary-700 enabled:hover:shadow-[0_6px_8px_rgba(59,130,246,0.4)] enabled:hover:-translate-y-px disabled:bg-none disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none"
      >
        <span v-if="isGenerating" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
        <span v-else>🤖</span>
        {{ isGenerating ? '生成中...' : `生成 ${count} 題` }}
      </button>

      <button
        v-if="questions.length > 0 && questions.length < count"
        @click="handleSupplement"
        :disabled="isGenerating"
        class="px-6 py-3 rounded-lg text-base font-semibold cursor-pointer transition-all duration-200 flex items-center gap-2 bg-white text-primary-500 border-2 border-primary-500 enabled:hover:bg-primary-50 enabled:hover:-translate-y-px disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-300 disabled:cursor-not-allowed"
      >
        ➕ 補充生成 {{ count - selectedCount }} 題
      </button>

      <div v-if="!canGenerate" class="text-sm text-danger-600 font-medium">
        ⚠️ 請至少選擇一個文件
      </div>
    </div>

    <!-- 已生成題目列表 -->
    <GeneratedQuestionList
      :questions="questions"
      :target-count="count"
      @toggle-selection="handleToggleSelection"
      @remove-question="handleRemoveQuestion"
      @clear-unselected="handleClearUnselected"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DocumentRangeSelector from './DocumentRangeSelector.vue'
import GeneratedQuestionList from './GeneratedQuestionList.vue'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    required: true
  },
  examInfo: {
    type: Object,
    required: true
  },
  templates: {
    type: Array,
    default: () => []
  },
  questions: {
    type: Array,
    default: () => []
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'generate',
  'toggle-selection',
  'remove-question',
  'clear-unselected'
])

const selectedDocuments = ref([])
const templateMode = ref('auto')
const selectedTemplateId = ref(null)

const availableTemplates = computed(() => {
  return props.templates.filter(t => t.question_type === props.type)
})

const canGenerate = computed(() => {
  return selectedDocuments.value.length > 0
})

const selectedCount = computed(() => {
  return props.questions.filter(q => q.selected).length
})

const handleGenerate = (generateCount) => {
  if (!canGenerate.value) return

  const template = templateMode.value === 'manual'
    ? props.templates.find(t => t.id === selectedTemplateId.value)
    : null  // null 表示自動匹配

  emit('generate', {
    type: props.type,
    count: generateCount,
    documents: selectedDocuments.value,
    template: template
  })
}

const handleSupplement = () => {
  const neededCount = props.count - selectedCount.value
  if (neededCount > 0) {
    handleGenerate(neededCount)
  }
}

const handleToggleSelection = (question) => {
  emit('toggle-selection', { type: props.type, question })
}

const handleRemoveQuestion = (question) => {
  emit('remove-question', { type: props.type, question })
}

const handleClearUnselected = () => {
  emit('clear-unselected', props.type)
}

// 只有當科目變化時才重置文件選擇（避免無故清空）
watch(
  () => props.examInfo?.subject,
  (newSubject, oldSubject) => {
    if (newSubject !== oldSubject && oldSubject !== undefined) {
      selectedDocuments.value = []
    }
  }
)
</script>
