<template>
  <div
    :class="[
      'border rounded-lg overflow-hidden cursor-pointer transition-all',
      selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
    ]"
    @click="$emit('view')"
  >
    <!-- Image Preview -->
    <div class="relative aspect-video bg-gray-100">
      <img
        v-if="questionImageUrl"
        :src="questionImageUrl"
        :alt="question.question_image"
        class="w-full h-full object-contain"
        @error="handleImageError"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </div>

      <!-- Selection checkbox -->
      <div class="absolute top-2 left-2" @click.stop>
        <input
          type="checkbox"
          :checked="selected"
          @change="$emit('toggle-select')"
          class="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer"
        />
      </div>

      <!-- Verification badge -->
      <div class="absolute top-2 right-2" @click.stop>
        <span
          v-if="question.images_verified"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
        >
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ t('imageQuestions.imageVerified') }}
        </span>
        <!-- Enhanced unverified badge with upload button -->
        <div v-else class="flex flex-col items-end space-y-1">
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            {{ t('imageQuestions.imageNotVerified') }}
          </span>
          <!-- Upload button for missing image -->
          <button
            @click="$emit('upload-image', { name: question.question_image, type: 'questions' })"
            class="inline-flex items-center px-2 py-1 rounded text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 transition-colors"
            :title="getMissingImageText()"
          >
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            {{ t('imageQuestions.uploadNow') }}
          </button>
        </div>
      </div>

      <!-- Answer image indicator -->
      <div v-if="question.answer_image" class="absolute bottom-2 right-2">
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {{ t('imageQuestions.answerImage') }}
        </span>
      </div>
    </div>

    <!-- Info -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-2">
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {{ question.subject }}
        </span>
        <span v-if="question.grade" class="text-xs text-gray-500">{{ question.grade }}</span>
      </div>

      <p v-if="question.question_description" class="text-sm text-gray-700 line-clamp-2 mb-2">
        {{ question.question_description }}
      </p>

      <div class="flex items-center justify-between text-xs text-gray-500">
        <span v-if="question.chapter" class="truncate max-w-[120px]">{{ question.chapter }}</span>
        <span v-if="question.page">P.{{ question.page }}</span>
      </div>

      <!-- Actions -->
      <div class="mt-3 pt-3 border-t border-gray-100 flex justify-end space-x-2" @click.stop>
        <button
          @click="$emit('edit')"
          class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded"
        >
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          {{ t('imageQuestions.edit') }}
        </button>
        <button
          @click="$emit('delete')"
          class="inline-flex items-center px-2 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded"
        >
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          {{ t('imageQuestions.delete') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { getQuestionImageUrl } from '@/api/imageQuestionService.js'

export default {
  name: 'ImageQuestionCard',
  props: {
    question: { type: Object, required: true },
    selected: { type: Boolean, default: false },
  },
  emits: ['view', 'edit', 'delete', 'toggle-select', 'upload-image'],
  setup(props) {
    const { t } = useLanguage()
    const imageError = ref(false)

    const questionImageUrl = computed(() => {
      if (imageError.value) return null
      return getQuestionImageUrl(props.question.question_image_path)
    })

    const handleImageError = () => {
      imageError.value = true
    }

    const getMissingImageText = () => {
      // Show the expected filename for the missing image
      const q = props.question
      const ext = q.question_image_ext || 'jpg'
      return t('imageQuestions.missingImage').replace('{filename}', `${q.question_image}.${ext}`)
    }

    return { t, questionImageUrl, handleImageError, getMissingImageText }
  },
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
