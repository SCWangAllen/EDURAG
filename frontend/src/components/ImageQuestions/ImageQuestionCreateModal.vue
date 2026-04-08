<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity" @click="$emit('close')">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.createTitle') }}</h3>
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
        <div class="px-4 py-5 sm:p-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <!-- Question Image Input with Suggestions -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ t('imageQuestions.questionImage') }}
              <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model="formData.question_image"
                type="text"
                :placeholder="t('imageQuestions.enterImageName')"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                @focus="showQuestionSuggestions = true"
                @input="handleQuestionImageSearch"
              />
              <!-- Suggestions dropdown -->
              <div
                v-if="showQuestionSuggestions && filteredQuestionImages.length > 0"
                class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-auto"
              >
                <div
                  v-for="img in filteredQuestionImages"
                  :key="img.name"
                  class="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center space-x-2"
                  @click="selectQuestionImage(img)"
                >
                  <div class="flex-shrink-0 w-8 h-8 bg-gray-100 rounded overflow-hidden">
                    <img
                      :src="getQuestionImageUrl(img.filename)"
                      :alt="img.name"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                  </div>
                  <span class="text-sm text-gray-900 truncate">{{ img.name }}</span>
                </div>
              </div>
              <!-- Click outside handler -->
              <div
                v-if="showQuestionSuggestions"
                class="fixed inset-0 z-0"
                @click="showQuestionSuggestions = false"
              ></div>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              {{ t('imageQuestions.imageNameHint') }}
            </p>
          </div>

          <!-- Answer Image Input with Suggestions -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ t('imageQuestions.answerImage') }}
            </label>
            <div class="relative">
              <input
                v-model="formData.answer_image"
                type="text"
                :placeholder="t('imageQuestions.enterImageName')"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                @focus="showAnswerSuggestions = true"
                @input="handleAnswerImageSearch"
              />
              <!-- Suggestions dropdown -->
              <div
                v-if="showAnswerSuggestions && filteredAnswerImages.length > 0"
                class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-auto"
              >
                <div
                  v-for="img in filteredAnswerImages"
                  :key="img.name"
                  class="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center space-x-2"
                  @click="selectAnswerImage(img)"
                >
                  <div class="flex-shrink-0 w-8 h-8 bg-gray-100 rounded overflow-hidden">
                    <img
                      :src="getAnswerImageUrl(img.filename)"
                      :alt="img.name"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                  </div>
                  <span class="text-sm text-gray-900 truncate">{{ img.name }}</span>
                </div>
              </div>
              <!-- Click outside handler -->
              <div
                v-if="showAnswerSuggestions"
                class="fixed inset-0 z-0"
                @click="showAnswerSuggestions = false"
              ></div>
            </div>
          </div>

          <!-- Subject -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ t('imageQuestions.subject') }}
              <span class="text-red-500">*</span>
            </label>
            <div class="flex space-x-2">
              <select
                v-if="!isNewSubject"
                v-model="formData.subject"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('imageQuestions.selectSubject') }}</option>
                <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
                  {{ subject.name }}
                </option>
              </select>
              <input
                v-else
                v-model="formData.subject"
                type="text"
                :placeholder="t('imageQuestions.newSubjectPlaceholder')"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                @click="toggleNewSubject"
                class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                {{ isNewSubject ? t('imageQuestions.selectExisting') : t('imageQuestions.addNew') }}
              </button>
            </div>
            <p v-if="isNewSubject" class="mt-1 text-xs text-gray-500">
              {{ t('imageQuestions.newSubjectHint') }}
            </p>
          </div>

          <!-- Grade：文字輸入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.grade') }}</label>
            <input
              v-model="formData.grade"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :placeholder="t('imageQuestions.gradePlaceholder') || '例如: G4'"
            />
          </div>

          <!-- Chapter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.chapter') }}</label>
            <input
              v-model="formData.chapter"
              type="text"
              :placeholder="t('imageQuestions.chapterPlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Page -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.page') }}</label>
            <input
              v-model="formData.page"
              type="text"
              :placeholder="t('imageQuestions.pagePlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.description') }}</label>
            <textarea
              v-model="formData.question_description"
              rows="3"
              :placeholder="t('imageQuestions.descriptionPlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <!-- Validation Errors -->
          <div v-if="errors.length > 0" class="bg-red-50 border border-red-200 rounded-md p-3">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div class="ml-3">
                <ul class="text-sm text-red-700 list-disc list-inside">
                  <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="$emit('close')"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ t('imageQuestions.cancel') }}
          </button>
          <button
            @click="handleCreate"
            :disabled="saving"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ saving ? t('imageQuestions.saving') : t('imageQuestions.create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { createImageQuestion, listImages, getQuestionImageUrl, getAnswerImageUrl } from '@/api/imageQuestionService.js'
import { subjectService } from '@/api/subjectService.js'

export default {
  name: 'ImageQuestionCreateModal',
  props: {
    visible: { type: Boolean, default: false },
  },
  emits: ['close', 'created'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const formData = reactive({
      question_image: '',
      answer_image: '',
      question_description: '',
      subject: '',
      chapter: '',
      grade: '',
      page: '',
    })

    const subjects = ref([])
    const isNewSubject = ref(false)
    const saving = ref(false)
    const errors = ref([])

    // Image suggestions state
    const allQuestionImages = ref([])
    const allAnswerImages = ref([])
    const filteredQuestionImages = ref([])
    const filteredAnswerImages = ref([])
    const showQuestionSuggestions = ref(false)
    const showAnswerSuggestions = ref(false)
    let questionSearchTimeout = null
    let answerSearchTimeout = null

    const gradeOptions = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']

    const loadSubjects = async () => {
      try {
        const response = await subjectService.getSubjects()
        subjects.value = response.subjects || []
      } catch {
        subjects.value = []
      }
    }

    const loadImages = async () => {
      try {
        const [questionRes, answerRes] = await Promise.all([
          listImages('questions', { limit: 100 }),
          listImages('answers', { limit: 100 }),
        ])
        allQuestionImages.value = questionRes.data.images || []
        allAnswerImages.value = answerRes.data.images || []
      } catch {
        allQuestionImages.value = []
        allAnswerImages.value = []
      }
    }

    const handleQuestionImageSearch = () => {
      if (questionSearchTimeout) clearTimeout(questionSearchTimeout)
      questionSearchTimeout = setTimeout(() => {
        const query = formData.question_image.toLowerCase().trim()
        if (query) {
          filteredQuestionImages.value = allQuestionImages.value.filter(
            img => img.name.toLowerCase().includes(query)
          ).slice(0, 10)
        } else {
          filteredQuestionImages.value = allQuestionImages.value.slice(0, 10)
        }
      }, 150)
    }

    const handleAnswerImageSearch = () => {
      if (answerSearchTimeout) clearTimeout(answerSearchTimeout)
      answerSearchTimeout = setTimeout(() => {
        const query = formData.answer_image.toLowerCase().trim()
        if (query) {
          filteredAnswerImages.value = allAnswerImages.value.filter(
            img => img.name.toLowerCase().includes(query)
          ).slice(0, 10)
        } else {
          filteredAnswerImages.value = allAnswerImages.value.slice(0, 10)
        }
      }, 150)
    }

    const selectQuestionImage = (img) => {
      formData.question_image = img.name
      showQuestionSuggestions.value = false
    }

    const selectAnswerImage = (img) => {
      formData.answer_image = img.name
      showAnswerSuggestions.value = false
    }

    const handleImageError = (event) => {
      event.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23e5e7eb" width="100" height="100"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-size="12">No Image</text></svg>'
    }

    const toggleNewSubject = () => {
      isNewSubject.value = !isNewSubject.value
      if (!isNewSubject.value) {
        formData.subject = ''
      }
    }

    const validate = () => {
      const errs = []

      if (!formData.question_image || !formData.question_image.trim()) {
        errs.push(t('imageQuestions.questionImageRequired'))
      }

      if (!formData.subject || !formData.subject.trim()) {
        errs.push(t('imageQuestions.subjectRequired'))
      }

      errors.value = errs
      return errs.length === 0
    }

    const resetForm = () => {
      formData.question_image = ''
      formData.answer_image = ''
      formData.question_description = ''
      formData.subject = ''
      formData.chapter = ''
      formData.grade = ''
      formData.page = ''
      errors.value = []
      isNewSubject.value = false
      showQuestionSuggestions.value = false
      showAnswerSuggestions.value = false
    }

    const handleCreate = async () => {
      if (!validate()) return

      try {
        saving.value = true

        const data = {
          question_image: formData.question_image.trim(),
          subject: formData.subject.trim(),
          question_image_ext: 'jpg',
          answer_image_ext: 'jpg',
        }

        if (formData.answer_image && formData.answer_image.trim()) {
          data.answer_image = formData.answer_image.trim()
        }
        if (formData.question_description && formData.question_description.trim()) {
          data.question_description = formData.question_description.trim()
        }
        if (formData.grade) {
          data.grade = formData.grade
        }
        if (formData.chapter && formData.chapter.trim()) {
          data.chapter = formData.chapter.trim()
        }
        if (formData.page && formData.page.trim()) {
          data.page = formData.page.trim()
        }

        await createImageQuestion(data)
        resetForm()
        emit('created')
        emit('close')
      } catch (error) {
        errors.value = [error.response?.data?.detail || error.message || t('imageQuestions.createError')]
      } finally {
        saving.value = false
      }
    }

    watch(() => props.visible, (newVal) => {
      if (newVal) {
        loadSubjects()
        loadImages()
        resetForm()
      }
    })

    onMounted(() => {
      if (props.visible) {
        loadSubjects()
        loadImages()
      }
    })

    onUnmounted(() => {
      if (questionSearchTimeout) clearTimeout(questionSearchTimeout)
      if (answerSearchTimeout) clearTimeout(answerSearchTimeout)
    })

    return {
      t,
      formData,
      subjects,
      isNewSubject,
      saving,
      errors,
      gradeOptions,
      filteredQuestionImages,
      filteredAnswerImages,
      showQuestionSuggestions,
      showAnswerSuggestions,
      toggleNewSubject,
      handleCreate,
      handleQuestionImageSearch,
      handleAnswerImageSearch,
      selectQuestionImage,
      selectAnswerImage,
      handleImageError,
      getQuestionImageUrl,
      getAnswerImageUrl,
    }
  },
}
</script>
