<template>
  <div
    class="p-6 hover:bg-gray-50"
    :class="{ 'bg-blue-50 border-l-4 border-blue-500': isSelected }"
  >
    <div class="flex items-start justify-between">
      <div class="flex items-start space-x-3">
        <input
          type="checkbox"
          :checked="isSelected"
          @change="$emit('toggle-select', question)"
          @click.stop
          class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        >
        <div class="flex-1 min-w-0 cursor-pointer" @click="$emit('view', question)">
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
          @click.stop="$emit('view', question)"
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
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage'
import { getSubjectColor, getDifficultyColor, formatDate, getQuestionTypeLabel } from '@/utils/formatters.js'

defineProps({
  question: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-select', 'view', 'edit', 'delete'])

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
</script>
