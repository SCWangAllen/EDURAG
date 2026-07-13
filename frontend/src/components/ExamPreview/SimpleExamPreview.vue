<template>
  <div class="w-full h-full min-h-[500px] relative bg-gray-100 rounded overflow-hidden">
    <!-- 載入中提示 -->
    <div v-if="isLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/95 z-10">
      <div class="w-10 h-10 border-[3px] border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
      <p class="mt-3 text-gray-500 text-sm">正在生成 PDF 預覽...</p>
    </div>

    <!-- PDF 預覽（iframe） -->
    <iframe
      v-if="pdfBlobUrl && !isLoading"
      :src="pdfBlobUrl"
      class="w-full h-full min-h-[500px] border-none bg-white"
      title="PDF Preview"
    />

    <!-- 空狀態提示 -->
    <div v-if="!pdfBlobUrl && !isLoading && !error" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      <p>請選擇題目以預覽考券</p>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="absolute inset-0 flex flex-col items-center justify-center p-5 text-center text-danger-600 bg-white/95">
      <span class="text-[2rem] mb-2">⚠️</span>
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
