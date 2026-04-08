<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity" @click="handleClose">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.uploadExcel') }}</h3>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="px-4 py-5 sm:p-6">
          <!-- File Upload -->
          <div v-if="!preview" class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              ref="fileInput"
              accept=".xlsx,.xls"
              @change="handleFileSelect"
              class="hidden"
            />
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <button
                @click="$refs.fileInput.click()"
                class="font-medium text-blue-600 hover:text-blue-500"
              >
                {{ t('imageQuestions.uploadExcel') }}
              </button>
            </p>
            <p class="mt-1 text-xs text-gray-500">Excel (.xlsx, .xls)</p>

            <!-- Loading -->
            <div v-if="uploading" class="mt-4 flex justify-center items-center">
              <svg class="animate-spin h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="ml-2 text-gray-500">{{ t('imageQuestions.loading') }}</span>
            </div>
          </div>

          <!-- Preview -->
          <div v-else>
            <!-- Summary -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-medium text-blue-900">{{ t('imageQuestions.uploadSuccess') }}</span>
              </div>
              <div class="mt-2 grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-blue-700">{{ t('imageQuestions.fileName') }}:</span>
                  <span class="ml-1 font-medium">{{ preview.file_name }}</span>
                </div>
                <div>
                  <span class="text-blue-700">{{ t('imageQuestions.totalRows') }}:</span>
                  <span class="ml-1 font-medium">{{ preview.total_rows }}</span>
                </div>
                <div>
                  <span class="text-green-700">{{ t('imageQuestions.validRows') }}:</span>
                  <span class="ml-1 font-medium text-green-600">{{ preview.valid_rows }}</span>
                  <span v-if="preview.error_rows > 0" class="ml-2 text-red-700">
                    ({{ t('imageQuestions.errorRows') }}: <span class="font-medium text-red-600">{{ preview.error_rows }}</span>)
                  </span>
                </div>
              </div>
            </div>

            <!-- Warnings -->
            <div v-if="preview.warnings && preview.warnings.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <h4 class="text-sm font-medium text-yellow-800 mb-2">{{ t('imageQuestions.warnings') }}</h4>
              <ul class="text-sm text-yellow-700 list-disc list-inside space-y-1">
                <li v-for="(warning, idx) in preview.warnings.slice(0, 10)" :key="idx">{{ warning }}</li>
                <li v-if="preview.warnings.length > 10">... {{ preview.warnings.length - 10 }} more warnings</li>
              </ul>
            </div>

            <!-- Items Table -->
            <div class="border rounded-lg overflow-hidden">
              <div class="max-h-96 overflow-y-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50 sticky top-0">
                    <tr>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.row') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.questionImage') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.subject') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.grade') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="item in preview.items" :key="item.row_number" :class="{ 'bg-red-50': item.has_error }">
                      <td class="px-3 py-2 text-sm text-gray-500">{{ item.row_number }}</td>
                      <td class="px-3 py-2 text-sm text-gray-900 truncate max-w-[200px]">{{ item.question_image }}</td>
                      <td class="px-3 py-2 text-sm text-gray-900">{{ item.subject }}</td>
                      <td class="px-3 py-2 text-sm text-gray-500">{{ item.grade || '-' }}</td>
                      <td class="px-3 py-2">
                        <span v-if="item.has_error" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          {{ item.error_message }}
                        </span>
                        <span v-else-if="item.question_image_exists" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                          </svg>
                          OK
                        </span>
                        <span v-else class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                          </svg>
                          Image missing
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="handleClose"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ t('imageQuestions.cancel') }}
          </button>
          <button
            v-if="preview && preview.valid_rows > 0"
            @click="confirmSave"
            :disabled="saving"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ saving ? t('imageQuestions.saving') : t('imageQuestions.confirmSave') }} ({{ preview.valid_rows }})
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useToast } from '@/composables/useToast.js'
import { uploadExcel } from '@/api/imageQuestionService.js'

export default {
  name: 'ImageQuestionUploadModal',
  props: {
    visible: { type: Boolean, default: false },
  },
  emits: ['close', 'uploaded'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    const fileInput = ref(null)
    const uploading = ref(false)
    const saving = ref(false)
    const preview = ref(null)
    const selectedFile = ref(null)

    const handleFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      selectedFile.value = file
      uploading.value = true

      try {
        // Preview only first
        const response = await uploadExcel(file, true)
        preview.value = response.data
      } catch (error) {
        toastError(t('imageQuestions.uploadError') + (error.response?.data?.detail || error.message), '上傳 Excel')
      } finally {
        uploading.value = false
      }
    }

    const confirmSave = async () => {
      if (!selectedFile.value) return

      saving.value = true

      try {
        // Save with preview_only = false
        const response = await uploadExcel(selectedFile.value, false)
        const savedCount = response.data.valid_rows

        showSuccess(t('imageQuestions.saveSuccess').replace('{count}', savedCount), '儲存圖片題目')
        emit('uploaded')
        resetState()
      } catch (error) {
        toastError(t('imageQuestions.saveError') + (error.response?.data?.detail || error.message), '儲存圖片題目')
      } finally {
        saving.value = false
      }
    }

    const resetState = () => {
      preview.value = null
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const handleClose = () => {
      resetState()
      emit('close')
    }

    return {
      t,
      fileInput,
      uploading,
      saving,
      preview,
      handleFileSelect,
      confirmSave,
      handleClose,
    }
  },
}
</script>
