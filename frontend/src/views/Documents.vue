<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 標題和操作按鈕 -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('documents.title') }}</h1>
        <div class="flex space-x-3">
          <button
            v-if="selectedDocuments.length > 0"
            @click="deleteSelectedDocuments"
            :disabled="deleting"
            class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
          >
            <svg v-if="deleting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            {{ deleting ? t('documents.deleting') : t('documents.deleteSelected') }} ({{ selectedDocuments.length }})
          </button>

          <button
            @click="downloadTemplate"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            {{ t('documents.downloadTemplate') }}
          </button>

          <label class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm cursor-pointer">
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

      <!-- 統計卡片 -->
      <DocumentStatCards :stats="stats" />

      <!-- 搜尋和篩選 -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.search') }}</label>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('documents.searchPlaceholder')"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.subject') }}</label>
            <select
              v-model="selectedSubject"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ t('documents.allSubjects') }}</option>
              <option v-for="subject in subjects" :key="subject" :value="subject">
                {{ subject }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.grade') }}</label>
            <select
              v-model="selectedGrade"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ t('documents.allGrades') }}</option>
              <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.pageSize') }}</label>
            <select
              v-model="pageSize"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>

          <div class="flex items-end">
            <button
              @click="searchDocuments"
              class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
            >
              {{ t('documents.searchButton') }}
            </button>
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
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2 text-sm text-gray-600">{{ t('selectAll') || '全選' }}</span>
              </label>
              <h2 class="text-lg font-medium text-gray-900">{{ t('documents.documentList') }}</h2>
            </div>
            <div class="text-sm text-gray-500">
              {{ selectedDocuments.length > 0 ? `${selectedDocuments.length}/${totalDocuments}` : totalDocuments }} {{ t('documents.totalCount') }}
            </div>
          </div>
        </div>

        <div v-if="loading" class="p-6 text-center">
          <div class="inline-flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ t('documents.loading') }}
          </div>
        </div>

        <div v-else-if="documents.length === 0" class="p-6 text-center text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p>{{ t('documents.noDocuments') }}</p>
          <p class="text-sm mt-1">{{ t('documents.noDocumentsHint') }}</p>
        </div>

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
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <div class="flex-1 min-w-0 cursor-pointer" @click="selectDocument(document)">
                  <div class="flex items-center space-x-3">
                    <h3 class="text-sm font-medium text-gray-900 truncate">
                      {{ document.title }}
                    </h3>
                  <span :class="getSubjectColor(document.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ document.subject }}
                  </span>
                  <span v-if="document.grade" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {{ document.grade }}
                  </span>
                  <span v-if="document.image_filename" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {{ t('documents.withImage') }}
                  </span>
                </div>

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
                  class="text-gray-400 hover:text-blue-600"
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
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
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
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '../composables/useToast.js'
import { usePagination } from '../composables/usePagination.js'
import { useSelection } from '../composables/useSelection.js'
import { useModal } from '../composables/useModal.js'
import { getSubjectColor, formatDate } from '@/utils/formatters.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import documentService from '../api/documentService.js'
import uploadService from '../api/uploadService.js'
import DocumentStatCards from '../components/Documents/DocumentStatCards.vue'
import DocumentUploadModal from '../components/Documents/DocumentUploadModal.vue'
import DocumentDetailModal from '../components/Documents/DocumentDetailModal.vue'

export default {
  name: 'Documents',
  components: {
    DocumentStatCards,
    DocumentUploadModal,
    DocumentDetailModal
  },
  setup() {
    const { t, isEnglish } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    // 響應式資料
    const loading = ref(false)
    const documents = ref([])
    const stats = ref(null)
    const subjects = ref([])
    const detailModalRef = ref(null)

    // 搜尋和篩選
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedGrade = ref('')

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

    // 計算屬性
    const isAllSelected = computed(() => selection.isAllSelected(documents.value))

    // 方法
    const loadDocuments = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          size: pageSize.value
        }

        if (selectedSubject.value) {
          params.subject = selectedSubject.value
        }

        if (selectedGrade.value) {
          params.grade = selectedGrade.value
        }

        if (searchQuery.value) {
          params.search = searchQuery.value
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

    const loadSubjects = async () => {
      try {
        const response = await documentService.getSubjects()
        subjects.value = response.subjects || []
      } catch (error) {
        try {
          const data = await documentService.getDocuments({ size: 1000 })
          const uniqueSubjects = [...new Set(data.documents.map(doc => doc.subject))]
          subjects.value = uniqueSubjects.filter(Boolean)
        } catch (fallbackError) {
        }
      }
    }

    const changePage = (page) => {
      currentPage.value = page
      loadDocuments()
    }

    const searchDocuments = () => {
      currentPage.value = 1
      loadDocuments()
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
        await uploadService.confirmSave(selectedFile.value)
        closeUploadModal()

        await loadDocuments()
        await loadStats()
        await loadSubjects()

        showSuccess(t('documents.uploadSuccess'), '上傳文件')

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
        showSuccess('文件已成功刪除', '刪除文件')

      } catch (error) {

        // 處理引用衝突錯誤 (409)
        if (error.response?.status === 409) {
          const detail = error.response.data.detail
          const references = detail.references

          let message = `文件「${document.title}」正被其他資料引用，無法直接刪除：\n\n`
          if (references.questions > 0) {
            message += `• ${references.questions} 個問題正在使用此文件\n`
          }
          if (references.embeddings > 0) {
            message += `• ${references.embeddings} 個向量嵌入正在使用此文件\n`
          }
          message += `\n是否要強制刪除？這將同時刪除所有相關的問題和嵌入向量，此操作無法撤銷！`

          if (confirm(message)) {
            try {
              await documentService.deleteDocument(document.id, true) // force = true
              await loadDocuments()
              await loadStats()
              showSuccess(
                `文件「${document.title}」已強制刪除，同時刪除了 ${references.questions} 個問題和 ${references.embeddings} 個向量嵌入`,
                '強制刪除文件'
              )
            } catch (forceError) {
              toastError(
                '強制刪除失敗: ' + (forceError.response?.data?.detail || forceError.message),
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
    }

    const toggleSelectAll = () => {
      selection.toggleSelectAll(documents.value)
    }

    const deleteSelectedDocuments = async () => {
      if (selectedDocuments.value.length === 0) {
        toastError(t('documents.noSelection') || '請先選擇要刪除的文件', '批次刪除文件')
        return
      }

      // 檢查是否有文件被引用
      const documentsWithReferences = []
      let totalQuestions = 0
      let totalEmbeddings = 0

      try {
        for (const document of selectedDocuments.value) {
          try {
            const references = await documentService.checkDocumentReferences(document.id)
            if (references.has_references) {
              documentsWithReferences.push({
                document,
                references
              })
              totalQuestions += references.questions
              totalEmbeddings += references.embeddings
            }
          } catch (error) {
          }
        }
      } catch (error) {
      }

      // 根據引用情況顯示不同的確認訊息
      let confirmMessage = ''
      let forceDelete = false

      if (documentsWithReferences.length > 0) {
        confirmMessage = `選中的文件中有 ${documentsWithReferences.length} 個文件被其他資料引用：\n\n`
        confirmMessage += `總共包含 ${totalQuestions} 個問題和 ${totalEmbeddings} 個向量嵌入\n\n`
        confirmMessage += `確定要刪除全部 ${selectedDocuments.value.length} 個文件嗎？`
        confirmMessage += `\n這將同時刪除所有相關的問題和嵌入向量，此操作無法撤銷！`
        forceDelete = true
      } else {
        confirmMessage = `確定要刪除選中的 ${selectedDocuments.value.length} 個文件嗎？此操作無法撤銷！`
      }

      if (!confirm(confirmMessage)) {
        return
      }

      deleting.value = true
      let successCount = 0
      let failedCount = 0
      let deletedQuestions = 0
      let deletedEmbeddings = 0

      try {
        for (const document of selectedDocuments.value) {
          try {
            const result = await documentService.deleteDocument(document.id, forceDelete)
            successCount++
            if (result.deleted_references) {
              deletedQuestions += result.deleted_references.questions || 0
              deletedEmbeddings += result.deleted_references.embeddings || 0
            }
          } catch (error) {
            failedCount++
          }
        }

        selectedDocuments.value = []

        await loadDocuments()
        await loadStats()

        let resultMessage = ''
        if (failedCount === 0) {
          resultMessage = `成功刪除 ${successCount} 個文件`
          if (deletedQuestions > 0 || deletedEmbeddings > 0) {
            resultMessage += `\n同時刪除了 ${deletedQuestions} 個問題和 ${deletedEmbeddings} 個向量嵌入`
          }
        } else {
          resultMessage = `成功刪除 ${successCount} 個文件，${failedCount} 個文件刪除失敗`
        }
        if (successCount > 0) {
          showSuccess(resultMessage, '批次刪除文件')
        } else {
          toastError(resultMessage, '批次刪除文件')
        }

      } catch (error) {
        toastError(t('documents.deleteError') || '批次刪除失敗', '批次刪除文件', error)
      } finally {
        deleting.value = false
      }
    }

    const closeDetailModal = () => {
      detailModal.close()
    }

    // 監聽器
    watch([pageSize, selectedSubject, selectedGrade], () => {
      currentPage.value = 1
      loadDocuments()
    }, { flush: 'post' })

    // 載入資料
    onMounted(async () => {
      await Promise.all([
        loadDocuments(),
        loadStats(),
        loadSubjects()
      ])
    })

    return {
      // 響應式資料
      loading,
      documents,
      stats,
      subjects,
      searchQuery,
      selectedSubject,
      selectedGrade,
      pageSize,
      currentPage,
      totalDocuments,
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

      // 批次選擇
      selectedDocuments,
      deleting,

      // 方法
      loadDocuments,
      searchDocuments,
      changePage,
      toggleDocumentSelection,
      toggleSelectAll,
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
      getSubjectColor,
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
