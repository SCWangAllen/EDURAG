<template>
  <div class="type-generate-section">
    <!-- 文件範圍選擇 -->
    <DocumentRangeSelector
      v-model="selectedDocuments"
      :exam-info="examInfo"
    />

    <!-- 模板選擇（可選） -->
    <div class="template-selector-section">
      <h4 class="section-title">📋 模板選擇 (可選)</h4>
      <div class="template-options">
        <label class="radio-option">
          <input type="radio" v-model="templateMode" value="auto" />
          <span>🤖 自動匹配模板</span>
        </label>
        <label class="radio-option">
          <input type="radio" v-model="templateMode" value="manual" />
          <span>✋ 手動選擇模板</span>
        </label>
      </div>

      <select
        v-if="templateMode === 'manual'"
        v-model="selectedTemplateId"
        class="template-select"
      >
        <option :value="null">請選擇模板...</option>
        <option v-for="template in availableTemplates" :key="template.id" :value="template.id">
          {{ template.name }} ({{ template.subject }})
        </option>
      </select>

      <div v-if="templateMode === 'auto'" class="auto-template-hint">
        💡 系統會自動為此題型找最合適的模板
      </div>
    </div>

    <!-- 生成按鈕 -->
    <div class="generate-actions">
      <button
        @click="handleGenerate(count)"
        :disabled="!canGenerate || isGenerating"
        class="btn-generate"
      >
        <span v-if="isGenerating" class="spinner-sm"></span>
        <span v-else>🤖</span>
        {{ isGenerating ? '生成中...' : `生成 ${count} 題` }}
      </button>

      <button
        v-if="questions.length > 0 && questions.length < count"
        @click="handleSupplement"
        :disabled="isGenerating"
        class="btn-supplement"
      >
        ➕ 補充生成 {{ count - selectedCount }} 題
      </button>

      <div v-if="!canGenerate" class="validation-hint">
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

<style scoped>
.type-generate-section {
  padding: 1.5rem 0;
}

.template-selector-section {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.template-options {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.radio-option input[type="radio"] {
  cursor: pointer;
}

.template-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.template-select:focus {
  outline: none;
  border-color: #3b82f6;
  ring: 2px;
  ring-color: #bfdbfe;
}

.auto-template-hint {
  padding: 0.75rem;
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #075985;
}

.generate-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.btn-generate,
.btn-supplement {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-generate {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.btn-generate:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  box-shadow: 0 6px 8px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

.btn-generate:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-supplement {
  background: white;
  color: #3b82f6;
  border: 2px solid #3b82f6;
}

.btn-supplement:hover:not(:disabled) {
  background: #eff6ff;
  transform: translateY(-1px);
}

.btn-supplement:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  border-color: #d1d5db;
  cursor: not-allowed;
}

.spinner-sm {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.validation-hint {
  font-size: 0.875rem;
  color: #dc2626;
  font-weight: 500;
}
</style>
