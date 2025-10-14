<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ t('generate.title') }}</h1>
          <p class="mt-2 text-sm text-gray-600">{{ t('generate.subtitle') }}</p>
        </div>
        <div>
          <button
            @click="resetForm"
            :disabled="generating"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            🔄 {{ t('generate.clearAllSettings') || '清空全部設定' }}
          </button>
        </div>
      </div>

      <!-- 傳統生成模式 -->
      <div class="bg-gray-50 rounded-lg p-6 mb-8">
        <div class="flex items-center mb-6">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-medium">1</span>
            </div>
          </div>
          <div class="ml-4">
            <h2 class="text-xl font-semibold text-gray-900">{{ t('generate.traditionalMode') || '傳統生成模式' }}</h2>
            <p class="text-sm text-gray-600">{{ t('generate.traditionalModeDesc') || '選擇一個模板和文件進行預覽生成' }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 左側：設定面板 -->
          <div class="lg:col-span-1 space-y-6">
            <!-- 模板選擇 -->
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.selectTemplate') }}</h3>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('templates.filterBySubject') }}</label>
              <select
                v-model="selectedSubject"
                @change="fetchTemplates"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('templates.allSubjects') }}</option>
                <option v-for="subject in subjects" :key="subject" :value="subject">
                  {{ isEnglish ? t('subjects.' + getSubjectKey(subject)) : subject }}
                </option>
              </select>
            </div>

            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div
                v-for="template in filteredTemplates"
                :key="template.id"
                @click="selectTemplate(template)"
                :class="[
                  'cursor-pointer p-3 border rounded-md transition-colors',
                  selectedTemplate?.id === template.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                ]"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">{{ template.name }}</h3>
                    <p class="text-xs text-gray-500">{{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : getSubjectDisplayName(template) }}</p>
                    <div class="mt-1">
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {{ getQuestionTypeLabel(template.question_type) || template.question_type || '未指定' }}
                      </span>
                    </div>
                  </div>
                  <div class="flex-shrink-0">
                    <span
                      :class="getSubjectStyle(template.subject) ? '' : getSubjectColor(template.subject)"
                      :style="getSubjectStyle(template.subject)"
                      class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                    >
                      {{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : getSubjectDisplayName(template) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="templates.length === 0 && !loadingTemplates" class="text-center py-4 text-gray-500">
              <p>{{ t('generate.noTemplatesAvailable') }}</p>
              <button @click="$router.push('/templates')" class="text-blue-600 hover:text-blue-800 text-sm">
                {{ t('generate.goCreateTemplate') }}
              </button>
            </div>
          </div>

          <!-- 文件選擇 -->
          <div class="bg-white shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.selectDocuments') }}</h3>

            <!-- 科目篩選 -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('documents.subject') }}</label>
              <select
                v-model="selectedDocumentSubject"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="">{{ t('documents.allSubjects') }}</option>
                <option v-for="subject in documentSubjects" :key="subject" :value="subject">
                  {{ isEnglish ? t('subjects.' + getSubjectKey(subject)) : subject }}
                </option>
              </select>
            </div>

            <!-- 年級篩選 -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('documents.grade') }}</label>
              <select
                v-model="selectedDocumentGrade"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="">{{ t('documents.allGrades') }}</option>
                <option value="G1">G1</option>
                <option value="G2">G2</option>
                <option value="G3">G3</option>
                <option value="G4">G4</option>
                <option value="G5">G5</option>
                <option value="G6">G6</option>
                <option value="ALL">ALL</option>
              </select>
            </div>

            <!-- 搜尋框 -->
            <div class="mb-4">
              <input
                v-model="documentSearchQuery"
                @input="searchDocuments"
                type="text"
                :placeholder="t('generate.searchDocuments')"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
            </div>

            <!-- 文件計數顯示 -->
            <div class="mb-3 text-sm text-gray-600">
              <span class="font-medium">{{ t('generate.showingDocuments') }}: </span>
              <span class="text-blue-600 font-semibold">{{ filteredDocuments.length }}</span>
              <span> / </span>
              <span class="text-gray-500">{{ t('generate.totalDocuments') }}: {{ documents.length }}</span>
            </div>

            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div
                v-for="document in filteredDocuments"
                :key="document.id"
                @click="selectDocument(document)"
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
                      <span v-if="document.page" class="text-xs text-gray-500">• {{ isEnglish ? 'Page ' + document.page : '第' + document.page + '頁' }}</span>
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
                      @click.stop="toggleDocumentSelection(document)"
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
          
          <!-- 傳統生成設定 -->
          <div class="bg-white shadow rounded-lg p-6">
            <!-- 生成數量調整 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('generate.questionCount') || '生成數量' }}</label>
              <input
                v-model.number="traditionalCount"
                type="number"
                min="1"
                max="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <!-- 問題類型顯示（從模板取得，不可選擇） -->
            <div v-if="selectedTemplate" class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">問題類型</label>
              <div class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-700">
                {{ getQuestionTypeLabel(selectedTemplate.question_type) }}
              </div>
              <p class="text-xs text-gray-500 mt-1">此題型由所選模板決定，可在模板管理頁面修改</p>
            </div>
            
            <div class="text-center">
              <button
                @click="generateTraditionalQuestions"
                :disabled="!selectedTemplate || selectedDocuments.length === 0 || generating"
                class="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <svg v-if="generating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ generating ? t('generate.generating') || '生成中...' : t('generate.traditionalGenerate') || '預覽生成' }}
              </button>
              <p class="text-xs text-gray-500 mt-2">
                {{ t('generate.traditionalGenerateDesc') || '基於選擇的模板和文件生成範例題目' }}
              </p>
            </div>
          </div>
        </div>

        <!-- 右側：預覽與結果 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 模板預覽 -->
          <div v-if="selectedTemplate" class="bg-white shadow rounded-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900">{{ t('generate.templatePreview') }}</h2>
              <div class="text-sm text-gray-500">
                {{ selectedDocuments.length }} {{ t('generate.documentsSelected') }}
              </div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-sm font-medium text-gray-900">{{ selectedTemplate.name }}</h3>
                <div class="text-xs text-gray-500">
                  內容長度: {{ previewContent.length }} 字符
                </div>
              </div>
              <div class="max-h-[600px] overflow-y-auto border border-gray-200 bg-white p-3 rounded text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                {{ previewContent }}
              </div>
              <div class="mt-3 text-xs text-gray-500 flex justify-between">
                <span>{{ t('generate.previewNote') }}</span>
                <span v-if="selectedDocuments.length > 0">
                  已選文件: {{ selectedDocuments.map(d => d.title).join(', ') }}
                </span>
              </div>
            </div>
          </div>

          <!-- 考卷預覽模式切換 -->
          <div v-if="generatedQuestions.length > 0" class="bg-white shadow rounded-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-medium text-gray-900">
                {{ t('generate.generatedResults') }} ({{ generatedQuestions.length }}{{ t('generate.questions') }})
              </h2>
              <div class="flex space-x-2">
                <button
                  @click="exportQuestions"
                  class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium"
                >
                  {{ t('export') }}
                </button>
                <button
                  @click="saveQuestions"
                  :disabled="saving"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50 flex items-center"
                >
                  <svg v-if="saving" class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ saving ? (isEnglish ? 'Saving...' : '儲存中...') : t('save') }}
                </button>
              </div>
            </div>

            <!-- 題目列表模式 -->
            <div class="space-y-4">
              <div
                v-for="(question, index) in generatedQuestions"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex justify-between items-start mb-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ getQuestionTypeLabel(question.type) }} {{ index + 1 }}
                  </span>
                </div>
                
                <div class="mb-3">
                  <h4 class="font-medium text-gray-900 mb-2">{{ question.prompt }}</h4>
                  
                  <div v-if="question.options" class="mb-2">
                    <ul class="space-y-1">
                      <li v-for="(option, optIndex) in question.options" :key="optIndex" class="text-sm text-gray-700">
                        {{ option }}
                      </li>
                    </ul>
                  </div>
                </div>
                
                <div class="bg-gray-50 p-3 rounded">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div>
                      <span class="font-medium text-gray-700">{{ t('generate.answer') }}：</span>
                      <span class="text-gray-900">{{ question.answer }}</span>
                    </div>
                    <div>
                      <span class="font-medium text-gray-700">{{ t('generate.source') }}：</span>
                      <span class="text-gray-600">{{ t('generate.document') }} {{ question.source.document_id }}</span>
                    </div>
                  </div>
                  <div class="mt-2">
                    <span class="font-medium text-gray-700">{{ t('generate.explanation') }}：</span>
                    <span class="text-gray-600">{{ question.explanation }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 空狀態 -->
          <div v-else class="bg-white shadow rounded-lg p-8 text-center">
            <div class="text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 class="text-lg font-medium text-gray-900 mb-2">{{ t('generate.readyToGenerate') }}</h3>
              <p class="text-sm text-gray-500 mb-4">{{ t('generate.selectRequirements') }}</p>
              <div class="text-left max-w-md mx-auto">
                <div class="flex items-center text-sm text-gray-600 mb-2">
                  <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  {{ t('generate.steps.selectTemplate') }}
                </div>
                <div class="flex items-center text-sm text-gray-600 mb-2">
                  <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  {{ t('generate.steps.selectDocument') }}
                </div>
                <div class="flex items-center text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  {{ t('generate.steps.setQuestionTypes') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 批次生成模式 -->
      <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 mt-8">
        <div class="flex items-center mb-6">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-medium">2</span>
            </div>
          </div>
          <div class="ml-4">
            <h2 class="text-xl font-semibold text-gray-900">{{ t('generate.batchMode') || '批次生成模式' }}</h2>
            <p class="text-sm text-gray-600">{{ t('generate.batchModeDesc') || '為每個文件配對合適的模板，批次生成題目' }}</p>
          </div>
        </div>

        <div class="bg-white rounded-lg p-6">
          <!-- 批次文件選擇區域 -->
          <div class="mb-6 pb-6 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.batchDocumentSelection') || '批次文件選擇' }}</h3>
            <p class="text-sm text-gray-600 mb-4">{{ t('generate.batchSelectDocuments') || '選擇要進行批次生成的文件' }}</p>
            
            <!-- 搜尋框 -->
            <div class="mb-4">
              <input
                v-model="batchDocumentSearchQuery"
                type="text"
                :placeholder="t('generate.batchSearchDocuments') || '搜尋批次生成文件...'"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
            </div>

            <!-- 文件選擇網格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
              <div
                v-for="document in filteredBatchDocuments"
                :key="`batch-select-${document.id}`"
                @click="toggleBatchDocumentSelection(document)"
                :class="[
                  'cursor-pointer p-3 border rounded-md transition-colors',
                  batchSelectedDocuments.some(d => d.id === document.id)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-300 hover:border-gray-400'
                ]"
              >
                <div class="flex items-center">
                  <input
                    type="checkbox"
                    :checked="batchSelectedDocuments.some(d => d.id === document.id)"
                    class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded mr-3"
                    @click.stop="toggleBatchDocumentSelection(document)"
                  >
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-medium text-gray-900 truncate">{{ document.title }}</h4>
                    <p class="text-xs text-gray-500">{{ document.chapter }} - {{ isEnglish ? 'Page ' + document.page : '第' + document.page + '頁' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="documents.length === 0" class="text-center py-8 text-gray-400">
              <p class="text-sm">{{ t('generate.noBatchDocuments') || '尚未選擇批次生成文件' }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- 左側：已選文件列表 -->
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.selectedDocuments') || '已選文件' }} ({{ batchSelectedDocuments.length }})</h3>
              <div v-if="batchSelectedDocuments.length === 0" class="text-center py-8 text-gray-500">
                <svg class="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <p class="text-sm">{{ t('generate.addBatchDocuments') || '請選擇文件進行批次生成' }}</p>
              </div>
              <div v-else class="space-y-2 max-h-96 overflow-y-auto">
                <div
                  v-for="document in batchSelectedDocuments"
                  :key="`batch-doc-${document.id}`"
                  class="p-3 border rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <h4 class="text-sm font-medium text-gray-900">{{ document.title }}</h4>
                  <p class="text-xs text-gray-500 mt-1">{{ document.chapter }} - {{ isEnglish ? 'Page ' + document.page : '第' + document.page + '頁' }}</p>
                  <div class="text-xs text-purple-600 mt-1">
                    {{ getDocumentPairings(document.id).length }}{{ t('generate.pairingCount') || '個模板配對' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 右側：文件-模板配對 -->
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.templatePairing') || '模板配對' }}</h3>
              <div v-if="batchSelectedDocuments.length === 0" class="text-center py-8 text-gray-400">
                <p class="text-sm">{{ t('generate.selectDocumentsAfterPairing') || '選擇文件後開始配對' }}</p>
              </div>
              <div v-else class="space-y-4 max-h-96 overflow-y-auto">
                <div v-for="document in batchSelectedDocuments" :key="`pairing-${document.id}`" class="border-l-4 border-purple-200 pl-4">
                  <div class="text-sm font-medium text-gray-900 mb-2">{{ document.title }}</div>
                  
                  <!-- 該文件的模板配對列表 -->
                  <div class="space-y-2">
                    <div 
                      v-for="(pairing, index) in getDocumentPairings(document.id)" 
                      :key="`pairing-${document.id}-${index}`"
                      @click="selectPairing(document.id, pairing.template_id)"
                      :class="[
                        'cursor-pointer p-2 border rounded text-xs transition-colors',
                        selectedPairing?.document_id === document.id && selectedPairing?.template_id === pairing.template_id
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-300 hover:border-gray-400'
                      ]"
                    >
                      <div class="flex justify-between items-center">
                        <span class="font-medium">{{ getTemplate(pairing.template_id)?.name }}</span>
                        <button
                          @click.stop="removePairing(document.id, pairing.template_id)"
                          class="text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </div>
                      <div class="flex justify-between items-center mt-1">
                        <span class="text-gray-500">{{ getTemplate(pairing.template_id) ? getSubjectDisplayName(getTemplate(pairing.template_id)) : '' }}</span>
                        <input
                          v-model.number="pairing.count"
                          @click.stop
                          type="number"
                          min="1"
                          max="10"
                          class="w-12 px-1 py-0.5 text-xs border border-gray-300 rounded"
                        >
                      </div>
                    </div>
                  </div>

                  <!-- 新增配對按鈕 -->
                  <div class="mt-2">
                    <select
                      @change="addPairing(document.id, $event.target.value, $event)"
                      class="w-full text-xs border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="">{{ t('generate.addTemplatePairing') || '+ 新增模板配對' }}</option>
                      <option
                        v-for="template in getAvailableTemplates(document.id)"
                        :key="template.id"
                        :value="template.id"
                      >
                        {{ template.name }} ({{ getSubjectDisplayName(template) }})
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- 新的模板組合管理區域 -->
          <div class="mt-8 p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-l-4 border-green-400">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">🎯 {{ t('generate.templateGroupGenerate') }}</h3>
              <div class="text-sm text-gray-600">
                {{ templateDocumentPairings.length }}{{ t('generate.templateGroupCount') }} · 預計{{ getTotalQuestionsFromGroups() }}題
              </div>
            </div>
            
            <div v-if="batchSelectedDocuments.length === 0" class="text-center py-8 text-gray-400">
              <p class="text-sm">請先選擇文件，然後創建模板組合</p>
            </div>
            
            <div v-else class="space-y-4">
              <!-- 模板選擇器 -->
              <div class="bg-white p-4 rounded-lg border">
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('generate.addTemplateGroup') }}</label>
                <select
                  @change="(e) => { console.log('🔄 選擇模板事件:', e.target.value); createTemplateGroup(e.target.value); e.target.value = ''; }"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">選擇模板建立組合...</option>
                  <option v-for="template in templates" :key="`template-group-${template.id}`" :value="template.id">
                    {{ template.name }} ({{ getSubjectDisplayName(template) }})
                  </option>
                </select>
              </div>

              <!-- 模板組合列表 -->
              <div class="space-y-4">
                <div 
                  v-for="group in templateDocumentPairings" 
                  :key="`group-${group.id}`"
                  @click="selectedTemplateGroup = group.id; selectedPairing = null"
                  :class="[
                    'cursor-pointer border rounded-lg p-4 transition-colors',
                    selectedTemplateGroup === group.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400 bg-white'
                  ]"
                >
                  <div class="flex justify-between items-start mb-3">
                    <div>
                      <h4 class="text-sm font-medium text-gray-900">📝 {{ group.template_name }}</h4>
                      <p class="text-xs text-gray-500">{{ group.subject_display || group.subject }} · 生成 {{ group.count }} 題</p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <input
                        v-model.number="group.count"
                        @click.stop
                        type="number"
                        min="1"
                        max="20"
                        class="w-16 px-2 py-1 text-xs border border-gray-300 rounded"
                      >
                      <button
                        @click.stop="removeTemplateGroup(group.id)"
                        class="text-red-500 hover:text-red-700 text-sm"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <!-- 已選文件清單 -->
                  <div class="mb-2">
                    <div class="text-xs text-gray-600 mb-1">已選文件 ({{ group.documents.length }})：</div>
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="docId in group.documents" 
                        :key="`group-${group.id}-doc-${docId}`"
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700"
                      >
                        {{ batchSelectedDocuments.find(d => d.id === docId)?.title }}
                        <button 
                          @click.stop="removeDocumentFromGroup(group.id, docId)"
                          class="ml-1 text-blue-500 hover:text-blue-700"
                        >
                          ×
                        </button>
                      </span>
                    </div>
                  </div>

                  <!-- 可用文件選擇器 -->
                  <div>
                    <select 
                      @change="addDocumentToGroup(group.id, parseInt($event.target.value)); $event.target.value = ''"
                      class="w-full text-xs border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="">+ 添加文件到此組合</option>
                      <option 
                        v-for="doc in batchSelectedDocuments.filter(d => !group.documents.includes(d.id))" 
                        :key="`group-${group.id}-available-${doc.id}`" 
                        :value="doc.id"
                      >
                        {{ doc.title }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- 統一預覽區域 -->
              <div class="mt-6">
                <div class="flex justify-between items-center mb-4">
                  <h4 class="text-lg font-medium text-gray-900">🔍 內容預覽</h4>
                  <div class="flex items-center space-x-3">
                    <!-- 中英文對照切換 -->
                    <label class="flex items-center text-sm text-gray-600">
                      <input 
                        v-model="showBilingualPreview" 
                        type="checkbox" 
                        class="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      >
                      {{ t('generate.bilingualPreview') }}
                    </label>
                    
                    <!-- 預覽區域開關 -->
                    <button 
                      @click="showPreview = !showPreview"
                      class="flex items-center text-sm text-gray-600 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100"
                    >
                      <svg v-if="showPreview" class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                      <svg v-else class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                      {{ showPreview ? t('generate.hidePreview') : t('generate.showPreview') }}
                    </button>
                  </div>
                </div>
                
                <div v-if="showPreview">
                  <!-- 文件配對預覽 -->
                <div v-if="selectedPairing && !selectedTemplateGroup" class="bg-gray-50 border rounded-lg p-4">
                  <div class="mb-3">
                    <div class="text-sm font-medium text-gray-900">📄 {{ getSelectedDocument()?.title }}</div>
                    <div class="text-xs text-gray-500">📝 {{ getSelectedTemplate()?.name }}</div>
                  </div>
                  <div class="max-h-96 overflow-y-auto border border-gray-200 bg-white p-4 rounded text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                    <div v-if="showBilingualPreview" class="space-y-4">
                      <!-- 中文版本 -->
                      <div class="border-b border-gray-100 pb-4">
                        <div class="text-xs font-semibold text-blue-600 mb-2">🇹🇼 中文版</div>
                        <div>{{ getPairingPreview() }}</div>
                      </div>
                      <!-- 英文版本 -->
                      <div>
                        <div class="text-xs font-semibold text-green-600 mb-2">🇺🇸 English Version</div>
                        <div>{{ getBilingualPairingPreview() }}</div>
                      </div>
                    </div>
                    <div v-else>
                      {{ getPairingPreview() }}
                    </div>
                  </div>
                  <div class="mt-3 text-sm text-gray-600 bg-white px-3 py-2 rounded border">
                    ⚡ 將生成 {{ getSelectedPairing()?.count || 1 }} 道題目
                  </div>
                </div>

                <!-- 模板組合預覽 -->
                <div v-else-if="selectedTemplateGroup" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div class="mb-3">
                    <div class="text-sm font-medium text-gray-900">
                      🎯 {{ templateDocumentPairings.find(g => g.id === selectedTemplateGroup)?.template_name }}
                    </div>
                    <div class="text-xs text-gray-600">
                      📑 {{ templateDocumentPairings.find(g => g.id === selectedTemplateGroup)?.documents.length }} 個文件組合
                      · {{ templateDocumentPairings.find(g => g.id === selectedTemplateGroup)?.subject }}
                    </div>
                  </div>
                  <div class="max-h-96 overflow-y-auto border border-gray-200 bg-white p-4 rounded text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                    <div v-if="showBilingualPreview" class="space-y-4">
                      <!-- 中文版本 -->
                      <div class="border-b border-gray-100 pb-4">
                        <div class="text-xs font-semibold text-blue-600 mb-2">🇹🇼 中文版</div>
                        <div>{{ getTemplateGroupPreview() }}</div>
                      </div>
                      <!-- 英文版本 -->
                      <div>
                        <div class="text-xs font-semibold text-green-600 mb-2">🇺🇸 English Version</div>
                        <div>{{ getBilingualTemplateGroupPreview() }}</div>
                      </div>
                    </div>
                    <div v-else>
                      {{ getTemplateGroupPreview() }}
                    </div>
                  </div>
                  <div class="mt-3 text-sm text-gray-600 bg-white px-3 py-2 rounded border">
                    ⚡ 將生成 {{ templateDocumentPairings.find(g => g.id === selectedTemplateGroup)?.count || 1 }} 道題目
                    · 📂 文件： {{ templateDocumentPairings.find(g => g.id === selectedTemplateGroup)?.documents.map(docId => batchSelectedDocuments.find(d => d.id === docId)?.title).join('、') }}
                  </div>
                </div>

                <!-- 空狀態 -->
                <div v-else class="text-center py-12 text-gray-400 border-2 border-dashed border-gray-200 rounded-lg">
                  <svg class="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  <p class="text-base font-medium">點擊配對或組合查看預覽</p>
                  <p class="text-sm mt-1">選擇文件配對或模板組合來預覽生成內容</p>
                </div>
                </div>
              </div>

            </div>
          </div>

          <!-- 批次生成按鈕 -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-600 space-y-1">
                <div v-if="getTotalPairings() > 0">
                  <span>📄文件配對: {{ getTotalPairings() }} 個</span>
                  <span class="mx-2">•</span>
                  <span>{{ getTotalQuestions() }} 題</span>
                </div>
                <div v-if="getTotalTemplateGroups() > 0">
                  <span>📝模板組合: {{ getTotalTemplateGroups() }} 個</span>
                  <span class="mx-2">•</span>
                  <span>{{ getTotalQuestionsFromGroups() }} 題</span>
                </div>
                <div class="font-medium text-purple-600">
                  總計預期: {{ getTotalQuestions() + getTotalQuestionsFromGroups() }} 題
                </div>
              </div>
              <button
                @click="generateBatchQuestions"
                :disabled="(!canGenerateBatch && templateDocumentPairings.length === 0) || generating"
                class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <svg v-if="generating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ generating ? t('generate.generating') || '生成中...' : t('generate.batchGenerate') || '批次生成' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 批次生成結果 -->
        <div v-if="batchGeneratedQuestions.length > 0" class="bg-white shadow rounded-lg p-6 mt-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium text-gray-900">
              {{ t('generate.batchResults') || '批次生成結果' }} ({{ batchGeneratedQuestions.length }}{{ t('generate.questions') || '題' }})
            </h2>
            <div class="flex space-x-2">
              <button
                @click="exportBatchQuestions"
                class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium"
              >
                {{ t('export') || '匯出' }}
              </button>
              <button
                @click="saveBatchQuestions"
                :disabled="saving"
                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50 flex items-center"
              >
                <svg v-if="saving" class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ saving ? (isEnglish ? 'Saving...' : '儲存中...') : t('save') || '儲存' }}
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <div
              v-for="(question, index) in batchGeneratedQuestions"
              :key="`batch-${index}`"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-start mb-2">
                <div class="flex items-center space-x-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {{ getQuestionTypeLabel(question.type) }} {{ index + 1 }}
                  </span>
                  <div v-if="question._meta" class="text-xs text-gray-500">
                    <span class="font-medium">{{ question._meta.documentName }}</span>
                    <span class="mx-1">•</span>
                    <span>{{ question._meta.templateName }}</span>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <h4 class="font-medium text-gray-900 mb-2">{{ question.prompt }}</h4>
                
                <div v-if="question.options" class="mb-2">
                  <ul class="space-y-1">
                    <li v-for="(option, optIndex) in question.options" :key="optIndex" class="text-sm text-gray-700">
                      {{ option }}
                    </li>
                  </ul>
                </div>
              </div>
              
              <div class="bg-gray-50 p-3 rounded">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                  <div>
                    <span class="font-medium text-gray-700">{{ t('generate.answer') || '答案' }}：</span>
                    <span class="text-gray-900">{{ question.answer }}</span>
                  </div>
                  <div v-if="question.source">
                    <span class="font-medium text-gray-700">{{ t('generate.source') || '來源' }}：</span>
                    <span class="text-gray-600">{{ t('generate.document') || '文件' }} {{ question.source.document_id }}</span>
                  </div>
                </div>
                <div class="mt-2">
                  <span class="font-medium text-gray-700">{{ t('generate.explanation') || '解釋' }}：</span>
                  <span class="text-gray-600">{{ question.explanation }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 進度對話框 -->
  <div v-if="showProgressDialog" class="fixed inset-0 z-50 overflow-y-auto" @click="$event.stopPropagation()">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      
      <!-- 進度對話框內容 -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="animate-spin h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ t('generate.generating') || '生成中...' }}
              </h3>
              <div class="mt-4">
                <!-- 進度條 -->
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    :style="{ width: generationProgress.total > 0 ? (generationProgress.current / generationProgress.total * 100) + '%' : '0%' }"
                  ></div>
                </div>
                <!-- 進度文字 -->
                <div class="mt-2 text-sm text-gray-600">
                  <div class="flex justify-between items-center">
                    <span>{{ generationProgress.current }} / {{ generationProgress.total }}</span>
                    <span>{{ generationProgress.total > 0 ? Math.round(generationProgress.current / generationProgress.total * 100) : 0 }}%</span>
                  </div>
                  <div class="mt-1 text-xs text-gray-500 truncate">
                    {{ generationProgress.currentTask }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 警告對話框 -->
  <div v-if="showWarningDialog" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showWarningDialog = false"></div>

      <!-- 警告對話框內容 -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <div class="sm:flex sm:items-start">
            <!-- 警告圖標 -->
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ currentWarning?.title || '警告' }}
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-600 whitespace-pre-line">
                  {{ currentWarning?.message }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            @click="showWarningDialog = false"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-yellow-600 text-base font-medium text-white hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            {{ t('close') || '關閉' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import templateService from '../api/templateService.js'
import subjectService from '../api/subjectService.js'
import documentService from '../api/documentService.js'
// import { generateQuestions, createQuestion } from '../api/questionService.js'
import { generateQuestionsByPrompt, generateQuestionsByTemplateEnhanced, createQuestion } from '../api/questionService.js'
import { useLanguage } from '../composables/useLanguage.js'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'

export default {
  name: 'Generate',
  setup() {
    // 多語言支持
    const { t, isEnglish, currentLanguage } = useLanguage()
    
    // 基本狀態
    const generating = ref(false)
    const saving = ref(false)
    const loadingTemplates = ref(false)
    const loadingDocuments = ref(false)
    const showPreview = ref(true) // 預覽區域顯示控制
    const showBilingualPreview = ref(false) // 中英文對照顯示控制
    const showExamPreview = ref(false) // 考卷預覽模式控制
    
    // 進度顯示相關狀態
    const generationProgress = ref({ current: 0, total: 0, currentTask: '' })
    const showProgressDialog = ref(false)
    
    // 模板相關
    const templates = ref([])
    const subjects = ref([]) // 用於篩選器的科目名稱陣列
    const subjectList = ref([]) // 用於顏色顯示的完整科目資料
    const selectedSubject = ref('')
    const selectedTemplate = ref(null) // 保留用於預覽
    
    // 考卷資料配置
    const examData = reactive({
      school: 'Abraham Academy',
      title: '2024 Semester 2 Science Midterm Exam',
      subtitle: '(Understanding God\'s World pp. 115-171)'
    })
    
    // 為每個題型選擇的模板
    const selectedTemplates = reactive({
      single_choice: null,
      cloze: null,
      short_answer: null
    })
    
    // 文件相關
    const documents = ref([])
    const selectedDocuments = ref([])  // 傳統生成用
    const documentSearchQuery = ref('')
    const selectedDocumentSubject = ref('')  // 文件科目篩選
    const selectedDocumentGrade = ref('')    // 文件年級篩選
    const documentSubjects = ref([])         // 文件科目清單
    const traditionalCount = ref(1)  // 傳統生成數量
    // selectedQuestionType 已移除，現在使用模板的 question_type 屬性

    // 批次生成的獨立文件選擇
    const batchSelectedDocuments = ref([])  // 批次生成專用
    const batchDocumentSearchQuery = ref('')
    
    // 統一文件選擇功能
    const createDocumentSelector = (selectedDocs, searchQuery, subjectFilter = null, gradeFilter = null) => {
      const toggleSelection = (document) => {
        const index = selectedDocs.value.findIndex(d => d.id === document.id)
        if (index > -1) {
          selectedDocs.value.splice(index, 1)
        } else {
          selectedDocs.value.push(document)
        }
      }

      const filteredDocs = computed(() => {
        let filtered = documents.value

        // 科目篩選
        if (subjectFilter && subjectFilter.value) {
          filtered = filtered.filter(doc => doc.subject === subjectFilter.value)
        }

        // 年級篩選
        if (gradeFilter && gradeFilter.value) {
          filtered = filtered.filter(doc => doc.grade === gradeFilter.value)
        }

        // 文字搜尋
        if (searchQuery.value) {
          const query = searchQuery.value.toLowerCase()
          filtered = filtered.filter(doc =>
            doc.title.toLowerCase().includes(query) ||
            (doc.chapter && doc.chapter.toLowerCase().includes(query))
          )
        }

        return filtered
      })

      return { toggleSelection, filteredDocs }
    }
    
    // 統一 Prompt 組合功能
    const buildPrompt = (template, documents, count, questionType = null) => {
      const documentsContent = documents.map(doc => 
        `Document: ${doc.title}\ncontent: ${doc.content}`
      ).join('\n\n')
      
      const fullPrompt = template.content
        .replace('{context}', documentsContent)
        .replace('{count}', traditionalCount.value)
      
      const jsonFormat = `[
  {
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }
]`
      
      let typeHint = ''
      if (questionType) {
        typeHint = `\n\n請特別注意生成${questionType === 'single_choice' ? '單選題' : questionType === 'cloze' ? '填空題' : '簡答題'}類型的問題。`
      }
      
      return `${fullPrompt}\n\n請生成${count}道題目，並以 JSON 格式回傳，格式如下：\n\n${jsonFormat}\n\n請確保生成的是有效的 JSON 格式。${typeHint}`
    }
    
    // 統一題目儲存功能
    const saveQuestionsBatch = async (questionsArray, sourceInfo) => {
      const results = { success: [], failed: [] }
      for (const [index, question] of questionsArray.entries()) {
        try {
          const questionData = {
            type: question.type || 'single_choice',
            content: question.content || question.prompt || question.question || question.text || '',
            options: question.options || null,
            correct_answer: question.answer,
            explanation: question.explanation || '',
            source_document_id: sourceInfo.documentId,
            source_content: sourceInfo.content,
            subject: sourceInfo.subject || 'General',
            chapter: sourceInfo.chapter,
            difficulty: 'medium'
          }
          
          await createQuestion(questionData)
          results.success.push({ index: index + 1, question: question.prompt.substring(0, 50) + '...' })
          
        } catch (error) {
          console.error(`❌ 儲存第 ${index + 1} 題失敗:`, error)
          results.failed.push({ 
            index: index + 1, 
            question: question.prompt.substring(0, 50) + '...', 
            error: error.response?.data?.detail || error.message 
          })
        }
      }
      
      return results
    }
    
    // 題型設定 - 每個題型的數量和模板選擇
    const questionTypes = reactive({
      single_choice: 3,
      cloze: 2,
      short_answer: 1
    })
    
    // 新的批次生成配對系統
    // 舊的配對系統（保留過渡期）
    const documentTemplatePairings = ref([])  // { document_id, template_id, count }
    const selectedPairing = ref(null)  // { document_id, template_id }
    
    // 新的配對系統 - 支援模板對多文件
    const templateDocumentPairings = ref([])  // { id, template_id, template_name, subject, documents: [doc_ids], count }
    const selectedTemplateGroup = ref(null)  // 選中的模板組合ID
    
    // 舊的批次生成配置（保留用於兼容性）
    
    // 生成結果
    const generatedQuestions = ref([])
    const batchGeneratedQuestions = ref([])  // 批次生成的獨立結果

    // 錯誤狀態管理
    const errors = ref({
      documents: null,
      templates: null,
      subjects: null,
      generation: null
    })

    const showErrorDialog = ref(false)
    const showWarningDialog = ref(false)
    const currentError = ref(null)
    const currentWarning = ref(null)

    // 錯誤處理方法
    const showError = (title, message, detail = null) => {
      currentError.value = { title, message, detail }
      showErrorDialog.value = true
      console.error(`${title}: ${message}`, detail)
    }

    // 警告通知方法
    const showWarning = (title, message) => {
      currentWarning.value = { title, message }
      showWarningDialog.value = true
      console.warn(`${title}: ${message}`)
    }

    const clearError = (errorType) => {
      if (errors.value[errorType]) {
        errors.value[errorType] = null
      }
    }

    // 計算屬性
    const filteredTemplates = computed(() => {
      if (!selectedSubject.value) return templates.value
      return templates.value.filter(template => template.subject === selectedSubject.value)
    })

    // 使用統一的文件選擇器
    const traditionalDocumentSelector = createDocumentSelector(
      selectedDocuments,
      documentSearchQuery,
      selectedDocumentSubject,
      selectedDocumentGrade
    )
    const batchDocumentSelector = createDocumentSelector(batchSelectedDocuments, batchDocumentSearchQuery)

    const filteredDocuments = traditionalDocumentSelector.filteredDocs

    const totalQuestions = computed(() => {
      return Object.values(questionTypes).reduce((sum, count) => sum + count, 0)
    })

    const canGenerate = computed(() => {
      // 檢查所有需要的題型是否都選擇了模板
      const hasRequiredTemplates = Object.entries(questionTypes).every(([type, count]) => {
        return count === 0 || selectedTemplates[type] !== null
      })
      
      return hasRequiredTemplates && 
             selectedDocuments.value.length > 0 && 
             totalQuestions.value > 0
    })

    const previewContent = computed(() => {
      if (!selectedTemplate.value?.content) return ''
      
      let contextContent = '範例文章內容...'
      
      if (selectedDocuments.value.length > 0) {
        // 顯示所有選中文件的完整內容
        contextContent = selectedDocuments.value.map(doc => {
          return `=== ${doc.title} ===\n${doc.chapter ? `章節: ${doc.chapter}\n` : ''}${doc.content}`
        }).join('\n\n')
      }
      
      return selectedTemplate.value.content
        .replace('{context}', contextContent)
        .replace('{count}', traditionalCount.value)
    })

    // 批次生成相關計算屬性

    const canGenerateBatch = computed(() => {
      // 使用新的配對系統邏輯
      return documentTemplatePairings.value.length > 0 && 
             documentTemplatePairings.value.some(p => p.count > 0)
    })

    // 方法
    const fetchTemplates = async () => {
      loadingTemplates.value = true
      try {
        const params = selectedSubject.value ? { subject: selectedSubject.value } : {}
        const data = await templateService.getTemplates(params)
        templates.value = data.templates || []
      } catch (error) {
        console.error('取得模板清單失敗:', error)
        errors.value.templates = {
          message: '無法載入模板清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        templates.value = []
        showError('模板載入失敗', '無法從伺服器取得模板清單，請檢查網路連線或聯絡系統管理員。', error.response?.data)
      } finally {
        loadingTemplates.value = false
      }
    }

    const refreshTemplates = async () => {
      console.log('🔄 [Generate] 手動重新載入模板...')
      const previousSelected = selectedTemplate.value
      await fetchTemplates()
      
      // 如果之前有選擇模板，重新設定選擇（獲取最新資料）
      if (previousSelected) {
        const updatedTemplate = templates.value.find(t => t.id === previousSelected.id)
        if (updatedTemplate) {
          console.log('🔄 [Generate] 重新選擇模板以獲取最新參數')
          console.log('📊 [Generate] 舊模板參數:', previousSelected.params)
          console.log('📊 [Generate] 新模板參數:', updatedTemplate.params)
          selectedTemplate.value = updatedTemplate
        }
      }
      
    }

    // 取得篩選器用的科目名稱清單
    const fetchSubjects = async () => {
      try {
        const data = await templateService.getSubjects()
        subjects.value = data.subjects || []
      } catch (error) {
        console.error('取得科目清單失敗:', error)
        errors.value.subjects = {
          message: '無法載入科目清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        subjects.value = []
        showError('科目載入失敗', '無法從伺服器取得科目清單，請檢查網路連線。', error.response?.data)
      }
    }

    // 取得完整的科目資料（包含顏色）
    const fetchSubjectList = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectList.value = data.subjects || []
      } catch (error) {
        console.error('取得完整科目資料失敗:', error)
        subjectList.value = []
      }
    }

    const fetchDocuments = async () => {
      loadingDocuments.value = true
      try {
        // 請求最多 100 個文件（後端允許的最大值）
        const data = await documentService.getDocuments({ size: 100 })
        documents.value = data.documents || []

        // 提取文件的科目清單（去重）
        const subjects = new Set()
        documents.value.forEach(doc => {
          if (doc.subject) {
            subjects.add(doc.subject)
          }
        })
        documentSubjects.value = Array.from(subjects).sort()

      } catch (error) {
        console.error('取得文件清單失敗:', error)
        errors.value.documents = {
          message: '無法載入文件清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        documents.value = []
        documentSubjects.value = []
        showError('文件載入失敗', '無法從伺服器取得文件清單，請檢查網路連線或確認已上傳文件。', error.response?.data)
      } finally {
        loadingDocuments.value = false
      }
    }

    const searchDocuments = () => {
      // 搜尋功能由 computed 屬性 filteredDocuments 處理
    }

    const selectTemplate = (template) => {
      console.log('🎯 [Generate] 選擇模板:', template)
      console.log('📝 [Generate] 模板詳細資料:', {
        id: template.id,
        name: template.name,
        subject: template.subject,
        params: template.params,
        hasParams: !!template.params,
        paramsType: typeof template.params,
        paramsContent: JSON.stringify(template.params, null, 2)
      })
      selectedTemplate.value = template
    }

    const selectDocument = (document) => {
      toggleDocumentSelection(document)
    }

    const toggleDocumentSelection = traditionalDocumentSelector.toggleSelection

    // 傳統生成方法 - 使用完整模板資訊
    const generateTraditionalQuestions = async () => {
      if (!selectedTemplate.value || selectedDocuments.value.length === 0) return
      
      generating.value = true
      try {
        // 準備完整的模板資訊
        
        const templateData = {
          id: selectedTemplate.value.id,
          name: selectedTemplate.value.name,
          content: selectedTemplate.value.content,
          subject: selectedTemplate.value.subject,
          params: selectedTemplate.value.params || {},
          created_at: selectedTemplate.value.created_at,
          updated_at: selectedTemplate.value.updated_at
        }
        
        
        // 準備文件資訊
        const documentsData = selectedDocuments.value.map(doc => ({
          id: doc.id,
          title: doc.title,
          content: doc.content,
          chapter: doc.chapter,
          page: doc.page,
          subject: doc.subject
        }))
        
        // 使用新的 enhanced API
        const requestData = {
          template: templateData,
          documents: documentsData,
          count: traditionalCount.value,
          question_type: selectedTemplate.value.question_type || 'single_choice',  // 使用模板的題型
          temperature: 0.7,
          max_tokens: 2000,
          model: 'claude-3-5-sonnet-20241022'
        }
        
        
        // 呼叫 Enhanced Template 驅動生成 API
        const response = await generateQuestionsByTemplateEnhanced(requestData)

        if (response.data && response.data.items) {
          generatedQuestions.value = response.data.items

          // 檢查是否有警告訊息
          if (response.data.warning) {
            showWarning('題目生成警告', response.data.warning)
          }

          // 如果是 fallback（完全失敗），顯示錯誤
          if (response.data.is_fallback) {
            showError('題目生成失敗', response.data.warning || '無法從所選文件生成有效題目')
          }
        } else {
          throw new Error('API 回應格式不正確')
        }
        
      } catch (error) {
        
        // 處理生成失敗
        errors.value.generation = {
          message: '題目生成失敗',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'ENHANCED_GENERATION_ERROR'
        }
        generatedQuestions.value = []
        showError('題目生成失敗', 
          `使用模板「${selectedTemplate.value.name}」生成題目時發生錯誤。\n請檢查：\n1. 網路連線是否正常\n2. 後端服務是否運行\n3. API 配置是否正確`,
          error.response?.data
        )
      } finally {
        generating.value = false
      }
    }

    // 批次生成方法
    const generateQuestions = async () => {
      if (!canGenerateBatch.value) return

      generating.value = true
      batchGeneratedQuestions.value = []  // 清空之前的結果
      
      try {
        console.log('開始批次生成題目')
        console.log('選中的文件數量:', selectedDocuments.value.length)
        console.log('文件配對:', documentTemplatePairings.value)
        
        const allBatchQuestions = []
        
        // 逐個處理每個文件-模板配對
        for (const pairing of documentTemplatePairings.value) {
          if (!pairing.document || !pairing.template) continue
          
          try {
            console.log(`處理配對: 文件${pairing.document.id} + 模板${pairing.template.id}`)
            
            // 組合完整的 prompt（與單次生成相同邏輯）
            const templateContent = pairing.template.content
            const documentContent = pairing.document.content
            const fullPrompt = templateContent
              .replace('{{context}}', documentContent)
              .replace('{context}', documentContent)
              .replace('{{count}}', pairing.count)
              .replace('{count}', pairing.count)
            
            const totalCount = questionTypes.single_choice + questionTypes.cloze + questionTypes.short_answer
            
            const completePrompt = `${fullPrompt}

請生成${totalCount}道題目，並以 JSON 格式回傳，格式如下：

[
  {
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }
]

請確保生成的是有效的 JSON 格式。`
            
            console.log(`發送 prompt 給配對 ${pairing.document.id}-${pairing.template.id}:`, completePrompt.substring(0, 200) + '...')
            
            // 呼叫單次生成 API
            const response = await generateQuestionsByPrompt({
              prompt: completePrompt,
              count: totalCount,
              temperature: 0.7,
              max_tokens: 4000,
              model: 'claude-3-5-sonnet-20241022'
            })
            
            if (response.data.items) {
              // 標記每個題目來自哪個配對
              const questionsWithMeta = response.data.items.map(item => ({
                ...item,
                _meta: {
                  documentName: pairing.document.title,
                  templateName: pairing.template.name,
                  documentId: pairing.document.id,
                  templateId: pairing.template.id
                }
              }))
              allBatchQuestions.push(...questionsWithMeta)
              console.log(`配對 ${pairing.document.id}-${pairing.template.id} 生成成功，題目數量:`, questionsWithMeta.length)
            }
          } catch (pairError) {
            console.error(`配對 ${pairing.document.id}-${pairing.template.id} 生成失敗:`, pairError)
          }
        }
        
        batchGeneratedQuestions.value = allBatchQuestions
        console.log('批次生成完成，總題目數量:', allBatchQuestions.length)
        
      } catch (error) {
        console.error('批次生成題目失敗:', error)
        
        // 處理批次生成失敗
        errors.value.generation = {
          message: '批次生成失敗',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'BATCH_GENERATION_ERROR'
        }
        
        batchGeneratedQuestions.value = []
        showError('批次生成失敗', 
          '批次生成題目時發生錯誤，請檢查網路連線和後端服務狀態。',
          error.response?.data
        )
      } finally {
        generating.value = false
        
        // 滾動到結果區域
        setTimeout(() => {
          const resultElement = document.querySelector('.space-y-4')?.closest('.bg-white')
          if (resultElement) {
            resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
      }
    }

    const exportQuestions = () => {
      // 實作匯出功能
      const jsonContent = JSON.stringify(generatedQuestions.value, null, 2)
      const blob = new Blob([jsonContent], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `questions_${new Date().getTime()}.json`
      a.click()
      URL.revokeObjectURL(url)
    }

    const saveQuestions = async () => {
      if (generatedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: isEnglish.value ? 'No questions to save!' : '沒有題目可儲存！',
          operation: '儲存題目'
        })
        return
      }

      saving.value = true
      try {
        // 獲取文件內容作為 source_content
        let sourceContent = '傳統生成'
        if (selectedDocuments.value.length > 0) {
          sourceContent = selectedDocuments.value.map(doc => 
            `Document: ${doc.title}\nContent: ${doc.content}`
          ).join('\n\n')
        }
        
        const sourceInfo = {
          documentId: selectedDocuments.value.length > 0 ? selectedDocuments.value[0].id : null,
          content: sourceContent,
          subject: selectedTemplate.value?.subject || 'General',
          chapter: selectedDocuments.value.length > 0 ? selectedDocuments.value[0].chapter : null
        }
        
        const results = await saveQuestionsBatch(generatedQuestions.value, sourceInfo)
        const totalQuestions = generatedQuestions.value.length
        const successCount = results.success.length
        
        // 顯示結果
        if (successCount === totalQuestions) {
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: isEnglish.value 
              ? `Successfully saved all ${totalQuestions} questions!` 
              : `成功儲存全部 ${totalQuestions} 道題目！`,
            operation: '儲存題目'
          })
        } else if (successCount > 0) {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.question} (${f.error})`).join('\n')
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: isEnglish.value
              ? `Saved ${successCount}/${totalQuestions} questions.\n\nFailed questions:\n${failedDetails}`
              : `儲存了 ${successCount}/${totalQuestions} 道題目。\n\n失敗的題目：\n${failedDetails}`,
            operation: '儲存題目'
          })
        } else {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.error}`).join('\n')
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: isEnglish.value
              ? `Failed to save any questions.\n\nErrors:\n${failedDetails}`
              : `所有題目儲存失敗。\n\n錯誤詳情：\n${failedDetails}`,
            operation: '儲存題目'
          })
        }

      } catch (error) {
        console.error('儲存問題時發生未預期的錯誤:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: isEnglish.value 
            ? 'An unexpected error occurred while saving questions.' 
            : '儲存問題時發生未預期的錯誤。',
          operation: '儲存題目',
          error
        })
      } finally {
        saving.value = false
      }
    }

    // 工具函數
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

    const getSubjectStyle = (subject) => {
      const subjectData = subjectList.value.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return {
          backgroundColor: subjectData.color,
          color: getTextColor(subjectData.color)
        }
      }
      return null
    }

    const getTextColor = (backgroundColor) => {
      const hex = backgroundColor.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)
      const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
      return brightness > 155 ? '#000000' : '#FFFFFF'
    }

    const getSubjectColor = (subject) => {
      // 從科目清單中查找對應的科目顏色，如果沒有找到就使用預設顏色
      const subjectData = subjectList.value.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return '' // 當有自定義顏色時，class 為空，使用 style
      }
      // 備用顏色方案（當科目資料庫中沒有顏色時）
      return 'bg-gray-100 text-gray-800'
    }

    const getSubjectDisplayName = (subjectNameOrTemplate) => {
      // 處理模板物件或純科目名稱
      let subjectToLookup = subjectNameOrTemplate
      let subjectId = null

      if (typeof subjectNameOrTemplate === 'object' && subjectNameOrTemplate !== null) {
        // 是模板物件
        subjectId = subjectNameOrTemplate.subject_id
        subjectToLookup = subjectNameOrTemplate.subject
      }

      // 優先使用 subject_id 查找
      if (subjectId) {
        const subjectData = subjectList.value.find(s => s.id === subjectId)
        if (subjectData) {
          return subjectData.grade ? `${subjectData.name} (${subjectData.grade})` : subjectData.name
        }
      }

      // Fallback: 使用科目名稱查找
      if (subjectToLookup) {
        const subjectData = subjectList.value.find(s => s.name === subjectToLookup)
        if (subjectData && subjectData.grade) {
          return `${subjectToLookup} (${subjectData.grade})`
        }
      }

      // 最後 fallback: 直接返回科目名稱
      return subjectToLookup || 'Unknown'
    }

    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || '未指定'
      
      // 使用 i18n 翻譯系統
      const typeKey = type.replace(/_/g, '_')
      const translationKey = `questions.${typeKey}`
      const translation = t(translationKey)
      
      // 如果有翻譯就用，沒有就顯示原始值
      return translation !== translationKey ? translation : type
    }

    // 為特定題型選擇模板
    const selectTemplateForType = (template, questionType) => {
      selectedTemplates[questionType] = template
    }

    // 批次文件選擇相關方法
    const filteredBatchDocuments = batchDocumentSelector.filteredDocs

    const toggleBatchDocumentSelection = (document) => {
      batchDocumentSelector.toggleSelection(document)
      // 如果移除文件，也移除與該文件相關的配對
      const isSelected = batchSelectedDocuments.value.some(d => d.id === document.id)
      if (!isSelected) {
        documentTemplatePairings.value = documentTemplatePairings.value.filter(p => p.document_id !== document.id)
      }
    }

    // 新的模板組合管理方法
    const createTemplateGroup = (templateId) => {
      console.log('🎯 建立模板組合，templateId:', templateId)
      
      // 確保 templateId 是數字
      const numericTemplateId = parseInt(templateId)
      if (!numericTemplateId) {
        console.log('❌ templateId 無效:', templateId)
        return
      }
      
      const template = getTemplate(numericTemplateId)
      console.log('📝 找到模板:', template)
      
      if (!template) {
        console.log('❌ 找不到模板，templateId:', numericTemplateId)
        return
      }
      
      const newGroup = {
        id: Date.now(), // 簡單的ID生成
        template_id: numericTemplateId,
        template_name: template.name,
        subject: template.subject,
        subject_display: getSubjectDisplayName(template),
        documents: [],
        count: 1
      }
      
      templateDocumentPairings.value.push(newGroup)
      console.log('✅ 成功建立模板組合:', newGroup)
      console.log('📊 當前所有組合:', templateDocumentPairings.value)
      
      return newGroup
    }

    const addDocumentToGroup = (groupId, documentId) => {
      const group = templateDocumentPairings.value.find(g => g.id === groupId)
      if (group && !group.documents.includes(documentId)) {
        group.documents.push(documentId)
      }
    }

    const removeDocumentFromGroup = (groupId, documentId) => {
      const group = templateDocumentPairings.value.find(g => g.id === groupId)
      if (group) {
        group.documents = group.documents.filter(id => id !== documentId)
        // 如果組裡沒有文件了，刪除整個組
        if (group.documents.length === 0) {
          templateDocumentPairings.value = templateDocumentPairings.value.filter(g => g.id !== groupId)
          if (selectedTemplateGroup.value === groupId) {
            selectedTemplateGroup.value = null
          }
        }
      }
    }

    const removeTemplateGroup = (groupId) => {
      templateDocumentPairings.value = templateDocumentPairings.value.filter(g => g.id !== groupId)
      if (selectedTemplateGroup.value === groupId) {
        selectedTemplateGroup.value = null
      }
    }

    const getTemplateGroupPreview = () => {
      if (!selectedTemplateGroup.value) return ''
      
      const group = templateDocumentPairings.value.find(g => g.id === selectedTemplateGroup.value)
      if (!group || group.documents.length === 0) return ''
      
      const template = getTemplate(group.template_id)
      if (!template) return ''
      
      // 將所有選中的文件合併為一個context
      const documents = group.documents
        .map(docId => batchSelectedDocuments.value.find(d => d.id === docId))
        .filter(Boolean)
      
      if (documents.length === 0) return ''
      
      let contextContent = documents.map(doc => 
        `=== ${doc.title} ===\n${doc.chapter ? `章節: ${doc.chapter}\n` : ''}${doc.content}`
      ).join('\n\n---\n\n')
      
      return template.content
        .replace('{context}', contextContent)
        .replace('{count}', group.count || 1)
    }

    const getTotalTemplateGroups = () => {
      return templateDocumentPairings.value.length
    }

    const getTotalQuestionsFromGroups = () => {
      return templateDocumentPairings.value.reduce((sum, group) => sum + group.count, 0)
    }

    // 舊的文件-模板配對方法（保留過渡期）
    const getDocumentPairings = (documentId) => {
      return documentTemplatePairings.value.filter(p => p.document_id === documentId)
    }

    const getTemplate = (templateId) => {
      return templates.value.find(t => t.id === templateId)
    }

    const getAvailableTemplates = (documentId) => {
      const usedTemplateIds = getDocumentPairings(documentId).map(p => p.template_id)
      return templates.value.filter(t => !usedTemplateIds.includes(t.id))
    }

    const addPairing = (documentId, templateId, event = null) => {
      console.log('🔗 嘗試添加配對:', { documentId, templateId })
      if (!templateId) {
        console.log('❌ templateId 為空，退出')
        return
      }
      
      // 檢查是否已存在相同配對
      const exists = documentTemplatePairings.value.some(p => 
        p.document_id === documentId && p.template_id === parseInt(templateId)
      )
      
      if (!exists) {
        const newPairing = {
          document_id: documentId,
          template_id: parseInt(templateId),
          count: 1
        }
        documentTemplatePairings.value.push(newPairing)
      } else {
      }
      
      // 重置下拉選單
      if (event && event.target) {
        event.target.value = ''
      }
    }

    const removePairing = (documentId, templateId) => {
      const index = documentTemplatePairings.value.findIndex(p => 
        p.document_id === documentId && p.template_id === templateId
      )
      if (index > -1) {
        documentTemplatePairings.value.splice(index, 1)
      }
      
      // 如果刪除的是當前選中的配對，清除選中狀態
      if (selectedPairing.value?.document_id === documentId && selectedPairing.value?.template_id === templateId) {
        selectedPairing.value = null
      }
    }

    const selectPairing = (documentId, templateId) => {
      selectedPairing.value = {
        document_id: documentId,
        template_id: templateId
      }
      // 清空模板組合選擇，確保只有一個預覽顯示
      selectedTemplateGroup.value = null
    }

    const getSelectedDocument = () => {
      if (!selectedPairing.value) return null
      return batchSelectedDocuments.value.find(d => d.id === selectedPairing.value.document_id)
    }

    const getSelectedTemplate = () => {
      if (!selectedPairing.value) return null
      return getTemplate(selectedPairing.value.template_id)
    }

    const getSelectedPairing = () => {
      if (!selectedPairing.value) return null
      return documentTemplatePairings.value.find(p => 
        p.document_id === selectedPairing.value.document_id && 
        p.template_id === selectedPairing.value.template_id
      )
    }

    const getPairingPreview = () => {
      const document = getSelectedDocument()
      const template = getSelectedTemplate()
      
      if (!document || !template) return ''
      
      let contextContent = `=== ${document.title} ===\n${document.chapter ? `章節: ${document.chapter}\n` : ''}${document.content}`
      
      const pairing = documentTemplatePairings.value.find(p => p.document_id === document.id && p.template_id === template.id)
      const count = pairing ? pairing.count : 1
      
      return template.content
        .replace('{context}', contextContent)
        .replace('{count}', count)
    }

    const getTotalPairings = () => {
      return documentTemplatePairings.value.length
    }

    const getTotalQuestions = () => {
      return documentTemplatePairings.value.reduce((sum, pairing) => sum + pairing.count, 0)
    }

    const generateBatchQuestions = async () => {
      
      // 檢查是否有任何配對系統可用
      const hasDocumentPairings = canGenerateBatch.value
      const hasTemplateGroups = templateDocumentPairings.value.length > 0 && 
                                 templateDocumentPairings.value.some(g => g.documents.length > 0 && g.count > 0)
      
      if (!hasDocumentPairings && !hasTemplateGroups) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '請先選擇文件並創建配對組合（文件配對或模板組合），並確保數量大於0',
          operation: '批次生成'
        })
        return
      }

      // 保存傳統生成的原始狀態
      const originalSelectedTemplate = selectedTemplate.value
      const originalSelectedDocuments = [...selectedDocuments.value]
      const originalTraditionalCount = traditionalCount.value
      // 不需要備份 selectedQuestionType，因為現在使用模板的 question_type

      generating.value = true
      batchGeneratedQuestions.value = []  // 清空之前的結果
      
      // 計算總任務數量
      const totalTasks = documentTemplatePairings.value.length + templateDocumentPairings.value.filter(g => g.documents.length > 0 && g.count > 0).length
      generationProgress.value = { current: 0, total: totalTasks, currentTask: '' }
      showProgressDialog.value = true
      
      try {
        
        const allBatchQuestions = []
        
        // 逐個處理每個文件-模板配對
        for (const pairing of documentTemplatePairings.value) {
          const template = getTemplate(pairing.template_id)
          const document = batchSelectedDocuments.value.find(d => d.id === pairing.document_id)
         
          if (!template || !document) continue
          
          // 更新當前任務（但不增加進度）
          generationProgress.value.currentTask = `生成中: ${document.title} × ${template.name}`
          
          try {
            
            // 設置傳統生成的狀態來重用 generateTraditionalQuestions
            selectedTemplate.value = template
            selectedDocuments.value = [document]
            traditionalCount.value = pairing.count
            // 題型由模板決定，不需要設定 selectedQuestionType
            
            
            // 呼叫傳統生成函數（會使用完整的模板參數和 Enhanced Template API）
            await generateTraditionalQuestions()
            
            // 收集結果並加上批次元數據
            if (generatedQuestions.value.length > 0) {
              const questionsWithMeta = generatedQuestions.value.map(item => ({
                ...item,
                _meta: {
                  documentName: document.title,
                  templateName: template.name,
                  documentId: document.id,
                  templateId: template.id,
                  templateParams: template.params, // 保存使用的模板參數
                  documentSubject: document.subject,
                  documentChapter: document.chapter
                }
              }))
              allBatchQuestions.push(...questionsWithMeta)
              
              // 清空 generatedQuestions 為下次循環做準備
              generatedQuestions.value = []
              
              // 題目生成成功後更新進度
              generationProgress.value.current++
              generationProgress.value.currentTask = `✅ 完成: ${document.title} × ${template.name} (${questionsWithMeta.length}題)`
            } else {
              // 即使沒有生成題目，也要更新進度
              generationProgress.value.current++
              generationProgress.value.currentTask = `⚠️ 無題目生成: ${document.title} × ${template.name}`
            }
          } catch (pairError) {
            // 發生錯誤時也要更新進度
            generationProgress.value.current++
            generationProgress.value.currentTask = `❌ 失敗: ${document.title} × ${template.name}`
          }
        }
        
        // 處理新的模板組合系統
        for (const group of templateDocumentPairings.value) {
          if (group.documents.length === 0 || group.count === 0) continue
          
          const template = getTemplate(group.template_id)
          if (!template) continue
          
          // 更新當前任務（但不增加進度）
          generationProgress.value.currentTask = `生成中: ${template.name} × ${group.documents.length}個文件組合`
          
          try {
            // 獲取組合中的所有文件
            const documents = group.documents
              .map(docId => batchSelectedDocuments.value.find(d => d.id === docId))
              .filter(Boolean)
            
            if (documents.length === 0) {
              // 沒有有效文件時也要更新進度
              generationProgress.value.current++
              generationProgress.value.currentTask = `⚠️ 無有效文件: ${template.name}`
              continue
            }
            
            // 設置傳統生成的狀態來重用 generateTraditionalQuestions
            selectedTemplate.value = template
            selectedDocuments.value = documents // 一次傳入多個文件
            traditionalCount.value = group.count
            // 題型由模板決定，不需要設定 selectedQuestionType
            
            // 呼叫傳統生成函數（會使用完整的模板參數和 Enhanced Template API）
            await generateTraditionalQuestions()
            
            // 收集結果並加上批次元數據
            if (generatedQuestions.value.length > 0) {
              const questionsWithMeta = generatedQuestions.value.map(item => ({
                ...item,
                _meta: {
                  templateGroupId: group.id,
                  templateName: group.template_name,
                  templateId: group.template_id,
                  templateParams: template.params,
                  templateSubject: group.subject,
                  documentCount: documents.length,
                  documentNames: documents.map(d => d.title).join(', '),
                  documentIds: documents.map(d => d.id),
                  generationType: 'template-group' // 標記為模板組合生成
                }
              }))
              allBatchQuestions.push(...questionsWithMeta)
              
              // 清空 generatedQuestions 為下次循環做準備
              generatedQuestions.value = []
              
              // 題目生成成功後更新進度
              generationProgress.value.current++
              generationProgress.value.currentTask = `✅ 完成組合: ${template.name} × ${documents.length}個文件 (${questionsWithMeta.length}題)`
            } else {
              // 即使沒有生成題目，也要更新進度
              generationProgress.value.current++
              generationProgress.value.currentTask = `⚠️ 無題目生成: ${template.name} 組合`
            }
          } catch (groupError) {
            // 發生錯誤時也要更新進度
            generationProgress.value.current++
            generationProgress.value.currentTask = `❌ 組合失敗: ${template.name}`
            console.error(`處理模板組合 ${group.template_name} 失敗:`, groupError)
          }
        }
        
        batchGeneratedQuestions.value = allBatchQuestions
        
        // 所有任務完成，顯示最終狀態
        generationProgress.value.currentTask = `🎉 批次生成完成！共生成 ${allBatchQuestions.length} 道題目`
        
        // 短暫顯示完成狀態
        await new Promise(resolve => setTimeout(resolve, 1000))
        
      } catch (error) {
        
        // 處理批次配對生成失敗
        errors.value.generation = {
          message: '批次配對生成失敗',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'BATCH_PAIRING_ERROR'
        }
        
        batchGeneratedQuestions.value = []
        showError('批次配對生成失敗', 
          '使用文件模板配對生成題目時發生錯誤，請檢查網路連線和後端服務狀態。',
          error.response?.data
        )
      } finally {
        // 關閉進度對話框
        showProgressDialog.value = false
        generationProgress.value = { current: 0, total: 0, currentTask: '' }
        
        // 恢復傳統生成的原始狀態
        selectedTemplate.value = originalSelectedTemplate
        selectedDocuments.value = originalSelectedDocuments
        traditionalCount.value = originalTraditionalCount
        // 不需要恢復 selectedQuestionType，因為現在使用模板的 question_type
        
        generating.value = false
        
        // 滾動到結果區域
        setTimeout(() => {
          const resultElement = document.querySelector('.space-y-4')?.closest('.bg-white')
          if (resultElement) {
            resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
      }
    }

    
    // 匯出批次結果
    const exportBatchQuestions = () => {
      if (batchGeneratedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('generate.noResults') || '沒有可匯出的結果',
          operation: '匯出題目'
        })
        return
      }
      
      const jsonContent = JSON.stringify(batchGeneratedQuestions.value, null, 2)
      const blob = new Blob([jsonContent], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `batch_generated_questions_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
    
    // 儲存批次結果到資料庫
    const saveBatchQuestions = async () => {
      if (batchGeneratedQuestions.value.length === 0) {
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: t('generate.noResults') || '沒有可儲存的結果',
          operation: '儲存批次題目'
        })
        return
      }
      
      saving.value = true
      try {
        
        // 批次生成不指定單一文件，每個問題都有自己的 sourceInfo
        
        // 為批次問題增加詳細的 meta 資訊到 sourceInfo
        const questionsWithSourceInfo = batchGeneratedQuestions.value.map(question => {
          let sourceInfo
          
          if (question._meta?.generationType === 'template-group') {
            // 模板組合生成：處理多個文件
            const documentIds = question._meta?.documentIds || []
            const documents = documentIds
              .map(id => batchSelectedDocuments.value.find(d => d.id === id))
              .filter(Boolean)
            
            // 將所有文件內容合併
            const combinedContent = documents.map(doc => 
              `=== ${doc.title} ===\n${doc.chapter ? `章節: ${doc.chapter}\n` : ''}${doc.content}`
            ).join('\n\n---\n\n')
            
            sourceInfo = {
              documentId: documents[0]?.id || null, // 使用第一個文件的ID作為主要文件
              content: combinedContent,
              subject: question._meta?.templateSubject || documents[0]?.subject || 'General',
              chapter: documents.map(d => d.chapter).filter(Boolean).join(', ') || null
            }
          } else {
            // 文件配對生成：單個文件
            const document = batchSelectedDocuments.value.find(d => d.id === question._meta?.documentId)
            
            sourceInfo = {
              documentId: question._meta?.documentId || null,
              content: document ? document.content : '',
              subject: question._meta?.documentSubject || document?.subject || 'General',
              chapter: question._meta?.documentChapter || document?.chapter || null
            }
          }
          
          return { question, sourceInfo }
        })
        
        let successCount = 0
        let failedCount = 0
        
        for (const { question, sourceInfo } of questionsWithSourceInfo) {
          try {
            const results = await saveQuestionsBatch([question], sourceInfo)
            successCount += results.success.length
            failedCount += results.failed.length
          } catch (error) {
            console.error('批次儲存單題失敗:', error)
            failedCount++
          }
        }
        
        const totalQuestions = batchGeneratedQuestions.value.length
        if (successCount === totalQuestions) {
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: `批次儲存完成！成功儲存全部 ${totalQuestions} 道題目`,
            operation: '儲存批次題目'
          })
        } else {
          eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
            message: `批次儲存完成！成功 ${successCount} 題，失敗 ${failedCount} 題`,
            operation: '儲存批次題目'
          })
        }
        
      } catch (error) {
        console.error('批次儲存過程中發生錯誤:', error)
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          message: '批次儲存失敗，請查看控制台了解詳情',
          operation: '儲存批次題目',
          error
        })
      } finally {
        saving.value = false
      }
    }

    // 重置表單
    const resetForm = () => {
      selectedSubject.value = ''
      selectedTemplate.value = null
      selectedDocuments.value = []
      generatedQuestions.value = []
      traditionalCount.value = 1
      // selectedQuestionType 已移除
      
      // 重置新的配對系統和批次文件選擇
      batchSelectedDocuments.value = []
      batchDocumentSearchQuery.value = ''
      documentTemplatePairings.value = []
      selectedPairing.value = null
      
      // 重置模板組合系統
      templateDocumentPairings.value = []
      selectedTemplateGroup.value = null
      
      // 重置所有題型的模板選擇
      Object.keys(selectedTemplates).forEach(type => {
        selectedTemplates[type] = null
      })
      
      // 重置題型數量
      questionTypes.single_choice = 3
      questionTypes.cloze = 2
      questionTypes.short_answer = 1
      
    }

    // 監聽語言變化
    watch(currentLanguage, async () => {
      await fetchTemplates()
    })

    // 生命週期
    onMounted(async () => {
      await fetchSubjects()
      await fetchSubjectList()
      await fetchTemplates()
      await fetchDocuments()
    })

    return {
      // 多語言
      t,
      isEnglish,
      currentLanguage,
      
      // 狀態
      generating,
      saving,
      loadingTemplates,
      loadingDocuments,
      showPreview,
      showBilingualPreview,
      generationProgress,
      showProgressDialog,
      templates,
      subjects,
      subjectList,
      selectedSubject,
      selectedTemplate,
      selectedTemplates,
      documents,
      selectedDocuments,
      documentSearchQuery,
      selectedDocumentSubject,
      selectedDocumentGrade,
      documentSubjects,
      traditionalCount,
      // selectedQuestionType 已移除，現在使用模板的 question_type
      questionTypes,
      generatedQuestions,
      batchGeneratedQuestions,
      
      // 配對系統狀態
      documentTemplatePairings,
      selectedPairing,
      
      // 新的模板組合系統
      templateDocumentPairings,
      selectedTemplateGroup,
      
      // 批次文件選擇狀態
      batchSelectedDocuments,
      batchDocumentSearchQuery,
      filteredBatchDocuments,
      
      // 計算屬性
      filteredTemplates,
      filteredDocuments,
      totalQuestions,
      canGenerate,
      canGenerateBatch,
      previewContent,
      
      // 方法
      fetchTemplates,
      fetchSubjectList,
      refreshTemplates,
      searchDocuments,
      selectTemplate,
      selectTemplateForType,
      selectDocument,
      toggleDocumentSelection,
      generateTraditionalQuestions,
      generateQuestions,
      resetForm,
      exportQuestions,
      saveQuestions,
      getSubjectKey,
      getSubjectColor,
      getSubjectStyle,
      getSubjectDisplayName,
      getTextColor,
      getQuestionTypeLabel,
      
      // 配對系統方法
      getDocumentPairings,
      getTemplate,
      getAvailableTemplates,
      addPairing,
      removePairing,
      selectPairing,
      getSelectedDocument,
      getSelectedTemplate,
      getSelectedPairing,
      getPairingPreview,
      getTotalPairings,
      getTotalQuestions,
      
      // 新的模板組合系統方法
      createTemplateGroup,
      addDocumentToGroup,
      removeDocumentFromGroup,
      removeTemplateGroup,
      getTemplateGroupPreview,
      getTotalTemplateGroups,
      getTotalQuestionsFromGroups,
      generateBatchQuestions,
      exportBatchQuestions,
      saveBatchQuestions,
      
      // 批次文件選擇方法
      toggleBatchDocumentSelection,
      
      // 錯誤處理
      errors,
      showErrorDialog,
      currentError,
      showError,
      clearError,

      // 警告處理
      showWarningDialog,
      currentWarning,
      showWarning
    }
  }
}
</script>