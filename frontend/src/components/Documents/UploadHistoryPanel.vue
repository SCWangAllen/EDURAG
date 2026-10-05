<template>
  <!--
    上傳紀錄:每次上傳的 Excel 一列(檔名、時間、文件數),可「檢視這批」(套用篩選)或「刪除這批」。
    預設收合;主篩選列與卡片不再常駐顯示上傳檔案(老師不是每次都要看),要找、要刪才打開這裡。
    與圖片題頁的 Import History 同一套樣式。
  -->
  <div class="bg-white shadow rounded-lg mb-6">
    <button
      type="button"
      class="w-full flex items-center justify-between px-4 py-3 text-left focus:outline-none"
      @click="expanded = !expanded"
    >
      <h3 class="text-sm font-medium text-gray-900">
        {{ t('documents.uploadHistory') }}
        <span v-if="sources.length > 0" class="ml-1 text-gray-400 font-normal">({{ sources.length }})</span>
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
      <div v-if="sources.length === 0" class="px-4 py-6 text-center text-sm text-gray-500">
        {{ t('documents.uploadHistoryEmpty') }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.uploadHistoryFile') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.uploadHistoryDate') }}</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.uploadHistoryCount') }}</th>
              <th class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="s in sources"
              :key="s.source_filename"
              :class="s.source_filename === activeSource ? 'bg-primary-50' : ''"
            >
              <td class="px-3 py-2 text-sm text-gray-900 max-w-[320px] truncate" :title="s.source_filename">{{ s.source_filename }}</td>
              <td class="px-3 py-2 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(s.latest) }}</td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ s.count }}</td>
              <td class="px-3 py-2 text-right whitespace-nowrap">
                <button
                  type="button"
                  class="text-primary-600 hover:text-primary-800 text-sm mr-3"
                  @click="$emit('view-source', s.source_filename)"
                >
                  {{ s.source_filename === activeSource ? t('documents.uploadHistoryViewing') : t('documents.uploadHistoryView') }}
                </button>
                <button
                  type="button"
                  class="text-red-600 hover:text-red-800 text-sm disabled:opacity-50"
                  :disabled="deleting"
                  @click="$emit('delete-source', s.source_filename)"
                >
                  {{ t('documents.uploadHistoryDelete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useLocalStorage } from '@/composables/useLocalStorage.js'

defineProps({
  // [{ source_filename, count, latest }]
  sources: { type: Array, default: () => [] },
  // 目前套用中的上傳檔案篩選
  activeSource: { type: String, default: '' },
  deleting: { type: Boolean, default: false }
})
defineEmits(['view-source', 'delete-source'])

const { t } = useLanguage()
const store = useLocalStorage('edurag:docUploadHistoryExpanded', false)
const expanded = ref(store.load() === true)
watch(expanded, (v) => store.save(v))

const formatDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString()
}
</script>
