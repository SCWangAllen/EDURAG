<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- Title and Action Buttons -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('imageQuestions.title') }}</h1>
        </div>
        <div class="flex space-x-3">
          <button
            @click="verifySelectedImages"
            :disabled="selectedQuestions.length === 0 || verifying"
            class="inline-flex items-center px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
          >
            <svg v-if="verifying" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ t('imageQuestions.verifySelected') }} ({{ selectedQuestions.length }})
          </button>
          <button
            @click="showImageLibraryModal = true"
            class="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md shadow-sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            {{ t('imageQuestions.imageLibrary') }}
          </button>
          <button
            @click="showImageUploadModal = true"
            class="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md shadow-sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            {{ t('imageQuestions.uploadImage') }}
          </button>
          <button
            @click="showCreateModal = true"
            class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ t('imageQuestions.createNew') }}
          </button>
          <button
            @click="showUploadModal = true"
            class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            {{ t('imageQuestions.uploadExcel') }}
          </button>
        </div>
      </div>

      <!-- Missing Images Alert -->
      <div
        v-if="missingImages && missingImages.total_missing > 0"
        class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-yellow-800">
              {{ t('imageQuestions.missingImagesTitle') }} ({{ missingImages.total_missing }})
            </h3>

            <!-- Question Images Missing -->
            <div v-if="missingImages.missing_question_images.length > 0" class="mt-2">
              <p class="text-sm text-yellow-700 font-medium">
                {{ t('imageQuestions.missingQuestionImages') }} ({{ missingImages.missing_question_images.length }}):
              </p>
              <ul class="mt-1 space-y-1 text-sm text-yellow-700 max-h-32 overflow-y-auto">
                <li v-for="item in missingImages.missing_question_images" :key="`q-${item.id}`" class="flex items-center justify-between">
                  <span class="truncate">
                    <span class="font-mono">{{ item.image_name }}.jpg</span>
                    <span class="text-yellow-600 ml-1">({{ item.subject }}{{ item.grade ? ` - ${item.grade}` : '' }})</span>
                  </span>
                  <button
                    @click="openImageUploadForMissing(item)"
                    class="ml-2 px-2 py-0.5 text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-800 rounded"
                  >
                    {{ t('imageQuestions.uploadNow') }}
                  </button>
                </li>
              </ul>
            </div>

            <!-- Answer Images Missing -->
            <div v-if="missingImages.missing_answer_images.length > 0" class="mt-2">
              <p class="text-sm text-yellow-700 font-medium">
                {{ t('imageQuestions.missingAnswerImages') }} ({{ missingImages.missing_answer_images.length }}):
              </p>
              <ul class="mt-1 space-y-1 text-sm text-yellow-700 max-h-32 overflow-y-auto">
                <li v-for="item in missingImages.missing_answer_images" :key="`a-${item.id}`" class="flex items-center justify-between">
                  <span class="truncate">
                    <span class="font-mono">{{ item.image_name }}.jpg</span>
                    <span class="text-yellow-600 ml-1">({{ item.subject }}{{ item.grade ? ` - ${item.grade}` : '' }})</span>
                  </span>
                  <button
                    @click="openImageUploadForMissing(item)"
                    class="ml-2 px-2 py-0.5 text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-800 rounded"
                  >
                    {{ t('imageQuestions.uploadNow') }}
                  </button>
                </li>
              </ul>
            </div>

            <p class="mt-2 text-xs text-yellow-600">
              {{ t('imageQuestions.missingImagesHint') }}
            </p>
          </div>
          <button
            @click="missingImagesCollapsed = !missingImagesCollapsed"
            class="flex-shrink-0 ml-2 text-yellow-400 hover:text-yellow-600"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6" v-if="stats">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('imageQuestions.totalQuestions') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.total_questions }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('imageQuestions.verified') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.verified_count }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('imageQuestions.unverified') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.unverified_count }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('imageQuestions.bySubject') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_subject || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter -->
      <ImageQuestionFilters
        v-model:searchQuery="searchQuery"
        v-model:selectedSubject="selectedSubject"
        v-model:selectedGrade="selectedGrade"
        v-model:selectedChapter="selectedChapter"
        v-model:selectedVerified="selectedVerified"
        :subjects="subjects"
        :grades="grades"
        :chapters="chapters"
        @search="searchQuestions"
      />

      <!-- Question List -->
      <ImageQuestionList
        :questions="questions"
        :loading="loading"
        :selected-questions="selectedQuestions"
        :total-questions="totalQuestions"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-size="pageSize"
        :is-all-selected="isAllSelected"
        @view="viewQuestion"
        @edit="editQuestion"
        @delete="deleteQuestion"
        @toggle-select="toggleQuestionSelection"
        @toggle-select-all="toggleSelectAll"
        @change-page="changePage"
        @upload-image="handleUploadImageFromCard"
      />
    </div>
  </div>

  <!-- Upload Modal -->
  <ImageQuestionUploadModal
    :visible="showUploadModal"
    @close="showUploadModal = false"
    @uploaded="handleUploadSuccess"
  />

  <!-- Detail Modal -->
  <ImageQuestionDetailModal
    :visible="showDetailModal"
    :question="selectedQuestion"
    @close="closeDetailModal"
    @edit="editQuestion"
    @delete="deleteQuestion"
  />

  <!-- Edit Modal -->
  <ImageQuestionEditModal
    :visible="showEditModal"
    :question="editingQuestion"
    @close="closeEditModal"
    @save="saveQuestion"
  />

  <!-- Create Modal -->
  <ImageQuestionCreateModal
    :visible="showCreateModal"
    @close="showCreateModal = false"
    @created="handleCreateSuccess"
  />

  <!-- Image Upload Modal -->
  <ImageUploadModal
    :visible="showImageUploadModal"
    :default-image-type="uploadImageType"
    :default-name="uploadImageName"
    @close="closeImageUploadModal"
    @uploaded="handleImageUploaded"
  />

  <!-- Image Library Modal -->
  <ImageLibraryModal
    :visible="showImageLibraryModal"
    @close="showImageLibraryModal = false"
    @renamed="handleImageRenamed"
  />
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '@/composables/useToast.js'
import {
  getImageQuestions,
  getImageQuestionStats,
  deleteImageQuestion,
  updateImageQuestion,
  verifyImages,
  getMissingImages,
} from '../api/imageQuestionService.js'
import ImageQuestionFilters from '@/components/ImageQuestions/ImageQuestionFilters.vue'
import ImageQuestionList from '@/components/ImageQuestions/ImageQuestionList.vue'
import ImageQuestionUploadModal from '@/components/ImageQuestions/ImageQuestionUploadModal.vue'
import ImageQuestionDetailModal from '@/components/ImageQuestions/ImageQuestionDetailModal.vue'
import ImageQuestionEditModal from '@/components/ImageQuestions/ImageQuestionEditModal.vue'
import ImageQuestionCreateModal from '@/components/ImageQuestions/ImageQuestionCreateModal.vue'
import ImageUploadModal from '@/components/ImageQuestions/ImageUploadModal.vue'
import ImageLibraryModal from '@/components/ImageQuestions/ImageLibraryModal.vue'

export default {
  name: 'ImageQuestions',
  components: {
    ImageQuestionFilters,
    ImageQuestionList,
    ImageQuestionUploadModal,
    ImageQuestionDetailModal,
    ImageQuestionEditModal,
    ImageQuestionCreateModal,
    ImageUploadModal,
    ImageLibraryModal,
  },
  setup() {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    // Data
    const loading = ref(false)
    const verifying = ref(false)
    const questions = ref([])
    const stats = ref(null)
    const missingImages = ref(null)
    const missingImagesCollapsed = ref(false)

    // Filters
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')
    const selectedChapter = ref('')
    const selectedVerified = ref('')
    const pageSize = ref(20)

    // Pagination
    const currentPage = ref(1)
    const totalQuestions = ref(0)
    const totalPages = ref(0)

    // Modals
    const showUploadModal = ref(false)
    const showDetailModal = ref(false)
    const showEditModal = ref(false)
    const showCreateModal = ref(false)
    const showImageUploadModal = ref(false)
    const showImageLibraryModal = ref(false)
    const selectedQuestion = ref(null)
    const editingQuestion = ref(null)
    const uploadImageType = ref('questions')
    const uploadImageName = ref('')

    // Selection
    const selectedQuestions = ref([])

    // Derived data from stats
    const subjects = computed(() => Object.keys(stats.value?.by_subject || {}))
    const grades = computed(() => Object.keys(stats.value?.by_grade || {}))
    const chapters = computed(() => Object.keys(stats.value?.by_chapter || {}))

    const isAllSelected = computed(() => {
      return questions.value.length > 0 &&
        questions.value.every(q => selectedQuestions.value.some(sq => sq.id === q.id))
    })

    // Methods
    const loadQuestions = async () => {
      try {
        loading.value = true

        const params = {
          page: currentPage.value,
          size: pageSize.value,
        }

        if (searchQuery.value) params.search = searchQuery.value
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedGrade.value) params.grade = selectedGrade.value
        if (selectedChapter.value) params.chapter = selectedChapter.value
        if (selectedVerified.value !== '') {
          params.verified = selectedVerified.value === 'true'
        }

        const response = await getImageQuestions(params)
        questions.value = response.data.questions || []
        totalQuestions.value = response.data.total || 0
        totalPages.value = response.data.pages || 0
      } catch (error) {
        toastError(t('imageQuestions.uploadError') + (error.response?.data?.detail || error.message), '載入題目')
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        const response = await getImageQuestionStats()
        stats.value = response.data
      } catch {
        stats.value = null
      }
    }

    const loadMissingImages = async () => {
      try {
        const response = await getMissingImages()
        missingImages.value = response.data
      } catch {
        missingImages.value = null
      }
    }

    const searchQuestions = () => {
      currentPage.value = 1
      loadQuestions()
    }

    const changePage = (page) => {
      currentPage.value = page
      loadQuestions()
    }

    const viewQuestion = (question) => {
      selectedQuestion.value = question
      showDetailModal.value = true
    }

    const editQuestion = (question) => {
      editingQuestion.value = { ...question }
      showEditModal.value = true
      showDetailModal.value = false
    }

    const deleteQuestion = async (question) => {
      if (!confirm(t('imageQuestions.deleteConfirm'))) return

      try {
        await deleteImageQuestion(question.id)
        await loadQuestions()
        await loadStats()
        showSuccess(t('imageQuestions.deleteSuccess'), '刪除題目')

        // Remove from selection if selected
        selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== question.id)
      } catch (error) {
        toastError(t('imageQuestions.deleteError') + (error.response?.data?.detail || error.message), '刪除題目')
      }
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedQuestion.value = null
    }

    const closeEditModal = () => {
      showEditModal.value = false
      editingQuestion.value = null
    }

    const saveQuestion = async (formData) => {
      try {
        await updateImageQuestion(editingQuestion.value.id, formData)
        closeEditModal()
        await loadQuestions()
        await loadStats()
        showSuccess(t('imageQuestions.updateSuccess'), '更新題目')
      } catch (error) {
        toastError(t('imageQuestions.updateError') + (error.response?.data?.detail || error.message), '更新題目')
      }
    }

    const toggleQuestionSelection = (question) => {
      const index = selectedQuestions.value.findIndex(q => q.id === question.id)
      if (index > -1) {
        selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== question.id)
      } else {
        selectedQuestions.value = [...selectedQuestions.value, question]
      }
    }

    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        // Deselect all on current page
        const currentPageIds = new Set(questions.value.map(q => q.id))
        selectedQuestions.value = selectedQuestions.value.filter(sq => !currentPageIds.has(sq.id))
      } else {
        // Select all on current page
        const currentSelected = new Set(selectedQuestions.value.map(sq => sq.id))
        const toAdd = questions.value.filter(q => !currentSelected.has(q.id))
        selectedQuestions.value = [...selectedQuestions.value, ...toAdd]
      }
    }

    const verifySelectedImages = async () => {
      if (selectedQuestions.value.length === 0) return

      try {
        verifying.value = true
        const questionIds = selectedQuestions.value.map(q => q.id)
        const response = await verifyImages(questionIds)
        const result = response.data

        await loadQuestions()
        await loadStats()
        await loadMissingImages()

        showSuccess(
          t('imageQuestions.verifySuccess')
            .replace('{verified}', result.verified)
            .replace('{failed}', result.failed),
          '驗證圖片'
        )
      } catch (error) {
        toastError(t('imageQuestions.verifyError') + (error.response?.data?.detail || error.message), '驗證圖片')
      } finally {
        verifying.value = false
      }
    }

    const handleUploadSuccess = async () => {
      showUploadModal.value = false
      await loadQuestions()
      await loadStats()
      await loadMissingImages()
    }

    const handleCreateSuccess = async () => {
      showCreateModal.value = false
      await loadQuestions()
      await loadStats()
      await loadMissingImages()
      showSuccess(t('imageQuestions.createSuccess'), t('imageQuestions.createTitle'))
    }

    const openImageUploadForMissing = (item) => {
      uploadImageType.value = item.image_type === 'answer' ? 'answers' : 'questions'
      uploadImageName.value = item.image_name
      showImageUploadModal.value = true
    }

    const handleUploadImageFromCard = ({ name, type }) => {
      uploadImageType.value = type
      uploadImageName.value = name
      showImageUploadModal.value = true
    }

    const closeImageUploadModal = () => {
      showImageUploadModal.value = false
      uploadImageName.value = ''
    }

    const handleImageUploaded = async () => {
      showSuccess(t('imageQuestions.imageUploadSuccess'), t('imageQuestions.uploadImageTitle'))
      await loadMissingImages()
    }

    const handleImageRenamed = async (data) => {
      showSuccess(
        t('imageQuestions.renameSuccess').replace('{count}', data.affectedQuestions),
        t('imageQuestions.imageLibrary')
      )
      // Reload questions to reflect the updated image names
      await loadQuestions()
    }

    // Watchers
    let searchTimeout = null
    watch(searchQuery, () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadQuestions()
      }, 300)
    })

    watch([selectedSubject, selectedGrade, selectedChapter, selectedVerified], () => {
      currentPage.value = 1
      loadQuestions()
    })

    // Init
    onMounted(async () => {
      await Promise.all([loadQuestions(), loadStats(), loadMissingImages()])
    })

    return {
      t,
      loading,
      verifying,
      questions,
      stats,
      missingImages,
      missingImagesCollapsed,
      searchQuery,
      selectedSubject,
      selectedGrade,
      selectedChapter,
      selectedVerified,
      pageSize,
      currentPage,
      totalQuestions,
      totalPages,
      showUploadModal,
      showDetailModal,
      showEditModal,
      showCreateModal,
      showImageUploadModal,
      showImageLibraryModal,
      selectedQuestion,
      editingQuestion,
      uploadImageType,
      uploadImageName,
      selectedQuestions,
      subjects,
      grades,
      chapters,
      isAllSelected,
      searchQuestions,
      changePage,
      viewQuestion,
      editQuestion,
      deleteQuestion,
      closeDetailModal,
      closeEditModal,
      saveQuestion,
      toggleQuestionSelection,
      toggleSelectAll,
      verifySelectedImages,
      handleUploadSuccess,
      handleCreateSuccess,
      openImageUploadForMissing,
      closeImageUploadModal,
      handleImageUploaded,
      handleUploadImageFromCard,
      handleImageRenamed,
    }
  },
}
</script>
