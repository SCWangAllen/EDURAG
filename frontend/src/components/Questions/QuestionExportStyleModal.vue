<template>
  <div v-if="visible" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-5xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
              🎨 {{ t('questions.selectedQuestionsStyleEditor') }} ({{ selectedQuestions.length }} {{ t('questions.selectedQuestions') }})
            </h3>
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
          <div class="space-y-4">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-sm font-medium text-gray-900">{{ t('questions.customStyleSettings') }}</h4>
              <button
                @click="showExamStyleEditor = !showExamStyleEditor"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                {{ showExamStyleEditor ? t('questions.hideEditor') : t('questions.showEditor') }}
              </button>
            </div>

            <!-- Style Editor -->
            <div v-if="showExamStyleEditor" class="space-y-4 max-h-96 overflow-y-auto">

              <!-- Export Options -->
              <div class="bg-blue-50 p-4 rounded border">
                <h5 class="font-medium text-blue-800 mb-3">📦 {{ t('questions.exportContentSelection') }}</h5>
                <div class="flex gap-4">
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.questionsOnly"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.answerSheetOnly = false; examStyles.exportOptions.completeExam = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📝 {{ t('questions.questionsOnly') }}</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.answerSheetOnly"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.questionsOnly = false; examStyles.exportOptions.completeExam = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📋 {{ t('questions.answerSheetOnly') }}</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.completeExam"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.questionsOnly = false; examStyles.exportOptions.answerSheetOnly = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📚 {{ t('questions.completeExam') }}</span>
                  </label>
                </div>
              </div>

              <!-- Exam Header Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <div class="flex items-center justify-between mb-3">
                  <h5 class="font-medium text-gray-800">📋 {{ t('questions.examHeaderSettings') }}</h5>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.header.enabled"
                      type="checkbox"
                      class="mr-2"
                    />
                    <span class="text-sm text-gray-600">{{ t('questions.enable') }}</span>
                  </label>
                </div>
                <div v-if="examStyles.header.enabled" class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.titlePrefix') }}</label>
                    <input
                      v-model="examStyles.header.titlePrefix"
                      :placeholder="t('questions.examinationExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.subtitle') }}</label>
                    <input
                      v-model="examStyles.header.subtitle"
                      :placeholder="t('questions.finalExamExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.timeLimit') }}</label>
                    <input
                      v-model="examStyles.header.duration"
                      :placeholder="t('questions.ninetyMinutesExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.totalScore') }}</label>
                    <input
                      v-model="examStyles.header.totalScore"
                      :placeholder="t('questions.hundredPointsExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                </div>
              </div>

              <!-- Question Section Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <h5 class="font-medium text-gray-800 mb-3">📝 {{ t('questions.questionSectionSettings') }}</h5>
                <div class="space-y-3">

                  <!-- Multiple Choice Settings -->
                  <div class="border border-blue-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-blue-700">Multiple Choice Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.singleChoice.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.singleChoice.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.singleChoice.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.singleChoice.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Fill-in-the-Blank Settings -->
                  <div class="border border-green-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-green-700">Fill-in-the-Blank Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.cloze.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.cloze.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.cloze.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.cloze.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Short Answer Settings -->
                  <div class="border border-yellow-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-yellow-700">Short Answer Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.shortAnswer.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.shortAnswer.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.shortAnswer.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.shortAnswer.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Auto Question Settings -->
                  <div class="border border-purple-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-purple-700">Auto Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.auto.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.auto.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.auto.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.auto.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                </div>
              </div>

              <!-- Answer Sheet Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <div class="flex items-center justify-between mb-3">
                  <h5 class="font-medium text-gray-800">📋 {{ t('questions.answerSheetSettings') }}</h5>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.answerSheet.enabled"
                      type="checkbox"
                      class="mr-2"
                    />
                    <span class="text-sm text-gray-600">{{ t('questions.enable') }} {{ t('questions.answerSheet') }}</span>
                  </label>
                </div>
                <div v-if="examStyles.answerSheet.enabled" class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.answerSheetFormat') }}</label>
                    <select
                      v-model="examStyles.answerSheet.format"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    >
                      <option value="table">{{ t('questions.tableFormat') }}</option>
                      <option value="list">{{ t('questions.listFormat') }}</option>
                      <option value="grid">{{ t('questions.gridFormat') }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.includeExplanation') }}</label>
                    <label class="flex items-center mt-1">
                      <input
                        v-model="examStyles.answerSheet.includeExplanation"
                        type="checkbox"
                        class="mr-2"
                      />
                      <span class="text-sm">{{ t('questions.showDetailedExplanation') }}</span>
                    </label>
                  </div>
                </div>
              </div>

            </div>

            <!-- Action Buttons -->
            <div class="flex justify-between items-center pt-4 border-t">
              <div class="flex gap-2">
                <button
                  @click="$emit('preview')"
                  class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                >
                  📋 {{ t('questions.previewStyle') }}
                </button>
                <button
                  @click="$emit('open-designer')"
                  class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
                >
                  🎨 {{ t('examDesigner.title') }}
                </button>
                <button
                  @click="handleSaveStyle"
                  class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                >
                  💾 {{ t('questions.saveStyle') }}
                </button>
              </div>

              <div class="flex gap-2">
                <button
                  @click="$emit('close')"
                  class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                >
                  {{ t('questions.cancel') }}
                </button>
                <button
                  @click="$emit('export')"
                  :disabled="exporting"
                  class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm disabled:opacity-50"
                >
                  <span v-if="exporting">{{ t('questions.exportingInProgress') }}</span>
                  <span v-else-if="examStyles.exportOptions.questionsOnly">📝 {{ t('questions.exportQuestions') }}</span>
                  <span v-else-if="examStyles.exportOptions.answerSheetOnly">📋 {{ t('questions.exportAnswerSheet') }}</span>
                  <span v-else>📚 {{ t('questions.exportCompleteExam') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useToast } from '@/composables/useToast.js'

export default {
  name: 'QuestionExportStyleModal',
  props: {
    visible: { type: Boolean, default: false },
    selectedQuestions: { type: Array, default: () => [] },
    exporting: { type: Boolean, default: false },
    examStyles: { type: Object, required: true }
  },
  emits: ['close', 'export', 'open-designer', 'preview', 'save-style'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    const showExamStyleEditor = ref(false)
    const selectedExamTemplate = ref('standard')

    const handleSaveStyle = () => {
      try {
        const styleData = {
          name: `Custom_${new Date().getTime()}`,
          template: selectedExamTemplate.value,
          styles: JSON.parse(JSON.stringify(props.examStyles)),
          created: new Date().toISOString()
        }

        localStorage.setItem('examStyles', JSON.stringify(styleData))
        showSuccess('考券樣式已儲存到本地', '儲存樣式')
      } catch (error) {
        toastError('儲存樣式失敗：' + (error.message || '未知錯誤'), '儲存樣式', error)
      }
    }

    return {
      t,
      showExamStyleEditor,
      selectedExamTemplate,
      handleSaveStyle
    }
  }
}
</script>
