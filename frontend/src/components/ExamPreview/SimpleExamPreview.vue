<template>
  <div class="pdf-preview">
    <!-- 載入中提示 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在生成 PDF 預覽...</p>
    </div>

    <!-- PDF 預覽（iframe） -->
    <iframe
      v-if="pdfBlobUrl && !isLoading"
      :src="pdfBlobUrl"
      class="pdf-iframe"
      title="PDF Preview"
    />

    <!-- 空狀態提示 -->
    <div v-if="!pdfBlobUrl && !isLoading && !error" class="empty-state">
      <p>請選擇題目以預覽考券</p>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import { generatePDFPreview } from '@/utils/pdfExporter.js'

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  config: {
    type: Object,
    default: () => ({})
  },
  questionTypeOrder: {
    type: Array,
    default: () => ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
  },
  editable: {
    type: Boolean,
    default: false
  },
  questionTypeConfig: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update-config'])

const pdfBlobUrl = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Debounce 實作
let debounceTimer = null
const useDebounceFn = (fn, delay) => {
  return (...args) => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => fn(...args), delay)
  }
}

// 檢查是否有題目可供預覽
const hasQuestions = computed(() => {
  return props.questions && props.questions.length > 0
})

// 生成 PDF 預覽
const generatePreview = async () => {
  // 無題目時不生成
  if (!hasQuestions.value) {
    pdfBlobUrl.value = null
    return
  }

  isLoading.value = true
  error.value = null

  // 清理舊的 blob URL
  if (pdfBlobUrl.value) {
    URL.revokeObjectURL(pdfBlobUrl.value)
    pdfBlobUrl.value = null
  }

  try {
    const examData = {
      questions: props.questions,
      config: props.config,
      questionTypeOrder: props.questionTypeOrder,
      questionTypeConfig: props.questionTypeConfig
    }

    const result = await generatePDFPreview(examData)

    if (result.success) {
      pdfBlobUrl.value = result.blobUrl
    } else {
      error.value = result.message || 'PDF 生成失敗'
    }
  } catch (e) {
    error.value = e.message || '發生未知錯誤'
  } finally {
    isLoading.value = false
  }
}

// Debounce 防抖（500ms）
const debouncedGenerate = useDebounceFn(generatePreview, 500)

// 監聽 props 變化，自動更新預覽
watch(
  () => [props.questions, props.config, props.questionTypeOrder, props.questionTypeConfig],
  () => {
    debouncedGenerate()
  },
  { deep: true, immediate: true }
)

// 清理 blob URL
onBeforeUnmount(() => {
  clearTimeout(debounceTimer)
  if (pdfBlobUrl.value) {
    URL.revokeObjectURL(pdfBlobUrl.value)
  }
})
</script>

<style scoped>
.pdf-preview {
  width: 100%;
  height: 100%;
  min-height: 500px;
  position: relative;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border: none;
  background: white;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 12px;
  color: #6b7280;
  font-size: 14px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 14px;
}

.error-message {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  color: #dc2626;
  background: rgba(255, 255, 255, 0.95);
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}
</style>
