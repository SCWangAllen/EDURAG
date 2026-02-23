<template>
  <div v-if="visible" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-4xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">{{ t('questions.questionDetail') }}</h3>
            <button
              @click="$emit('close')"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="question" class="p-6">
          <div class="space-y-6">
            <!-- Question Content -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }}</label>
              <div class="p-4 bg-gray-50 rounded-md">
                {{ question.content }}
              </div>
            </div>

            <!-- Options (if single choice question) -->
            <div v-if="question.type === 'single_choice' && question.options">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.options') }}</label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in question.options"
                  :key="index"
                  class="flex items-center p-3 bg-gray-50 rounded-md"
                >
                  <span class="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    {{ String.fromCharCode(65 + index) }}
                  </span>
                  <span>{{ option }}</span>
                </div>
              </div>
            </div>

            <!-- Correct Answer -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }}</label>
              <div class="p-4 bg-green-50 border border-green-200 rounded-md">
                {{ question.correct_answer }}
              </div>
            </div>

            <!-- Explanation -->
            <div v-if="question.explanation">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <div class="p-4 bg-blue-50 border border-blue-200 rounded-md">
                {{ question.explanation }}
              </div>
            </div>

            <!-- Other Information -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.type') }}</label>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ getTypeLabel(question.type) }}
                </span>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.difficulty') }}</label>
                <span :class="getDifficultyColor(question.difficulty)" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium">
                  {{ getDifficultyLabel(question.difficulty) }}
                </span>
              </div>

              <div v-if="question.subject">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.subject') }}</label>
                <span>{{ question.subject }}</span>
              </div>

              <div v-if="question.grade">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.grade') }}</label>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {{ question.grade }}
                </span>
              </div>

              <div v-if="question.chapter">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.chapter') }}</label>
                <span>{{ question.chapter }}</span>
              </div>

              <div v-if="question.page || question.page_number">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.pageNumber') || '頁數' }}</label>
                <span>{{ question.page || question.page_number }}</span>
              </div>
            </div>

            <!-- Source Content -->
            <div v-if="question.source_content">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.sourceContent') }}</label>
              <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-md max-h-40 overflow-y-auto">
                {{ question.source_content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '@/composables/useLanguage.js'
import { getDifficultyColor, getQuestionTypeLabel } from '@/utils/formatters.js'

export default {
  name: 'QuestionDetailModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    question: {
      type: Object,
      default: null
    }
  },
  emits: ['close'],
  setup(props) {
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
      getDifficultyColor
    }
  }
}
</script>
