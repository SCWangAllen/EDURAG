<template>
  <div v-if="visible" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal 標題 -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ isEditing ? t('documents.editDocument') : t('documents.documentDetail') }}
          </h3>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- 編輯表單 -->
        <div v-if="document" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentTitle') }}</label>
              <input
                v-model="editForm.title"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentSubject') }}</label>
              <input
                v-model="editForm.subject"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.grade') }}</label>
              <select
                v-model="editForm.grade"
                :disabled="!isEditing"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
                <option value="">{{ t('documents.allGrades') }}</option>
                <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.page') }}</label>
              <input
                v-model="editForm.page_number"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                :placeholder="t('documents.pagePlaceholder') || '例如: 1, 2-3, 10'"
              >
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentChapter') }}</label>
              <input
                v-model="editForm.chapter"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.content') }}</label>
            <textarea
              v-model="editForm.content"
              :disabled="!isEditing"
              rows="15"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 font-mono text-sm"
            ></textarea>
          </div>

          <!-- 操作按鈕 -->
          <div class="flex justify-between pt-4 border-t">
            <div>
              <span class="text-sm text-gray-500">
                {{ t('documents.contentLen') }}: {{ editForm.content.length }} {{ t('documents.characters') }} |
                {{ t('documents.createdAt') }}: {{ formatDate(document.created_at) }}
              </span>
            </div>

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
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm"
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import { formatDate } from '@/utils/formatters.js'

export default {
  name: 'DocumentDetailModal',
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
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const isEditing = ref(false)
    const saving = ref(false)
    const editForm = reactive({
      title: '',
      content: '',
      subject: '',
      grade: '',
      chapter: '',
      page_number: ''
    })

    const populateForm = (doc) => {
      editForm.title = doc.title
      editForm.content = doc.content
      editForm.subject = doc.subject
      editForm.grade = doc.grade || ''
      editForm.chapter = doc.chapter || ''
      editForm.page_number = doc.page_number || ''
    }

    watch(() => props.document, (newDoc) => {
      if (newDoc) {
        populateForm(newDoc)
        isEditing.value = false
      }
    })

    const startEdit = () => {
      isEditing.value = true
    }

    const saveEdit = () => {
      saving.value = true
      emit('saved', {
        title: editForm.title,
        content: editForm.content,
        subject: editForm.subject,
        grade: editForm.grade,
        chapter: editForm.chapter,
        page_number: editForm.page_number
      })
    }

    const handleClose = () => {
      isEditing.value = false
      emit('close')
    }

    const resetSaving = () => {
      saving.value = false
    }

    return {
      t,
      formatDate,
      isEditing,
      saving,
      editForm,
      startEdit,
      saveEdit,
      handleClose,
      resetSaving
    }
  }
}
</script>
