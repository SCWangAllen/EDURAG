<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- 標題和操作按鈕 -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ t('questions.title') }}</h1>
          <p class="mt-1 text-sm text-gray-600">{{ t('questions.subtitle') }}</p>
        </div>
        <div class="flex space-x-3">
          <button
            v-if="selectedQuestions.length > 0"
            @click="exportSelectedQuestions"
            :disabled="exporting"
            class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
          >
            <svg v-if="exporting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
            </svg>
            {{ exporting ? t('questions.exporting') : t('questions.exportSelected') }} ({{ selectedQuestions.length }})
          </button>
          
          <button
            @click="exportQuestions"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
            </svg>
            {{ t('questions.export') }}
          </button>
        </div>
      </div>

      <!-- 統計卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6" v-if="stats">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.totalQuestions') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.total_questions }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h2m-2 0v4a2 2 0 002 2h2a2 2 0 002-2v-4m0 0V9a2 2 0 00-2-2h-2m2 4h4"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.byType') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_type || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.bySubject') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_subject || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('questions.byDifficulty') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ Object.keys(stats.by_difficulty || {}).length }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜尋和篩選 -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.search') }}</label>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('questions.searchPlaceholder')"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterByType') }}</label>
            <select
              v-model="selectedType"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ t('questions.allTypes') }}</option>
              <option value="single_choice">{{ t('questions.single_choice') }}</option>
              <option value="cloze">{{ t('questions.cloze') }}</option>
              <option value="short_answer">{{ t('questions.short_answer') }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterBySubject') }}</label>
            <select
              v-model="selectedSubject"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ t('questions.allSubjects') }}</option>
              <option v-for="subject in subjects" :key="subject" :value="subject">
                {{ subject }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterByDifficulty') }}</label>
            <select
              v-model="selectedDifficulty"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ t('questions.allDifficulties') }}</option>
              <option value="easy">{{ t('questions.easy') }}</option>
              <option value="medium">{{ t('questions.medium') }}</option>
              <option value="hard">{{ t('questions.hard') }}</option>
            </select>
          </div>
          
          <div class="flex items-end">
            <button
              @click="searchQuestions"
              class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
            >
              {{ t('questions.search') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 問題列表 -->
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
              <h2 class="text-lg font-medium text-gray-900">{{ t('questions.questionList') }}</h2>
            </div>
            <div class="text-sm text-gray-500">
              {{ selectedQuestions.length > 0 ? `${selectedQuestions.length}/${totalQuestions}` : totalQuestions }} {{ t('questions.results') }}
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="p-6 text-center">
          <div class="inline-flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ t('questions.loading') }}
          </div>
        </div>
        
        <div v-else-if="questions.length === 0" class="p-6 text-center text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p>{{ t('questions.noQuestions') }}</p>
          <p class="text-sm mt-1">{{ t('questions.noQuestionsHint') }}</p>
        </div>
        
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="question in questions"
            :key="question.id"
            class="p-6 hover:bg-gray-50"
            :class="{ 'bg-blue-50 border-l-4 border-blue-500': selectedQuestions.some(q => q.id === question.id) }"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-3">
                <input
                  type="checkbox"
                  :checked="selectedQuestions.some(q => q.id === question.id)"
                  @change="toggleQuestionSelection(question)"
                  @click.stop
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <div class="flex-1 min-w-0 cursor-pointer" @click="selectQuestion(question)">
                  <div class="flex items-center space-x-3">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {{ getTypeLabel(question.type) }}
                    </span>
                  <span v-if="question.subject" :class="getSubjectColor(question.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ question.subject }}
                  </span>
                  <span :class="getDifficultyColor(question.difficulty)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ getDifficultyLabel(question.difficulty) }}
                  </span>
                </div>
                
                <div class="mt-2">
                  <h3 class="text-sm font-medium text-gray-900 line-clamp-2">
                    {{ question.content }}
                  </h3>
                </div>
                
                  <div class="mt-2 text-sm text-gray-500">
                    <span v-if="question.chapter">{{ question.chapter }} • </span>
                    {{ formatDate(question.created_at) }}
                  </div>
                </div>
              </div>
              
              <div class="flex items-center space-x-2 ml-4">
                <button
                  @click.stop="viewQuestion(question)"
                  class="text-gray-400 hover:text-blue-600"
                  :title="t('questions.view')"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
                <button
                  @click.stop="editQuestion(question)"
                  class="text-gray-400 hover:text-green-600"
                  :title="t('questions.edit')"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click.stop="deleteQuestion(question)"
                  class="text-gray-400 hover:text-red-600"
                  :title="t('questions.delete')"
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
              {{ t('questions.previous') }}
            </button>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              {{ t('questions.next') }}
            </button>
          </div>
          
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                {{ t('questions.showing') }} <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
                {{ t('questions.to') }} <span class="font-medium">{{ Math.min(currentPage * pageSize, totalQuestions) }}</span>
                {{ t('questions.of') }} <span class="font-medium">{{ totalQuestions }}</span> {{ t('questions.results') }}
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

  <!-- 問題詳情 Modal -->
  <div v-if="showDetailModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-4xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">{{ t('questions.questionDetail') }}</h3>
            <button
              @click="closeDetailModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div v-if="selectedQuestion" class="p-6">
          <div class="space-y-6">
            <!-- 問題內容 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }}</label>
              <div class="p-4 bg-gray-50 rounded-md">
                {{ selectedQuestion.content }}
              </div>
            </div>

            <!-- 選項（如果是單選題） -->
            <div v-if="selectedQuestion.type === 'single_choice' && selectedQuestion.options">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.options') }}</label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in selectedQuestion.options"
                  :key="index"
                  class="flex items-center p-3 bg-gray-50 rounded-md"
                >
                  <span class="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    {{ String.fromCharCode(65 + index) }}
                  </span>
                  <span>{{ option }}</span>
                </div>
              </div>
            </div>

            <!-- 正確答案 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }}</label>
              <div class="p-4 bg-green-50 border border-green-200 rounded-md">
                {{ selectedQuestion.correct_answer }}
              </div>
            </div>

            <!-- 解釋 -->
            <div v-if="selectedQuestion.explanation">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <div class="p-4 bg-blue-50 border border-blue-200 rounded-md">
                {{ selectedQuestion.explanation }}
              </div>
            </div>

            <!-- 其他資訊 -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.type') }}</label>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ getTypeLabel(selectedQuestion.type) }}
                </span>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.difficulty') }}</label>
                <span :class="getDifficultyColor(selectedQuestion.difficulty)" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium">
                  {{ getDifficultyLabel(selectedQuestion.difficulty) }}
                </span>
              </div>
              
              <div v-if="selectedQuestion.subject">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.subject') }}</label>
                <span>{{ selectedQuestion.subject }}</span>
              </div>
              
              <div v-if="selectedQuestion.chapter">
                <label class="block text-sm font-medium text-gray-700">{{ t('questions.chapter') }}</label>
                <span>{{ selectedQuestion.chapter }}</span>
              </div>
            </div>

            <!-- 來源內容 -->
            <div v-if="selectedQuestion.source_content">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.sourceContent') }}</label>
              <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-md max-h-40 overflow-y-auto">
                {{ selectedQuestion.source_content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 編輯問題 Modal -->
  <div v-if="showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-4xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">{{ t('questions.editQuestion') }}</h3>
            <button
              @click="closeEditModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6">
          <div class="space-y-6">
            <!-- 問題類型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.type') }} *</label>
              <select
                v-model="editForm.type"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="single_choice">{{ t('questions.single_choice') }}</option>
                <option value="cloze">{{ t('questions.cloze') }}</option>
                <option value="short_answer">{{ t('questions.short_answer') }}</option>
              </select>
            </div>

            <!-- 問題內容 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }} *</label>
              <textarea
                v-model="editForm.content"
                rows="4"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.contentPlaceholder')"
              ></textarea>
            </div>

            <!-- 選項（單選題用） -->
            <div v-if="editForm.type === 'single_choice'">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.options') }} *</label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in editForm.options"
                  :key="index"
                  class="flex items-center space-x-2"
                >
                  <span class="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                    {{ String.fromCharCode(65 + index) }}
                  </span>
                  <input
                    v-model="editForm.options[index]"
                    type="text"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    :placeholder="t('questions.optionPlaceholder') + ' ' + String.fromCharCode(65 + index)"
                  >
                  <button
                    v-if="editForm.options.length > 2"
                    @click="removeOption(index)"
                    class="text-red-600 hover:text-red-800"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
                <button
                  v-if="editForm.options.length < 8"
                  @click="addOption"
                  class="flex items-center px-3 py-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                  {{ t('questions.addOption') }}
                </button>
              </div>
            </div>

            <!-- 正確答案 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }} *</label>
              <input
                v-model="editForm.correct_answer"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.answerPlaceholder')"
              >
            </div>

            <!-- 解釋 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <textarea
                v-model="editForm.explanation"
                rows="3"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.explanationPlaceholder')"
              ></textarea>
            </div>

            <!-- 其他資訊 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.subject') }}</label>
                <input
                  v-model="editForm.subject"
                  type="text"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  :placeholder="t('questions.subjectPlaceholder')"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.chapter') }}</label>
                <input
                  v-model="editForm.chapter"
                  type="text"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  :placeholder="t('questions.chapterPlaceholder')"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.difficulty') }}</label>
                <select
                  v-model="editForm.difficulty"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="easy">{{ t('questions.easy') }}</option>
                  <option value="medium">{{ t('questions.medium') }}</option>
                  <option value="hard">{{ t('questions.hard') }}</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button
              @click="closeEditModal"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              {{ t('cancel') }}
            </button>
            <button
              @click="saveQuestion"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm"
            >
              {{ t('questions.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 匯出 Modal -->
  <div v-if="showExportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">{{ t('questions.exportTitle') }}</h3>
          <button
            @click="closeExportModal"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="p-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.exportFormat') }}</label>
            <select
              v-model="exportFormat"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="xlsx">Excel</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.exportFilters') }}</label>
            <div class="space-y-3">
              <select
                v-model="exportFilters.subject"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('questions.allSubjects') }}</option>
                <option v-for="subject in subjects" :key="subject" :value="subject">
                  {{ subject }}
                </option>
              </select>
              
              <select
                v-model="exportFilters.question_type"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('questions.allTypes') }}</option>
                <option value="single_choice">{{ t('questions.single_choice') }}</option>
                <option value="cloze">{{ t('questions.cloze') }}</option>
                <option value="short_answer">{{ t('questions.short_answer') }}</option>
              </select>
              
              <select
                v-model="exportFilters.difficulty"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('questions.allDifficulties') }}</option>
                <option value="easy">{{ t('questions.easy') }}</option>
                <option value="medium">{{ t('questions.medium') }}</option>
                <option value="hard">{{ t('questions.hard') }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="closeExportModal"
            class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            {{ t('cancel') }}
          </button>
          <button
            @click="confirmExport"
            :disabled="exporting"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
          >
            <span v-if="exporting" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ t('questions.exporting') }}
            </span>
            <span v-else>{{ t('questions.confirmExport') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { getQuestions, deleteQuestion as deleteQuestionAPI, getQuestionStats, exportQuestions as exportQuestionsAPI } from '../api/questionService.js'

export default {
  name: 'Questions',
  setup() {
    const { t, isEnglish } = useLanguage()
    
    // 響應式資料
    const loading = ref(false)
    const questions = ref([])
    const stats = ref(null)
    const subjects = ref([])
    
    // 搜尋和篩選
    const searchQuery = ref('')
    const selectedType = ref('')
    const selectedSubject = ref('')
    const selectedDifficulty = ref('')
    const pageSize = ref(20)
    
    // 分頁
    const currentPage = ref(1)
    const totalQuestions = ref(0)
    const totalPages = ref(0)
    
    // Modal 控制
    const showDetailModal = ref(false)
    const showExportModal = ref(false)
    const showEditModal = ref(false)
    const selectedQuestion = ref(null)
    
    // 批次選擇相關
    const selectedQuestions = ref([])
    const exporting = ref(false)
    
    // 編輯相關
    const editingQuestion = ref(null)
    const editForm = reactive({
      type: '',
      content: '',
      options: [],
      correct_answer: '',
      explanation: '',
      subject: '',
      chapter: '',
      difficulty: 'medium'
    })
    
    // 匯出相關
    const exportFormat = ref('json')
    const exportFilters = reactive({
      subject: '',
      question_type: '',
      difficulty: ''
    })

    // 計算屬性
    const pageNumbers = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    const isAllSelected = computed(() => {
      return questions.value.length > 0 && selectedQuestions.value.length === questions.value.length
    })

    // 方法
    const loadQuestions = async () => {
      try {
        loading.value = true
        console.log('🔄 開始載入問題列表...')
        
        const params = {
          page: currentPage.value,
          size: pageSize.value
        }
        
        if (searchQuery.value) params.search = searchQuery.value
        if (selectedType.value) params.question_type = selectedType.value
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value

        console.log('📤 API 請求參數:', params)
        
        const response = await getQuestions(params)
        console.log('📥 API 原始回應:', response)
        
        questions.value = response.data.questions || []
        totalQuestions.value = response.data.total || 0
        totalPages.value = response.data.pages || 0
        
        console.log('✅ Questions loaded successfully:', {
          questions: questions.value.length,
          total: totalQuestions.value,
          pages: totalPages.value
        })
        
        if (questions.value.length === 0) {
          console.warn('⚠️  沒有找到問題資料！')
        }
      } catch (error) {
        console.error('❌ Load questions failed:', error)
        if (error.response) {
          console.error('📋 Error response:', error.response.data)
          console.error('📋 Error status:', error.response.status)
        } else if (error.request) {
          console.error('🌐 Network error:', error.request)
          alert('網路連線錯誤：無法連接到後端服務，請確認後端是否在運行。')
        } else {
          console.error('🔧 Request setup error:', error.message)
        }
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        console.log('🔄 開始載入統計資料...')
        const response = await getQuestionStats()
        console.log('📥 統計 API 原始回應:', response)
        
        stats.value = response.data
        
        // 提取科目清單
        if (stats.value && stats.value.by_subject) {
          subjects.value = Object.keys(stats.value.by_subject).filter(Boolean)
        }
        
        console.log('✅ Question stats loaded:', stats.value)
        console.log('📚 提取的科目清單:', subjects.value)
      } catch (error) {
        console.error('❌ Load question stats failed:', error)
        if (error.response) {
          console.error('📋 Stats error response:', error.response.data)
        } else if (error.request) {
          console.error('🌐 Stats network error:', error.request)
        }
      }
    }

    const searchQuestions = () => {
      currentPage.value = 1
      loadQuestions()
    }

    const changePage = (page) => {
      currentPage.value = page
      loadQuestions()
    }

    // 問題操作相關
    const selectQuestion = (question) => {
      selectedQuestion.value = question
      showDetailModal.value = true
    }

    const viewQuestion = (question) => {
      selectQuestion(question)
    }

    const editQuestion = (question) => {
      console.log('🔧 開始編輯問題:', question)
      editingQuestion.value = { ...question }
      
      // 填入編輯表單
      editForm.type = question.type || ''
      editForm.content = question.content || ''
      editForm.options = question.options ? [...question.options] : []
      editForm.correct_answer = question.correct_answer || ''
      editForm.explanation = question.explanation || ''
      editForm.subject = question.subject || ''
      editForm.chapter = question.chapter || ''
      editForm.difficulty = question.difficulty || 'medium'
      
      // 如果是單選題但沒有選項，建立預設選項
      if (editForm.type === 'single_choice' && editForm.options.length === 0) {
        editForm.options = ['', '', '', '']
      }
      
      showEditModal.value = true
    }

    const deleteQuestion = async (question) => {
      if (!confirm(t('questions.deleteConfirm'))) return
      
      try {
        await deleteQuestionAPI(question.id)
        await loadQuestions()
        await loadStats()
        alert(t('questions.deleteSuccess'))
      } catch (error) {
        console.error('Delete question failed:', error)
        alert(t('questions.deleteError') + (error.response?.data?.detail || error.message))
      }
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedQuestion.value = null
    }

    const closeEditModal = () => {
      showEditModal.value = false
      editingQuestion.value = null
      // 重置編輯表單
      Object.keys(editForm).forEach(key => {
        if (key === 'options') {
          editForm[key] = []
        } else if (key === 'difficulty') {
          editForm[key] = 'medium'
        } else {
          editForm[key] = ''
        }
      })
    }

    const saveQuestion = async () => {
      try {
        // 驗證必填欄位
        if (!editForm.content.trim()) {
          alert(t('questions.contentRequired'))
          return
        }
        if (!editForm.correct_answer.trim()) {
          alert(t('questions.answerRequired'))
          return
        }

        // 如果是單選題，驗證選項
        if (editForm.type === 'single_choice') {
          const validOptions = editForm.options.filter(opt => opt.trim())
          if (validOptions.length < 2) {
            alert(t('questions.optionsRequired'))
            return
          }
          editForm.options = validOptions
        }

        console.log('💾 儲存編輯的問題:', editForm)
        
        // 呼叫 API 更新問題
        const { updateQuestion } = await import('../api/questionService.js')
        await updateQuestion(editingQuestion.value.id, editForm)
        
        closeEditModal()
        await loadQuestions()
        await loadStats()
        alert(t('questions.updateSuccess'))
      } catch (error) {
        console.error('Save question failed:', error)
        alert(t('questions.updateError') + (error.response?.data?.detail || error.message))
      }
    }

    const addOption = () => {
      editForm.options.push('')
    }

    const removeOption = (index) => {
      if (editForm.options.length > 2) {
        editForm.options.splice(index, 1)
      }
    }

    // 匯出相關
    const exportQuestions = () => {
      showExportModal.value = true
    }

    const closeExportModal = () => {
      showExportModal.value = false
      exportFormat.value = 'json'
      exportFilters.subject = ''
      exportFilters.question_type = ''
      exportFilters.difficulty = ''
    }

    const confirmExport = async () => {
      try {
        exporting.value = true
        await exportQuestionsAPI({
          format: exportFormat.value,
          subject: exportFilters.subject || null,
          question_type: exportFilters.question_type || null,
          difficulty: exportFilters.difficulty || null
        })
        
        closeExportModal()
        alert(t('questions.exportSuccess'))
      } catch (error) {
        console.error('Export questions failed:', error)
        alert(t('questions.exportError') + (error.response?.data?.detail || error.message))
      } finally {
        exporting.value = false
      }
    }

    // 批次選擇相關方法
    const toggleQuestionSelection = (question) => {
      const index = selectedQuestions.value.findIndex(q => q.id === question.id)
      if (index > -1) {
        selectedQuestions.value.splice(index, 1)
      } else {
        selectedQuestions.value.push(question)
      }
    }

    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedQuestions.value = []
      } else {
        selectedQuestions.value = [...questions.value]
      }
    }

    const exportSelectedQuestions = async () => {
      if (selectedQuestions.value.length === 0) {
        alert('請先選擇要匯出的問題')
        return
      }

      try {
        exporting.value = true
        
        // 準備匯出資料
        const exportData = selectedQuestions.value.map(q => ({
          id: q.id,
          type: q.type,
          content: q.content,
          options: q.options,
          correct_answer: q.correct_answer,
          explanation: q.explanation,
          subject: q.subject,
          chapter: q.chapter,
          difficulty: q.difficulty,
          created_at: q.created_at
        }))

        // 建立檔案並下載
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
          type: 'application/json' 
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `questions_selected_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        // 清除選擇
        selectedQuestions.value = []
        
        alert(`已匯出 ${exportData.length} 道選中的題目`)
      } catch (error) {
        console.error('Export selected questions failed:', error)
        alert('匯出失敗: ' + error.message)
      } finally {
        exporting.value = false
      }
    }

    // 工具方法
    const getTypeLabel = (type) => {
      const typeMap = {
        'single_choice': t('questions.single_choice'),
        'cloze': t('questions.cloze'),
        'short_answer': t('questions.short_answer')
      }
      return typeMap[type] || type
    }

    const getDifficultyLabel = (difficulty) => {
      const difficultyMap = {
        'easy': t('questions.easy'),
        'medium': t('questions.medium'),
        'hard': t('questions.hard')
      }
      return difficultyMap[difficulty] || difficulty
    }

    const getDifficultyColor = (difficulty) => {
      const colorMap = {
        'easy': 'bg-green-100 text-green-800',
        'medium': 'bg-yellow-100 text-yellow-800',
        'hard': 'bg-red-100 text-red-800'
      }
      return colorMap[difficulty] || 'bg-gray-100 text-gray-800'
    }

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
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    // 監聽器
    watch([selectedType, selectedSubject, selectedDifficulty], () => {
      currentPage.value = 1
      loadQuestions()
    })

    // 載入資料
    onMounted(async () => {
      await Promise.all([
        loadQuestions(),
        loadStats()
      ])
    })

    return {
      // 語言
      t,
      isEnglish,
      
      // 資料
      loading,
      questions,
      stats,
      subjects,
      
      // 搜尋和篩選
      searchQuery,
      selectedType,
      selectedSubject,
      selectedDifficulty,
      pageSize,
      
      // 分頁
      currentPage,
      totalQuestions,
      totalPages,
      pageNumbers,
      
      // Modal
      showDetailModal,
      showExportModal,
      showEditModal,
      selectedQuestion,
      editingQuestion,
      editForm,
      
      // 匯出
      exporting,
      exportFormat,
      exportFilters,
      
      // 方法
      searchQuestions,
      changePage,
      selectQuestion,
      viewQuestion,
      editQuestion,
      deleteQuestion,
      closeDetailModal,
      closeEditModal,
      saveQuestion,
      addOption,
      removeOption,
      exportQuestions,
      closeExportModal,
      confirmExport,
      
      // 批次選擇
      selectedQuestions,
      exporting,
      isAllSelected,
      toggleQuestionSelection,
      toggleSelectAll,
      exportSelectedQuestions,
      
      // 工具方法
      getTypeLabel,
      getDifficultyLabel,
      getDifficultyColor,
      getSubjectColor,
      formatDate
    }
  }
}
</script>