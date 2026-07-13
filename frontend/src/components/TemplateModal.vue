<template>
  <BaseModal
    :model-value="show"
    size="xl"
    :title="template ? t('templates.modal.editTitle') : t('templates.modal.createTitle')"
    @update:model-value="$emit('close')"
  >
    <form id="templateModalForm" @submit.prevent="handleSubmit">
      <div class="space-y-6">
        <!-- 基本資訊 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('templates.modal.templateName') }} <span class="text-red-500">*</span>
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              maxlength="100"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              :placeholder="t('templates.modal.templateNamePlaceholder')"
            />
          </div>

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('templates.modal.subject') }} <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <select
                id="subject"
                v-model="selectedSubjectId"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">{{ t('templates.modal.selectSubject') }}</option>
                <option v-for="subject in subjectOptions" :key="subject.id" :value="subject.id">
                  ● {{ getDisplayName(subject.name) }}{{ subject.grade ? ` (${getGradeLabel(subject.grade)})` : '' }}
                </option>
              </select>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              {{ t('templates.modal.subjectManageHint') }}
            </p>
          </div>
        </div>

        <!-- 題型選擇 -->
        <div>
          <label for="question_type" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('templates.modal.questionType') }} <span class="text-red-500">*</span>
          </label>
          <select
            id="question_type"
            v-model="form.question_type"
            required
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="" disabled>{{ t('templates.modal.selectQuestionType') }}</option>
            <option value="single_choice">{{ t('questions.single_choice') }}</option>
            <option value="cloze">{{ t('questions.cloze') }}</option>
            <option value="short_answer">{{ t('questions.short_answer') }}</option>
            <option value="true_false">{{ t('questions.true_false') }}</option>
            <option value="matching">{{ t('questions.matching') }}</option>
            <option value="sequence">{{ t('questions.sequence') }}</option>
            <option value="enumeration">{{ t('questions.enumeration') }}</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            {{ t('templates.modal.questionTypeHint') }}
          </p>
        </div>

        <!-- 適用年級（多選） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('templates.modal.applicableGrades') }}
          </label>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="grade in gradeOptions"
              :key="grade.value"
              class="inline-flex items-center px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors"
              :class="form.grades.includes(grade.value)
                ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
                : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'"
            >
              <input
                type="checkbox"
                :value="grade.value"
                v-model="form.grades"
                class="sr-only"
              />
              {{ grade.label }}
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-1">
            {{ t('templates.modal.applicableGradesHint') }}
          </p>
        </div>

        <!-- Prompt 模板 -->
        <div>
          <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('templates.modal.promptTemplate') }} <span class="text-red-500">*</span>
          </label>
          <div class="mb-2">
            <p class="text-xs text-gray-500">
              {{ t('templates.modal.promptHint') }}
            </p>
          </div>
          <textarea
            id="content"
            v-model="form.content"
            required
            rows="12"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 font-mono text-sm"
            :placeholder="t('templates.modal.promptPlaceholder')"
          ></textarea>
        </div>

        <!-- 參數設定 -->
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 mb-4">{{ t('templates.modal.llmParams') }}</h4>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="temperature" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('templates.modal.temperature') }}
              </label>
              <div class="flex items-center space-x-2">
                <input
                  id="temperature"
                  v-model.number="form.params.temperature"
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  class="flex-1"
                />
                <span class="text-sm text-gray-600 min-w-[3rem]">
                  {{ form.params.temperature }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ t('templates.modal.temperatureHint') }}</p>
            </div>

            <div>
              <label for="maxTokens" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('templates.modal.maxTokens') }}
              </label>
              <input
                id="maxTokens"
                v-model.number="form.params.max_tokens"
                type="number"
                min="100"
                max="8192"
                step="100"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
              <p class="text-xs text-gray-500 mt-1">{{ t('templates.modal.maxTokensHint') }}</p>
            </div>

            <div>
              <label for="topP" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('templates.modal.topP') }}
              </label>
              <div class="flex items-center space-x-2">
                <input
                  id="topP"
                  v-model.number="form.params.top_p"
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  class="flex-1"
                />
                <span class="text-sm text-gray-600 min-w-[3rem]">
                  {{ form.params.top_p }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ t('templates.modal.topPHint') }}</p>
            </div>

            <div>
              <label for="frequencyPenalty" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('templates.modal.frequencyPenalty') }}
              </label>
              <div class="flex items-center space-x-2">
                <input
                  id="frequencyPenalty"
                  v-model.number="form.params.frequency_penalty"
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  class="flex-1"
                />
                <span class="text-sm text-gray-600 min-w-[3rem]">
                  {{ form.params.frequency_penalty }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ t('templates.modal.frequencyPenaltyHint') }}</p>
            </div>
          </div>
        </div>

        <!-- 預覽區域 -->
        <div v-if="form.content" class="bg-blue-50 p-4 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 mb-2">{{ t('templates.modal.preview') }}</h4>
          <div class="text-sm text-gray-700 whitespace-pre-wrap">
            {{ previewContent }}
          </div>
        </div>
      </div>
    </form>

    <template #footer>
      <button
        type="button"
        @click="$emit('close')"
        class="px-4 py-2 rounded-md border border-gray-300 shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ t('cancel') }}
      </button>
      <button
        type="submit"
        form="templateModalForm"
        :disabled="saving"
        class="px-4 py-2 rounded-md border border-transparent shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
      >
        {{ saving ? t('templates.modal.saving') : t('templates.modal.save') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import subjectService from '../api/subjectService.js'
import { useToast } from '@/composables/useToast.js'
import { useLanguage } from '../composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'TemplateModal',
  components: {
    BaseModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    template: {
      type: Object,
      default: null
    },
    subjects: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'save', 'subject-created'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目顯示名 / 年級標籤來自統一來源
    const { getDisplayName, getGradeLabel } = useSubjects()
    const saving = ref(false)
    const subjectOptions = ref([]) // Subject options list
    const selectedSubjectId = ref(null) // Currently selected subject ID

    const form = reactive({
      name: '',
      subject_id: null, // 科目ID
      content: '',
      question_type: '', // 移除預設值，讓使用者明確選擇
      grades: [], // 適用年級列表
      params: {
        temperature: 0.7,
        max_tokens: 8100,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
    })

    // 年級選項（統一來源）
    const gradeOptions = GRADE_OPTIONS

    // 載入科目清單
    const loadSubjects = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectOptions.value = data.subjects || []
      } catch (error) {
        subjectOptions.value = []
      }
    }

    // 監聽 subjects prop 變化
    watch(() => props.subjects, (newSubjects) => {
      if (newSubjects && newSubjects.length > 0) {
        subjectOptions.value = newSubjects
      }
    }, { immediate: true, deep: true })

    const handleLegacySubject = async (subjectName) => {
      try {
        // 優先使用 props 中的科目清單，如果沒有才重新載入
        if (subjectOptions.value.length === 0) {
          if (props.subjects && props.subjects.length > 0) {
            subjectOptions.value = props.subjects
          } else {
            await loadSubjects()
          }
        }

        // 查找是否已有對應的科目
        const existingSubject = subjectOptions.value.find(s => s.name === subjectName)

        if (existingSubject) {
          // 科目已存在，直接使用其ID
          form.subject_id = existingSubject.id
          selectedSubjectId.value = existingSubject.id
        } else {
          // 科目不存在，自動建立
          const newSubject = await subjectService.createSubject({
            name: subjectName,
            description: `自動從模板建立的科目`,
            color: '#3B82F6'  // 使用預設藍色
          })

          // 發出事件通知父組件重新載入科目
          emit('subject-created', newSubject.subject)

          // 設定為新建立的科目
          form.subject_id = newSubject.subject.id
          selectedSubjectId.value = newSubject.subject.id
        }
      } catch (error) {
        // 失敗時設為空，讓使用者手動選擇
        form.subject_id = null
        selectedSubjectId.value = null
      }
    }

    const resetForm = () => {
      form.name = ''
      form.subject_id = null
      form.content = ''
      form.question_type = '' // 清空題型，讓使用者重新選擇
      form.grades = [] // 清空年級選擇
      selectedSubjectId.value = null
      form.params = {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
    }

    const previewContent = computed(() => {
      return form.content.replace('{context}', t('templates.modal.sampleContent'))
    })


    // 監聽 template prop 變化來填充表單
    watch(() => props.template, async (newTemplate) => {
      if (newTemplate) {
        // 編輯模式：載入現有模板資料
        form.name = newTemplate.name || ''
        form.content = newTemplate.content || ''
        form.question_type = newTemplate.question_type || 'single_choice'
        form.grades = [...(newTemplate.grades || [])] // 複製陣列避免引用問題
        form.params = {
          temperature: 0.7,
          max_tokens: 1000,
          top_p: 1.0,
          frequency_penalty: 0.0,
          ...newTemplate.params
        }

        // 處理科目ID設定
        if (newTemplate.subject_id) {
          // 如果已有 subject_id，直接使用
          form.subject_id = newTemplate.subject_id
          selectedSubjectId.value = newTemplate.subject_id
        } else if (newTemplate.subject) {
          // 如果沒有 subject_id 但有 subject 名稱，需要查找或建立對應的科目
          await handleLegacySubject(newTemplate.subject)
        } else {
          // 都沒有的話設為空
          form.subject_id = null
          selectedSubjectId.value = null
        }
      }
      // 移除 resetForm() - 新增模式下不要重置，因為會清除使用者選擇的題型
    }, { immediate: true })

    // 監聽 show prop 變化
    watch(() => props.show, (newShow, oldShow) => {
      if (newShow && !oldShow) {
        // Modal 開啟時
        if (!props.template) {
          // 新增模式：總是重置表單為空白狀態
          resetForm()
        } else {
          // 編輯模式：由 template watcher 處理
        }
      }
    })

    // 監聽科目ID變化，同步到 form
    watch(selectedSubjectId, (newSubjectId) => {
      form.subject_id = newSubjectId
    })

    // Debug: 監聽 question_type 變化
    watch(() => form.question_type, (newType, oldType) => {
    })

    const handleSubmit = async () => {
      // 驗證科目是否已選擇
      if (!form.subject_id) {
        toastError(t('templates.modal.validation.selectSubject'), '模板創建')
        return
      }

      // 驗證必要欄位
      if (!form.name.trim()) {
        toastError(t('templates.modal.validation.templateNameRequired'), '模板創建')
        return
      }

      if (!form.content.trim()) {
        toastError(t('templates.modal.validation.templateContentRequired'), '模板創建')
        return
      }

      // 驗證題型是否已選擇
      if (!form.question_type) {
        toastError(t('templates.modal.validation.selectQuestionType'), '模板創建')
        return
      }

      saving.value = true

      try {
        // 找到選中科目的名稱
        const selectedSubject = subjectOptions.value.find(s => s.id === form.subject_id)
        const subjectName = selectedSubject ? selectedSubject.name : null

        const templateData = {
          name: form.name.trim(),
          subject_id: form.subject_id,
          subject: subjectName, // 添加科目名稱
          content: form.content.trim(),
          question_type: form.question_type, // 修復：新增 question_type 欄位
          grades: form.grades, // 新增：適用年級列表
          params: form.params
        }

        emit('save', templateData)
      } catch (error) {
        toastError('儲存模板時發生錯誤', '模板創建', error)
      } finally {
        saving.value = false
      }
    }

    // 載入科目清單
    onMounted(async () => {
      await loadSubjects()
    })

    return {
      t,
      getDisplayName,
      getGradeLabel,
      saving,
      form,
      subjectOptions,
      selectedSubjectId,
      gradeOptions,
      previewContent,
      loadSubjects,
      handleLegacySubject,
      handleSubmit
    }
  }
}
</script>
