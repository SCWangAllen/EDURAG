<template>
  <BaseModal
    :model-value="visible"
    size="2xl"
    :title="t('generate.pickerTitle')"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <!-- 篩選列：科目 + 年級 + 上傳來源 + 搜尋 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
        <SubjectSelect
          v-model="subjectFilter"
          :placeholder="t('documents.allSubjects')"
          size="sm"
        />
        <select
          v-model="gradeFilter"
          class="w-full px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
        >
          <option value="">{{ t('documents.allGrades') }}</option>
          <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ getGradeLabel(g.value) }}</option>
        </select>
        <select
          v-model="sourceFilter"
          class="w-full px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
        >
          <option value="">{{ t('documents.allSourceFiles') }}</option>
          <option v-for="s in sources" :key="s.source_filename" :value="s.source_filename">
            {{ s.source_filename }} ({{ s.count }})
          </option>
        </select>
        <input
          v-model="searchInput"
          @keyup.enter="handleSearchEnter"
          @input="handleSearchInput"
          type="text"
          :placeholder="t('generate.searchDocuments')"
          class="w-full px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
        >
        <!-- 頁碼範圍:填 115–171 再按「全選篩選結果」,整個範圍一次選完 -->
        <div class="flex items-center gap-1" :title="t('documents.pageRange')">
          <input v-model="pageFromFilter" type="number" min="1" max="1000000" :placeholder="t('documents.pageFrom')" class="w-full min-w-0 px-2 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:border-primary-500">
          <span class="text-gray-400">–</span>
          <input v-model="pageToFilter" type="number" min="1" max="1000000" :placeholder="t('documents.pageTo')" class="w-full min-w-0 px-2 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:border-primary-500">
        </div>
      </div>

      <!-- 計數 + 全選篩選結果 / 清除全部 -->
      <div class="flex items-center justify-between text-sm">
        <div class="text-gray-600">
          <span class="text-primary-600 font-semibold">{{ total }}</span>
          <span class="text-gray-500"> {{ t('generate.totalDocuments') }}</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="total > 0"
            type="button"
            class="text-xs text-primary-600 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="selectingAll"
            @click="selectAllFiltered"
          >{{ selectAllFilteredLabel }}</button>
          <button
            v-if="selected.length > 0"
            type="button"
            class="text-xs text-gray-500 hover:underline"
            @click="$emit('update:selected', [])"
          >{{ t('generate.clearAllSelected') }}</button>
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="border border-gray-200 rounded-md min-h-[360px] max-h-[420px] overflow-y-auto">
        <div v-if="loading" class="p-8 text-center text-sm text-gray-500">
          {{ t('documents.loading') }}
        </div>
        <EmptyState
          v-else-if="rows.length === 0"
          icon="📄"
          :title="t('generate.pickerEmpty')"
        />
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="doc in rows"
            :key="doc.id"
            @click="toggleDoc(doc)"
            :class="[
              'flex items-center gap-3 p-3 cursor-pointer transition-colors',
              isSelected(doc) ? 'bg-green-50' : 'hover:bg-gray-50'
            ]"
          >
            <input
              type="checkbox"
              :checked="isSelected(doc)"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded flex-shrink-0"
              @click.stop="toggleDoc(doc)"
            >
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ doc.title }}</p>
              <div class="flex items-center gap-2 mt-1 flex-wrap">
                <span v-if="doc.chapter" class="text-xs text-gray-500">{{ doc.chapter }}</span>
                <span v-if="doc.page" class="text-xs text-gray-500">{{ formatPage(doc.page) }}</span>
                <span
                  v-if="doc.subject"
                  :class="subjectBadgeClass(doc.subject)"
                  :style="subjectBadgeStyle(doc.subject)"
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                >{{ getDisplayName(doc.subject) }}</span>
                <span
                  v-if="doc.grade"
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                >{{ getGradeLabel(doc.grade) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-3 text-sm text-gray-600">
        <button
          type="button"
          class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          :disabled="page <= 1"
          @click="changePage(page - 1)"
        >{{ t('documents.previous') }}</button>
        <span>{{ pageOfLabel }}</span>
        <button
          type="button"
          class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          :disabled="page >= totalPages"
          @click="changePage(page + 1)"
        >{{ t('documents.next') }}</button>
      </div>
    </div>

    <template #footer>
      <span class="text-sm text-gray-600 mr-auto self-center">{{ selectedCountLabel }}</span>
      <BaseButton variant="primary" @click="$emit('update:visible', false)">
        {{ t('generate.pickerDone') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { useToast } from '@/composables/useToast.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import documentService from '@/api/documentService.js'
import BaseModal from '@/components/Base/BaseModal.vue'
import BaseButton from '@/components/Base/BaseButton.vue'
import SubjectSelect from '@/components/Base/SubjectSelect.vue'
import { formatPage, normalizeBounds } from '@/utils/pageRange.js'
import EmptyState from '@/components/Base/EmptyState.vue'

const PAGE_SIZE = 20

export default {
  name: 'DocumentPickerModal',
  components: { BaseModal, BaseButton, SubjectSelect, EmptyState },
  props: {
    visible: { type: Boolean, default: false },
    // 目前已選的文件（完整物件，Generate.vue 為唯一來源）
    selected: { type: Array, default: () => [] }
  },
  emits: ['update:visible', 'update:selected'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { getDisplayName, getGradeLabel, subjectBadgeStyle, subjectBadgeClass } = useSubjects()
    const { showError: toastError } = useToast()

    const subjectFilter = ref('')
    const gradeFilter = ref('')
    const sourceFilter = ref('')
    const pageFromFilter = ref('')
    const pageToFilter = ref('')
    const searchInput = ref('')
    const search = ref('')

    const page = ref(1)
    const total = ref(0)
    const rows = ref([])
    const loading = ref(false)
    const selectingAll = ref(false)
    const sources = ref([])
    let sourcesLoaded = false

    const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

    const selectedIds = computed(() => new Set(props.selected.map(d => d.id)))
    const isSelected = (doc) => selectedIds.value.has(doc.id)

    // 依目前篩選條件組請求參數；withPaging=false 用於「全選篩選結果」，不帶 page/size 讓後端回傳全部
    const buildParams = (withPaging) => {
      const params = { sort: 'chapter' }
      if (subjectFilter.value) params.subject = subjectFilter.value
      if (gradeFilter.value) params.grade = gradeFilter.value
      if (sourceFilter.value) params.source_file = sourceFilter.value
      if (search.value) params.search = search.value
      const bounds = normalizeBounds(pageFromFilter.value, pageToFilter.value)
      if (bounds.from) params.page_from = bounds.from
      if (bounds.to) params.page_to = bounds.to
      if (withPaging) {
        params.page = page.value
        params.size = PAGE_SIZE
      }
      return params
    }

    const fetchPage = async () => {
      loading.value = true
      try {
        const data = await documentService.getDocuments(buildParams(true))
        rows.value = data.documents || []
        total.value = data.total || 0
      } catch (error) {
        rows.value = []
        total.value = 0
        toastError(error.response?.data?.detail || error.message, t('generate.pickerTitle'), error)
      } finally {
        loading.value = false
      }
    }

    const loadSources = async () => {
      try {
        const data = await documentService.getDocumentSources()
        sources.value = data.sources || []
        sourcesLoaded = true
      } catch (error) {
        sources.value = []
      }
    }

    const changePage = (target) => {
      if (target < 1 || target > totalPages.value) return
      page.value = target
      fetchPage()
    }

    const toggleDoc = (doc) => {
      const next = isSelected(doc)
        ? props.selected.filter(d => d.id !== doc.id)
        : [...props.selected, doc]
      emit('update:selected', next)
    }

    const selectAllFiltered = async () => {
      selectingAll.value = true
      try {
        const data = await documentService.getDocuments(buildParams(false))
        const fetched = data.documents || []
        const existingIds = selectedIds.value
        const merged = [...props.selected, ...fetched.filter(d => !existingIds.has(d.id))]
        emit('update:selected', merged)
      } catch (error) {
        toastError(error.response?.data?.detail || error.message, t('generate.selectAllFiltered'), error)
      } finally {
        selectingAll.value = false
      }
    }

    // 搜尋：Enter 立即觸發、輸入時 300ms 防抖（與 Templates.vue 的既有模式一致）
    let searchDebounceTimer = null
    const runSearch = () => {
      page.value = 1
      search.value = searchInput.value
      fetchPage()
    }
    const handleSearchEnter = () => {
      if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer)
        searchDebounceTimer = null
      }
      runSearch()
    }
    const handleSearchInput = () => {
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
      searchDebounceTimer = setTimeout(runSearch, 300)
    }

    watch([subjectFilter, gradeFilter, sourceFilter], () => {
      page.value = 1
      fetchPage()
    })
    // 頁碼輸入 300ms 後才查
    let pageRangeTimer = null
    watch([pageFromFilter, pageToFilter], () => {
      if (pageRangeTimer) clearTimeout(pageRangeTimer)
      pageRangeTimer = setTimeout(() => { page.value = 1; fetchPage() }, 300)
    })

    // 每次開啟 modal 時重新載入目前頁（確保資料是最新的）；上傳來源清單只需載入一次
    onUnmounted(() => {
      if (pageRangeTimer) clearTimeout(pageRangeTimer)
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
    })

    watch(() => props.visible, (isVisible) => {
      if (!isVisible) {
        // 關閉時取消還沒送出的搜尋,避免關掉後才打 API
        if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
        searchDebounceTimer = null
        return
      }
      if (!sourcesLoaded) loadSources()
      fetchPage()
    })

    const tr = (key, vars) => {
      let str = t(key)
      Object.entries(vars).forEach(([k, v]) => {
        str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v)
      })
      return str
    }

    const selectedCountLabel = computed(() => tr('generate.pickerSelectedCount', { count: props.selected.length }))
    const selectAllFilteredLabel = computed(() => tr('generate.selectAllFilteredCount', { count: total.value }))
    const pageOfLabel = computed(() => tr('generate.pageOf', { current: page.value, total: totalPages.value }))

    return {
      t,
      getDisplayName,
      getGradeLabel,
      subjectBadgeStyle,
      subjectBadgeClass,
      gradeOptions: GRADE_OPTIONS,

      subjectFilter,
      gradeFilter,
      sourceFilter,
      searchInput,
      sources,

      page,
      total,
      totalPages,
      rows,
      loading,
      selectingAll,

      isSelected,
      toggleDoc,
      selectAllFiltered,
      pageFromFilter,
      pageToFilter,
      formatPage,
      changePage,
      handleSearchEnter,
      handleSearchInput,

      selectedCountLabel,
      selectAllFilteredLabel,
      pageOfLabel
    }
  }
}
</script>
