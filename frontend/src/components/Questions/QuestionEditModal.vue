<template>
  <div v-if="visible" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-4xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">{{ t('questions.editQuestion') }}</h3>
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

        <div class="p-6">
          <div class="space-y-6">
            <!-- Question Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.type') }} *</label>
              <select
                v-model="editForm.type"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="single_choice">{{ t('questions.single_choice') }}</option>
                <option value="cloze">{{ t('questions.cloze') }}</option>
                <option value="short_answer">{{ t('questions.short_answer') }}</option>
                <option value="true_false">{{ t('questions.true_false') }}</option>
                <option value="matching">{{ t('questions.matching') }}</option>
                <option value="sequence">{{ t('questions.sequence') }}</option>
                <option value="enumeration">{{ t('questions.enumeration') }}</option>
                <option value="symbol_identification">{{ t('questions.symbol_identification') }}</option>
                <option value="mixed">{{ t('questions.mixed') }}</option>
                <option value="auto">{{ t('questions.auto') }}</option>
              </select>
            </div>

            <!-- Question Content -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }} *</label>
              <textarea
                v-model="editForm.content"
                rows="4"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.contentPlaceholder')"
              ></textarea>
            </div>

            <!-- Options (for single choice questions) -->
            <div v-if="editForm.type === 'single_choice'">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.options') }} *</label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in editForm.options"
                  :key="index"
                  class="flex items-center space-x-2"
                >
                  <span class="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                    {{ String.fromCharCode(65 + index) }}
                  </span>
                  <input
                    v-model="editForm.options[index]"
                    type="text"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    :placeholder="t('questions.optionPlaceholder') + ' ' + String.fromCharCode(65 + index)"
                  >
                  <button
                    v-if="editForm.options.length > 2"
                    @click="removeOption(index)"
                    class="text-red-600 hover:text-red-800"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
                <button
                  v-if="editForm.options.length < 8"
                  @click="addOption"
                  class="flex items-center px-3 py-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                  {{ t('questions.addOption') }}
                </button>
              </div>
            </div>

            <!-- Correct Answer -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }} *</label>
              <input
                v-model="editForm.correct_answer"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.answerPlaceholder')"
              >
            </div>

            <!-- Explanation -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <textarea
                v-model="editForm.explanation"
                rows="3"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.explanationPlaceholder')"
              ></textarea>
            </div>

            <!-- Other Information -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.subject') }}</label>
                <input
                  v-model="editForm.subject"
                  type="text"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  :placeholder="t('questions.subjectPlaceholder')"
                >
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.chapter') }}</label>
                <input
                  v-model="editForm.chapter"
                  type="text"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  :placeholder="t('questions.chapterPlaceholder')"
                >
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.difficulty') }}</label>
                <select
                  v-model="editForm.difficulty"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="easy">{{ t('questions.easy') }}</option>
                  <option value="medium">{{ t('questions.medium') }}</option>
                  <option value="hard">{{ t('questions.hard') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.grade') }}</label>
                <select
                  v-model="editForm.grade"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">{{ t('questions.allGrades') }}</option>
                  <option value="G1">G1</option>
                  <option value="G2">G2</option>
                  <option value="G3">G3</option>
                  <option value="G4">G4</option>
                  <option value="G5">G5</option>
                  <option value="G6">G6</option>
                  <option value="ALL">ALL</option>
                </select>
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <button
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              {{ t('cancel') }}
            </button>
            <button
              @click="handleSave"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm"
            >
              {{ t('questions.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'

export default {
  name: 'QuestionEditModal',
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
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const editForm = reactive({
      type: '',
      content: '',
      options: [],
      correct_answer: '',
      explanation: '',
      subject: '',
      chapter: '',
      difficulty: 'medium',
      grade: ''
    })

    watch(() => props.question, (question) => {
      if (question) {
        editForm.type = question.type || ''
        editForm.content = question.content || ''
        editForm.options = question.options ? [...question.options] : []
        editForm.correct_answer = question.correct_answer || ''
        editForm.explanation = question.explanation || ''
        editForm.subject = question.subject || ''
        editForm.chapter = question.chapter || ''
        editForm.difficulty = question.difficulty || 'medium'
        editForm.grade = question.grade || ''

        if (editForm.type === 'single_choice' && editForm.options.length === 0) {
          editForm.options = ['', '', '', '']
        }
      }
    }, { immediate: true })

    const addOption = () => {
      editForm.options.push('')
    }

    const removeOption = (index) => {
      if (editForm.options.length > 2) {
        editForm.options.splice(index, 1)
      }
    }

    const handleSave = () => {
      emit('save', { ...editForm, options: [...editForm.options] })
    }

    return {
      t,
      editForm,
      addOption,
      removeOption,
      handleSave
    }
  }
}
</script>
