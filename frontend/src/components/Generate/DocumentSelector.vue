<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Step2. {{ t('generate.selectDocuments').replace('Step2. ', '') }}</h3>

    <!-- 篩選列：科目 + 年級 + 搜尋 同一行 -->
    <div class="flex gap-2 mb-4">
      <select
        v-model="localSubject"
        class="flex-1 min-w-0 px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
      >
        <option value="">{{ t('documents.allSubjects') }}</option>
        <option v-for="subject in documentSubjects" :key="subject" :value="subject">
          {{ isEnglish ? t('subjects.' + getSubjectKey(subject)) : subject }}
        </option>
      </select>
      <select
        v-model="localGrade"
        class="w-24 px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
      >
        <option value="">{{ t('documents.allGrades') }}</option>
        <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
      </select>
      <input
        v-model="localSearch"
        @input="$emit('search-documents')"
        type="text"
        :placeholder="t('generate.searchDocuments')"
        class="flex-1 min-w-0 px-2 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
      >
    </div>

    <!-- 文件計數顯示 -->
    <div class="mb-3 text-sm text-gray-600">
      <span class="text-blue-600 font-semibold">{{ filteredDocuments.length }}</span>
      <span class="text-gray-500"> / {{ documents.length }} {{ t('generate.totalDocuments') }}</span>
    </div>

    <!-- 文件列表：固定高度約 3 個項目 -->
    <div class="space-y-2 h-[210px] overflow-y-auto">
      <div
        v-for="document in filteredDocuments"
        :key="document.id"
        @click="$emit('select-document', document)"
        :class="[
          'cursor-pointer p-3 border rounded-md transition-colors',
          selectedDocuments.some(d => d.id === document.id)
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-900">{{ document.title }}</h3>
            <div class="flex items-center gap-2 mt-1">
              <p class="text-xs text-gray-500">{{ document.chapter }}</p>
              <span v-if="document.page" class="text-xs text-gray-500">• {{ document.page }}</span>
              <span v-if="document.subject" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {{ document.subject }}
              </span>
              <span v-if="document.grade" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                {{ document.grade }}
              </span>
            </div>
          </div>
          <div class="flex-shrink-0">
            <input
              type="checkbox"
              :checked="selectedDocuments.some(d => d.id === document.id)"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              @click.stop="$emit('toggle-document', document)"
            >
          </div>
        </div>
      </div>
    </div>

    <div v-if="documents.length === 0 && !loadingDocuments" class="text-center py-4 text-gray-500">
      <p>{{ t('generate.noDocumentsAvailable') }}</p>
      <button @click="$router.push('/documents')" class="text-blue-600 hover:text-blue-800 text-sm">
        {{ t('generate.goImportDocuments') }}
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'

export default {
  name: 'DocumentSelector',
  props: {
    documents: { type: Array, default: () => [] },
    filteredDocuments: { type: Array, default: () => [] },
    selectedDocuments: { type: Array, default: () => [] },
    documentSubjects: { type: Array, default: () => [] },
    selectedDocumentSubject: { type: String, default: '' },
    selectedDocumentGrade: { type: String, default: '' },
    documentSearchQuery: { type: String, default: '' },
    gradeOptions: { type: Array, default: () => [] },
    loadingDocuments: { type: Boolean, default: false }
  },
  emits: ['update:selectedDocumentSubject', 'update:selectedDocumentGrade', 'update:documentSearchQuery', 'select-document', 'toggle-document', 'search-documents'],
  setup(props, { emit }) {
    const { t, isEnglish } = useLanguage()

    // Helper for subject key translation
    const getSubjectKey = (subjectName) => {
      const mapping = {
        '健康': 'health',
        '英文': 'english',
        '歷史': 'history',
        'Health': 'health',
        'English': 'english',
        'History': 'history'
      }
      return mapping[subjectName] || 'health'
    }

    // Computed for v-model
    const localSubject = computed({
      get: () => props.selectedDocumentSubject,
      set: (val) => emit('update:selectedDocumentSubject', val)
    })
    const localGrade = computed({
      get: () => props.selectedDocumentGrade,
      set: (val) => emit('update:selectedDocumentGrade', val)
    })
    const localSearch = computed({
      get: () => props.documentSearchQuery,
      set: (val) => emit('update:documentSearchQuery', val)
    })

    return { t, isEnglish, getSubjectKey, localSubject, localGrade, localSearch }
  }
}
</script>
