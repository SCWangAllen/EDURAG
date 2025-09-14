<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <!-- Title and Action Buttons -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ t('questions.title') }}</h1>
          <p class="mt-1 text-sm text-gray-600">{{ t('questions.subtitle') }}</p>
        </div>
        <div class="flex space-x-3">
          <div v-if="selectedQuestions.length > 0" class="flex space-x-2">
            <button
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
              JSON ({{ selectedQuestions.length }})
            </button>
            
            <div class="relative inline-block">
              <button
                @click="showSelectedExportMenu = !showSelectedExportMenu"
                :disabled="exporting || selectedQuestions.length === 0"
                class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm disabled:opacity-50"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
📝 {{ t('questions.examPaper') }} ({{ selectedQuestions.length }})
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              
              <!-- Selected Questions Export Options Dropdown -->
              <div v-if="showSelectedExportMenu" class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div class="py-2">
                  <button
                    @click="openExamDesigner"
                    class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"></path>
                    </svg>
🎨 {{ t('questions.customExamEditor') }}
                  </button>
                </div>
              </div>
              
              <!-- Click Outside to Close Dropdown -->
              <div v-if="showSelectedExportMenu" @click="showSelectedExportMenu = false" class="fixed inset-0 z-40"></div>
            </div>
          </div>
          
          <!-- Removed old export feature, now using custom exam editor -->
        </div>
      </div>

      <!-- Statistics Cards -->
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

      <!-- Search and Filter -->
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
              <option value="single_choice">{{ t('questions.single_choice') || '單選題' }}</option>
              <option value="cloze">{{ t('questions.cloze') || '填空題' }}</option>
              <option value="short_answer">{{ t('questions.short_answer') || '簡答題' }}</option>
              <option value="true_false">{{ t('questions.true_false') || '是非題' }}</option>
              <option value="matching">{{ t('questions.matching') || '配對題' }}</option>
              <option value="sequence">{{ t('questions.sequence') || '順序題' }}</option>
              <option value="enumeration">{{ t('questions.enumeration') || '列舉題' }}</option>
              <option value="symbol_identification">{{ t('questions.symbol_identification') || '符號辨識題' }}</option>
              <option value="mixed">{{ t('questions.mixed') || '混合題型' }}</option>
              <option value="auto">{{ t('questions.auto') || '自動題型' }}</option>
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

      <!-- Question List -->
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
                <span class="ml-2 text-sm text-gray-600">{{ t('questions.selectAll') }}</span>
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
        
        <!-- Pagination -->
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

  <!-- Selected Questions Style Editor Modal -->
  <div v-if="showSelectedExportStyleModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="relative max-w-5xl w-full max-h-screen overflow-auto">
      <div class="bg-white rounded-lg shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
🎨 {{ t('questions.selectedQuestionsStyleEditor') }} ({{ selectedQuestions.length }} {{ t('questions.selectedQuestions') }})
            </h3>
            <button
              @click="closeSelectedExportStyleModal"
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
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-sm font-medium text-gray-900">{{ t('questions.customStyleSettings') }}</h4>
              <button
                @click="showExamStyleEditor = !showExamStyleEditor"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                {{ showExamStyleEditor ? t('questions.hideEditor') : t('questions.showEditor') }}
              </button>
            </div>

            <!-- Style Editor -->
            <div v-if="showExamStyleEditor" class="space-y-4 max-h-96 overflow-y-auto">
              

              <!-- Export Options -->
              <div class="bg-blue-50 p-4 rounded border">
                <h5 class="font-medium text-blue-800 mb-3">📦 {{ t('questions.exportContentSelection') }}</h5>
                <div class="flex gap-4">
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.questionsOnly"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.answerSheetOnly = false; examStyles.exportOptions.completeExam = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📝 {{ t('questions.questionsOnly') }}</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.answerSheetOnly"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.questionsOnly = false; examStyles.exportOptions.completeExam = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📋 {{ t('questions.answerSheetOnly') }}</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.exportOptions.completeExam"
                      type="radio"
                      name="exportType"
                      @change="examStyles.exportOptions.questionsOnly = false; examStyles.exportOptions.answerSheetOnly = false"
                      class="mr-2"
                    />
                    <span class="text-sm">📚 {{ t('questions.completeExam') }}</span>
                  </label>
                </div>
              </div>

              <!-- Exam Header Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <div class="flex items-center justify-between mb-3">
                  <h5 class="font-medium text-gray-800">📋 {{ t('questions.examHeaderSettings') }}</h5>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.header.enabled"
                      type="checkbox"
                      class="mr-2"
                    />
                    <span class="text-sm text-gray-600">{{ t('questions.enable') }}</span>
                  </label>
                </div>
                <div v-if="examStyles.header.enabled" class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.titlePrefix') }}</label>
                    <input
                      v-model="examStyles.header.titlePrefix"
                      :placeholder="t('questions.examinationExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.subtitle') }}</label>
                    <input
                      v-model="examStyles.header.subtitle"
                      :placeholder="t('questions.finalExamExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.timeLimit') }}</label>
                    <input
                      v-model="examStyles.header.duration"
                      :placeholder="t('questions.ninetyMinutesExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.totalScore') }}</label>
                    <input
                      v-model="examStyles.header.totalScore"
                      :placeholder="t('questions.hundredPointsExample')"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                </div>
              </div>

              <!-- Question Section Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <h5 class="font-medium text-gray-800 mb-3">📝 {{ t('questions.questionSectionSettings') }}</h5>
                <div class="space-y-3">
                  
                  <!-- Multiple Choice Settings -->
                  <div class="border border-blue-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-blue-700">Multiple Choice Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.singleChoice.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.singleChoice.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.singleChoice.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.singleChoice.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Fill-in-the-Blank Settings -->
                  <div class="border border-green-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-green-700">Fill-in-the-Blank Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.cloze.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.cloze.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.cloze.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.cloze.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Short Answer Settings -->
                  <div class="border border-yellow-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-yellow-700">Short Answer Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.shortAnswer.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.shortAnswer.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.shortAnswer.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.shortAnswer.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <!-- Auto Question Settings -->
                  <div class="border border-purple-200 rounded p-3 bg-white">
                    <div class="flex items-center justify-between mb-2">
                      <h6 class="font-medium text-purple-700">Auto Questions</h6>
                      <label class="flex items-center">
                        <input
                          v-model="examStyles.sections.auto.enabled"
                          type="checkbox"
                          class="mr-2"
                        />
                        <span class="text-sm text-gray-600">{{ t('questions.includeThisType') }}</span>
                      </label>
                    </div>
                    <div v-if="examStyles.sections.auto.enabled" class="grid grid-cols-2 gap-2">
                      <input
                        v-model="examStyles.sections.auto.title"
                        placeholder="{{ t('questions.sectionTitle') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        v-model="examStyles.sections.auto.pointsPerQuestion"
                        type="number"
                        placeholder="{{ t('questions.pointsPerQuestion') }}"
                        class="px-3 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                </div>
              </div>

              <!-- Answer Sheet Settings -->
              <div class="bg-gray-50 p-4 rounded border">
                <div class="flex items-center justify-between mb-3">
                  <h5 class="font-medium text-gray-800">📋 {{ t('questions.answerSheetSettings') }}</h5>
                  <label class="flex items-center">
                    <input
                      v-model="examStyles.answerSheet.enabled"
                      type="checkbox"
                      class="mr-2"
                    />
                    <span class="text-sm text-gray-600">{{ t('questions.enable') }} {{ t('questions.answerSheet') }}</span>
                  </label>
                </div>
                <div v-if="examStyles.answerSheet.enabled" class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.answerSheetFormat') }}</label>
                    <select
                      v-model="examStyles.answerSheet.format"
                      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    >
                      <option value="table">{{ t('questions.tableFormat') }}</option>
                      <option value="list">{{ t('questions.listFormat') }}</option>
                      <option value="grid">{{ t('questions.gridFormat') }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm text-gray-600 mb-1">{{ t('questions.includeExplanation') }}</label>
                    <label class="flex items-center mt-1">
                      <input
                        v-model="examStyles.answerSheet.includeExplanation"
                        type="checkbox"
                        class="mr-2"
                      />
                      <span class="text-sm">{{ t('questions.showDetailedExplanation') }}</span>
                    </label>
                  </div>
                </div>
              </div>
              
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-between items-center pt-4 border-t">
              <div class="flex gap-2">
                <button
                  @click="previewSelectedExamStyle"
                  class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                >
                  📋 {{ t('questions.previewStyle') }}
                </button>
                <button
                  @click="openExamDesigner"
                  class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
                >
                  🎨 {{ t('examDesigner.title') }}
                </button>
                <button
                  @click="saveExamStyle"
                  class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                >
                  💾 {{ t('questions.saveStyle') }}
                </button>
              </div>
              
              <div class="flex gap-2">
                <button
                  @click="closeSelectedExportStyleModal"
                  class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                >
                  {{ t('questions.cancel') }}
                </button>
                <button
                  @click="exportSelectedWithCustomStyle"
                  :disabled="exporting"
                  class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm disabled:opacity-50"
                >
                  <span v-if="exporting">{{ t('questions.exportingInProgress') }}</span>
                  <span v-else-if="examStyles.exportOptions.questionsOnly">📝 {{ t('questions.exportQuestions') }}</span>
                  <span v-else-if="examStyles.exportOptions.answerSheetOnly">📋 {{ t('questions.exportAnswerSheet') }}</span>
                  <span v-else>📚 {{ t('questions.exportCompleteExam') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Question Detail Modal -->
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
            <!-- Question Content -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }}</label>
              <div class="p-4 bg-gray-50 rounded-md">
                {{ selectedQuestion.content }}
              </div>
            </div>

            <!-- Options (if single choice question) -->
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

            <!-- Correct Answer -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }}</label>
              <div class="p-4 bg-green-50 border border-green-200 rounded-md">
                {{ selectedQuestion.correct_answer }}
              </div>
            </div>

            <!-- Explanation -->
            <div v-if="selectedQuestion.explanation">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <div class="p-4 bg-blue-50 border border-blue-200 rounded-md">
                {{ selectedQuestion.explanation }}
              </div>
            </div>

            <!-- Other Information -->
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

            <!-- Source Content -->
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

  <!-- Edit Question Modal -->
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
            <!-- Question Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.type') }} *</label>
              <select
                v-model="editForm.type"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="single_choice">{{ t('questions.single_choice') }}</option>
                <option value="cloze">{{ t('questions.cloze') }}</option>
                <option value="short_answer">{{ t('questions.short_answer') }}</option>
                <option value="true_false">{{ t('questions.true_false') }}</option>
                <option value="matching">{{ t('questions.matching') }}</option>
                <option value="sequence">{{ t('questions.sequence') }}</option>
                <option value="enumeration">{{ t('questions.enumeration') }}</option>
                <option value="symbol_identification">{{ t('questions.symbol_identification') }}</option>
                <option value="mixed">{{ t('questions.mixed') }}</option>
                <option value="auto">{{ t('questions.auto') }}</option>
              </select>
            </div>

            <!-- Question Content -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.content') }} *</label>
              <textarea
                v-model="editForm.content"
                rows="4"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.contentPlaceholder')"
              ></textarea>
            </div>

            <!-- Options (for single choice questions) -->
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

            <!-- Correct Answer -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.correctAnswer') }} *</label>
              <input
                v-model="editForm.correct_answer"
                type="text"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.answerPlaceholder')"
              >
            </div>

            <!-- Explanation -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('questions.explanation') }}</label>
              <textarea
                v-model="editForm.explanation"
                rows="3"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                :placeholder="t('questions.explanationPlaceholder')"
              ></textarea>
            </div>

            <!-- Other Information -->
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


  <!-- ExamDesigner Modal -->
  <div v-if="showExamDesigner" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="w-full max-w-7xl max-h-[95vh] overflow-hidden">
      <ExamDesigner
        :visible="showExamDesigner"
        :selected-questions="selectedQuestions"
        :initial-exam-styles="examStyles"
        @close="closeExamDesigner"
        @save="handleExamDesignerSave"
        @export="handleExamDesignerExport"
      />
    </div>
  </div>

</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { getQuestions, deleteQuestion as deleteQuestionAPI, getQuestionStats } from '../api/questionService.js'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'
import ExamDesigner from '@/components/ExamDesigner/ExamDesigner.vue'
// 移除 examGenerator 依賴
import { exportQuestionsAsJson, generateFilename } from '@/utils/markdownExporter.js'

export default {
  name: 'Questions',
  components: {
    ExamDesigner
  },
  setup() {
    const { t, isEnglish } = useLanguage()
    
    // Reactive data
    const loading = ref(false)
    const questions = ref([])
    const stats = ref(null)
    const subjects = ref([])
    
    // Search and filter
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
    const showEditModal = ref(false)
    const selectedQuestion = ref(null)
    
    // Batch selection related
    const selectedQuestions = ref([])
    const exporting = ref(false)
    
    // Cross-page persistence for selected questions using localStorage
    const SELECTED_QUESTIONS_KEY = 'edurag_selected_questions'
    
    // localStorage helper functions
    const saveSelectedQuestions = () => {
      try {
        const selectedIds = selectedQuestions.value.map(q => q.id)
        localStorage.setItem(SELECTED_QUESTIONS_KEY, JSON.stringify(selectedIds))
        console.log('💾 ' + t('questions.savedSelectedQuestionIds') + ':', selectedIds)
      } catch (error) {
        console.error(t('questions.failedToSave') + ':', error)
      }
    }
    
    const loadSelectedQuestions = () => {
      try {
        const savedIds = localStorage.getItem(SELECTED_QUESTIONS_KEY)
        if (savedIds) {
          const ids = JSON.parse(savedIds)
          console.log('📂 ' + t('questions.loadedSelectedQuestionIds') + ':', ids)
          return ids
        }
      } catch (error) {
        console.error(t('questions.failedToLoad') + ':', error)
      }
      return []
    }
    
    const clearSelectedQuestions = () => {
      try {
        localStorage.removeItem(SELECTED_QUESTIONS_KEY)
        console.log('🗑️ ' + t('questions.clearedSelectedQuestions'))
      } catch (error) {
        console.error(t('questions.failedToClear') + ':', error)
      }
    }
    
    const restoreSelectedQuestions = () => {
      const savedIds = loadSelectedQuestions()
      if (savedIds.length > 0) {
        // Find questions in current page that match saved IDs
        const matchingQuestions = questions.value.filter(q => savedIds.includes(q.id))
        
        // Add matching questions to selectedQuestions if they're not already there
        matchingQuestions.forEach(question => {
          if (!selectedQuestions.value.some(q => q.id === question.id)) {
            selectedQuestions.value.push(question)
          }
        })
        
        if (matchingQuestions.length > 0) {
          console.log('🔄 ' + t('questions.restoredSelectedQuestions') + ':', matchingQuestions.length)
        }
      }
    }
    
    // Editing related
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

    // Exam style editor related
    const showExamStyleEditor = ref(false)
    const selectedExamTemplate = ref('standard')
    const showSelectedExportMenu = ref(false)
    const showExamDesigner = ref(false)
    
    // New layout system
    const examStyles = reactive({
      
      header: {
        enabled: true,
        titlePrefix: 'Examination',
        subtitle: '',
        duration: '90 minutes',
        totalScore: '100 points',
        schoolName: '○○學校'
      },
      sections: {
        singleChoice: {
          enabled: true,
          title: 'Multiple Choice Questions',
          instruction: 'Choose the best answer for each question.',
          pointsPerQuestion: 2
        },
        cloze: {
          enabled: true,
          title: 'Fill-in-the-Blank Questions',
          instruction: 'Complete the sentences with appropriate words.',
          pointsPerQuestion: 3
        },
        shortAnswer: {
          enabled: true,
          title: 'Short Answer Questions',
          instruction: 'Provide brief answers to the following questions.',
          pointsPerQuestion: 5
        },
        auto: {
          enabled: true,
          title: 'Auto-Generated Questions',
          instruction: 'Answer the following questions based on the provided information.',
          pointsPerQuestion: 4
        }
      },
      content: {
        includeQuestions: true,
        includeInstructions: true
      },
      answerSheet: {
        enabled: true,
        title: 'Answer Sheet',
        studentInfo: 'Name: ________________　Student ID: ________________　Class: ________________',
        format: 'table',
        includeExplanation: true
      },
      exportOptions: {
        questionsOnly: false,
        answerSheetOnly: false,
        completeExam: true
      }
    })

    // Exam style templates (simplified version)
    const examTemplates = {
      standard: {
        header: {
          enabled: true,
          titlePrefix: 'Examination',
          subtitle: '',
          duration: '90 minutes',
          totalScore: '100 points'
        },
        sections: {
          singleChoice: {
            enabled: true,
            title: 'Part I: Multiple Choice Questions',
            instruction: 'Choose the best answer for each question.',
            pointsPerQuestion: 2
          },
          cloze: {
            enabled: true,
            title: 'Part II: Fill-in-the-Blank Questions',
            instruction: 'Complete the sentences with appropriate words.',
            pointsPerQuestion: 3
          },
          shortAnswer: {
            enabled: true,
            title: 'Part III: Short Answer Questions',
            instruction: 'Provide brief answers to the following questions.',
            pointsPerQuestion: 5
          },
          auto: {
            enabled: true,
            title: 'Part IV: Auto-Generated Questions',
            instruction: 'Answer the following questions based on the provided information.',
            pointsPerQuestion: 4
          }
        },
        content: {
          includeQuestions: true,
          includeInstructions: true
        },
        answerSheet: {
          enabled: true,
          title: '📋 Answer Sheet',
          studentInfo: '**Name:** ________________　**Student ID:** ________________　**Class:** ________________',
          format: 'table',
          includeExplanation: true
        },
        exportOptions: {
          questionsOnly: false,
          answerSheetOnly: false,
          completeExam: true
        }
      },
      simple: {
        header: {
          enabled: true,
          titlePrefix: 'Quiz',
          subtitle: '',
          duration: '60 minutes',
          totalScore: '50 points'
        },
        sections: {
          singleChoice: {
            enabled: true,
            title: 'Multiple Choice',
            instruction: 'Pick the correct answer.',
            pointsPerQuestion: 2
          },
          cloze: {
            enabled: true,
            title: 'Fill in the Blanks',
            instruction: 'Complete each sentence.',
            pointsPerQuestion: 2
          },
          shortAnswer: {
            enabled: true,
            title: 'Short Answers',
            instruction: 'Give short answers.',
            pointsPerQuestion: 3
          },
          auto: {
            enabled: true,
            title: 'Questions',
            instruction: 'Answer each question.',
            pointsPerQuestion: 2
          }
        },
        content: {
          includeQuestions: true,
          includeInstructions: true
        },
        answerSheet: {
          enabled: true,
          title: 'Answers',
          studentInfo: 'Name: ________________　Class: ________________',
          format: 'list',
          includeExplanation: false
        },
        exportOptions: {
          questionsOnly: false,
          answerSheetOnly: false,
          completeExam: true
        }
      }
    }

    // Computed properties
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
        console.log('🔄 Starting to load question list...')
        
        const params = {
          page: currentPage.value,
          size: pageSize.value
        }
        
        if (searchQuery.value) params.search = searchQuery.value
        if (selectedType.value) params.question_type = selectedType.value
        if (selectedSubject.value) params.subject = selectedSubject.value
        if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value

        console.log('📤 API request params:', params)
        
        const response = await getQuestions(params)
        console.log('📥 API raw response:', response)
        
        questions.value = response.data.questions || []
        totalQuestions.value = response.data.total || 0
        totalPages.value = response.data.pages || 0
        
        console.log('✅ Questions loaded successfully:', {
          questions: questions.value.length,
          total: totalQuestions.value,
          pages: totalPages.value
        })
        
        if (questions.value.length === 0) {
          console.warn('⚠️  No question data found!')
        }
        
        // Restore previously selected questions from localStorage
        restoreSelectedQuestions()
      } catch (error) {
        console.error('❌ Load questions failed:', error)
        if (error.response) {
          console.error('📋 Error response:', error.response.data)
          console.error('📋 Error status:', error.response.status)
        } else if (error.request) {
          console.error('🌐 Network error:', error.request)
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: 'Network connection error: Unable to connect to backend service, please check if backend is running.',
            operation: 'Load questions'
          })
        } else {
          console.error('🔧 Request setup error:', error.message)
        }
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        console.log('🔄 Starting to load statistics data...')
        const response = await getQuestionStats()
        console.log('📥 Statistics API raw response:', response)
        
        stats.value = response.data
        
        // Extract subject list
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
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('questions.deleteSuccess'),
          operation: '刪除問題'
        })
      } catch (error) {
        console.error('Delete question failed:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('questions.deleteError') + (error.response?.data?.detail || error.message),
          operation: '刪除問題',
          error
        })
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
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: t('questions.contentRequired'),
            operation: '編輯問題'
          })
          return
        }
        if (!editForm.correct_answer.trim()) {
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: t('questions.answerRequired'),
            operation: '編輯問題'
          })
          return
        }

        // 如果是單選題，驗證選項
        if (editForm.type === 'single_choice') {
          const validOptions = editForm.options.filter(opt => opt.trim())
          if (validOptions.length < 2) {
            eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
              message: t('questions.optionsRequired'),
              operation: '編輯問題'
            })
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
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('questions.updateSuccess'),
          operation: '更新問題'
        })
      } catch (error) {
        console.error('Save question failed:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('questions.updateError') + (error.response?.data?.detail || error.message),
          operation: '更新問題',
          error
        })
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

    // Removed old export functions, now using batch selection custom exam editor

    // Original exportMarkdownExam function removed, now using batch selection custom exam editor
    
    
    const generateSingleChoiceQuestions = (questions, startNumber) => {
      return questions.map((q, index) => {
        const questionNum = startNumber + index
        console.log('生成選擇題:', questionNum, 'Content:', q.content, 'Options:', q.options)
        let questionText = `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`
        
        if (q.options && q.options.length > 0) {
          q.options.forEach(option => {
            questionText += `   ${option}\n`
          })
        } else {
          questionText += `   (Options missing)\n`
        }
        
        questionText += `\n`
        return questionText
      }).join('')
    }
    
    const generateClozeQuestions = (questions, startNumber) => {
      return questions.map((q, index) => {
        const questionNum = startNumber + index
        console.log('生成填空題:', questionNum, 'Content:', q.content)
        return `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`
      }).join('')
    }
    
    const generateShortAnswerQuestions = (questions, startNumber) => {
      return questions.map((q, index) => {
        const questionNum = startNumber + index
        console.log('生成簡答題:', questionNum, 'Content:', q.content)
        return `**${questionNum}.** ${q.content || 'Question content missing'}\n\n<br><br><br>\n\n`
      }).join('')
    }
    
    const generateAutoQuestions = (questions, startNumber) => {
      return questions.map((q, index) => {
        const questionNum = startNumber + index
        console.log('生成Auto題目:', questionNum, 'Content:', q.content, 'Options:', q.options)
        let questionText = `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`
        
        // Auto 類型需要檢查是否有選項，如果有就顯示標準格式
        if (Array.isArray(q.options) && q.options.length > 0) {
          // 有選項，使用標準的 A、B、C、D 格式
          const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
          q.options.forEach((option, optIndex) => {
            if (option && option.trim()) {
              questionText += `   ${optionLabels[optIndex]}. ${option}\n`
            }
          })
          questionText += `\n`
        } else {
          // 沒有選項，當作填空或簡答處理
          questionText += `\n<br><br>\n`
        }
        
        return questionText
      }).join('')
    }
    
    const generateAnswerSheet = (questionsByType) => {
      let answerSheet = `\n---\n\n# 📋 Answer Sheet\n\n**Name:** ________________　**Student ID:** ________________　**Class:** ________________\n\n`
      
      let questionNumber = 1
      
      if (questionsByType.single_choice.length > 0) {
        answerSheet += `## Part I: Multiple Choice Answers\n\n`
        
        // 創建表格形式的答案欄
        const singleChoiceCount = questionsByType.single_choice.length
        let tableRows = []
        
        for (let i = 0; i < singleChoiceCount; i += 5) {
          const rowQuestions = []
          const rowAnswers = []
          
          for (let j = 0; j < 5 && (i + j) < singleChoiceCount; j++) {
            const qNum = questionNumber + i + j
            rowQuestions.push(`${qNum}`)
            rowAnswers.push('____')
          }
          
          tableRows.push(`| ${rowQuestions.join(' | ')} |`)
          tableRows.push(`| ${rowAnswers.join(' | ')} |`)
          
          if (i === 0) {
            tableRows.splice(1, 0, `|${'---|'.repeat(rowQuestions.length)}`)
          }
          
          tableRows.push('') // 空行分隔
        }
        
        answerSheet += tableRows.join('\n') + '\n'
        questionNumber += singleChoiceCount
      }
      
      if (questionsByType.cloze.length > 0) {
        answerSheet += `## Part II: Fill-in-the-Blank Answers\n\n`
        questionsByType.cloze.forEach((q, index) => {
          const qNum = questionNumber + index
          answerSheet += `**${qNum}.** ________________________\n\n`
        })
        questionNumber += questionsByType.cloze.length
      }
      
      if (questionsByType.short_answer.length > 0) {
        answerSheet += `## Part III: Short Answer Responses\n\n`
        questionsByType.short_answer.forEach((q, index) => {
          const qNum = questionNumber + index
          answerSheet += `**${qNum}.** \n\n<br><br><br><br>\n\n`
        })
        questionNumber += questionsByType.short_answer.length
      }
      
      if (questionsByType.auto.length > 0) {
        answerSheet += `## Part IV: Auto-Generated Question Answers\n\n`
        questionsByType.auto.forEach((q, index) => {
          const qNum = questionNumber + index
          if (Array.isArray(q.options) && q.options.length > 0) {
            // 有選項，當作選擇題處理
            answerSheet += `**${qNum}.** ____\n\n`
          } else if (q.original_type === 'cloze' || q.type === 'cloze') {
            // 完形填空格式
            answerSheet += `**${qNum}.** ________________________\n\n`
          } else {
            // 簡答題格式 
            answerSheet += `**${qNum}.** \n`
            answerSheet += `${'_'.repeat(50)}\n\n${'_'.repeat(50)}\n\n`
          }
        })
      }
      
      // 添加標準答案（供教師參考）
      answerSheet += `\n---\n\n# 🔑 Answer Key (For Instructor Reference)\n\n`
      
      let answerNumber = 1
      
      if (questionsByType.single_choice.length > 0) {
        answerSheet += `## Multiple Choice Answer Key\n\n`
        questionsByType.single_choice.forEach((q, index) => {
          answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
          if (q.explanation) {
            answerSheet += `   *Explanation: ${q.explanation}*\n`
          }
          answerSheet += '\n'
        })
        answerNumber += questionsByType.single_choice.length
      }
      
      if (questionsByType.cloze.length > 0) {
        answerSheet += `## Fill-in-the-Blank Answer Key\n\n`
        questionsByType.cloze.forEach((q, index) => {
          answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
          if (q.explanation) {
            answerSheet += `   *Explanation: ${q.explanation}*\n`
          }
          answerSheet += '\n'
        })
        answerNumber += questionsByType.cloze.length
      }
      
      if (questionsByType.short_answer.length > 0) {
        answerSheet += `## Short Answer Reference Answers\n\n`
        questionsByType.short_answer.forEach((q, index) => {
          answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
          if (q.explanation) {
            answerSheet += `   *Notes: ${q.explanation}*\n`
          }
          answerSheet += '\n'
        })
        answerNumber += questionsByType.short_answer.length
      }
      
      if (questionsByType.auto.length > 0) {
        answerSheet += `## Auto-Generated Question Answer Key\n\n`
        questionsByType.auto.forEach((q, index) => {
          answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
          if (q.explanation) {
            answerSheet += `   *Explanation: ${q.explanation}*\n`
          }
          answerSheet += '\n'
        })
      }
      
      return answerSheet
    }
    
    const downloadMarkdownFile = (content, filename) => {
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${filename}.md`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
    
    // 匯出選中題目為 Markdown 考券

    // Batch selection related方法
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
        clearSelectedQuestions()
      } else {
        selectedQuestions.value = [...questions.value]
        // saveSelectedQuestions() will be called automatically by the watcher
      }
    }

    const exportSelectedQuestions = async () => {
      if (selectedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: "請先選擇要匯出的問題",
          operation: "匯出選中問題"
        })
        return
      }

      try {
        exporting.value = true
        
        // 使用新的匯出工具函數
        const filename = generateFilename("selected_questions")
        exportQuestionsAsJson(selectedQuestions.value, filename)

        // Clear selection and localStorage
        const count = selectedQuestions.value.length
        selectedQuestions.value = []
        clearSelectedQuestions()
        
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: `已匯出 ${count} 道選中的題目`,
          operation: "匯出選中問題"
        })
      } catch (error) {
        console.error("Export selected questions failed:", error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: "匯出失敗: " + error.message,
          operation: "匯出選中問題",
          error
        })
      } finally {
        exporting.value = false
      }
    }
    // 工具方法
    const getTypeLabel = (type) => {
      const typeMap = {
        // 傳統題型
        'single_choice': t('questions.single_choice'),
        'cloze': t('questions.cloze'),
        'short_answer': t('questions.short_answer'),
        // G1~G2 題型
        'true_false': t('questions.true_false'),
        'matching': t('questions.matching'),
        'sequence': t('questions.sequence'),
        'enumeration': t('questions.enumeration'),
        'symbol_identification': t('questions.symbol_identification'),
        // 系統題型
        'mixed': t('questions.mixed'),
        'auto': t('questions.auto')
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

    // 生成考券標題
    const generateExamTitle = (questions, customTitle = null) => {
      if (customTitle) {
        return customTitle
      }
      
      const subjects = [...new Set(questions.map(q => q.subject).filter(Boolean))]
      const subjectText = subjects.length > 0 ? subjects.join(' & ') : 'General'
      const today = new Date()
      const dateStr = today.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
      })
      return `${subjectText} Examination - ${dateStr}`
    }

    // 樣式管理方法
    const applyExamTemplate = () => {
      if (examTemplates[selectedExamTemplate.value]) {
        Object.assign(examStyles, examTemplates[selectedExamTemplate.value])
      }
    }


    // ExamDesigner 相關方法
    const openExamDesigner = () => {
      if (selectedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: "請先選擇要設計的題目",
          operation: "開啟考券設計器"
        })
        return
      }
      
      showExamDesigner.value = true
      closeSelectedExportStyleModal() // 關閉樣式編輯器
      console.log('🎨 開啟考券設計器，題目數量:', selectedQuestions.value.length)
    }

    const closeExamDesigner = () => {
      showExamDesigner.value = false
      console.log('🎨 關閉考券設計器')
    }

    const handleExamDesignerSave = (templateData) => {
      // 儲存自訂樣式到 localStorage
      const savedTemplates = JSON.parse(localStorage.getItem('customExamTemplates') || '[]')
      savedTemplates.push(templateData)
      localStorage.setItem('customExamTemplates', JSON.stringify(savedTemplates))
      
      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: '考券樣式已儲存',
        operation: '儲存樣式'
      })
      
      console.log('💾 考券設計器樣式已儲存:', templateData.name)
    }

    const handleExamDesignerExport = (exportData) => {
      // 使用考券設計器的匯出功能
      const { title, questions, examStyles: designerStyles, markdown } = exportData
      
      // 更新目前的 examStyles
      Object.assign(examStyles, designerStyles)
      
      // 觸發匯出
      exportSelectedWithCustomStyle()
      
      console.log('📤 考券設計器匯出:', title, questions.length + '題')
    }

    const saveExamStyle = () => {
      try {
        const styleData = {
          name: `Custom_${new Date().getTime()}`,
          template: selectedExamTemplate.value,
          styles: JSON.parse(JSON.stringify(examStyles)),
          created: new Date().toISOString()
        }
        
        localStorage.setItem('examStyles', JSON.stringify(styleData))
        
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: '考券樣式已儲存到本地',
          operation: '儲存樣式'
        })
      } catch (error) {
        console.error('Save exam style failed:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '儲存樣式失敗：' + (error.message || '未知錯誤'),
          operation: '儲存樣式',
          error
        })
      }
    }



    // 使用自訂樣式生成 Markdown 的函數
    const generateCustomMarkdown = (title, questions, styles) => {
      const totalQuestions = questions.length
      const subjects = [...new Set(questions.map(q => q.subject).filter(Boolean))]
      
      let markdown = ''
      
      // 依題型分組
      const questionsByType = {
        single_choice: questions.filter(q => q.type === 'single_choice'),
        cloze: questions.filter(q => q.type === 'cloze'), 
        short_answer: questions.filter(q => q.type === 'short_answer'),
        auto: questions.filter(q => q.type === 'auto')
      }

      // 根據匯出選項決定內容
      if (!styles.exportOptions.answerSheetOnly) {
        // 生成考券內容
        if (styles.header.enabled) {
          markdown += `# ${title}\n\n`
          
          if (styles.header.subtitle) {
            markdown += `**${styles.header.subtitle}**\n\n`
          }
          
          markdown += `**Subject:** ${subjects.join(' & ') || 'General'}  \n`
          markdown += `**Duration:** ${styles.header.duration}  \n`
          markdown += `**Total Score:** ${styles.header.totalScore}  \n`
          markdown += `**Total Questions:** ${totalQuestions}  \n\n`
          
          if (styles.content.includeInstructions) {
            markdown += `---\n\n## 📋 Instructions\n\n`
            markdown += `1. Read all questions carefully before answering\n`
            markdown += `2. Write your answers clearly in the answer sheet\n`
            markdown += `3. Check your work before submission\n\n`
            markdown += `---\n\n`
          }
        }
        
        let questionNumber = 1
        
        // 生成各個題型區塊（只生成啟用的）
        if (questionsByType.single_choice.length > 0 && styles.sections.singleChoice.enabled) {
          const sectionStyle = styles.sections.singleChoice
          markdown += `## ${sectionStyle.title}\n\n`
          if (sectionStyle.instruction) {
            markdown += `*${sectionStyle.instruction}*\n\n`
          }
          markdown += generateSingleChoiceQuestions(questionsByType.single_choice, questionNumber)
          questionNumber += questionsByType.single_choice.length
        }
        
        if (questionsByType.cloze.length > 0 && styles.sections.cloze.enabled) {
          const sectionStyle = styles.sections.cloze
          markdown += `\n## ${sectionStyle.title}\n\n`
          if (sectionStyle.instruction) {
            markdown += `*${sectionStyle.instruction}*\n\n`
          }
          markdown += generateClozeQuestions(questionsByType.cloze, questionNumber)
          questionNumber += questionsByType.cloze.length
        }
        
        if (questionsByType.short_answer.length > 0 && styles.sections.shortAnswer.enabled) {
          const sectionStyle = styles.sections.shortAnswer
          markdown += `\n## ${sectionStyle.title}\n\n`
          if (sectionStyle.instruction) {
            markdown += `*${sectionStyle.instruction}*\n\n`
          }
          markdown += generateShortAnswerQuestions(questionsByType.short_answer, questionNumber)
          questionNumber += questionsByType.short_answer.length
        }
        
        if (questionsByType.auto.length > 0 && styles.sections.auto.enabled) {
          const sectionStyle = styles.sections.auto
          markdown += `\n## ${sectionStyle.title}\n\n`
          if (sectionStyle.instruction) {
            markdown += `*${sectionStyle.instruction}*\n\n`
          }
          markdown += generateAutoQuestions(questionsByType.auto, questionNumber)
        }
      }
      
      // 生成答案欄（如果啟用且不是只要考券）
      if (styles.answerSheet.enabled && !styles.exportOptions.questionsOnly) {
        // 只包含啟用的題型
        const enabledQuestionsByType = {}
        if (styles.sections.singleChoice.enabled && questionsByType.single_choice.length > 0) {
          enabledQuestionsByType.single_choice = questionsByType.single_choice
        }
        if (styles.sections.cloze.enabled && questionsByType.cloze.length > 0) {
          enabledQuestionsByType.cloze = questionsByType.cloze
        }
        if (styles.sections.shortAnswer.enabled && questionsByType.short_answer.length > 0) {
          enabledQuestionsByType.short_answer = questionsByType.short_answer
        }
        if (styles.sections.auto.enabled && questionsByType.auto.length > 0) {
          enabledQuestionsByType.auto = questionsByType.auto
        }
        
        markdown += generateCustomAnswerSheet(enabledQuestionsByType, styles)
      }
      
      return markdown
    }

    // 使用自訂樣式生成答案欄的函數
    const generateCustomAnswerSheet = (questionsByType, styles) => {
      let answerSheet = `\n---\n\n# ${styles.answerSheet.title}\n\n${styles.answerSheet.studentInfo}\n\n`
      
      let questionNumber = 1
      
      // 根據格式生成不同樣式的答案欄
      if (styles.answerSheet.format === 'table') {
        if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
          answerSheet += `## Part I: Multiple Choice Answers\n\n`
          
          const singleChoiceCount = questionsByType.single_choice.length
          let tableRows = []
          
          for (let i = 0; i < singleChoiceCount; i += 5) {
            const rowQuestions = []
            const rowAnswers = []
            
            for (let j = 0; j < 5 && (i + j) < singleChoiceCount; j++) {
              const qNum = questionNumber + i + j
              rowQuestions.push(`${qNum}`)
              rowAnswers.push('____')
            }
            
            tableRows.push(`| ${rowQuestions.join(' | ')} |`)
            tableRows.push(`| ${rowAnswers.join(' | ')} |`)
            
            if (i === 0) {
              tableRows.splice(1, 0, `|${'---|'.repeat(rowQuestions.length)}`)
            }
            
            tableRows.push('') // 空行分隔
          }
          
          answerSheet += tableRows.join('\n') + '\n'
          questionNumber += singleChoiceCount
        }
      } else if (styles.answerSheet.format === 'list') {
        if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
          answerSheet += `## Multiple Choice Answers\n\n`
          questionsByType.single_choice.forEach((q, index) => {
            const qNum = questionNumber + index
            answerSheet += `${qNum}. ____\n`
          })
          answerSheet += '\n'
          questionNumber += questionsByType.single_choice.length
        }
      } else if (styles.answerSheet.format === 'grid') {
        if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
          answerSheet += `## Multiple Choice Grid\n\n`
          answerSheet += `| Q# | A | B | C | D | Answer |\n`
          answerSheet += `|----|---|---|---|---|--------|\n`
          questionsByType.single_choice.forEach((q, index) => {
            const qNum = questionNumber + index
            answerSheet += `| ${qNum} | ○ | ○ | ○ | ○ | ____ |\n`
          })
          answerSheet += '\n'
          questionNumber += questionsByType.single_choice.length
        }
      }
      
      // 其他題型答案欄（保持一致格式）
      if (questionsByType.cloze && questionsByType.cloze.length > 0) {
        answerSheet += `## Fill-in-the-Blank Answers\n\n`
        questionsByType.cloze.forEach((q, index) => {
          const qNum = questionNumber + index
          answerSheet += `**${qNum}.** ________________________\n\n`
        })
        questionNumber += questionsByType.cloze.length
      }
      
      if (questionsByType.short_answer && questionsByType.short_answer.length > 0) {
        answerSheet += `## Short Answer Responses\n\n`
        questionsByType.short_answer.forEach((q, index) => {
          const qNum = questionNumber + index
          answerSheet += `**${qNum}.** \n\n<br><br><br><br>\n\n`
        })
        questionNumber += questionsByType.short_answer.length
      }
      
      if (questionsByType.auto && questionsByType.auto.length > 0) {
        answerSheet += `## Auto-Generated Question Answers\n\n`
        questionsByType.auto.forEach((q, index) => {
          const qNum = questionNumber + index
          if (Array.isArray(q.options) && q.options.length > 0) {
            answerSheet += `**${qNum}.** ____\n\n`
          } else if (q.original_type === 'cloze' || q.type === 'cloze') {
            answerSheet += `**${qNum}.** ________________________\n\n`
          } else {
            answerSheet += `**${qNum}.** \n`
            answerSheet += `${'_'.repeat(50)}\n\n${'_'.repeat(50)}\n\n`
          }
        })
      }
      
      // 添加答案解析（如果啟用）
      if (styles.answerSheet.includeExplanation) {
        answerSheet += `\n---\n\n# 🔑 Answer Key (For Instructor Reference)\n\n`
        
        let answerNumber = 1
        
        if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
          answerSheet += `## Multiple Choice Answer Key\n\n`
          questionsByType.single_choice.forEach((q, index) => {
            answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
            if (q.explanation) {
              answerSheet += `   *Explanation: ${q.explanation}*\n`
            }
            answerSheet += '\n'
          })
          answerNumber += questionsByType.single_choice.length
        }
        
        if (questionsByType.cloze && questionsByType.cloze.length > 0) {
          answerSheet += `## Fill-in-the-Blank Answer Key\n\n`
          questionsByType.cloze.forEach((q, index) => {
            answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
            if (q.explanation) {
              answerSheet += `   *Explanation: ${q.explanation}*\n`
            }
            answerSheet += '\n'
          })
          answerNumber += questionsByType.cloze.length
        }
        
        if (questionsByType.short_answer && questionsByType.short_answer.length > 0) {
          answerSheet += `## Short Answer Reference Answers\n\n`
          questionsByType.short_answer.forEach((q, index) => {
            answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
            if (q.explanation) {
              answerSheet += `   *Notes: ${q.explanation}*\n`
            }
            answerSheet += '\n'
          })
          answerNumber += questionsByType.short_answer.length
        }
        
        if (questionsByType.auto && questionsByType.auto.length > 0) {
          answerSheet += `## Auto-Generated Question Answer Key\n\n`
          questionsByType.auto.forEach((q, index) => {
            answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
            if (q.explanation) {
              answerSheet += `   *Explanation: ${q.explanation}*\n`
            }
            answerSheet += '\n'
          })
        }
      }
      
      return answerSheet
    }

    // 選中問題樣式編輯相關方法
    
    // 在當前頁面顯示預覽的備用方案
    const showInlinePreview = (markdown) => {
      // 創建預覽內容並顯示在console或alert中
      console.log('=== 考券預覽 ===')
      console.log(markdown)
      
      eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
        message: '預覽內容已輸出到瀏覽器控制台，請按F12查看',
        operation: '預覽考券'
      })
      
      // 也可以創建一個簡單的alert預覽
      if (markdown.length < 1000) {
        alert(`考券預覽：\n\n${markdown.substring(0, 800)}${markdown.length > 800 ? '...' : ''}`)
      }
    }

    const exportSelectedWithCustomStyle = async () => {
      if (selectedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '請先選擇要匯出的問題',
          operation: '匯出選中問題'
        })
        return
      }

      try {
        exporting.value = true
        
        // 生成考券標題
        const examTitle = generateExamTitle(selectedQuestions.value)
        
        // 直接使用 PDF 導出
        const examData = {
          questions: selectedQuestions.value,
          config: examStyles,
          questionTypeOrder: examStyles.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
        }
        
        // 動態導入 PDF 導出器
        const { exportToPDF } = await import('@/utils/pdfExporter.js')
        const result = await exportToPDF(examData, `${examTitle.replace(/[^a-zA-Z0-9\-_\s]/g, '_')}.pdf`)
        
        // 關閉 Modal
        showSelectedExportStyleModal.value = false
        
        if (result.success) {
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: `成功匯出 ${selectedQuestions.value.length} 道選中題目為 PDF`,
            operation: '匯出 PDF 考券'
          })
        } else {
          throw new Error(result.message)
        }
        
      } catch (error) {
        console.error('Export selected questions with custom style failed:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '匯出考券失敗：' + (error.message || '未知錯誤'),
          operation: '匯出自定義考券',
          error
        })
      } finally {
        exporting.value = false
      }
    }

    // Debounced search function
    let searchTimeout = null
    const debouncedSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadQuestions()
      }, 300) // 300ms debounce
    }

    // Watchers
    watch(searchQuery, () => {
      debouncedSearch()
    })
    
    watch([selectedType, selectedSubject, selectedDifficulty], () => {
      currentPage.value = 1
      loadQuestions()
    })
    
    // Watch for changes in selected questions and save to localStorage
    watch(selectedQuestions, (newValue) => {
      saveSelectedQuestions()
      console.log('🔄 ' + t('questions.selectedQuestionsChanged') + ':', newValue.length)
    }, { deep: true })

    // Load data
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
      
      // Search and filter
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
      showEditModal,
      showExamDesigner,
      selectedQuestion,
      editingQuestion,
      editForm,
      
      // 匯出
      exporting,
      
      // 考券樣式編輯器
      showExamStyleEditor,
      selectedExamTemplate,
      showSelectedExportMenu,
      examStyles,
      
      
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
      
      // 批次選擇
      selectedQuestions,
      isAllSelected,
      toggleQuestionSelection,
      toggleSelectAll,
      exportSelectedQuestions,
      
      // 樣式管理方法
      applyExamTemplate,
      saveExamStyle,
      generateCustomAnswerSheet,
      
      
      // 簡化的預覽方法
      showInlinePreview,
      exportSelectedWithCustomStyle,
      
      // ExamDesigner 相關方法
      openExamDesigner,
      closeExamDesigner,
      handleExamDesignerSave,
      handleExamDesignerExport,
      
      // 工具方法
      getTypeLabel,
      getDifficultyLabel,
      getDifficultyColor,
      getSubjectColor,
      formatDate,
      generateExamTitle
    }
  }
}
</script>