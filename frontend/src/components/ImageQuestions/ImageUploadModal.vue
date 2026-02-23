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
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.uploadImageTitle') }}</h3>
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
        <div class="px-4 py-5 sm:p-6 space-y-4">
          <!-- Image Type Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('imageQuestions.imageTypeLabel') }}
            </label>
            <div class="flex space-x-4">
              <label class="inline-flex items-center">
                <input
                  type="radio"
                  v-model="imageType"
                  value="questions"
                  class="form-radio h-4 w-4 text-blue-600"
                />
                <span class="ml-2 text-sm text-gray-700">{{ t('imageQuestions.questionImageType') }}</span>
              </label>
              <label class="inline-flex items-center">
                <input
                  type="radio"
                  v-model="imageType"
                  value="answers"
                  class="form-radio h-4 w-4 text-blue-600"
                />
                <span class="ml-2 text-sm text-gray-700">{{ t('imageQuestions.answerImageType') }}</span>
              </label>
            </div>
          </div>

          <!-- Custom Name Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ t('imageQuestions.customImageName') }}
            </label>
            <input
              v-model="customName"
              type="text"
              :placeholder="t('imageQuestions.customNamePlaceholder')"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <p class="mt-1 text-xs text-gray-500">
              {{ t('imageQuestions.customNameHint') }}
            </p>
          </div>

          <!-- File Drop Zone -->
          <div
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
            :class="[
              isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
              selectedFile ? 'bg-green-50 border-green-300' : ''
            ]"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
          >
            <div v-if="!selectedFile">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <p class="mt-2 text-sm text-gray-600">
                {{ t('imageQuestions.dropImageHere') }}
              </p>
              <p class="mt-1 text-xs text-gray-500">
                {{ t('imageQuestions.supportedFormats') }}
              </p>
              <label class="mt-3 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
                {{ t('imageQuestions.selectFile') }}
                <input
                  type="file"
                  class="hidden"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  @change="handleFileSelect"
                />
              </label>
            </div>

            <!-- Selected File Preview -->
            <div v-else class="flex items-center justify-center space-x-4">
              <div class="flex-shrink-0 w-20 h-20 bg-gray-100 rounded overflow-hidden">
                <img
                  :src="previewUrl"
                  :alt="selectedFile.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="text-left">
                <p class="text-sm font-medium text-gray-900 truncate max-w-[200px]">
                  {{ selectedFile.name }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatFileSize(selectedFile.size) }}
                </p>
                <button
                  @click="clearFile"
                  class="mt-1 text-xs text-red-600 hover:text-red-800"
                >
                  {{ t('imageQuestions.removeFile') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Upload Progress -->
          <div v-if="uploading" class="mt-2">
            <div class="flex items-center">
              <svg class="animate-spin h-4 w-4 text-blue-500 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-sm text-gray-600">{{ t('imageQuestions.uploading') }}</span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="ml-3 text-sm text-red-700">{{ error }}</p>
            </div>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-3">
            <div class="flex">
              <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <p class="ml-3 text-sm text-green-700">{{ successMessage }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="$emit('close')"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ t('imageQuestions.close') }}
          </button>
          <button
            @click="handleUpload"
            :disabled="!selectedFile || uploading"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <svg v-if="uploading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ uploading ? t('imageQuestions.uploading') : t('imageQuestions.uploadButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { uploadImage } from '@/api/imageQuestionService.js'

export default {
  name: 'ImageUploadModal',
  props: {
    visible: { type: Boolean, default: false },
    defaultImageType: { type: String, default: 'questions' },
    defaultName: { type: String, default: '' },
  },
  emits: ['close', 'uploaded'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const imageType = ref(props.defaultImageType)
    const customName = ref(props.defaultName)
    const selectedFile = ref(null)
    const previewUrl = ref(null)
    const isDragging = ref(false)
    const uploading = ref(false)
    const error = ref('')
    const successMessage = ref('')

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    const handleFileSelect = (event) => {
      const file = event.target.files?.[0]
      if (file) {
        setFile(file)
      }
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const file = event.dataTransfer?.files?.[0]
      if (file && file.type.startsWith('image/')) {
        setFile(file)
      }
    }

    const setFile = (file) => {
      selectedFile.value = file
      error.value = ''
      successMessage.value = ''

      // Create preview URL
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
      previewUrl.value = URL.createObjectURL(file)

      // Auto-fill custom name from filename if empty
      if (!customName.value) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
        customName.value = nameWithoutExt.replace(/[^a-zA-Z0-9_\-]/g, '_')
      }
    }

    const clearFile = () => {
      selectedFile.value = null
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
        previewUrl.value = null
      }
      error.value = ''
      successMessage.value = ''
    }

    const handleUpload = async () => {
      if (!selectedFile.value) return

      try {
        uploading.value = true
        error.value = ''
        successMessage.value = ''

        const response = await uploadImage(
          imageType.value,
          selectedFile.value,
          customName.value || null
        )

        successMessage.value = response.data.message
        emit('uploaded', response.data)

        // Clear file after successful upload
        setTimeout(() => {
          clearFile()
          customName.value = ''
        }, 1500)

      } catch (err) {
        error.value = err.response?.data?.detail || err.message || t('imageQuestions.uploadError')
      } finally {
        uploading.value = false
      }
    }

    const resetForm = () => {
      clearFile()
      customName.value = props.defaultName
      imageType.value = props.defaultImageType
      error.value = ''
      successMessage.value = ''
    }

    watch(() => props.visible, (newVal) => {
      if (newVal) {
        resetForm()
      }
    })

    watch(() => props.defaultName, (newVal) => {
      customName.value = newVal
    })

    watch(() => props.defaultImageType, (newVal) => {
      imageType.value = newVal
    })

    return {
      t,
      imageType,
      customName,
      selectedFile,
      previewUrl,
      isDragging,
      uploading,
      error,
      successMessage,
      formatFileSize,
      handleFileSelect,
      handleDrop,
      clearFile,
      handleUpload,
    }
  },
}
</script>
