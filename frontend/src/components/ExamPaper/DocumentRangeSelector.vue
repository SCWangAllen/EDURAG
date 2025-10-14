<template>
  <div class="document-range-selector">
    <h4 class="section-title">📚 文件範圍選擇</h4>

    <!-- 篩選條件 -->
    <div class="filters">
      <div class="filter-group">
        <label class="filter-label">科目</label>
        <select v-model="filters.subject" class="form-select-sm" @change="handleFilterChange">
          <option value="">全部</option>
          <option v-for="subject in availableSubjects" :key="subject" :value="subject">
            {{ subject }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">年級</label>
        <div class="grade-checkboxes">
          <label v-for="grade in grades" :key="grade" class="grade-checkbox">
            <input
              type="checkbox"
              :value="grade"
              v-model="filters.grades"
              @change="handleFilterChange"
            />
            <span>{{ grade }}</span>
          </label>
        </div>
      </div>

      <div class="filter-group flex-grow">
        <label class="filter-label">搜尋</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="搜尋文件標題..."
          class="form-input-sm"
          @input="handleFilterChange"
        />
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="document-list">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>載入文件中...</p>
      </div>

      <div v-else-if="filteredDocuments.length === 0" class="empty-state">
        <p>沒有符合條件的文件</p>
      </div>

      <div v-else class="document-items">
        <div class="select-all-row">
          <label class="checkbox-label">
            <input
              type="checkbox"
              :checked="isAllSelected"
              @change="toggleSelectAll"
            />
            <span>全選 ({{ filteredDocuments.length }} 個文件)</span>
          </label>
        </div>

        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          @click="toggleDocument(doc)"
          :class="['document-item', { selected: isDocumentSelected(doc.id) }]"
        >
          <div class="doc-checkbox">
            <input
              type="checkbox"
              :checked="isDocumentSelected(doc.id)"
              @click.stop="toggleDocument(doc)"
            />
          </div>
          <div class="doc-info">
            <div class="doc-title">{{ doc.title }}</div>
            <div class="doc-meta">
              <span v-if="doc.subject" class="meta-badge subject">{{ doc.subject }}</span>
              <span v-if="doc.grade" class="meta-badge grade">{{ doc.grade }}</span>
              <span v-if="doc.chapter" class="meta-text">{{ doc.chapter }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 已選摘要 -->
    <div class="selection-summary">
      已選擇 <strong>{{ selectedDocuments.length }}</strong> 個文件
      <button
        v-if="selectedDocuments.length > 0"
        @click="clearSelection"
        class="btn-clear-sm"
      >
        清空
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import documentService from '../../api/documentService.js'

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

const emit = defineEmits(['update:modelValue'])

const documents = ref([])
const loading = ref(false)
const filters = ref({
  subject: '',
  grades: [],
  search: ''
})

const selectedDocuments = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const availableSubjects = computed(() => {
  const subjects = new Set()
  documents.value.forEach(doc => {
    if (doc.subject) subjects.add(doc.subject)
  })
  return Array.from(subjects).sort()
})

const grades = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'ALL']

const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 科目篩選
  if (filters.value.subject) {
    filtered = filtered.filter(doc => doc.subject === filters.value.subject)
  }

  // 年級篩選
  if (filters.value.grades.length > 0) {
    filtered = filtered.filter(doc => filters.value.grades.includes(doc.grade))
  }

  // 搜尋篩選
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(query) ||
      (doc.chapter && doc.chapter.toLowerCase().includes(query))
    )
  }

  return filtered
})

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
    const data = await documentService.getDocuments({ size: 100 })
    documents.value = data.documents || []
  } catch (error) {
    console.error('載入文件失敗:', error)
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
  loadDocuments()
})
</script>

<style scoped>
.document-range-selector {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group.flex-grow {
  flex: 1;
  min-width: 200px;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-select-sm,
.form-input-sm {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.form-select-sm:focus,
.form-input-sm:focus {
  outline: none;
  border-color: #3b82f6;
  ring: 2px;
  ring-color: #bfdbfe;
}

.grade-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.grade-checkbox {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.grade-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.document-list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  max-height: 400px;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.document-items {
  display: flex;
  flex-direction: column;
}

.select-all-row {
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 500;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s;
}

.document-item:last-child {
  border-bottom: none;
}

.document-item:hover {
  background: #f9fafb;
}

.document-item.selected {
  background: #eff6ff;
}

.doc-checkbox input[type="checkbox"] {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
  word-wrap: break-word;
}

.doc-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.meta-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.meta-badge.subject {
  background: #dbeafe;
  color: #1e40af;
}

.meta-badge.grade {
  background: #fef3c7;
  color: #92400e;
}

.meta-text {
  color: #6b7280;
}

.selection-summary {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #075985;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-clear-sm {
  padding: 0.25rem 0.75rem;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear-sm:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}
</style>
