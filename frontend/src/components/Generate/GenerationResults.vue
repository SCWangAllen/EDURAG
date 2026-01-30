<template>
  <!-- 生成結果 -->
  <div v-if="generatedQuestions.length > 0" class="bg-white shadow rounded-lg p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-medium text-gray-900">
        {{ t('generate.generatedResults') }} ({{ generatedQuestions.length }}{{ t('generate.questions') }})
      </h2>
      <div class="flex space-x-2">
        <button
          @click="$emit('export')"
          class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium"
        >
          {{ t('export') }}
        </button>
        <button
          @click="$emit('save')"
          :disabled="saving"
          class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50 flex items-center"
        >
          <svg v-if="saving" class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ saving ? (isEnglish ? 'Saving...' : '儲存中...') : t('save') }}
        </button>
      </div>
    </div>

    <!-- 題目列表模式 -->
    <div class="space-y-4">
      <div
        v-for="(question, index) in generatedQuestions"
        :key="index"
        class="border border-gray-200 rounded-lg p-4"
      >
        <div class="flex justify-between items-start mb-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {{ getQuestionTypeLabel(question.type) }} {{ index + 1 }}
          </span>
        </div>

        <div class="mb-3">
          <h4 class="font-medium text-gray-900 mb-2">{{ question.prompt }}</h4>

          <div v-if="question.options" class="mb-2">
            <ul class="space-y-1">
              <li v-for="(option, optIndex) in question.options" :key="optIndex" class="text-sm text-gray-700">
                {{ option }}
              </li>
            </ul>
          </div>
        </div>

        <div class="bg-gray-50 p-3 rounded">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <div>
              <span class="font-medium text-gray-700">{{ t('generate.answer') }}：</span>
              <span class="text-gray-900">{{ question.answer }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-700">{{ t('generate.source') }}：</span>
              <span class="text-gray-600">{{ t('generate.document') }} {{ question.source.document_id }}</span>
            </div>
          </div>
          <div class="mt-2">
            <span class="font-medium text-gray-700">{{ t('generate.explanation') }}：</span>
            <span class="text-gray-600">{{ question.explanation }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 空狀態 -->
  <div v-else class="bg-white shadow rounded-lg p-8 text-center">
    <div class="text-gray-500">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">{{ t('generate.readyToGenerate') }}</h3>
      <p class="text-sm text-gray-500 mb-4">{{ t('generate.selectRequirements') }}</p>
      <div class="text-left max-w-md mx-auto">
        <div class="flex items-center text-sm text-gray-600 mb-2">
          <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ t('generate.steps.selectTemplate') }}
        </div>
        <div class="flex items-center text-sm text-gray-600 mb-2">
          <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ t('generate.steps.selectDocument') }}
        </div>
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ t('generate.steps.setQuestionTypes') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '../../composables/useLanguage.js'
import { getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'

export default {
  name: 'GenerationResults',
  props: {
    generatedQuestions: {
      type: Array,
      default: () => []
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  emits: ['export', 'save'],
  setup() {
    const { t, isEnglish } = useLanguage()

    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || '未指定'
      return getQuestionTypeLabelUtil(type, t) || type
    }

    return {
      t,
      isEnglish,
      getQuestionTypeLabel
    }
  }
}
</script>
