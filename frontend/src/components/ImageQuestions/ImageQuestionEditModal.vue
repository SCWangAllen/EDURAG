<template>
  <BaseModal
    :model-value="visible"
    size="md"
    :title="t('imageQuestions.edit')"
    @update:model-value="$emit('close')"
  >
    <div v-if="formData" class="space-y-4">
      <!-- Question Image -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.questionImage') }}</label>
        <input
          v-model="formData.question_image"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      <!-- Answer Image -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.answerImage') }}</label>
        <input
          v-model="formData.answer_image"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
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
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">{{ t('imageQuestions.selectSubject') }}</option>
            <option v-for="subject in subjectList" :key="subject.id" :value="subject.name">
              {{ subject.name }}
            </option>
          </select>
          <input
            v-else
            v-model="newSubjectName"
            type="text"
            :placeholder="t('imageQuestions.newSubjectPlaceholder')"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
          <button
            type="button"
            @click="toggleNewSubject"
            class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 whitespace-nowrap"
          >
            {{ isNewSubject ? t('imageQuestions.selectExisting') : t('imageQuestions.addNew') }}
          </button>
        </div>
      </div>

      <!-- Grade：下拉選單（G1–G6 / ALL，ALL=全年級通用） -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.grade') }}</label>
        <select
          v-model="formData.grade"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">—</option>
          <option v-for="opt in gradeOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <!-- Chapter -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.chapter') }}</label>
        <input
          v-model="formData.chapter"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      <!-- Page -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.page') }}</label>
        <input
          v-model="formData.page"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      <!-- Blank Count -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.blankCount') }}</label>
        <input
          v-model.number="formData.blank_count"
          type="number"
          min="1"
          max="50"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
        <p class="mt-1 text-xs text-gray-500">{{ t('imageQuestions.blankCountHint') }}</p>
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.description') }}</label>
        <textarea
          v-model="formData.question_description"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        ></textarea>
      </div>
    </div>

    <template #footer>
      <button
        @click="$emit('close')"
        class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
      >
        {{ t('imageQuestions.cancel') }}
      </button>
      <button
        @click="handleSave"
        class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
      >
        {{ t('save') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import subjectService from '@/api/subjectService.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'ImageQuestionEditModal',
  components: {
    BaseModal
  },
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
          blank_count: newVal.blank_count || 1,
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
              description: t('ui.md_auto_created_image_question_edit_desc'),
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
      gradeOptions: GRADE_OPTIONS,
      toggleNewSubject,
      handleSave
    }
  },
}
</script>
