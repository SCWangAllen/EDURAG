<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 transition-opacity" @click="$emit('close')">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.imageLibrary') }}</h3>
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
        <div class="px-4 py-5 sm:p-6">
          <!-- Tabs -->
          <div class="flex border-b border-gray-200 mb-4">
            <button
              @click="activeTab = 'questions'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                activeTab === 'questions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ t('imageQuestions.questionImages') }}
              <span class="ml-1 text-xs text-gray-400">({{ questionImages.length }})</span>
            </button>
            <button
              @click="activeTab = 'answers'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                activeTab === 'answers'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ t('imageQuestions.answerImages') }}
              <span class="ml-1 text-xs text-gray-400">({{ answerImages.length }})</span>
            </button>

            <!-- Search -->
            <div class="ml-auto flex items-center">
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="t('imageQuestions.searchImages')"
                class="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div class="flex gap-4">
            <!-- Image Grid -->
            <div class="flex-1 overflow-auto max-h-[400px]">
              <div v-if="loading" class="flex items-center justify-center py-12">
                <svg class="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>

              <div v-else-if="filteredImages.length === 0" class="text-center py-12 text-gray-500">
                {{ t('imageQuestions.noImagesInLibrary') }}
              </div>

              <div v-else class="grid grid-cols-4 gap-3">
                <div
                  v-for="image in filteredImages"
                  :key="image.name"
                  @click="selectImage(image)"
                  :class="[
                    'relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all group',
                    selectedImage?.name === image.name
                      ? 'border-blue-500 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <div class="aspect-square bg-gray-100">
                    <img
                      :src="getImageSrc(image)"
                      :alt="image.name"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                    <p class="text-xs text-white truncate font-medium">{{ image.name }}</p>
                    <p class="text-xs text-gray-300">
                      {{ t('imageQuestions.referenceCount').replace('{count}', image.referenceCount || 0) }}
                    </p>
                  </div>
                  <!-- Edit icon overlay -->
                  <div class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span class="inline-flex items-center justify-center w-6 h-6 bg-white rounded-full shadow">
                      <svg class="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                      </svg>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Details Panel -->
            <div class="w-72 border-l border-gray-200 pl-4">
              <template v-if="selectedImage">
                <h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('imageQuestions.selectedImage') }}</h4>

                <!-- Preview -->
                <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-3">
                  <img
                    :src="getImageSrc(selectedImage)"
                    :alt="selectedImage.name"
                    class="w-full h-full object-contain"
                  />
                </div>

                <p class="text-sm font-medium text-gray-900 mb-1">{{ selectedImage.filename }}</p>

                <!-- References -->
                <div class="mb-4">
                  <h5 class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    {{ t('imageQuestions.imageReferences') }}
                  </h5>

                  <div v-if="loadingReferences" class="flex items-center text-sm text-gray-500">
                    <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    {{ t('imageQuestions.loadingReferences') }}
                  </div>

                  <div v-else-if="references.length === 0" class="text-sm text-gray-500 italic">
                    {{ t('imageQuestions.noReferences') }}
                  </div>

                  <ul v-else class="space-y-1 max-h-24 overflow-y-auto">
                    <li
                      v-for="ref in references"
                      :key="ref.id"
                      class="text-xs text-gray-600 py-1 px-2 bg-gray-50 rounded"
                    >
                      {{ ref.subject }}{{ ref.grade ? ` / ${ref.grade}` : '' }}{{ ref.chapter ? ` / ${ref.chapter}` : '' }}
                    </li>
                  </ul>
                </div>

                <!-- Rename Form -->
                <div class="border-t border-gray-200 pt-3">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    {{ t('imageQuestions.newImageName') }}
                  </label>
                  <input
                    v-model="newName"
                    type="text"
                    :placeholder="selectedImage.name"
                    class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />

                  <label class="flex items-center mt-2 text-sm text-gray-600">
                    <input
                      v-model="updateQuestions"
                      type="checkbox"
                      class="form-checkbox h-4 w-4 text-blue-600 rounded"
                    />
                    <span class="ml-2">{{ t('imageQuestions.updateRelatedQuestions') }}</span>
                  </label>

                  <!-- Error Message -->
                  <div v-if="error" class="mt-2 text-sm text-red-600">
                    {{ error }}
                  </div>

                  <!-- Success Message -->
                  <div v-if="successMessage" class="mt-2 text-sm text-green-600">
                    {{ successMessage }}
                  </div>

                  <button
                    @click="handleRename"
                    :disabled="!newName || newName === selectedImage.name || renaming"
                    class="mt-3 w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg v-if="renaming" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    {{ renaming ? t('imageQuestions.renaming') : t('imageQuestions.renameImage') }}
                  </button>
                </div>
              </template>

              <template v-else>
                <div class="flex items-center justify-center h-full text-sm text-gray-400">
                  {{ t('imageQuestions.searchImages') }}
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end">
          <button
            @click="$emit('close')"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ t('imageQuestions.close') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import {
  listImages,
  getImageReferences,
  renameImage,
  getImageUrl,
} from '@/api/imageQuestionService.js'

export default {
  name: 'ImageLibraryModal',
  props: {
    visible: { type: Boolean, default: false },
  },
  emits: ['close', 'renamed'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    // State
    const activeTab = ref('questions')
    const searchQuery = ref('')
    const loading = ref(false)
    const questionImages = ref([])
    const answerImages = ref([])
    const selectedImage = ref(null)
    const references = ref([])
    const loadingReferences = ref(false)
    const newName = ref('')
    const updateQuestions = ref(true)
    const renaming = ref(false)
    const error = ref('')
    const successMessage = ref('')

    // Computed
    const currentImages = computed(() => {
      return activeTab.value === 'questions' ? questionImages.value : answerImages.value
    })

    const filteredImages = computed(() => {
      if (!searchQuery.value) return currentImages.value
      const query = searchQuery.value.toLowerCase()
      return currentImages.value.filter(img => img.name.toLowerCase().includes(query))
    })

    // Methods
    const loadImages = async () => {
      loading.value = true
      try {
        const [qResponse, aResponse] = await Promise.all([
          listImages('questions', { limit: 200 }),
          listImages('answers', { limit: 200 }),
        ])
        questionImages.value = qResponse.data.images.map(img => ({
          ...img,
          referenceCount: 0,
        }))
        answerImages.value = aResponse.data.images.map(img => ({
          ...img,
          referenceCount: 0,
        }))
      } catch (err) {
        console.error('Failed to load images:', err)
      } finally {
        loading.value = false
      }
    }

    const getImageSrc = (image) => {
      return getImageUrl(image.filename, activeTab.value)
    }

    const handleImageError = (event) => {
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="%239CA3AF"%3E%3Cpath stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /%3E%3C/svg%3E'
    }

    const selectImage = async (image) => {
      selectedImage.value = image
      newName.value = image.name
      error.value = ''
      successMessage.value = ''

      // Load references
      loadingReferences.value = true
      try {
        const response = await getImageReferences(activeTab.value, image.name)
        references.value = response.data.references
        // Update reference count
        image.referenceCount = response.data.total
      } catch (err) {
        console.error('Failed to load references:', err)
        references.value = []
      } finally {
        loadingReferences.value = false
      }
    }

    const handleRename = async () => {
      if (!selectedImage.value || !newName.value || newName.value === selectedImage.value.name) {
        return
      }

      // Validate name format
      const namePattern = /^[a-zA-Z0-9_\-]+$/
      if (!namePattern.test(newName.value)) {
        error.value = t('imageQuestions.invalidImageName')
        return
      }

      renaming.value = true
      error.value = ''
      successMessage.value = ''

      try {
        const response = await renameImage(
          activeTab.value,
          selectedImage.value.name,
          newName.value,
          updateQuestions.value
        )

        successMessage.value = t('imageQuestions.renameSuccess').replace('{count}', response.data.affected_questions)

        // Update local state
        const oldName = selectedImage.value.name
        selectedImage.value.name = newName.value
        selectedImage.value.filename = `${newName.value}.${selectedImage.value.extension}`

        // Update in the list
        const images = activeTab.value === 'questions' ? questionImages.value : answerImages.value
        const index = images.findIndex(img => img.name === oldName)
        if (index !== -1) {
          images[index] = { ...selectedImage.value }
        }

        emit('renamed', {
          imageType: activeTab.value,
          oldName,
          newName: newName.value,
          affectedQuestions: response.data.affected_questions,
        })

      } catch (err) {
        const detail = err.response?.data?.detail || err.message
        if (detail.includes('已存在')) {
          error.value = t('imageQuestions.imageNameExists')
        } else {
          error.value = t('imageQuestions.renameError') + ': ' + detail
        }
      } finally {
        renaming.value = false
      }
    }

    const resetState = () => {
      selectedImage.value = null
      references.value = []
      newName.value = ''
      error.value = ''
      successMessage.value = ''
      searchQuery.value = ''
    }

    // Watchers
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        loadImages()
        resetState()
      }
    })

    watch(activeTab, () => {
      selectedImage.value = null
      references.value = []
      newName.value = ''
      error.value = ''
      successMessage.value = ''
    })

    return {
      t,
      activeTab,
      searchQuery,
      loading,
      questionImages,
      answerImages,
      filteredImages,
      selectedImage,
      references,
      loadingReferences,
      newName,
      updateQuestions,
      renaming,
      error,
      successMessage,
      getImageSrc,
      handleImageError,
      selectImage,
      handleRename,
    }
  },
}
</script>
