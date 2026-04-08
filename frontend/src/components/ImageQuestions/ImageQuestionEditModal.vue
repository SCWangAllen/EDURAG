<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity" @click="$emit('close')">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.edit') }}</h3>
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
        <div v-if="formData" class="px-4 py-5 sm:p-6 space-y-4">
          <!-- Question Image -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.questionImage') }}</label>
            <input
              v-model="formData.question_image"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Answer Image -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.answerImage') }}</label>
            <input
              v-model="formData.answer_image"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Optional"
            />
          </div>

          <!-- Subject：下拉選單 + 新增按鈕 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.subject') }}</label>
            <div class="flex space-x-2">
              <select
                v-if="!isNewSubject"
                v-model="formData.subject"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('imageQuestions.selectSubject') || '選擇科目' }}</option>
                <option v-for="subject in subjectList" :key="subject.id" :value="subject.name">
                  {{ subject.name }}
                </option>
              </select>
              <input
                v-else
                v-model="newSubjectName"
                type="text"
                :placeholder="t('imageQuestions.newSubjectPlaceholder') || '輸入新科目名稱'"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                @click="toggleNewSubject"
                class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 whitespace-nowrap"
              >
                {{ isNewSubject ? t('imageQuestions.selectExisting') || '選擇現有' : t('imageQuestions.addNew') || '新增' }}
              </button>
            </div>
          </div>

          <!-- Grade -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.grade') }}</label>
            <input
              v-model="formData.grade"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., G4"
            />
          </div>

          <!-- Chapter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.chapter') }}</label>
            <input
              v-model="formData.chapter"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Page -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.page') }}</label>
            <input
              v-model="formData.page"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.description') }}</label>
            <textarea
              v-model="formData.question_description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
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
            @click="handleSave"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            {{ t('save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import subjectService from '@/api/subjectService.js'

export default {
  name: 'ImageQuestionEditModal',
  props: {
    visible: { type: Boolean, default: false },
    question: { type: Object, default: null },
  },
  emits: ['close', 'save', 'subject-created'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const formData = ref(null)
    const subjectList = ref([])
    const isNewSubject = ref(false)
    const newSubjectName = ref('')

    const loadSubjects = async () => {
      try {
        const response = await subjectService.getSubjects()
        subjectList.value = response.subjects || []
      } catch (error) {
        console.error('Failed to load subjects:', error)
      }
    }

    const toggleNewSubject = () => {
      isNewSubject.value = !isNewSubject.value
      if (!isNewSubject.value) {
        newSubjectName.value = ''
      }
    }

    watch(() => props.visible, (newVisible) => {
      if (newVisible) {
        loadSubjects()
        isNewSubject.value = false
        newSubjectName.value = ''
      }
    })

    watch(() => props.question, (newVal) => {
      if (newVal) {
        formData.value = {
          question_image: newVal.question_image,
          answer_image: newVal.answer_image,
          question_description: newVal.question_description,
          subject: newVal.subject,
          grade: newVal.grade,
          chapter: newVal.chapter,
          page: newVal.page,
        }
      } else {
        formData.value = null
      }
    }, { immediate: true })

    const handleSave = async () => {
      if (!formData.value) return

      let subjectToSave = formData.value.subject

      // 如果是新增科目模式，先創建科目
      if (isNewSubject.value && newSubjectName.value.trim()) {
        try {
          const existingSubject = subjectList.value.find(
            s => s.name.toLowerCase() === newSubjectName.value.trim().toLowerCase()
          )

          if (existingSubject) {
            subjectToSave = existingSubject.name
          } else {
            const response = await subjectService.createSubject({
              name: newSubjectName.value.trim(),
              description: '自動建立於圖片題目編輯',
              color: '#3B82F6'
            })
            subjectToSave = response.subject.name
            emit('subject-created', response.subject)
            await loadSubjects()
          }
        } catch (error) {
          if (error.response?.data?.detail?.includes('已存在')) {
            subjectToSave = newSubjectName.value.trim()
          } else {
            console.error('Failed to create subject:', error)
          }
        }
      }

      emit('save', { ...formData.value, subject: subjectToSave })
    }

    onMounted(() => {
      if (props.visible) {
        loadSubjects()
      }
    })

    return {
      t,
      formData,
      subjectList,
      isNewSubject,
      newSubjectName,
      toggleNewSubject,
      handleSave
    }
  },
}
</script>
