<template>
  <div class="relative">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Search Input -->
    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        @focus="showDropdown = true"
        @input="handleSearch"
      />
      <div class="absolute inset-y-0 right-0 flex items-center pr-3">
        <svg
          v-if="loading"
          class="animate-spin h-4 w-4 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg
          v-else
          class="h-4 w-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>

    <!-- Dropdown -->
    <div
      v-if="showDropdown && images.length > 0"
      class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
    >
      <div
        v-for="image in images"
        :key="image.name"
        class="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center space-x-3"
        @click="selectImage(image)"
      >
        <!-- Thumbnail -->
        <div class="flex-shrink-0 w-12 h-12 bg-gray-100 rounded overflow-hidden">
          <img
            :src="getImageUrl(image)"
            :alt="image.name"
            class="w-full h-full object-cover"
            @error="handleImageError"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ image.name }}</p>
          <p class="text-xs text-gray-500">.{{ image.extension }}</p>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div
      v-if="showDropdown && !loading && searchQuery && images.length === 0"
      class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg p-3 text-center text-sm text-gray-500"
    >
      {{ t('imageQuestions.noImagesFound') || 'No images found' }}
    </div>

    <!-- Selected Preview -->
    <div v-if="modelValue && showPreview" class="mt-2">
      <div class="flex items-center space-x-3 p-2 bg-gray-50 rounded-md">
        <div class="flex-shrink-0 w-16 h-16 bg-gray-100 rounded overflow-hidden">
          <img
            :src="getSelectedImageUrl()"
            :alt="modelValue"
            class="w-full h-full object-cover"
            @error="handleImageError"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ modelValue }}</p>
          <button
            type="button"
            class="text-xs text-red-600 hover:text-red-800"
            @click="clearSelection"
          >
            {{ t('imageQuestions.clearSelection') || 'Clear' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Click outside handler -->
    <div
      v-if="showDropdown"
      class="fixed inset-0 z-0"
      @click="showDropdown = false"
    ></div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { listImages, getImageUrl as getImageUrlApi } from '@/api/imageQuestionService.js'

export default {
  name: 'ImageSelector',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    imageType: {
      type: String,
      default: 'questions',
      validator: (value) => ['questions', 'answers'].includes(value),
    },
    label: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    required: {
      type: Boolean,
      default: false,
    },
    showPreview: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const searchQuery = ref(props.modelValue || '')
    const images = ref([])
    const loading = ref(false)
    const showDropdown = ref(false)
    let searchTimeout = null

    const loadImages = async (search = '') => {
      try {
        loading.value = true
        const response = await listImages(props.imageType, { search, limit: 50 })
        images.value = response.data.images || []
      } catch {
        images.value = []
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        loadImages(searchQuery.value)
      }, 300)
    }

    const selectImage = (image) => {
      searchQuery.value = image.name
      emit('update:modelValue', image.name)
      showDropdown.value = false
    }

    const clearSelection = () => {
      searchQuery.value = ''
      emit('update:modelValue', '')
    }

    const getImageUrl = (image) => {
      return getImageUrlApi(image.filename, props.imageType)
    }

    const getSelectedImageUrl = () => {
      return getImageUrlApi(props.modelValue, props.imageType)
    }

    const handleImageError = (event) => {
      event.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23e5e7eb" width="100" height="100"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-size="12">No Image</text></svg>'
    }

    watch(() => props.modelValue, (newVal) => {
      if (newVal !== searchQuery.value) {
        searchQuery.value = newVal || ''
      }
    })

    onMounted(() => {
      loadImages()
    })

    onUnmounted(() => {
      if (searchTimeout) clearTimeout(searchTimeout)
    })

    return {
      t,
      searchQuery,
      images,
      loading,
      showDropdown,
      handleSearch,
      selectImage,
      clearSelection,
      getImageUrl,
      getSelectedImageUrl,
      handleImageError,
    }
  },
}
</script>
