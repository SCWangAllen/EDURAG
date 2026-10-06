<template>
  <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
    <h4 class="text-base font-semibold text-gray-900 mb-4">📚 {{ t('ui.ed_document_range_selection') }}</h4>

    <!-- 篩選條件 -->
    <div class="flex gap-4 mb-4 flex-wrap">
      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-gray-700">{{ t('ui.ed_subject_label') }}</label>
        <SubjectSelect
          v-model="filters.subject"
          :options="availableSubjects"
          :placeholder="t('ui.ed_all_option')"
          @change="handleFilterChange"
        />
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-gray-700">{{ t('ui.ed_grade_label') }}</label>
        <div class="flex flex-wrap gap-3">
          <label v-for="grade in grades" :key="grade" class="flex items-center gap-1 text-sm cursor-pointer">
            <input
              type="checkbox"
              :value="grade"
              v-model="filters.grades"
              @change="handleFilterChange"
              class="cursor-pointer"
            />
            <span>{{ getGradeLabel(grade) }}</span>
          </label>
        </div>
      </div>

      <div class="flex flex-col gap-2 flex-1 min-w-[200px]">
        <label class="text-sm font-medium text-gray-700">{{ t('search') }}</label>
        <input
          v-model="filters.search"
          type="text"
          :placeholder="t('ui.ed_search_doc_title_placeholder')"
          class="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500"
          @input="handleFilterChange"
        />
      </div>

      <!-- 頁碼範圍(課本頁數):與「全選」搭配,填 115–171 再全選就是整個範圍 -->
      <div class="flex flex-col gap-2 min-w-[160px]">
        <label class="text-sm font-medium text-gray-700">{{ t('ui.ed_page_range') }}</label>
        <div class="flex items-center gap-1">
          <input v-model="filters.pageFrom" type="number" min="1" max="1000000" :placeholder="t('documents.pageFrom')" class="w-full min-w-0 px-2 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500" />
          <span class="text-gray-400">–</span>
          <input v-model="filters.pageTo" type="number" min="1" max="1000000" :placeholder="t('documents.pageTo')" class="w-full min-w-0 px-2 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500" />
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="bg-white border border-gray-200 rounded-md max-h-[400px] overflow-y-auto">
      <div v-if="loading" class="p-8 text-center text-gray-500 text-sm">
        <div class="w-8 h-8 border-[3px] border-gray-200 border-t-primary-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p>{{ t('ui.ed_loading_documents') }}</p>
      </div>

      <div v-else-if="filteredDocuments.length === 0" class="p-8 text-center text-gray-500 text-sm">
        <p>{{ t('ui.ed_no_matching_documents') }}</p>
      </div>

      <div v-else class="flex flex-col">
        <div class="px-4 py-3 bg-gray-100 border-b border-gray-200 font-medium">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              :checked="isAllSelected"
              @change="toggleSelectAll"
            />
            <span>{{ t('ui.ed_select_all') }} ({{ filteredDocuments.length }} {{ t('ui.ed_documents_unit') }})</span>
          </label>
        </div>

        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          @click="toggleDocument(doc)"
          class="flex items-center gap-3 px-4 py-3 border-b border-gray-100 last:border-b-0 cursor-pointer transition-colors duration-200"
          :class="isDocumentSelected(doc.id) ? 'bg-primary-50' : 'hover:bg-gray-50'"
        >
          <div>
            <input
              type="checkbox"
              :checked="isDocumentSelected(doc.id)"
              @click.stop="toggleDocument(doc)"
              class="w-[1.125rem] h-[1.125rem] cursor-pointer"
            />
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-900 mb-1 break-words">{{ doc.title }}</div>
            <div class="flex flex-wrap gap-2 text-xs">
              <span v-if="doc.subject" class="px-2 py-0.5 rounded font-medium bg-primary-100 text-primary-800">{{ getDisplayName(doc.subject) }}</span>
              <span v-if="doc.grade" class="px-2 py-0.5 rounded font-medium bg-warning-100 text-amber-800">{{ getGradeLabel(doc.grade) }}</span>
              <span v-if="doc.chapter" class="text-gray-500">{{ doc.chapter }}</span>
              <span v-if="doc.page" class="text-gray-500">{{ formatPage(doc.page) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 已選摘要 -->
    <div class="mt-4 px-4 py-3 bg-sky-100 border border-sky-200 rounded-md text-sm text-sky-800 flex items-center justify-between">
      {{ t('ui.ed_selected_prefix') }} <strong>{{ selectedDocuments.length }}</strong> {{ t('ui.ed_documents_unit') }}
      <button
        v-if="selectedDocuments.length > 0"
        @click="clearSelection"
        class="px-3 py-1 bg-white border border-slate-300 rounded text-xs cursor-pointer transition-all duration-200 hover:bg-slate-50 hover:border-slate-400"
      >
        {{ t('ui.ed_clear_button') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import documentService from '../../api/documentService.js'
import { pageInRange, selectionPageRange, formatPage } from '../../utils/pageRange.js'
import { gradeSortIndex } from '../../constants/grades.js'

const gradeSortIndexCompare = (a, b) => gradeSortIndex(a) - gradeSortIndex(b)
import { useSubjects } from '@/composables/useSubjects.js'
import { useLanguage } from '@/composables/useLanguage.js'
import SubjectSelect from '@/components/Base/SubjectSelect.vue'

const { t } = useLanguage()

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  examInfo: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'scope-range'])

// 科目/年級唯一來源
const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded } = useSubjects()

const documents = ref([])
const loading = ref(false)
const filters = ref({
  subject: '',
  grades: [],
  search: '',
  pageFrom: '',
  pageTo: ''
})

const selectedDocuments = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 逐層限制:科目清單 = 實際有教材的科目;年級清單 = 該科目(沒選就全部)實際有教材的年級。
// 老師亂點不會點出「看起來有、其實是空的」組合
const availableSubjects = computed(() => {
  const names = new Set(documents.value.map(doc => doc.subject).filter(Boolean))
  return Array.from(names).sort()
})
const grades = computed(() => {
  const pool = filters.value.subject
    ? documents.value.filter(doc => doc.subject === filters.value.subject)
    : documents.value
  const set = new Set(pool.map(doc => doc.grade).filter(g => g && g !== 'ALL'))
  return Array.from(set).sort(gradeSortIndexCompare)
})
// 換科目後,已勾但該科目沒有的年級自動取消
watch(() => filters.value.subject, () => {
  const allowed = new Set(grades.value)
  filters.value.grades = filters.value.grades.filter(g => allowed.has(g))
})

const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 科目篩選
  if (filters.value.subject) {
    filtered = filtered.filter(doc => doc.subject === filters.value.subject)
  }

  // 年級篩選（doc.grade === 'ALL' 為全年級通用，任何年級篩選都命中）
  if (filters.value.grades.length > 0) {
    filtered = filtered.filter(doc => doc.grade === 'ALL' || filters.value.grades.includes(doc.grade))
  }

  // 搜尋篩選
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(query) ||
      (doc.chapter && doc.chapter.toLowerCase().includes(query))
    )
  }

  // 頁碼範圍(前端解析;解析不出頁碼的在有範圍時排除)
  if (filters.value.pageFrom || filters.value.pageTo) {
    filtered = filtered.filter(doc => pageInRange(doc.page ?? doc.page_number, filters.value.pageFrom, filters.value.pageTo))
  }

  return filtered
})

// 選到的教材頁碼範圍 → 往上拋,組卷頁拿來自動帶副標「pp. 115–171」
watch(() => props.modelValue, (docs) => {
  emit('scope-range', selectionPageRange(docs))
}, { deep: true })

const isAllSelected = computed(() => {
  if (filteredDocuments.value.length === 0) return false
  return filteredDocuments.value.every(doc => isDocumentSelected(doc.id))
})

const isDocumentSelected = (docId) => {
  return selectedDocuments.value.some(d => d.id === docId)
}

const toggleDocument = (doc) => {
  const index = selectedDocuments.value.findIndex(d => d.id === doc.id)
  if (index > -1) {
    selectedDocuments.value = selectedDocuments.value.filter(d => d.id !== doc.id)
  } else {
    selectedDocuments.value = [...selectedDocuments.value, doc]
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    // 取消全選
    const idsToRemove = new Set(filteredDocuments.value.map(d => d.id))
    selectedDocuments.value = selectedDocuments.value.filter(d => !idsToRemove.has(d.id))
  } else {
    // 全選
    const newDocs = filteredDocuments.value.filter(d => !isDocumentSelected(d.id))
    selectedDocuments.value = [...selectedDocuments.value, ...newDocs]
  }
}

const clearSelection = () => {
  selectedDocuments.value = []
}

const handleFilterChange = () => {
  // 篩選條件變化時不自動清空選擇
  // 使用者可以跨篩選條件選擇文件
}

const loadDocuments = async () => {
  loading.value = true
  try {
    // 不帶 size 回傳全部;fields=light 不帶內文(線上 2,300 筆連內文要抓好幾秒,老師以為壞了),
    // 生成前 GeneratePanel 會依 id 補抓選到那幾筆的內文
    const data = await documentService.getDocuments({ fields: 'light' })
    documents.value = data.documents || []
  } catch (error) {
    documents.value = []
  } finally {
    loading.value = false
  }
}

// 根據考券資訊自動設定篩選條件
watch(() => props.examInfo, (newInfo) => {
  if (newInfo.subject) {
    filters.value.subject = newInfo.subject
  }
  if (newInfo.grade) {
    filters.value.grades = [newInfo.grade]
  }
}, { immediate: true })

onMounted(() => {
  ensureLoaded()
  loadDocuments()
})
</script>
