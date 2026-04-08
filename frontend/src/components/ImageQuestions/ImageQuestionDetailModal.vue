<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity" @click="$emit('close')">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.questionDetail') }}</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div v-if="question" class="px-4 py-5 sm:p-6">
          <!-- Images -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <!-- Question Image -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('imageQuestions.questionImage') }}</h4>
              <div class="border rounded-lg overflow-hidden bg-gray-50">
                <img
                  v-if="questionImageUrl"
                  :src="questionImageUrl"
                  :alt="question.question_image"
                  class="w-full h-auto"
                  @error="questionImageError = true"
                />
                <div v-else class="flex items-center justify-center h-48 text-gray-400">
                  <div class="text-center">
                    <svg class="mx-auto w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <span class="text-sm">{{ t('imageQuestions.questionImageMissing') }}</span>
                  </div>
                </div>
              </div>
              <p class="mt-1 text-xs text-gray-500 truncate">{{ question.question_image_path }}</p>
            </div>

            <!-- Answer Image -->
            <div v-if="question.answer_image">
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('imageQuestions.answerImage') }}</h4>
              <div class="border rounded-lg overflow-hidden bg-gray-50">
                <img
                  v-if="answerImageUrl"
                  :src="answerImageUrl"
                  :alt="question.answer_image"
                  class="w-full h-auto"
                  @error="answerImageError = true"
                />
                <div v-else class="flex items-center justify-center h-48 text-gray-400">
                  <div class="text-center">
                    <svg class="mx-auto w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <span class="text-sm">{{ t('imageQuestions.answerImageMissing') }}</span>
                  </div>
                </div>
              </div>
              <p class="mt-1 text-xs text-gray-500 truncate">{{ question.answer_image_path }}</p>
            </div>
          </div>

          <!-- Metadata -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <span class="text-xs text-gray-500 block">{{ t('imageQuestions.subject') }}</span>
              <span class="font-medium">{{ question.subject }}</span>
            </div>
            <div v-if="question.grade">
              <span class="text-xs text-gray-500 block">{{ t('imageQuestions.grade') }}</span>
              <span class="font-medium">{{ question.grade }}</span>
            </div>
            <div v-if="question.chapter">
              <span class="text-xs text-gray-500 block">{{ t('imageQuestions.chapter') }}</span>
              <span class="font-medium">{{ question.chapter }}</span>
            </div>
            <div v-if="question.page">
              <span class="text-xs text-gray-500 block">{{ t('imageQuestions.page') }}</span>
              <span class="font-medium">{{ question.page }}</span>
            </div>
          </div>

          <!-- Description -->
          <div v-if="question.question_description" class="mb-6">
            <span class="text-xs text-gray-500 block mb-1">{{ t('imageQuestions.description') }}</span>
            <p class="text-gray-700">{{ question.question_description }}</p>
          </div>

          <!-- Verification status -->
          <div class="flex items-center mb-6">
            <span
              :class="[
                'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                question.images_verified
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              ]"
            >
              <svg
                v-if="question.images_verified"
                class="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              {{ question.images_verified ? t('imageQuestions.imageVerified') : t('imageQuestions.imageNotVerified') }}
            </span>
          </div>

          <!-- Timestamps -->
          <div class="grid grid-cols-2 gap-4 text-sm text-gray-500">
            <div>
              <span class="block">{{ t('imageQuestions.createdAt') }}</span>
              <span>{{ formatDate(question.created_at) }}</span>
            </div>
            <div>
              <span class="block">{{ t('imageQuestions.updatedAt') }}</span>
              <span>{{ formatDate(question.updated_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="$emit('edit', question)"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            {{ t('imageQuestions.edit') }}
          </button>
          <button
            @click="$emit('delete', question)"
            class="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            {{ t('imageQuestions.delete') }}
          </button>
          <button
            @click="$emit('close')"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            {{ t('imageQuestions.close') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { getQuestionImageUrl, getAnswerImageUrl } from '@/api/imageQuestionService.js'

export default {
  name: 'ImageQuestionDetailModal',
  props: {
    visible: { type: Boolean, default: false },
    question: { type: Object, default: null },
  },
  emits: ['close', 'edit', 'delete'],
  setup(props) {
    const { t } = useLanguage()
    const questionImageError = ref(false)
    const answerImageError = ref(false)

    const questionImageUrl = computed(() => {
      if (questionImageError.value || !props.question) return null
      return getQuestionImageUrl(props.question.question_image_path)
    })

    const answerImageUrl = computed(() => {
      if (answerImageError.value || !props.question?.answer_image_path) return null
      return getAnswerImageUrl(props.question.answer_image_path)
    })

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    // Reset error states when question changes
    watch(() => props.question, () => {
      questionImageError.value = false
      answerImageError.value = false
    })

    return {
      t,
      questionImageUrl,
      answerImageUrl,
      questionImageError,
      answerImageError,
      formatDate,
    }
  },
}
</script>
