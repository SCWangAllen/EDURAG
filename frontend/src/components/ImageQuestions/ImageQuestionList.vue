<template>
  <div class="bg-white shadow rounded-lg">
    <!-- Header -->
    <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
      <div class="flex justify-between items-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          {{ t('imageQuestions.questionList') }} ({{ totalQuestions }} {{ t('imageQuestions.totalCount') }})
        </h3>
        <div class="flex items-center space-x-2">
          <input
            type="checkbox"
            :checked="isAllSelected"
            @change="$emit('toggle-select-all')"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span class="text-sm text-gray-500">{{ t('selectAll') }}</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="ml-2 text-gray-500">{{ t('imageQuestions.loading') }}</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="questions.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">{{ t('imageQuestions.noQuestions') }}</h3>
      <p class="mt-1 text-sm text-gray-500">{{ t('imageQuestions.noQuestionsHint') }}</p>
    </div>

    <!-- Question Grid -->
    <div v-else class="p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ImageQuestionCard
          v-for="question in questions"
          :key="question.id"
          :question="question"
          :selected="isSelected(question)"
          @view="$emit('view', question)"
          @edit="$emit('edit', question)"
          @delete="$emit('delete', question)"
          @toggle-select="$emit('toggle-select', question)"
          @upload-image="$emit('upload-image', $event)"
        />
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="px-4 py-3 bg-gray-50 border-t border-gray-200 sm:px-6">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          {{ t('imageQuestions.showing') }} {{ (currentPage - 1) * pageSize + 1 }}
          {{ t('imageQuestions.to') }} {{ Math.min(currentPage * pageSize, totalQuestions) }}
          {{ t('imageQuestions.of') }} {{ totalQuestions }} {{ t('imageQuestions.results') }}
        </div>
        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
          <button
            @click="$emit('change-page', currentPage - 1)"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="sr-only">{{ t('imageQuestions.previous') }}</span>
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <button
            v-for="page in pageNumbers"
            :key="page"
            @click="$emit('change-page', page)"
            :class="[
              'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
              page === currentPage
                ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
          <button
            @click="$emit('change-page', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="sr-only">{{ t('imageQuestions.next') }}</span>
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import ImageQuestionCard from './ImageQuestionCard.vue'

export default {
  name: 'ImageQuestionList',
  components: { ImageQuestionCard },
  props: {
    questions: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    selectedQuestions: { type: Array, default: () => [] },
    totalQuestions: { type: Number, default: 0 },
    currentPage: { type: Number, default: 1 },
    totalPages: { type: Number, default: 0 },
    pageSize: { type: Number, default: 20 },
    isAllSelected: { type: Boolean, default: false },
  },
  emits: ['view', 'edit', 'delete', 'toggle-select', 'toggle-select-all', 'change-page', 'upload-image'],
  setup(props) {
    const { t } = useLanguage()

    const isSelected = (question) => {
      return props.selectedQuestions.some(q => q.id === question.id)
    }

    const pageNumbers = computed(() => {
      const pages = []
      const start = Math.max(1, props.currentPage - 2)
      const end = Math.min(props.totalPages, start + 4)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    return { t, isSelected, pageNumbers }
  },
}
</script>
