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
            <option v-for="qt in templateQuestionTypes" :key="qt.value" :value="qt.value">
              {{ t(qt.labelKey) }}
            </option>
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
          <div v-if="gradeOptions.length" class="flex flex-wrap gap-2">
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
          <p v-else class="text-sm text-gray-400">
            {{ t('templates.modal.selectSubjectForGrades') }}
          </p>
          <p class="text-xs text-gray-500 mt-1">
            {{ t('templates.modal.applicableGradesHint') }}
          </p>
        </div>

        <!-- Prompt 模板 -->
        <div>
          <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('templates.modal.promptTemplate') }} <span class="text-red-500">*</span>
          </label>
          <div class="mb-2 rounded-md bg-blue-50 border border-blue-100 p-3">
            <p class="text-xs text-gray-600 whitespace-pre-line leading-relaxed">
              {{ t('templates.modal.promptHint') }}
            </p>
          </div>
          <div class="flex flex-wrap gap-2 mb-2">
            <button
              type="button"
              @click="insertPlaceholder('{context}')"
              class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-primary-500"
            >
              {{ t('templates.modal.insertContext') }}
            </button>
            <button
              type="button"
              @click="insertPlaceholder('{count}')"
              class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-primary-500"
            >
              {{ t('templates.modal.insertCount') }}
            </button>
          </div>
          <textarea
            id="content"
            ref="contentTextarea"
            v-model="form.content"
            required
            rows="12"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 font-mono text-sm"
            :placeholder="t('templates.modal.promptPlaceholder')"
          ></textarea>
        </div>

        <!-- 此題型的輸出格式(唯讀):由系統依題型自動注入,老師不用寫 JSON -->
        <div v-if="currentOutputExample" class="bg-gray-50 border border-gray-200 p-3 rounded-lg">
          <p class="text-xs text-gray-600 mb-2">
            {{ t('templates.modal.outputFormatHint') }}
          </p>
          <pre class="text-xs text-gray-700 bg-white border border-gray-100 rounded p-2 overflow-x-auto font-mono">{{ currentOutputExample }}</pre>
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
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import subjectService from '../api/subjectService.js'
import templateService from '../api/templateService.js'
import { useToast } from '@/composables/useToast.js'
import { useLanguage } from '../composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { TEMPLATE_QUESTION_TYPES } from '@/constants/index.js'
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
    },
    // 由「題型範本庫」開啟建立時預選的題型(自動帶入該題型起始範本)
    presetType: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'save', 'subject-created'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目顯示名 / 年級標籤 / 動態年級來源皆來自統一的 subject 樹
    const { getDisplayName, getGradeLabel, gradesFor, ensureLoaded } = useSubjects()
    const saving = ref(false)
    const subjectOptions = ref([]) // Subject options list
    const selectedSubjectId = ref(null) // Currently selected subject ID
    const contentTextarea = ref(null) // Prompt textarea 參照，用於游標插入佔位符

    // 在游標處插入佔位符（取不到 textarea 或選取範圍時 append 到內容尾端）
    const insertPlaceholder = (placeholder) => {
      const el = contentTextarea.value
      if (el && typeof el.selectionStart === 'number') {
        const start = el.selectionStart
        const end = el.selectionEnd
        const value = form.content
        form.content = value.slice(0, start) + placeholder + value.slice(end)
        nextTick(() => {
          const pos = start + placeholder.length
          el.focus()
          el.setSelectionRange(pos, pos)
        })
      } else {
        form.content += placeholder
      }
    }

    const form = reactive({
      name: '',
      subject_id: null, // 科目ID
      content: '',
      question_type: '', // 移除預設值，讓使用者明確選擇
      grades: [], // 適用年級列表
      params: {} // LLM 參數已交後端預設，不再由老師於表單設定
    })

    // 年級選項：動態來自「所選科目」在後端 subject 樹裡實際擁有的年級，
    // union 目前已選(相容舊資料,保留可見可取消)。未選科目時為空。
    const gradeOptions = computed(() => {
      const selected = subjectOptions.value.find(s => s.id === form.subject_id)
      const subjectGrades = selected ? gradesFor(selected.name) : []
      const union = [...new Set([...subjectGrades, ...form.grades])]
      return union.map(g => ({ value: g, label: getGradeLabel(g) }))
    })

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
            description: t('ui.md_auto_created_subject_desc'),
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
      form.params = {} // LLM 參數交後端預設
    }

    const previewContent = computed(() => {
      return form.content
        .replace(/\{context\}/g, t('templates.modal.sampleContent'))
        .replace(/\{count\}/g, '5')
    })

    // 題型範本(單一真實來源,來自後端 /templates/question-types)
    const starterList = ref([])
    const starterMap = computed(() =>
      Object.fromEntries(starterList.value.map(s => [s.question_type, s]))
    )
    const currentStarter = computed(() => starterMap.value[form.question_type] || null)
    // 目前題型的輸出範例(唯讀顯示,讓老師看到目標長相)
    const currentOutputExample = computed(() =>
      currentStarter.value
        ? JSON.stringify(currentStarter.value.output_example, null, 2)
        : ''
    )
    const loadStarters = async () => {
      try {
        const data = await templateService.getQuestionTypes()
        starterList.value = data.question_types || []
      } catch (error) {
        starterList.value = []
      }
    }


    // 監聽 template prop 變化來填充表單
    watch(() => props.template, async (newTemplate) => {
      if (newTemplate) {
        // 編輯模式：載入現有模板資料
        form.name = newTemplate.name || ''
        form.content = newTemplate.content || ''
        form.question_type = newTemplate.question_type || 'single_choice'
        form.grades = [...(newTemplate.grades || [])] // 複製陣列避免引用問題
        form.params = { ...(newTemplate.params || {}) } // 保留既有值,後端會忽略/floor

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
          // 若由題型範本庫帶入預選題型 → 設定後觸發自動帶入起始範本
          if (props.presetType) {
            form.question_type = props.presetType
          }
        } else {
          // 編輯模式：由 template watcher 處理
        }
      }
    })

    // 監聽科目ID變化，同步到 form；切換科目時剔除不屬於新科目的年級
    watch(selectedSubjectId, (newSubjectId) => {
      form.subject_id = newSubjectId
      const selected = subjectOptions.value.find(s => s.id === newSubjectId)
      if (selected) {
        const allowed = gradesFor(selected.name)
        form.grades = form.grades.filter(g => allowed.includes(g))
      }
    })

    // 選題型時自動帶入該題型的起始範本(純指示語);只在內容為空、或還停留在
    // 前一題型範本時才覆寫,避免蓋掉老師已編輯的內容。
    watch(() => form.question_type, (newType, oldType) => {
      if (!newType) return
      const starter = starterMap.value[newType]?.starter_prose
      if (!starter) return
      const prevStarter = oldType ? starterMap.value[oldType]?.starter_prose : ''
      if (!form.content.trim() || form.content === prevStarter) {
        form.content = starter
      }
    })

    const handleSubmit = async () => {
      // 驗證科目是否已選擇
      if (!form.subject_id) {
        toastError(t('templates.modal.validation.selectSubject'), t('ui.md_template_creation'))
        return
      }

      // 驗證必要欄位
      if (!form.name.trim()) {
        toastError(t('templates.modal.validation.templateNameRequired'), t('ui.md_template_creation'))
        return
      }

      if (!form.content.trim()) {
        toastError(t('templates.modal.validation.templateContentRequired'), t('ui.md_template_creation'))
        return
      }

      // 驗證是否包含 {context} 佔位符（否則生成時教材不會被帶入，會靜默失敗）
      if (!form.content.includes('{context}')) {
        toastError(t('templates.modal.contextRequired'), t('ui.md_template_creation'))
        return
      }

      // 驗證題型是否已選擇
      if (!form.question_type) {
        toastError(t('templates.modal.validation.selectQuestionType'), t('ui.md_template_creation'))
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
        toastError(t('ui.md_save_template_error'), t('ui.md_template_creation'), error)
      } finally {
        saving.value = false
      }
    }

    // 載入科目清單 + subject 樹(動態年級)+ 題型範本
    onMounted(async () => {
      await Promise.all([loadSubjects(), ensureLoaded(), loadStarters()])
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
      templateQuestionTypes: TEMPLATE_QUESTION_TYPES,
      previewContent,
      currentOutputExample,
      contentTextarea,
      insertPlaceholder,
      loadSubjects,
      handleLegacySubject,
      handleSubmit
    }
  }
}
</script>
