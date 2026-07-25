<template>
  <BaseModal
    :model-value="visible"
    size="xl"
    :title="isEditing ? t('documents.editDocument') : t('documents.documentDetail')"
    @update:model-value="handleClose"
  >
    <!-- 編輯表單 -->
    <div v-if="document" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentTitle') }}</label>
              <input
                v-model="editForm.title"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50"
              >
            </div>

            <!-- 科目：下拉選單 + 新增按鈕 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentSubject') }}</label>
              <div v-if="isEditing" class="flex space-x-2">
                <select
                  v-if="!isNewSubject"
                  v-model="editForm.subject"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">{{ t('documents.selectSubject') }}</option>
                  <option v-for="name in subjectNames" :key="name" :value="name">
                    {{ getDisplayName(name) }}
                  </option>
                </select>
                <input
                  v-else
                  v-model="newSubjectName"
                  type="text"
                  :placeholder="t('documents.newSubjectPlaceholder')"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
                <button
                  type="button"
                  @click="toggleNewSubject"
                  class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 whitespace-nowrap"
                >
                  {{ isNewSubject ? t('documents.selectExisting') : t('documents.addNew') }}
                </button>
              </div>
              <input
                v-else
                :value="editForm.subject"
                disabled
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm disabled:bg-gray-50"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.grade') }}</label>
              <select
                v-model="editForm.grade"
                :disabled="!isEditing"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50"
              >
                <option value="">{{ getGradeLabel('') }}</option>
                <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ getGradeLabel(g.value) }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.page') }}</label>
              <input
                v-model="editForm.page_number"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50"
                :placeholder="t('documents.pagePlaceholder')"
              >
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentChapter') }}</label>
              <input
                v-model="editForm.chapter"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.content') }}</label>
            <textarea
              v-model="editForm.content"
              :disabled="!isEditing"
              rows="15"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 font-mono text-sm"
            ></textarea>
          </div>

    </div>

    <template v-if="document" #footer>
      <div class="flex justify-between items-center w-full">
        <span class="text-sm text-gray-500">
          {{ t('documents.contentLen') }}: {{ editForm.content.length }} {{ t('documents.characters') }} |
          {{ t('documents.createdAt') }}: {{ formatDate(document.created_at) }}
        </span>

        <div class="flex space-x-3">
          <button
            @click="handleClose"
            class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ isEditing ? t('documents.cancel') : t('documents.close') }}
          </button>

          <button
            v-if="!isEditing"
            @click="startEdit"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-md shadow-sm"
          >
            {{ t('documents.startEdit') }}
          </button>

          <button
            v-if="isEditing"
            @click="saveEdit"
            :disabled="saving"
            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
          >
            <span v-if="saving" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ t('documents.saving') }}
            </span>
            <span v-else>{{ t('documents.saveChanges') }}</span>
          </button>
        </div>
      </div>
    </template>
  </BaseModal>
</template>

<script>
import { ref, reactive, watch, onMounted } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { formatDate } from '@/utils/formatters.js'
import subjectService from '@/api/subjectService.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'DocumentDetailModal',
  components: {
    BaseModal
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    document: {
      type: Object,
      default: null
    },
    gradeOptions: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'saved', 'subject-created'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    // 科目唯一來源
    const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded, refresh } = useSubjects()

    const isEditing = ref(false)
    const saving = ref(false)
    const isNewSubject = ref(false)
    const newSubjectName = ref('')

    const editForm = reactive({
      title: '',
      content: '',
      subject: '',
      grade: '',
      chapter: '',
      page_number: ''
    })

    const toggleNewSubject = () => {
      isNewSubject.value = !isNewSubject.value
      if (!isNewSubject.value) {
        newSubjectName.value = ''
      }
    }

    const populateForm = (doc) => {
      editForm.title = doc.title
      editForm.content = doc.content
      editForm.subject = doc.subject
      editForm.grade = doc.grade || ''
      editForm.chapter = doc.chapter || ''
      editForm.page_number = doc.page_number || ''
    }

    watch(() => props.visible, (newVisible) => {
      if (newVisible) {
        ensureLoaded()
        isNewSubject.value = false
        newSubjectName.value = ''
      }
    })

    watch(() => props.document, (newDoc) => {
      if (newDoc) {
        populateForm(newDoc)
        isEditing.value = false
      }
    })

    const startEdit = () => {
      isEditing.value = true
      ensureLoaded()
    }

    const saveEdit = async () => {
      saving.value = true

      let subjectToSave = editForm.subject

      // 如果是新增科目模式，先創建科目
      if (isNewSubject.value && newSubjectName.value.trim()) {
        try {
          const typed = newSubjectName.value.trim()
          const existingName = subjectNames.value.find(
            name => name.toLowerCase() === typed.toLowerCase()
          )

          if (existingName) {
            subjectToSave = existingName
          } else {
            const response = await subjectService.createSubject({
              name: typed,
              description: t('ui.md_auto_created_document_edit_desc'),
              color: '#3B82F6'
            })
            subjectToSave = response.subject.name
            emit('subject-created', response.subject)
            await refresh()
          }
        } catch (error) {
          if (error.response?.data?.detail?.includes('已存在')) {
            subjectToSave = newSubjectName.value.trim()
          } else {
            console.error('Failed to create subject:', error)
          }
        }
      }

      emit('saved', {
        title: editForm.title,
        content: editForm.content,
        subject: subjectToSave,
        grade: editForm.grade,
        chapter: editForm.chapter,
        page_number: editForm.page_number
      })
    }

    const handleClose = () => {
      isEditing.value = false
      isNewSubject.value = false
      newSubjectName.value = ''
      emit('close')
    }

    const resetSaving = () => {
      saving.value = false
    }

    onMounted(() => {
      if (props.visible) {
        ensureLoaded()
      }
    })

    return {
      t,
      formatDate,
      subjectNames,
      getDisplayName,
      getGradeLabel,
      isEditing,
      saving,
      editForm,
      isNewSubject,
      newSubjectName,
      toggleNewSubject,
      startEdit,
      saveEdit,
      handleClose,
      resetSaving
    }
  }
}
</script>
