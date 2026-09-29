<template>
  <div v-if="!hasError" class="bg-white shadow rounded-lg mb-6">
    <button
      type="button"
      class="w-full flex items-center justify-between px-4 py-3 text-left focus:outline-none"
      @click="expanded = !expanded"
    >
      <h3 class="text-sm font-medium text-gray-900">
        {{ t('imageQuestions.importBatches') }}
        <span v-if="batches.length > 0" class="ml-1 text-gray-400 font-normal">({{ batches.length }})</span>
      </h3>
      <svg
        class="w-5 h-5 text-gray-400 transition-transform duration-150"
        :class="{ '-rotate-180': expanded }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </button>

    <div v-show="expanded" class="border-t border-gray-200">
      <div v-if="loading && batches.length === 0" class="px-4 py-6 text-center text-sm text-gray-500">
        {{ t('imageQuestions.loading') }}
      </div>
      <div v-else-if="batches.length === 0" class="px-4 py-6 text-center text-sm text-gray-500">
        {{ t('imageQuestions.importBatchEmpty') }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.importBatchFile') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.importBatchDate') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.importBatchTotal') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.importBatchVerified') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('imageQuestions.importBatchMissing') }}</th>
              <th class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="batch in batches" :key="batch.batch_id">
              <td class="px-3 py-2 text-sm max-w-[240px] truncate">
                <span v-if="batch.source_filename" class="text-gray-900">{{ batch.source_filename }}</span>
                <span v-else class="text-gray-400">{{ t('imageQuestions.importBatchNoFilename') }}</span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(batch.imported_at) }}</td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ batch.total }}</td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ batch.verified }}</td>
              <td class="px-3 py-2 text-sm" :class="batch.missing > 0 ? 'text-red-600 font-medium' : 'text-gray-900'">
                {{ batch.missing }}
              </td>
              <td class="px-3 py-2 text-right whitespace-nowrap">
                <button
                  type="button"
                  class="text-primary-600 hover:text-primary-800 text-sm mr-3"
                  @click="$emit('view-batch', batch.batch_id)"
                >
                  {{ t('imageQuestions.importBatchView') }}
                </button>
                <button
                  type="button"
                  class="text-red-600 hover:text-red-800 text-sm"
                  @click="openDeleteDialog(batch)"
                >
                  {{ t('imageQuestions.importBatchDelete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <BaseModal v-model="showDeleteModal" :title="t('imageQuestions.importBatchDeleteTitle')" size="sm">
    <div v-if="deletingBatch" class="space-y-3 text-sm text-gray-700">
      <p class="font-medium text-gray-900">
        {{ deletingBatch.source_filename || t('imageQuestions.importBatchNoFilename') }}
      </p>
      <p class="text-gray-500">{{ t('imageQuestions.importBatchDeleteHint') }}</p>
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" v-model="deleteOrphanImages" class="rounded border-gray-300" />
        <span>{{ t('imageQuestions.importBatchDeleteOrphans') }}</span>
      </label>
    </div>
    <template #footer>
      <button
        type="button"
        class="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        @click="showDeleteModal = false"
      >
        {{ t('imageQuestions.cancel') }}
      </button>
      <button
        type="button"
        :disabled="deleting"
        class="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
        @click="confirmDelete"
      >
        {{ t('imageQuestions.importBatchDelete') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useToast } from '@/composables/useToast.js'
import { getImportBatches, deleteImportBatch } from '@/api/imageQuestionService.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'ImportBatchesPanel',
  components: { BaseModal },
  emits: ['view-batch', 'deleted'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()

    const batches = ref([])
    const loading = ref(false)
    const expanded = ref(false)
    const hasError = ref(false)
    let initialized = false
    let errorToasted = false

    const formatDate = (iso) => {
      if (!iso) return '-'
      const d = new Date(iso)
      if (Number.isNaN(d.getTime())) return iso
      return d.toLocaleString()
    }

    // API 尚未部署或暫時出錯時整塊隱藏,只 toast 一次避免每次重載都跳提示
    const fetchBatches = async () => {
      loading.value = true
      try {
        const res = await getImportBatches()
        batches.value = res.data?.batches || []
        hasError.value = false
        if (!initialized) {
          initialized = true
          if (batches.value.length > 0) {
            expanded.value = true
          }
        }
      } catch (error) {
        hasError.value = true
        batches.value = []
        if (!errorToasted) {
          errorToasted = true
          toastError(
            t('imageQuestions.uploadError') + (error.response?.data?.detail || error.message),
            t('imageQuestions.importBatches')
          )
        }
      } finally {
        loading.value = false
      }
    }

    const showDeleteModal = ref(false)
    const deletingBatch = ref(null)
    const deleteOrphanImages = ref(false)
    const deleting = ref(false)

    const openDeleteDialog = (batch) => {
      deletingBatch.value = batch
      deleteOrphanImages.value = false
      showDeleteModal.value = true
    }

    const confirmDelete = async () => {
      if (!deletingBatch.value) return
      const batchId = deletingBatch.value.batch_id
      deleting.value = true
      try {
        const res = await deleteImportBatch(batchId, deleteOrphanImages.value)
        const { deleted_questions, deleted_images, kept_images } = res.data || {}
        showDeleteModal.value = false
        deletingBatch.value = null
        showSuccess(
          t('imageQuestions.batchDeleted')
            .replace('{n}', deleted_questions ?? 0)
            .replace('{m}', (deleted_images || []).length)
            .replace('{k}', kept_images ?? 0),
          t('imageQuestions.importBatches')
        )
        await fetchBatches()
        emit('deleted', batchId)
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message,
          t('imageQuestions.importBatchDeleteTitle')
        )
      } finally {
        deleting.value = false
      }
    }

    fetchBatches()

    return {
      t,
      batches,
      loading,
      expanded,
      hasError,
      formatDate,
      showDeleteModal,
      deletingBatch,
      deleteOrphanImages,
      deleting,
      openDeleteDialog,
      confirmDelete,
      reload: fetchBatches,
    }
  },
}
</script>
