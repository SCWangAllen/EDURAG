<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- Title and Action Buttons -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('imageQuestions.title') }}</h1>
        </div>
        <div class="flex space-x-3">
          <BaseButton variant="secondary" @click="showImageLibraryModal = true">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            {{ t('imageQuestions.imageLibrary') }}
          </BaseButton>
          <BaseButton variant="secondary" @click="showImageUploadModal = true">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            {{ t('imageQuestions.uploadImage') }}
          </BaseButton>
          <BaseButton variant="secondary" @click="showCreateModal = true">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ t('imageQuestions.createNew') }}
          </BaseButton>
          <BaseButton variant="secondary" @click="downloadTemplate">
            {{ t('imageQuestions.downloadTemplate') }}
          </BaseButton>
          <BaseButton variant="primary" @click="showUploadModal = true">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            {{ t('imageQuestions.uploadExcel') }}
          </BaseButton>
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
              <span v-if="missingImagesCollapsed" class="ml-2 font-normal text-yellow-700">
                {{ t('imageQuestions.missingSummary').replace('{q}', missingImages.missing_question_images.length).replace('{a}', missingImages.missing_answer_images.length) }}
              </span>
            </h3>

            <div v-show="!missingImagesCollapsed">
            <!-- Question Images Missing -->
            <div v-if="missingImages.missing_question_images.length > 0" class="mt-2">
              <p class="text-sm text-yellow-700 font-medium">
                {{ t('imageQuestions.missingQuestionImages') }} ({{ missingImages.missing_question_images.length }}):
              </p>
              <ul class="mt-1 space-y-1 text-sm text-yellow-700 max-h-32 overflow-y-auto">
                <li v-for="item in missingImages.missing_question_images" :key="`q-${item.id}`" class="flex items-center justify-between">
                  <span class="truncate">
                    <span class="font-mono">{{ item.image_name }}.jpg</span>
                    <span class="text-yellow-600 ml-1">({{ getDisplayName(item.subject) }}{{ item.grade ? ` - ${getGradeLabel(item.grade)}` : '' }})</span>
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
                    <span class="text-yellow-600 ml-1">({{ getDisplayName(item.subject) }}{{ item.grade ? ` - ${getGradeLabel(item.grade)}` : '' }})</span>
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
          </div>
          <!-- 展開 / 收合(預設收起,狀態記在瀏覽器) -->
          <button
            type="button"
            @click="toggleMissingImages"
            :title="missingImagesCollapsed ? t('imageQuestions.missingExpand') : t('imageQuestions.missingCollapse')"
            class="flex-shrink-0 ml-2 inline-flex items-center gap-1 text-xs text-yellow-700 hover:text-yellow-900"
          >
            <span>{{ missingImagesCollapsed ? t('imageQuestions.missingExpand') : t('imageQuestions.missingCollapse') }}</span>
            <svg class="w-4 h-4 transition-transform" :class="missingImagesCollapsed ? '' : 'rotate-180'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Import Batches Panel -->
      <ImportBatchesPanel
        ref="importBatchesPanelRef"
        @view-batch="handleViewBatch"
        @deleted="handleImportBatchDeleted"
      />

      <!-- Statistics Cards -->
      <StatsStrip storage-key="edurag:imageStatsCollapsed" :items="statItems" />


      <!-- Active import-batch filter chip -->
      <div v-if="activeBatchId" class="flex items-center mb-3">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm bg-primary-50 text-primary-700 border border-primary-200">
          {{ t('imageQuestions.importBatchFilterChip').replace('{name}', activeBatchLabel) }}
          <button
            type="button"
            class="text-primary-500 hover:text-primary-800 font-medium leading-none"
            @click="clearBatchFilter"
          >
            &times;
          </button>
        </span>
      </div>

      <!-- Search and Filter -->
      <ImageQuestionFilters
        v-model:searchQuery="searchQuery"
        v-model:selectedSubject="selectedSubject"
        v-model:selectedGrade="selectedGrade"
        v-model:selectedChapter="selectedChapter"
        v-model:selectedVerified="selectedVerified"
        v-model:sortBy="sortBy"
        v-model:sortDir="sortDir"
        :subjects="subjects"
        :grades="grades"
        :chapters="chapters"
        :missing-image-names="missingImageNames"
        @search="searchQuestions"
      />

      <!-- Batch toolbar(選取 ≥1 時出現) -->
      <div
        v-if="selectedQuestions.length > 0"
        class="flex flex-wrap items-center justify-between gap-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-4"
      >
        <span class="text-sm font-medium text-blue-800">
          {{ t('imageQuestions.selectedCount').replace('{n}', selectedQuestions.length) }}
        </span>
        <div class="flex flex-wrap items-center gap-2">
          <BaseButton variant="secondary" :loading="verifying" @click="verifySelectedImages">
            {{ t('imageQuestions.verifySelected') }}
          </BaseButton>
          <BaseButton variant="secondary" @click="showBatchTagModal = true">
            {{ t('imageQuestions.batchRetag') }}
          </BaseButton>
          <button
            type="button"
            :disabled="deleting"
            class="px-3 py-2 rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
            @click="handleBatchDelete"
          >
            {{ t('imageQuestions.batchDelete') }}
          </button>
          <button
            type="button"
            class="px-2 py-2 text-sm text-gray-500 hover:text-gray-700"
            @click="clearSelection"
          >
            {{ t('imageQuestions.clearSelection') }}
          </button>
        </div>
      </div>

      <!-- Question List -->
      <ImageQuestionList
        :questions="questions"
        :loading="loading"
        :selected-questions="selectedQuestions"
        :total-questions="totalQuestions"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-size="pageSize"
        @change-page-size="changePageSize"
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

  <!-- Batch Re-tag Modal -->
  <BatchTagModal
    :visible="showBatchTagModal"
    :count="selectedQuestions.length"
    :applying="batchTagging"
    @close="showBatchTagModal = false"
    @apply="handleBatchTag"
  />
</template>

<script>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useLocalStorage } from '@/composables/useLocalStorage.js'
import { useLanguage } from '../composables/useLanguage.js'
import StatsStrip from '../components/Base/StatsStrip.vue'
import { useToast } from '@/composables/useToast.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import {
  getImageQuestions,
  getImageQuestionStats,
  deleteImageQuestion,
  batchDeleteImageQuestions,
  batchUpdateImageQuestions,
  updateImageQuestion,
  verifyImages,
  getMissingImages,
  downloadTemplate as downloadImageTemplate
} from '../api/imageQuestionService.js'
import ImageQuestionFilters from '@/components/ImageQuestions/ImageQuestionFilters.vue'
import ImportBatchesPanel from '@/components/ImageQuestions/ImportBatchesPanel.vue'
import BatchTagModal from '@/components/ImageQuestions/BatchTagModal.vue'
import ImageQuestionList from '@/components/ImageQuestions/ImageQuestionList.vue'
import ImageQuestionUploadModal from '@/components/ImageQuestions/ImageQuestionUploadModal.vue'
import ImageQuestionDetailModal from '@/components/ImageQuestions/ImageQuestionDetailModal.vue'
import ImageQuestionEditModal from '@/components/ImageQuestions/ImageQuestionEditModal.vue'
import ImageQuestionCreateModal from '@/components/ImageQuestions/ImageQuestionCreateModal.vue'
import ImageUploadModal from '@/components/ImageQuestions/ImageUploadModal.vue'
import ImageLibraryModal from '@/components/ImageQuestions/ImageLibraryModal.vue'
import BaseButton from '@/components/Base/BaseButton.vue'

export default {
  name: 'ImageQuestions',
  components: {
    StatsStrip,
    ImageQuestionFilters,
    ImportBatchesPanel,
    BatchTagModal,
    ImageQuestionList,
    ImageQuestionUploadModal,
    ImageQuestionDetailModal,
    ImageQuestionEditModal,
    ImageQuestionCreateModal,
    ImageUploadModal,
    ImageLibraryModal,
    BaseButton,
  },
  setup() {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目唯一來源
    const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded } = useSubjects()

    // Data
    const loading = ref(false)
    const verifying = ref(false)
    const questions = ref([])
    const stats = ref(null)
    const downloadTemplate = async () => {
      try {
        await downloadImageTemplate()
      } catch (error) {
        showError(t('imageQuestions.downloadTemplateFailed') || 'Download failed', 'template', error)
      }
    }
    // 統計一行摘要(StatsStrip)
    const statItems = computed(() => stats.value ? [
      { label: t('imageQuestions.totalQuestions'), value: stats.value.total_questions ?? 0 },
      { label: t('imageQuestions.verified'), value: stats.value.verified_count ?? 0 },
      { label: t('imageQuestions.unverified'), value: stats.value.unverified_count ?? 0 },
      { label: t('imageQuestions.bySubject'), value: Object.keys(stats.value.by_subject || {}).length }
    ] : [])
    const missingImages = ref(null)
    // 缺圖清單預設收起(29 題會佔掉半個畫面),展開與否記在瀏覽器
    const missingCollapsedStore = useLocalStorage('edurag:missingImagesCollapsed', true)
    const missingImagesCollapsed = ref(missingCollapsedStore.load() !== false)
    const toggleMissingImages = () => {
      missingImagesCollapsed.value = !missingImagesCollapsed.value
      missingCollapsedStore.save(missingImagesCollapsed.value)
    }

    // Filters
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')
    const selectedChapter = ref('')
    const selectedVerified = ref('')
    const sortBy = ref('created_at')
    const sortDir = ref('desc')

    // 匯入批次篩選(從「匯入紀錄」面板點「檢視此批」進來)
    const importBatchesPanelRef = ref(null)
    const activeBatchId = ref(null)
    const activeBatchLabel = computed(() => {
      if (!activeBatchId.value) return ''
      const list = importBatchesPanelRef.value?.batches || []
      const found = list.find(b => b.batch_id === activeBatchId.value)
      return found?.source_filename || activeBatchId.value
    })
    const pageSize = ref(20)
    // 每頁筆數(20 / 50 / 100):換了就回到第 1 頁重新載入
    const changePageSize = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadQuestions()
    }

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
    const showBatchTagModal = ref(false)
    const selectedQuestion = ref(null)
    const editingQuestion = ref(null)
    const uploadImageType = ref('questions')
    const uploadImageName = ref('')

    // Selection(跨頁保留:持久化到 localStorage)
    const SELECTION_KEY = 'edurag_selected_image_questions'
    const loadSelection = () => {
      try {
        const raw = localStorage.getItem(SELECTION_KEY)
        return raw ? JSON.parse(raw) : []
      } catch {
        return []
      }
    }
    const selectedQuestions = ref(loadSelection())
    const deleting = ref(false)
    const batchTagging = ref(false)
    watch(selectedQuestions, (val) => {
      try {
        localStorage.setItem(SELECTION_KEY, JSON.stringify(val))
      } catch {
        // localStorage 不可用時忽略
      }
    }, { deep: true })
    const clearSelection = () => {
      selectedQuestions.value = []
    }

    // 科目/年級來自統一來源；章節仍從題目統計動態取得
    const subjects = subjectNames
    const grades = GRADE_OPTIONS.map(g => g.value)
    const chapters = computed(() => Object.keys(stats.value?.by_chapter || {}))

    // 缺圖清單的檔名(question/answer 皆含)→ 供搜尋框 datalist 自動完成
    // 注意:question_image 欄位存的是不含副檔名的檔名,搜尋是 ilike 比對該欄位,
    // 建議值不可加 .jpg,否則選了建議值反而查不到(#0 rows)。
    const missingImageNames = computed(() => {
      const names = new Set()
      ;(missingImages.value?.missing_question_images || []).forEach(item => names.add(item.image_name))
      ;(missingImages.value?.missing_answer_images || []).forEach(item => names.add(item.image_name))
      return Array.from(names)
    })

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
          sort_by: sortBy.value,
          sort_dir: sortDir.value,
        }

        if (searchQuery.value) params.search = searchQuery.value
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedGrade.value) params.grade = selectedGrade.value
        if (selectedChapter.value) params.chapter = selectedChapter.value
        if (selectedVerified.value !== '') {
          params.verified = selectedVerified.value === 'true'
        }
        if (activeBatchId.value) params.import_batch_id = activeBatchId.value

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

    // 「檢視此批」:套用匯入批次篩選並回到第一頁
    const handleViewBatch = (batchId) => {
      activeBatchId.value = batchId
      currentPage.value = 1
      loadQuestions()
    }

    const clearBatchFilter = () => {
      activeBatchId.value = null
      currentPage.value = 1
      loadQuestions()
    }

    // 整批刪除後:若目前篩選的正是被刪除的批次,清掉篩選;無論如何都重整清單/統計/缺圖
    const handleImportBatchDeleted = async (deletedBatchId) => {
      if (activeBatchId.value === deletedBatchId) {
        activeBatchId.value = null
        currentPage.value = 1
      }
      await loadQuestions()
      await loadStats()
      await loadMissingImages()
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
        importBatchesPanelRef.value?.reload()
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

    // 上一次點選的卡片,Shift + 點另一張時把中間整段(本頁順序)都勾起來
    const lastClickedId = ref(null)
    const toggleQuestionSelection = (question, opts = {}) => {
      const list = questions.value
      if (opts.shift && lastClickedId.value != null) {
        const a = list.findIndex(q => q.id === lastClickedId.value)
        const b = list.findIndex(q => q.id === question.id)
        if (a > -1 && b > -1) {
          const [from, to] = a < b ? [a, b] : [b, a]
          const selectedIds = new Set(selectedQuestions.value.map(q => q.id))
          const additions = list.slice(from, to + 1).filter(q => !selectedIds.has(q.id))
          selectedQuestions.value = [...selectedQuestions.value, ...additions]
          lastClickedId.value = question.id
          return
        }
      }
      const index = selectedQuestions.value.findIndex(q => q.id === question.id)
      if (index > -1) {
        selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== question.id)
      } else {
        selectedQuestions.value = [...selectedQuestions.value, question]
      }
      lastClickedId.value = question.id
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
        importBatchesPanelRef.value?.reload()

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

    const handleBatchDelete = async () => {
      if (selectedQuestions.value.length === 0) return
      if (!confirm(t('imageQuestions.batchDeleteConfirm').replace('{n}', selectedQuestions.value.length))) return
      try {
        deleting.value = true
        const ids = selectedQuestions.value.map(q => q.id)
        const res = await batchDeleteImageQuestions(ids)
        const { success_count, failed_count } = res.data
        clearSelection()
        await loadQuestions()
        await loadStats()
        await loadMissingImages()
        importBatchesPanelRef.value?.reload()
        if (failed_count > 0) {
          toastError(
            t('imageQuestions.batchDeletePartial')
              .replace('{ok}', success_count)
              .replace('{fail}', failed_count),
            '批次刪除'
          )
        } else {
          showSuccess(
            t('imageQuestions.batchDeleteSuccess').replace('{n}', success_count),
            '批次刪除'
          )
        }
      } catch (error) {
        toastError(t('imageQuestions.batchDeleteError') + (error.response?.data?.detail || error.message), '批次刪除')
      } finally {
        deleting.value = false
      }
    }

    const handleBatchTag = async (fields) => {
      if (selectedQuestions.value.length === 0) return
      try {
        batchTagging.value = true
        const ids = selectedQuestions.value.map(q => q.id)
        const res = await batchUpdateImageQuestions(ids, fields)
        const { success_count } = res.data
        showBatchTagModal.value = false
        clearSelection()
        await loadQuestions()
        await loadStats()
        showSuccess(
          t('imageQuestions.batchRetagSuccess').replace('{n}', success_count),
          '批次改標籤'
        )
      } catch (error) {
        toastError(t('imageQuestions.batchRetagError') + (error.response?.data?.detail || error.message), '批次改標籤')
      } finally {
        batchTagging.value = false
      }
    }

    const handleUploadSuccess = async () => {
      showUploadModal.value = false
      await loadQuestions()
      await loadStats()
      await loadMissingImages()
      importBatchesPanelRef.value?.reload()
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
      // 上傳圖片後也重載清單,讓新圖即時反映(修正原本不刷新的問題)
      await loadQuestions()
      await loadStats()
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

    // 排序變更 → 回第一頁重載
    watch([sortBy, sortDir], () => {
      currentPage.value = 1
      loadQuestions()
    })

    // Init
    onMounted(async () => {
      await Promise.all([loadQuestions(), loadStats(), loadMissingImages(), ensureLoaded()])
    })

    // 頁面被 keep-alive 快取後再次切回時,重新整理清單/統計(保留篩選/排序/分頁/選取狀態)
    let isFirstActivation = true
    onActivated(() => {
      if (isFirstActivation) {
        isFirstActivation = false
        return
      }
      loadQuestions()
      loadStats()
      loadMissingImages()
    })

    return {
      t,
      getDisplayName,
      getGradeLabel,
      loading,
      verifying,
      questions,
      stats,
      missingImages,
      missingImagesCollapsed,
      toggleMissingImages,
      searchQuery,
      selectedSubject,
      selectedGrade,
      selectedChapter,
      selectedVerified,
      sortBy,
      sortDir,
      pageSize,
      changePageSize,
      importBatchesPanelRef,
      activeBatchId,
      activeBatchLabel,
      handleViewBatch,
      clearBatchFilter,
      handleImportBatchDeleted,
      currentPage,
      totalQuestions,
      statItems,
      downloadTemplate,
      totalPages,
      showUploadModal,
      showDetailModal,
      showEditModal,
      showCreateModal,
      showImageUploadModal,
      showImageLibraryModal,
      showBatchTagModal,
      deleting,
      batchTagging,
      selectedQuestion,
      editingQuestion,
      uploadImageType,
      uploadImageName,
      selectedQuestions,
      subjects,
      grades,
      chapters,
      missingImageNames,
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
      clearSelection,
      handleBatchDelete,
      handleBatchTag,
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
