<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <label class="flex items-center">
            <input
              type="checkbox"
              :checked="isAllSelected"
              @change="$emit('toggle-select-all')"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <span class="ml-2 text-sm text-gray-600">{{ t('questions.selectAll') }}</span>
          </label>
          <h2 class="text-lg font-medium text-gray-900">{{ t('questions.questionList') }}</h2>
        </div>
        <div class="text-sm text-gray-500">
          {{ selectedQuestions.length > 0 ? `${selectedQuestions.length}/${totalQuestions}` : totalQuestions }} {{ t('questions.results') }}
        </div>
      </div>
    </div>

    <div v-if="loading" class="p-6 text-center">
      <div class="inline-flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ t('questions.loading') }}
      </div>
    </div>

    <div v-else-if="questions.length === 0" class="p-6 text-center text-gray-500">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <p>{{ t('questions.noQuestions') }}</p>
      <p class="text-sm mt-1">{{ t('questions.noQuestionsHint') }}</p>
    </div>

    <div v-else class="divide-y divide-gray-200">
      <div
        v-for="question in questions"
        :key="question.id"
        class="p-6 hover:bg-gray-50"
        :class="{ 'bg-blue-50 border-l-4 border-blue-500': selectedQuestions.some(q => q.id === question.id) }"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3">
            <input
              type="checkbox"
              :checked="selectedQuestions.some(q => q.id === question.id)"
              @change="$emit('toggle-select', question)"
              @click.stop
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <div class="flex-1 min-w-0 cursor-pointer" @click="$emit('select', question)">
              <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ getTypeLabel(question.type) }}
                </span>
                <span v-if="question.subject" :class="getSubjectColor(question.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ t(`subjects.${question.subject.toLowerCase()}`) || question.subject }}
                </span>
                <span :class="getDifficultyColor(question.difficulty)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ getDifficultyLabel(question.difficulty) }}
                </span>
              </div>

              <div class="mt-2">
                <h3 class="text-sm font-medium text-gray-900 line-clamp-2">
                  {{ question.content }}
                </h3>
              </div>

              <div class="mt-2 text-sm text-gray-500">
                <span v-if="question.chapter">{{ question.chapter }} • </span>
                {{ formatDate(question.created_at) }}
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <button
              @click.stop="$emit('select', question)"
              class="text-gray-400 hover:text-blue-600"
              :title="t('questions.view')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
            </button>
            <button
              @click.stop="$emit('edit', question)"
              class="text-gray-400 hover:text-green-600"
              :title="t('questions.edit')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button
              @click.stop="$emit('delete', question)"
              class="text-gray-400 hover:text-red-600"
              :title="t('questions.delete')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
      <div class="flex-1 flex justify-between sm:hidden">
        <button
          @click="$emit('change-page', currentPage - 1)"
          :disabled="currentPage <= 1"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          {{ t('questions.previous') }}
        </button>
        <button
          @click="$emit('change-page', currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          {{ t('questions.next') }}
        </button>
      </div>

      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            {{ t('questions.showing') }} <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
            {{ t('questions.to') }} <span class="font-medium">{{ Math.min(currentPage * pageSize, totalQuestions) }}</span>
            {{ t('questions.of') }} <span class="font-medium">{{ totalQuestions }}</span> {{ t('questions.results') }}
          </p>
        </div>

        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
            <button
              @click="$emit('change-page', currentPage - 1)"
              :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
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
              :disabled="currentPage >= totalPages"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '@/composables/useLanguage.js'
import { getSubjectColor, getDifficultyColor, formatDate, getQuestionTypeLabel } from '@/utils/formatters.js'

export default {
  name: 'QuestionListSection',
  props: {
    questions: { type: Array, required: true },
    loading: { type: Boolean, default: false },
    selectedQuestions: { type: Array, default: () => [] },
    totalQuestions: { type: Number, default: 0 },
    currentPage: { type: Number, default: 1 },
    totalPages: { type: Number, default: 0 },
    pageNumbers: { type: Array, default: () => [] },
    pageSize: { type: Number, default: 20 },
    isAllSelected: { type: Boolean, default: false }
  },
  emits: ['select', 'edit', 'delete', 'toggle-select', 'toggle-select-all', 'change-page'],
  setup() {
    const { t } = useLanguage()

    const getTypeLabel = (type) => getQuestionTypeLabel(type, t)

    const getDifficultyLabel = (difficulty) => {
      const difficultyMap = {
        'easy': t('questions.easy'),
        'medium': t('questions.medium'),
        'hard': t('questions.hard')
      }
      return difficultyMap[difficulty] || difficulty
    }

    return {
      t,
      getTypeLabel,
      getDifficultyLabel,
      getDifficultyColor,
      getSubjectColor,
      formatDate
    }
  }
}
</script>
