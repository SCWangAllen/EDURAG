<template>
  <BaseModal
    :model-value="visible"
    size="2xl"
    :title="t('documents.excelPreview')"
    @update:model-value="$emit('close')"
  >
    <!-- 預覽內容 -->
    <div v-if="uploadPreview" class="space-y-4">
      <!-- 格式說明 -->
      <div class="bg-gray-50 border border-gray-200 p-4 rounded-lg text-sm">
        <p class="font-medium text-gray-800 mb-1">{{ t('documents.formatGuideTitle') }}</p>
        <p class="text-gray-600">
          <span class="font-medium">{{ t('documents.requiredColumns') }}:</span>
          Words, Chapter, Subject, Imagesrelated
        </p>
        <p class="text-gray-600">
          <span class="font-medium">{{ t('documents.optionalColumns') }}:</span>
          Grade, Page
        </p>
        <ul class="mt-1 text-gray-500 list-disc list-inside space-y-0.5">
          <li>{{ t('documents.ruleWords') }}</li>
          <li>{{ t('documents.ruleSubject') }}</li>
          <li>{{ t('documents.ruleGrade') }}</li>
        </ul>
      </div>

      <!-- 警示摘要 -->
      <div v-if="warningRowCount > 0" class="bg-yellow-50 border border-yellow-200 p-3 rounded-lg text-sm text-yellow-800">
        ⚠️ {{ t('documents.warnRowsSummary').replace('{n}', warningRowCount) }}
      </div>

      <!-- 統計信息 -->
      <div class="bg-blue-50 p-4 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-blue-800 font-medium">{{ uploadPreview.message }}</span>
        </div>
        <div class="mt-2 text-sm text-blue-700">
          {{ t('documents.fileName') }}: {{ uploadPreview.file_name }} |
          {{ t('documents.totalDocs') }}: {{ uploadPreview.total_documents }} {{ t('documents.items') }}
        </div>
      </div>

      <!-- 文件列表預覽 -->
      <div class="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.index') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.excelTitle') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.subject') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.chapter') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.contentLength') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.chunkCount') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.notes') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="doc in uploadPreview.documents"
              :key="doc.index"
              :class="doc.warnings && doc.warnings.length ? 'bg-yellow-50 hover:bg-yellow-100' : 'hover:bg-gray-50'"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ doc.index }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">
                <div class="truncate max-w-xs" :title="doc.title">{{ doc.title }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getSubjectColor(doc.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ doc.subject }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                <div class="truncate max-w-xs" :title="doc.chapter">{{ doc.chapter }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ doc.content_length }} {{ t('documents.characters') }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ doc.chunk_count }} {{ t('documents.chunks') }}</td>
              <td class="px-6 py-4 text-sm">
                <span v-if="!doc.warnings || !doc.warnings.length" class="text-green-600">✓</span>
                <div v-else class="space-y-0.5">
                  <span
                    v-for="code in doc.warnings"
                    :key="code"
                    class="block text-xs text-yellow-800"
                  >⚠️ {{ warningText(code) }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <template v-if="uploadPreview" #footer>
      <button
        @click="$emit('close')"
        class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
      >
        {{ t('documents.cancel') }}
      </button>
      <button
        @click="$emit('confirm')"
        :disabled="uploading"
        class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
      >
        <span v-if="uploading" class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ t('documents.saving') }}
        </span>
        <span v-else>{{ t('documents.confirmSave') }}</span>
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import { getSubjectColor } from '@/utils/formatters.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'DocumentUploadModal',
  components: {
    BaseModal
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    uploadPreview: {
      type: Object,
      default: null
    },
    uploading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'confirm'],
  setup(props) {
    const { t } = useLanguage()

    // 有警示的列數
    const warningRowCount = computed(() =>
      (props.uploadPreview?.documents || []).filter(d => d.warnings && d.warnings.length).length
    )

    // warning 代碼 → i18n 文字
    const warningText = (code) => t(`documents.warn_${code}`)

    return { t, getSubjectColor, warningRowCount, warningText }
  }
}
</script>
