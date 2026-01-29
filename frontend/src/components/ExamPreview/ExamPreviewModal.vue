<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="closeModal"></div>
      
      <!-- 模態框內容 -->
      <div class="relative bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-xl transform transition-all">
        <!-- 頁眉 -->
        <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              {{ t('examPreview.modal.title', { title }) }}
            </h3>
            <div class="flex items-center space-x-3">
              <button
                @click="openPrintWindow"
                class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                {{ t('examPreview.modal.print') }}
              </button>
              <button
                @click="closeModal"
                class="text-gray-400 hover:text-gray-600"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 預覽資訊 -->
          <div class="mt-3 text-sm text-gray-600">
            <span>{{ t('examPreview.modal.questionCount', { count: questions.length }) }}</span>
            <span class="mx-2">|</span>
            <span>{{ t('examPreview.modal.subject', { subjects }) }}</span>
            <span class="mx-2">|</span>
            <span>{{ t('examPreview.modal.generatedTime', { time: new Date().toLocaleString() }) }}</span>
          </div>
        </div>
        
        <!-- 預覽內容 -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div class="bg-gray-100 p-4 rounded-lg">
            <div class="bg-white shadow-lg max-w-4xl mx-auto">
              <!-- 切換預覽模式 -->
              <div class="p-4 border-b border-gray-200 flex justify-end space-x-2">
                <button
                  @click="useTemplateView = false"
                  :class="[
                    'px-3 py-1 rounded text-sm font-medium',
                    !useTemplateView ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  ]"
                >
                  簡單預覽
                </button>
                <button
                  @click="useTemplateView = true"
                  :class="[
                    'px-3 py-1 rounded text-sm font-medium',
                    useTemplateView ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  ]"
                >
                  考卷格式預覽
                </button>
              </div>
              
              <!-- 根據選擇顯示不同預覽 -->
              <SimpleExamPreview
                v-if="!useTemplateView"
                :questions="questions"
                :config="examStyles"
              />
              <ExamTemplate
                v-else
                :examData="examData"
                :questions="questions"
              />
            </div>
          </div>
        </div>
        
        <!-- 頁尾 -->
        <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex justify-between items-center">
          <div class="text-sm text-gray-500">
            {{ t('examPreview.modal.hint') }}
          </div>
          <div class="flex space-x-3">
            <button
              @click="closeModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              {{ t('close') }}
            </button>
            <button
              @click="openPrintWindow"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
            >
              {{ t('examPreview.modal.openPrintWindow') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { exportToPDF } from '@/utils/pdfExporter.js'
import SimpleExamPreview from './SimpleExamPreview.vue'
import ExamTemplate from './ExamTemplate.vue'
import { useLanguage } from '../../composables/useLanguage.js'

const { t } = useLanguage()

// 切換預覽模式
const useTemplateView = ref(false)

// 考卷資料配置
const examData = ref({
  school: 'Abraham Academy',
  title: '2024 Semester 2 Science Exam',
  subtitle: 'Comprehensive Assessment'
})

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  questions: {
    type: Array,
    required: true
  },
  examStyles: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const subjects = computed(() => {
  const uniqueSubjects = [...new Set(props.questions.map(q => q.subject).filter(Boolean))]
  return uniqueSubjects.join(', ') || t('examPreview.modal.general')
})

// 移除不需要的 markdown 內容生成

const closeModal = () => {
  emit('close')
}

const openPrintWindow = async () => {
  const examData = {
    questions: props.questions,
    config: props.examStyles,
    questionTypeOrder: props.examStyles.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
  }
  
  const result = await exportToPDF(examData, `${props.title}.pdf`)
  
  if (result.success) {
  } else {
    alert(t('examPreview.modal.popupBlocked') + ': ' + result.message)
  }
}
</script>

<style scoped>
/* 模態框動畫 */
.fixed.inset-0 {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.transform.transition-all {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: scale(0.95) translateY(-20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
</style>