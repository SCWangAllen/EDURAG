<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 標題和操作按鈕 -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">{{ t('documents.title') }}</h1>
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
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6" v-if="stats">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('documents.totalDocuments') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.total_documents }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('documents.subjectCount') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.subjects || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('documents.withImages') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.has_images }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h2m-2 0v4a2 2 0 002 2h2a2 2 0 002-2v-4m0 0V9a2 2 0 00-2-2h-2m2 4h4"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('documents.chapterCount') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.top_chapters || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜尋和篩選 -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
  <div v-if="showUploadModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal 標題 -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">{{ t('documents.excelPreview') }}</h3>
          <button
            @click="closeUploadModal"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <!-- 預覽內容 -->
        <div v-if="uploadPreview" class="space-y-4">
          <!-- 統計信息 -->
          <div class="bg-blue-50 p-4 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.title') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.subject') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.chapter') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.contentLength') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ t('documents.chunkCount') }}</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="doc in uploadPreview.documents" :key="doc.index" class="hover:bg-gray-50">
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
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- 操作按鈕 -->
          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button
              @click="closeUploadModal"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              {{ t('documents.cancel') }}
            </button>
            <button
              @click="confirmUpload"
              :disabled="uploading"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
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
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 文件詳情/編輯 Modal -->
  <div v-if="showDetailModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal 標題 -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ isEditing ? t('documents.editDocument') : t('documents.documentDetail') }}
          </h3>
          <button
            @click="closeDetailModal"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <!-- 編輯表單 -->
        <div v-if="selectedDocument" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentTitle') }}</label>
              <input
                v-model="editForm.title"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentSubject') }}</label>
              <input
                v-model="editForm.subject"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>
            
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.documentChapter') }}</label>
              <input
                v-model="editForm.chapter"
                :disabled="!isEditing"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
              >
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('documents.content') }}</label>
            <textarea
              v-model="editForm.content"
              :disabled="!isEditing"
              rows="15"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 font-mono text-sm"
            ></textarea>
          </div>
          
          <!-- 操作按鈕 -->
          <div class="flex justify-between pt-4 border-t">
            <div>
              <span class="text-sm text-gray-500">
                {{ t('documents.contentLen') }}: {{ editForm.content.length }} {{ t('documents.characters') }} | 
                {{ t('documents.createdAt') }}: {{ formatDate(selectedDocument.created_at) }}
              </span>
            </div>
            
            <div class="flex space-x-3">
              <button
                @click="closeDetailModal"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                {{ isEditing ? t('documents.cancel') : t('documents.close') }}
              </button>
              
              <button
                v-if="!isEditing"
                @click="startEdit"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm"
              >
                {{ t('documents.startEdit') }}
              </button>
              
              <button
                v-if="isEditing"
                @click="saveEdit"
                :disabled="saving"
                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
              >
                <span v-if="saving" class="inline-flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ t('documents.saving') }}
                </span>
                <span v-else>{{ t('documents.saveChanges') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import documentService from '../api/documentService.js'
import uploadService from '../api/uploadService.js'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'

export default {
  name: 'Documents',
  setup() {
    const { t, isEnglish } = useLanguage()
    
    // 響應式資料
    const loading = ref(false)
    const documents = ref([])
    const stats = ref(null)
    const subjects = ref([])
    
    // 搜尋和篩選
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const pageSize = ref(20)
    const currentPage = ref(1)
    const totalDocuments = ref(0)
    const totalPages = computed(() => Math.ceil(totalDocuments.value / pageSize.value))
    
    // Modal 控制
    const showUploadModal = ref(false)
    const showDetailModal = ref(false)
    const isEditing = ref(false)
    const uploading = ref(false)
    const saving = ref(false)
    
    // 上傳相關
    const uploadPreview = ref(null)
    const selectedFile = ref(null)
    
    // 文件詳情/編輯
    const selectedDocument = ref(null)
    const editForm = reactive({
      title: '',
      content: '',
      subject: '',
      chapter: ''
    })
    
    // 批次選擇相關
    const selectedDocuments = ref([])
    const deleting = ref(false)
    
    // 計算屬性
    const pageNumbers = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })
    
    const isAllSelected = computed(() => {
      return documents.value.length > 0 && selectedDocuments.value.length === documents.value.length
    })
    
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
        
        if (searchQuery.value) {
          params.search = searchQuery.value
        }
        
        const data = await documentService.getDocuments(params)
        documents.value = data.documents || []
        totalDocuments.value = data.total || 0
        
      } catch (error) {
        console.error('Load documents failed:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadStats = async () => {
      try {
        stats.value = await documentService.getDocumentStats()
      } catch (error) {
        console.error('Load statistics failed:', error)
      }
    }
    
    const loadSubjects = async () => {
      try {
        // 從 API 載入科目清單
        const response = await documentService.getSubjects()
        subjects.value = response.subjects || []
      } catch (error) {
        console.error('Load subjects failed:', error)
        // 備用方案：從已載入的文件中提取唯一科目
        try {
          const data = await documentService.getDocuments({ size: 1000 })
          const uniqueSubjects = [...new Set(data.documents.map(doc => doc.subject))]
          subjects.value = uniqueSubjects.filter(Boolean)
        } catch (fallbackError) {
          console.error('Fallback load subjects failed:', fallbackError)
        }
      }
    }
    
    const searchDocuments = () => {
      currentPage.value = 1
      loadDocuments()
    }
    
    const changePage = (page) => {
      currentPage.value = page
      loadDocuments()
    }
    
    // Excel 上傳相關
    const downloadTemplate = async () => {
      try {
        await uploadService.downloadTemplate()
      } catch (error) {
        console.error('Download template failed:', error)
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
        console.error('Upload failed:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('documents.uploadError') + (error.response?.data?.detail || error.message),
          operation: '上傳文件',
          error
        })
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
        
        // 重新載入資料
        await loadDocuments()
        await loadStats()
        await loadSubjects()
        
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('documents.uploadSuccess'),
          operation: '上傳文件'
        })
        
      } catch (error) {
        console.error('確認儲存失敗:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('documents.saveError') + (error.response?.data?.detail || error.message),
          operation: '儲存文件',
          error
        })
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
      selectedDocument.value = document
      editForm.title = document.title
      editForm.content = document.content
      editForm.subject = document.subject
      editForm.chapter = document.chapter || ''
      isEditing.value = false
      showDetailModal.value = true
    }
    
    const editDocument = (document) => {
      selectDocument(document)
      isEditing.value = true
    }
    
    const startEdit = () => {
      isEditing.value = true
    }
    
    const saveEdit = async () => {
      saving.value = true
      try {
        await documentService.updateDocument(selectedDocument.value.id, {
          title: editForm.title,
          content: editForm.content,
          subject: editForm.subject,
          chapter: editForm.chapter
        })
        
        closeDetailModal()
        await loadDocuments()
        
      } catch (error) {
        console.error('儲存失敗:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('documents.saveError') + (error.response?.data?.detail || error.message),
          operation: '儲存文件',
          error
        })
      } finally {
        saving.value = false
      }
    }
    
    const deleteDocument = async (document) => {
      if (!confirm(`${t('documents.deleteConfirm')} ${document.title}?`)) return
      
      try {
        await documentService.deleteDocument(document.id)
        await loadDocuments()
        await loadStats()
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: '文件已成功刪除',
          operation: '刪除文件'
        })
        
      } catch (error) {
        console.error('刪除失敗:', error)
        
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
              eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
                message: `文件「${document.title}」已強制刪除，同時刪除了 ${references.questions} 個問題和 ${references.embeddings} 個向量嵌入`,
                operation: '強制刪除文件'
              })
            } catch (forceError) {
              console.error('強制刪除失敗:', forceError)
              eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
                message: '強制刪除失敗: ' + (forceError.response?.data?.detail || forceError.message),
                operation: '強制刪除文件',
                error: forceError
              })
            }
          }
        } else {
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: t('documents.deleteError') + (error.response?.data?.detail || error.message),
            operation: '刪除文件',
            error
          })
        }
      }
    }
    
    // 批次選擇方法
    const toggleDocumentSelection = (document) => {
      const index = selectedDocuments.value.findIndex(d => d.id === document.id)
      if (index > -1) {
        selectedDocuments.value.splice(index, 1)
      } else {
        selectedDocuments.value.push(document)
      }
    }
    
    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedDocuments.value = []
      } else {
        selectedDocuments.value = [...documents.value]
      }
    }
    
    const deleteSelectedDocuments = async () => {
      if (selectedDocuments.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('documents.noSelection') || '請先選擇要刪除的文件',
          operation: '批次刪除文件'
        })
        return
      }
      
      // 檢查是否有文件被引用
      const documentsWithReferences = []
      let totalQuestions = 0
      let totalEmbeddings = 0
      
      try {
        console.log('檢查選中文件的引用情況...')
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
            console.warn(`檢查文件 ${document.title} 引用失敗:`, error)
          }
        }
      } catch (error) {
        console.error('檢查引用失敗:', error)
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
        // 逐個刪除文件
        for (const document of selectedDocuments.value) {
          try {
            const result = await documentService.deleteDocument(document.id, forceDelete)
            successCount++
            if (result.deleted_references) {
              deletedQuestions += result.deleted_references.questions || 0
              deletedEmbeddings += result.deleted_references.embeddings || 0
            }
          } catch (error) {
            console.error(`刪除文件 ${document.title} 失敗:`, error)
            failedCount++
          }
        }
        
        // 清空選擇
        selectedDocuments.value = []
        
        // 重新加載文件列表和統計
        await loadDocuments()
        await loadStats()
        
        // 顯示結果
        let resultMessage = ''
        if (failedCount === 0) {
          resultMessage = `成功刪除 ${successCount} 個文件`
          if (deletedQuestions > 0 || deletedEmbeddings > 0) {
            resultMessage += `\n同時刪除了 ${deletedQuestions} 個問題和 ${deletedEmbeddings} 個向量嵌入`
          }
        } else {
          resultMessage = `成功刪除 ${successCount} 個文件，${failedCount} 個文件刪除失敗`
        }
        if (batchDeleteResult.value.successCount > 0) {
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: resultMessage,
            operation: '批次刪除文件'
          })
        } else {
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: resultMessage,
            operation: '批次刪除文件'
          })
        }
        
      } catch (error) {
        console.error('批次刪除失敗:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('documents.deleteError') || '批次刪除失敗',
          operation: '批次刪除文件',
          error
        })
      } finally {
        deleting.value = false
      }
    }
    
    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedDocument.value = null
      isEditing.value = false
    }
    
    // 工具方法
    const getSubjectColor = (subject) => {
      const colors = {
        '健康': 'bg-green-100 text-green-800',
        '英文': 'bg-blue-100 text-blue-800',
        '歷史': 'bg-purple-100 text-purple-800',
        'Health': 'bg-green-100 text-green-800',
        'English': 'bg-blue-100 text-blue-800',
        'History': 'bg-purple-100 text-purple-800'
      }
      return colors[subject] || 'bg-gray-100 text-gray-800'
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-TW')
    }
    
    // 監聽器
    watch([pageSize], () => {
      currentPage.value = 1
      loadDocuments()
    })
    
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
      pageSize,
      currentPage,
      totalDocuments,
      totalPages,
      showUploadModal,
      showDetailModal,
      isEditing,
      uploading,
      saving,
      uploadPreview,
      selectedDocument,
      editForm,
      
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
      startEdit,
      saveEdit,
      deleteDocument,
      closeDetailModal,
      getSubjectColor,
      formatDate,
      
      // 語言
      t,
      isEnglish
    }
  }
}
</script>