<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 標題和操作按鈕 -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('documents.title') }}</h1>
        <div class="flex space-x-3">
          <BaseButton
            v-if="selectedDocuments.length > 0"
            variant="danger"
            :loading="deleting"
            @click="deleteSelectedDocuments"
          >
            <svg v-if="!deleting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            {{ deleting ? t('documents.deleting') : t('documents.deleteSelected') }} ({{ selectedDocuments.length }})
          </BaseButton>

          <BaseButton
            v-if="selectedDocuments.length > 0"
            variant="secondary"
            @click="showCopyToGradesModal = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            {{ t('documents.copyToGrades') }} ({{ selectedDocuments.length }})
          </BaseButton>

          <BaseButton
            v-if="selectedSourceFile"
            variant="danger"
            :loading="deletingUpload"
            @click="deleteSelectedUpload"
          >
            <svg v-if="!deletingUpload" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            {{ deletingUpload ? t('documents.deleting') : t('documents.deleteUpload').replace('{n}', currentSourceCount) }}
          </BaseButton>

          <BaseButton variant="secondary" @click="downloadTemplate">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            {{ t('documents.downloadTemplate') }}
          </BaseButton>

          <label class="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-md shadow-sm cursor-pointer">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            {{ t('documents.uploadExcel') }}
            <input
              type="file"
              accept=".xlsx,.xls"
              @change="handleFileSelect"
              class="hidden"
              ref="fileInput"
            >
          </label>
        </div>
      </div>

      <!-- 上傳格式提示 -->
      <p class="text-sm text-gray-500 mb-6 -mt-3">
        💡 {{ t('documents.uploadHint') }}
      </p>

      <!-- 統計卡片 -->
      <StatsStrip storage-key="edurag:documentStatsCollapsed" :items="statItems" />

      <!-- 搜尋和篩選 -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-4">
          <FormInput
            v-model="searchQuery"
            :label="t('documents.search')"
            :placeholder="t('documents.searchPlaceholder')"
            @keyup.enter="searchDocuments"
          />

          <SubjectSelect
            v-model="selectedSubject"
            :label="t('documents.subject')"
            :placeholder="t('documents.allSubjects')"
          />

          <FormSelect v-model="selectedGrade" :label="t('documents.grade')">
            <option value="">{{ t('documents.allGrades') }}</option>
            <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ getGradeLabel(g.value) }}</option>
          </FormSelect>

          <FormSelect v-model="sortBy" :label="t('documents.sortBy')">
            <option value="chapter">{{ t('documents.sortByChapter') }}</option>
            <option value="newest">{{ t('documents.sortByNewest') }}</option>
          </FormSelect>

          <FormSelect v-model="selectedSourceFile" :label="t('documents.sourceFile')">
            <option value="">{{ t('documents.allSourceFiles') }}</option>
            <option v-for="s in documentSources" :key="s.source_filename" :value="s.source_filename">
              {{ s.source_filename }} ({{ s.count }})
            </option>
          </FormSelect>

          <FormSelect v-model="pageSize" :label="t('documents.pageSize')">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </FormSelect>

          <div class="flex items-end">
            <BaseButton variant="primary" class="w-full" @click="searchDocuments">
              {{ t('documents.searchButton') }}
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-3">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                >
                <span class="ml-2 text-sm text-gray-600">{{ t('selectAll') || '全選' }}</span>
              </label>
              <h2 class="text-lg font-medium text-gray-900">{{ t('documents.documentList') }}</h2>
            </div>
            <div class="flex items-center gap-4 text-sm text-gray-500">
              <span>{{ selectedDocuments.length > 0 ? `${selectedDocuments.length}/${totalDocuments}` : totalDocuments }} {{ t('documents.totalCount') }}</span>
              <!-- 上方翻頁(老師需求:不用捲到最下面才能換頁) -->
              <div v-if="totalPages > 1" class="flex items-center gap-2 text-gray-600">
                <button type="button" @click="changePage(currentPage - 1)" :disabled="currentPage <= 1" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50">{{ t('documents.previous') }}</button>
                <span>{{ currentPage }} / {{ totalPages }}</span>
                <button type="button" @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50">{{ t('documents.next') }}</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 跨頁全選提示 -->
        <div
          v-if="showCrossPagePrompt"
          class="px-6 py-3 bg-blue-50 border-b border-blue-200 text-sm text-blue-800 flex items-center justify-center flex-wrap gap-x-2 gap-y-1"
        >
          <span>{{ t('documents.selectedCurrentPage') }} {{ documents.length }} {{ t('documents.countUnit') }}</span>
          <button class="font-medium underline hover:text-blue-900" @click="selectAllFiltered">
            {{ t('documents.selectAllFiltered') }} {{ totalDocuments }} {{ t('documents.countUnit') }}
          </button>
        </div>
        <div
          v-else-if="showAllSelectedNotice"
          class="px-6 py-3 bg-blue-50 border-b border-blue-200 text-sm text-blue-800 flex items-center justify-center flex-wrap gap-x-2 gap-y-1"
        >
          <span>{{ t('documents.allSelected') }} {{ selectedDocuments.length }} {{ t('documents.countUnit') }}</span>
          <button class="font-medium underline hover:text-blue-900" @click="clearAllSelection">
            {{ t('documents.clearSelection') }}
          </button>
        </div>

        <div v-if="loading" class="p-6 text-center">
          <div class="inline-flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ t('documents.loading') }}
          </div>
        </div>

        <EmptyState
          v-else-if="documents.length === 0"
          icon="📄"
          :title="t('documents.noDocuments')"
          :description="t('documents.noDocumentsHint')"
        />

        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="document in documents"
            :key="document.id"
            class="p-6 hover:bg-gray-50"
            :class="{ 'bg-blue-50 border-l-4 border-blue-500': selectedDocuments.some(d => d.id === document.id) }"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-3">
                <input
                  type="checkbox"
                  :checked="selectedDocuments.some(d => d.id === document.id)"
                  @change="toggleDocumentSelection(document)"
                  @click.stop
                  class="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                >
                <div class="flex-1 min-w-0 cursor-pointer" @click="selectDocument(document)">
                  <div class="flex items-center space-x-3">
                    <h3 class="text-sm font-medium text-gray-900 truncate">
                      {{ document.title }}
                    </h3>
                  <span :class="subjectBadgeClass(document.subject)" :style="subjectBadgeStyle(document.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ getDisplayName(document.subject) }}
                  </span>
                  <span v-if="document.grade" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {{ document.grade }}
                  </span>
                  <span v-if="document.image_filename" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {{ t('documents.withImage') }}
                  </span>
                </div>

                <p v-if="document.source_filename" class="mt-0.5 text-xs text-gray-400 truncate">
                  {{ document.source_filename }}
                </p>

                <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                  <div v-if="document.chapter" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h2m-2 0v4a2 2 0 002 2h2a2 2 0 002-2v-4m0 0V9a2 2 0 00-2-2h-2m2 4h4"></path>
                    </svg>
                    {{ document.chapter }}
                  </div>
                  <div class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                    </svg>
                    {{ document.content.length }} {{ t('documents.characters') }}
                  </div>
                  <div>{{ formatDate(document.created_at) }}</div>
                </div>

                  <p class="mt-2 text-sm text-gray-600 line-clamp-2">
                    {{ document.content.substring(0, 150) }}{{ document.content.length > 150 ? '...' : '' }}
                  </p>
                </div>
              </div>

              <div class="flex items-center space-x-2 ml-4">
                <button
                  @click.stop="editDocument(document)"
                  class="text-gray-400 hover:text-primary-600"
                  :title="t('documents.edit')"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click.stop="deleteDocument(document)"
                  class="text-gray-400 hover:text-red-600"
                  :title="t('documents.delete')"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分頁 -->
        <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              {{ t('documents.previous') }}
            </button>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              {{ t('documents.next') }}
            </button>
          </div>

          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                {{ t('documents.showing') }} <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
                {{ t('documents.to') }} <span class="font-medium">{{ Math.min(currentPage * pageSize, totalDocuments) }}</span>
                {{ t('documents.of') }} <span class="font-medium">{{ totalDocuments }}</span> {{ t('documents.results') }}
              </p>
            </div>

            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="changePage(currentPage - 1)"
                  :disabled="currentPage <= 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>

                <button
                  v-for="page in pageNumbers"
                  :key="page"
                  @click="changePage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === currentPage
                      ? 'z-10 bg-blue-50 border-blue-500 text-primary-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>

                <button
                  @click="changePage(currentPage + 1)"
                  :disabled="currentPage >= totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Excel 上傳預覽 Modal -->
  <DocumentUploadModal
    :visible="showUploadModal"
    :upload-preview="uploadPreview"
    :uploading="uploading"
    @close="closeUploadModal"
    @confirm="confirmUpload"
  />

  <!-- 文件詳情/編輯 Modal -->
  <DocumentDetailModal
    ref="detailModalRef"
    :visible="showDetailModal"
    :document="selectedDocument"
    :grade-options="gradeOptions"
    @close="closeDetailModal"
    @saved="handleDetailSaved"
  />

  <!-- 複製到年級 Modal -->
  <CopyToGradesModal
    :visible="showCopyToGradesModal"
    :count="selectedDocuments.length"
    :copying="copyingToGrades"
    @close="showCopyToGradesModal = false"
    @confirm="copySelectedDocumentsToGrades"
  />
</template>

<script>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '../composables/useToast.js'
import { usePagination } from '../composables/usePagination.js'
import { useSelection } from '../composables/useSelection.js'
import { useModal } from '../composables/useModal.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { formatDate } from '@/utils/formatters.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import documentService from '../api/documentService.js'
import uploadService from '../api/uploadService.js'
import StatsStrip from '../components/Base/StatsStrip.vue'
import DocumentUploadModal from '../components/Documents/DocumentUploadModal.vue'
import DocumentDetailModal from '../components/Documents/DocumentDetailModal.vue'
import CopyToGradesModal from '../components/Documents/CopyToGradesModal.vue'
import BaseButton from '../components/Base/BaseButton.vue'
import FormInput from '../components/Base/FormInput.vue'
import FormSelect from '../components/Base/FormSelect.vue'
import SubjectSelect from '../components/Base/SubjectSelect.vue'
import EmptyState from '../components/Base/EmptyState.vue'

export default {
  name: 'Documents',
  components: {
    StatsStrip,
    DocumentUploadModal,
    DocumentDetailModal,
    CopyToGradesModal,
    BaseButton,
    FormInput,
    FormSelect,
    SubjectSelect,
    EmptyState
  },
  setup() {
    const { t, isEnglish } = useLanguage()
    const { showSuccess, showInfo, showError: toastError } = useToast()
    // 科目/年級唯一來源
    const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded, refresh, subjectBadgeClass, subjectBadgeStyle } = useSubjects()

    // 響應式資料
    const loading = ref(false)
    const documents = ref([])
    const stats = ref(null)
    // 統計一行摘要(StatsStrip):總數 / 科目數 / 含圖片 / 章節數
    const statItems = computed(() => stats.value ? [
      { label: t('documents.totalDocuments'), value: stats.value.total_documents ?? 0 },
      { label: t('documents.subjectCount'), value: Object.keys(stats.value.subjects || {}).length },
      { label: t('documents.withImages'), value: stats.value.has_images ?? 0 },
      { label: t('documents.chapterCount'), value: Object.keys(stats.value.top_chapters || {}).length }
    ] : [])
    const detailModalRef = ref(null)

    // 搜尋和篩選
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')
    const sortBy = ref('chapter')
    const selectedSourceFile = ref('')
    const documentSources = ref([])

    // 分頁（fetchFn 稍後設定）
    const pagination = usePagination(null, 20)
    const { currentPage, pageSize, totalPages, pageNumbers, changePage: paginationChangePage } = pagination
    const totalDocuments = pagination.totalItems

    // Modal 控制
    const showUploadModal = ref(false)
    const detailModal = useModal()
    const showDetailModal = detailModal.isOpen
    const uploading = ref(false)

    // 上傳相關
    const uploadPreview = ref(null)
    const selectedFile = ref(null)

    // 文件詳情
    const selectedDocument = detailModal.data

    // 批次選擇
    const selection = useSelection('id')
    const selectedDocuments = selection.selectedItems
    const deleting = ref(false)
    const deletingUpload = ref(false)
    // 是否已「選取符合篩選的全部」（跨頁全選）
    const selectAllAcrossPages = ref(false)

    // 複製到年級
    const showCopyToGradesModal = ref(false)
    const copyingToGrades = ref(false)

    // 計算屬性
    const isAllSelected = computed(() => selection.isAllSelected(documents.value))

    // 當頁已全選、且庫內尚有更多符合篩選的文件 → 顯示跨頁全選提示
    const showCrossPagePrompt = computed(() =>
      !selectAllAcrossPages.value &&
      isAllSelected.value &&
      totalDocuments.value > documents.value.length
    )
    // 已跨頁全選 → 顯示「已選全部 / 清除選取」
    const showAllSelectedNotice = computed(() => selectAllAcrossPages.value)

    // 目前選取的「上傳檔案」在來源清單中對應的文件數量
    const currentSourceCount = computed(() => {
      const found = documentSources.value.find(s => s.source_filename === selectedSourceFile.value)
      return found ? found.count : 0
    })

    // 方法
    const loadDocuments = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          size: pageSize.value,
          ...buildFilterParams()
        }

        const data = await documentService.getDocuments(params)
        documents.value = data.documents || []
        totalDocuments.value = data.total || 0


      } catch (error) {
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        stats.value = await documentService.getDocumentStats()
      } catch (error) {
      }
    }

    // 上傳來源檔案清單(用於「上傳檔案」篩選下拉;依目前的科目/年級篩選)
    const loadDocumentSources = async () => {
      try {
        const params = {}
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedGrade.value) params.grade = selectedGrade.value
        const data = await documentService.getDocumentSources(params)
        documentSources.value = data.sources || []
        // 目前選取的上傳檔案若已不在新清單中(例如換了篩選),清除選取
        if (selectedSourceFile.value && !documentSources.value.some(s => s.source_filename === selectedSourceFile.value)) {
          selectedSourceFile.value = ''
        }
      } catch (error) {
        documentSources.value = []
      }
    }

    const changePage = (page) => {
      currentPage.value = page
      loadDocuments()
    }

    const searchDocuments = () => {
      currentPage.value = 1
      selectAllAcrossPages.value = false
      loadDocuments()
    }

    // 目前篩選條件（清單載入、跨頁全選與批次刪除共用）
    const buildFilterParams = () => {
      const params = {}
      if (selectedSubject.value) params.subject = selectedSubject.value
      if (selectedGrade.value) params.grade = selectedGrade.value
      if (searchQuery.value) params.search = searchQuery.value
      if (sortBy.value) params.sort = sortBy.value
      if (selectedSourceFile.value) params.source_file = selectedSourceFile.value
      return params
    }

    // 選取符合目前篩選的全部文件（不帶 size → 後端回傳全部）
    const selectAllFiltered = async () => {
      try {
        const data = await documentService.getDocuments(buildFilterParams())
        selectedDocuments.value = data.documents || []
        selectAllAcrossPages.value = true
      } catch (error) {
        toastError(t('documents.selectAllError'), '選取全部', error)
      }
    }

    // 清除全部選取
    const clearAllSelection = () => {
      selection.clearSelection()
      selectAllAcrossPages.value = false
    }

    // Excel 上傳相關
    const downloadTemplate = async () => {
      try {
        await uploadService.downloadTemplate()
      } catch (error) {
      }
    }

    const handleFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      selectedFile.value = file

      try {
        uploadPreview.value = await uploadService.uploadExcel(file, true)
        showUploadModal.value = true
      } catch (error) {
        toastError(
          t('documents.uploadError') + (error.response?.data?.detail || error.message),
          '上傳文件',
          error
        )
      }

      // 清空 input
      event.target.value = ''
    }

    const confirmUpload = async () => {
      if (!selectedFile.value) return

      uploading.value = true
      try {
        const result = await uploadService.confirmSave(selectedFile.value)
        closeUploadModal()

        await loadDocuments()
        await loadStats()
        await loadDocumentSources()
        await refresh()

        // 有 created/replaced 統計時顯示明細,否則退回原本的通用訊息
        const hasCounts = result && (result.created !== undefined || result.replaced !== undefined)
        const message = hasCounts
          ? t('documents.uploadSuccessWithCounts')
              .replace('{created}', result.created || 0)
              .replace('{replaced}', result.replaced || 0)
          : t('documents.uploadSuccess')

        showSuccess(message, '上傳文件')

      } catch (error) {
        toastError(
          t('documents.saveError') + (error.response?.data?.detail || error.message),
          '儲存文件',
          error
        )
      } finally {
        uploading.value = false
      }
    }

    const closeUploadModal = () => {
      showUploadModal.value = false
      uploadPreview.value = null
      selectedFile.value = null
    }

    // 文件操作相關
    const selectDocument = (document) => {
      detailModal.open(document)
    }

    const editDocument = (document) => {
      detailModal.open(document)
      // 讓子元件 watch 到 document 變化後，透過 nextTick 啟動編輯
      setTimeout(() => {
        if (detailModalRef.value) {
          detailModalRef.value.startEdit()
        }
      }, 0)
    }

    const handleDetailSaved = async (formData) => {
      try {
        await documentService.updateDocument(selectedDocument.value.id, formData)
        closeDetailModal()
        await loadDocuments()
      } catch (error) {
        if (detailModalRef.value) {
          detailModalRef.value.resetSaving()
        }
        toastError(
          t('documents.saveError') + (error.response?.data?.detail || error.message),
          '儲存文件',
          error
        )
      }
    }

    const deleteDocument = async (document) => {
      if (!confirm(`${t('documents.deleteConfirm')} ${document.title}?`)) return

      try {
        await documentService.deleteDocument(document.id)
        await loadDocuments()
        await loadStats()
        await loadDocumentSources()
        showSuccess(t('ui.vw_document_delete_success'), '刪除文件')

      } catch (error) {

        // 處理引用衝突錯誤 (409)
        if (error.response?.status === 409) {
          const detail = error.response.data.detail
          const references = detail.references

          let message = t('ui.vw_ref_conflict_intro').replace('{title}', document.title)
          if (references.questions > 0) {
            message += t('ui.vw_ref_conflict_questions_line').replace('{count}', references.questions)
          }
          if (references.embeddings > 0) {
            message += t('ui.vw_ref_conflict_embeddings_line').replace('{count}', references.embeddings)
          }
          message += t('ui.vw_ref_conflict_force_prompt')

          if (confirm(message)) {
            try {
              await documentService.deleteDocument(document.id, true) // force = true
              await loadDocuments()
              await loadStats()
              await loadDocumentSources()
              showSuccess(
                t('ui.vw_force_delete_success')
                  .replace('{title}', document.title)
                  .replace('{questions}', references.questions)
                  .replace('{embeddings}', references.embeddings),
                '強制刪除文件'
              )
            } catch (forceError) {
              toastError(
                t('ui.vw_force_delete_failed_prefix') + (forceError.response?.data?.detail || forceError.message),
                '強制刪除文件',
                forceError
              )
            }
          }
        } else {
          toastError(
            t('documents.deleteError') + (error.response?.data?.detail || error.message),
            '刪除文件',
            error
          )
        }
      }
    }

    // 批次選擇方法
    const toggleDocumentSelection = (document) => {
      selection.toggleSelection(document)
      // 手動改動選取即脫離「跨頁全選」狀態
      selectAllAcrossPages.value = false
    }

    const toggleSelectAll = () => {
      selection.toggleSelectAll(documents.value)
      // 當頁全選是頁面層級操作，脫離「跨頁全選」狀態
      selectAllAcrossPages.value = false
    }

    const deleteSelectedDocuments = async () => {
      if (selectedDocuments.value.length === 0) {
        toastError(t('documents.noSelection'), '批次刪除文件')
        return
      }

      const count = selectedDocuments.value.length
      const confirmMessage =
        `${t('documents.batchDeleteConfirm')} ${count} ${t('documents.batchDeleteConfirmSuffix')}`
      if (!confirm(confirmMessage)) return

      await runBatchDelete(false)
    }

    // 單次 batch API 刪除；引用處理交由後端 failed 回報
    const runBatchDelete = async (force) => {
      const ids = selectedDocuments.value.map(d => d.id)
      deleting.value = true

      try {
        const result = await documentService.batchDeleteDocuments(ids, force)
        const successCount = result.success_count || 0
        const failedCount = result.failed_count || 0
        const failed = result.failed || []

        // 全部失敗且皆因引用 → 詢問是否強制刪除，帶 force 重打
        const allFailedByReference = !force &&
          successCount === 0 && failedCount > 0 &&
          failed.every(f => (f.reason || '').includes('引用'))
        if (allFailedByReference) {
          const forceConfirm =
            `${failedCount} ${t('documents.forceDeleteConfirmSuffix')}`
          if (confirm(forceConfirm)) {
            await runBatchDelete(true)
            return
          }
        }

        // 失敗原因列於 console，失敗項保留在 selection
        if (failedCount > 0) {
          failed.forEach(f => console.warn(`文件 ${f.id} 刪除失敗：${f.reason}`))
        }
        const failedIds = new Set(failed.map(f => f.id))
        selectedDocuments.value = selectedDocuments.value.filter(d => failedIds.has(d.id))
        if (failedIds.size === 0) selectAllAcrossPages.value = false

        let resultMessage =
          `${t('documents.deleteSuccessCount')} ${successCount} ${t('documents.countUnit')}`
        if (failedCount > 0) {
          resultMessage +=
            `，${t('documents.deleteFailedCount')} ${failedCount} ${t('documents.countUnit')}`
        }
        if (successCount > 0) {
          showSuccess(resultMessage, '批次刪除文件')
        } else {
          toastError(resultMessage, '批次刪除文件')
        }

        await loadDocuments()
        await loadStats()
        await loadDocumentSources()

      } catch (error) {
        toastError(
          t('documents.deleteError') + (error.response?.data?.detail || error.message),
          '批次刪除文件',
          error
        )
      } finally {
        deleting.value = false
      }
    }

    // 刪除整批上傳(依目前「上傳檔案」篩選選中的來源檔名,一鍵刪除整批文件)
    const deleteSelectedUpload = async () => {
      const sourceFilename = selectedSourceFile.value
      if (!sourceFilename) return

      const confirmMessage = t('documents.deleteUploadConfirm')
        .replace('{file}', sourceFilename)
        .replace('{count}', currentSourceCount.value)
      if (!confirm(confirmMessage)) return

      await runDeleteBySource(sourceFilename, false)
    }

    const runDeleteBySource = async (sourceFilename, force) => {
      deletingUpload.value = true
      // 刪除範圍 = 目前的科目 / 年級篩選(下拉顯示的筆數就是依這個範圍算的)
      const scope = { subject: selectedSubject.value, grade: selectedGrade.value }
      try {
        const first = await documentService.deleteBySource(sourceFilename, force, scope)
        let deleted = first.success_count || 0
        let kept = first.failed_count || 0

        // 有文件被題目引用且尚未強制刪除 → 詢問是否一併刪除題目
        if (!force && kept > 0) {
          const forceMessage = t('documents.deleteUploadForceConfirm').replace('{failed}', kept)
          if (confirm(forceMessage)) {
            const second = await documentService.deleteBySource(sourceFilename, true, scope)
            deleted += second.success_count || 0
            kept = second.failed_count || 0
          }
        }

        const title = t('documents.deleteUploadTitle')
        if (kept > 0) {
          // 老師選擇保留有題目引用的文件:提示保留數,且不清掉篩選,讓剩下的文件留在畫面上
          showInfo(
            t('documents.deleteUploadPartial').replace('{deleted}', deleted).replace('{failed}', kept),
            title
          )
          await loadDocuments()
        } else {
          showSuccess(
            t('documents.deleteUploadDone').replace('{deleted}', deleted).replace('{file}', sourceFilename),
            title
          )
          // 清掉篩選即觸發 watch 重新載入列表,不再另外呼叫 loadDocuments 以免抓兩次
          selectedSourceFile.value = ''
        }
        await loadDocumentSources()
        await loadStats()
      } catch (error) {
        toastError(
          t('documents.deleteError') + (error.response?.data?.detail || error.message),
          t('documents.deleteUploadTitle'),
          error
        )
      } finally {
        deletingUpload.value = false
      }
    }

    // 複製選取文件到指定年級(例如把 G4-G6 教材複製給對應的國中先修班使用)
    const copySelectedDocumentsToGrades = async (targetGrades) => {
      if (selectedDocuments.value.length === 0 || targetGrades.length === 0) return

      copyingToGrades.value = true
      try {
        const ids = selectedDocuments.value.map(d => d.id)
        const result = await documentService.copyDocumentsToGrades(ids, targetGrades)

        const created = result.created || 0
        const skippedCount = result.skipped_count || 0
        const reasons = [...new Set((result.skipped_items || []).map(item => item.reason).filter(Boolean))]

        let message = t('documents.copyResultCreated').replace('{count}', created)
        if (skippedCount > 0) {
          message += t('documents.copyResultSkipped')
            .replace('{count}', skippedCount)
            .replace('{reason}', reasons.join('、') || t('documents.copyResultUnknownReason'))
        }

        if (created > 0) {
          showSuccess(message, t('documents.copyToGrades'))
          // 有複製成功才關視窗、清選取;全部被略過時保留選取,老師可改選年級再試
          showCopyToGradesModal.value = false
          selection.clearSelection()
          selectAllAcrossPages.value = false
          await loadDocuments()
          await loadStats()
        } else {
          toastError(message, t('documents.copyToGrades'))
        }
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('documents.copyFailed'),
          t('documents.copyToGrades'),
          error
        )
      } finally {
        copyingToGrades.value = false
      }
    }

    const closeDetailModal = () => {
      detailModal.close()
    }

    // 監聽器
    watch([pageSize, selectedSubject, selectedGrade, sortBy, selectedSourceFile], () => {
      currentPage.value = 1
      // 篩選改變 → 先前的「跨頁全選」不再對應，重置提示
      selectAllAcrossPages.value = false
      loadDocuments()
    }, { flush: 'post' })

    // 科目/年級篩選改變 → 「上傳檔案」下拉選項需依新篩選重新載入
    watch([selectedSubject, selectedGrade], () => {
      loadDocumentSources()
    })

    // 載入資料
    onMounted(async () => {
      await Promise.all([
        loadDocuments(),
        loadStats(),
        loadDocumentSources(),
        ensureLoaded()
      ])
    })

    // 頁面被 keep-alive 快取後再次切回時,重新整理清單/統計(保留篩選/搜尋/分頁/選取狀態)
    let isFirstActivation = true
    onActivated(() => {
      if (isFirstActivation) {
        isFirstActivation = false
        return
      }
      loadDocuments()
      loadStats()
    })

    return {
      // 響應式資料
      loading,
      documents,
      stats,
      subjectNames,
      searchQuery,
      selectedSubject,
      selectedGrade,
      sortBy,
      selectedSourceFile,
      documentSources,
      pageSize,
      currentPage,
      totalDocuments,
      statItems,
      totalPages,
      showUploadModal,
      showDetailModal,
      uploading,
      uploadPreview,
      selectedDocument,
      detailModalRef,

      // 計算屬性
      pageNumbers,
      isAllSelected,
      showCrossPagePrompt,
      showAllSelectedNotice,

      // 批次選擇
      selectedDocuments,
      deleting,

      // 刪除整批上傳
      deletingUpload,
      currentSourceCount,
      deleteSelectedUpload,

      // 複製到年級
      showCopyToGradesModal,
      copyingToGrades,
      copySelectedDocumentsToGrades,

      // 方法
      loadDocuments,
      searchDocuments,
      changePage,
      toggleDocumentSelection,
      toggleSelectAll,
      selectAllFiltered,
      clearAllSelection,
      deleteSelectedDocuments,
      downloadTemplate,
      handleFileSelect,
      confirmUpload,
      closeUploadModal,
      selectDocument,
      editDocument,
      handleDetailSaved,
      deleteDocument,
      closeDetailModal,
      subjectBadgeClass,
      subjectBadgeStyle,
      getDisplayName,
      getGradeLabel,
      formatDate,

      // 常數
      gradeOptions: GRADE_OPTIONS,

      // 語言
      t,
      isEnglish
    }
  }
}
</script>
