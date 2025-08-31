<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ t('generate.title') }}</h1>
          <p class="mt-2 text-sm text-gray-600">{{ t('generate.subtitle') }}</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="refreshTemplates"
            :disabled="loadingTemplates"
            class="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            title="重新載入模板（獲取最新參數）"
          >
            <svg v-if="loadingTemplates" class="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-700 inline" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            🔄 重新載入
          </button>
          <button
            @click="resetForm"
            :disabled="generating"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {{ t('reset') }}
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
                    <p class="text-xs text-gray-500">{{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : template.subject }}</p>
                  </div>
                  <div class="flex-shrink-0">
                    <span :class="getSubjectColor(template.subject)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                      {{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : template.subject }}
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
            
            <div class="mb-4">
              <input
                v-model="documentSearchQuery"
                @input="searchDocuments"
                type="text"
                :placeholder="t('generate.searchDocuments')"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
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
                    <p class="text-xs text-gray-500">{{ document.chapter }} - {{ isEnglish ? 'Page ' + document.page : '第' + document.page + '頁' }}</p>
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
            
            <!-- 問題類型選擇 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('generate.questionType') || '問題類型' }}</label>
              <select
                v-model="selectedQuestionType"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('generate.autoDetect') || '自動判斷' }}</option>
                <option value="single_choice">{{ t('questions.single_choice') || '單選題' }}</option>
                <option value="cloze">{{ t('questions.cloze') || '填空題' }}</option>
                <option value="short_answer">{{ t('questions.short_answer') || '簡答題' }}</option>
              </select>
              <p class="text-xs text-gray-500 mt-1">{{ t('generate.questionTypeHint') || '選擇空白則由 AI 自動判斷最適合的題型' }}</p>
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

          <!-- 生成結果 -->
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

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 左側：已選文件列表 -->
            <div class="lg:col-span-1">
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

            <!-- 中間：文件-模板配對 -->
            <div class="lg:col-span-1">
              <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.templatePairing') || '模板配對' }}</h3>
              <div v-if="batchSelectedDocuments.length === 0" class="text-center py-8 text-gray-400">
                <p class="text-sm">{{ t('generate.selectDocumentsAfterPairing') || '選擇文件後開始配對' }}</p>
              </div>
              <div v-else class="space-y-4">
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
                        <span class="text-gray-500">{{ getTemplate(pairing.template_id)?.subject }}</span>
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
                        {{ template.name }} ({{ template.subject }})
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右側：配對預覽 -->
            <div class="lg:col-span-1">
              <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.pairingPreview') || '配對預覽' }}</h3>
              <div v-if="!selectedPairing" class="text-center py-8 text-gray-400">
                <svg class="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                <p class="text-sm">{{ t('generate.clickPairingToPreview') || '點擊配對查看預覽' }}</p>
              </div>
              <div v-else class="bg-gray-50 p-4 rounded-lg">
                <div class="mb-3">
                  <div class="text-sm font-medium text-gray-900">{{ getSelectedDocument()?.title }}</div>
                  <div class="text-xs text-gray-500">{{ getSelectedTemplate()?.name }}</div>
                </div>
                <div class="max-h-80 overflow-y-auto border border-gray-200 bg-white p-3 rounded text-xs text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                  {{ getPairingPreview() }}
                </div>
                <div class="mt-2 text-xs text-gray-500">
                  {{ t('generate.willGenerate') || '將生成' }} {{ getSelectedPairing()?.count || 1 }}{{ t('generate.questionsCount') || '道題目' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 批次生成按鈕 -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-600">
                <span>{{ t('generate.totalPairings') || '總配對' }}: {{ getTotalPairings() }} {{ t('items') || '個' }}</span>
                <span class="mx-2">•</span>
                <span>{{ t('generate.expectedQuestions') || '預計生成' }}: {{ getTotalQuestions() }} {{ t('generate.questions') || '題' }}</span>
              </div>
              <button
                @click="() => { console.log('🔘 批次生成按鈕被點擊'); generateBatchQuestions(); }"
                :disabled="!canGenerateBatch || generating"
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import templateService from '../api/templateService.js'
import documentService from '../api/documentService.js'
// import { generateQuestions, createQuestion } from '../api/questionService.js'
import { generateQuestionsByPrompt, generateQuestionsByTemplateEnhanced, createQuestion } from '../api/questionService.js'
import { useLanguage } from '../composables/useLanguage.js'

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
    
    // 模板相關
    const templates = ref([])
    const subjects = ref([])
    const selectedSubject = ref('')
    const selectedTemplate = ref(null) // 保留用於預覽
    
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
    const traditionalCount = ref(1)  // 傳統生成數量
    const selectedQuestionType = ref('')  // 傳統生成問題類型選擇
    
    // 批次生成的獨立文件選擇
    const batchSelectedDocuments = ref([])  // 批次生成專用
    const batchDocumentSearchQuery = ref('')
    
    // 統一文件選擇功能
    const createDocumentSelector = (selectedDocs, searchQuery) => {
      const toggleSelection = (document) => {
        const index = selectedDocs.value.findIndex(d => d.id === document.id)
        if (index > -1) {
          selectedDocs.value.splice(index, 1)
        } else {
          selectedDocs.value.push(document)
        }
      }
      
      const filteredDocs = computed(() => {
        if (!searchQuery.value) return documents.value
        const query = searchQuery.value.toLowerCase()
        return documents.value.filter(doc => 
          doc.title.toLowerCase().includes(query) ||
          doc.chapter.toLowerCase().includes(query)
        )
      })
      
      return { toggleSelection, filteredDocs }
    }
    
    // 統一 Prompt 組合功能
    const buildPrompt = (template, documents, count, questionType = null) => {
      const documentsContent = documents.map(doc => 
        `Document: ${doc.title}\ncontent: ${doc.content}`
      ).join('\n\n')
      
      const fullPrompt = template.content.replace('{context}', documentsContent)
      
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
      console.log(sourceInfo)
      for (const [index, question] of questionsArray.entries()) {
        try {
          console.log(`📝 第 ${index + 1} 題詳細資料:`, {
            type: question.type,
            prompt: question.prompt?.substring(0, 100) + '...',
            options: question.options,
            answer: question.answer,
            hasOptions: !!question.options,
            optionsType: typeof question.options,
            optionsLength: question.options?.length
          })
          
          const questionData = {
            type: question.type || 'single_choice',
            content: question.prompt,
            options: question.options || null,
            correct_answer: question.answer,
            explanation: question.explanation || '',
            source_document_id: sourceInfo.documentId,
            source_content: sourceInfo.content,
            subject: sourceInfo.subject || 'General',
            chapter: sourceInfo.chapter,
            difficulty: 'medium'
          }
          
          console.log(`💾 準備儲存的問題資料:`, questionData)
          
          await createQuestion(questionData)
          results.success.push({ index: index + 1, question: question.prompt.substring(0, 50) + '...' })
          console.log(`✅ 第 ${index + 1} 題儲存成功`)
          
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
    const documentTemplatePairings = ref([])  // { document_id, template_id, count }
    const selectedPairing = ref(null)  // { document_id, template_id }
    
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
    const currentError = ref(null)

    // 錯誤處理方法
    const showError = (title, message, detail = null) => {
      currentError.value = { title, message, detail }
      showErrorDialog.value = true
      console.error(`${title}: ${message}`, detail)
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
    const traditionalDocumentSelector = createDocumentSelector(selectedDocuments, documentSearchQuery)
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
      
      return selectedTemplate.value.content.replace('{context}', contextContent)
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
      
      console.log('✅ [Generate] 模板重新載入完成')
    }

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

    const fetchDocuments = async () => {
      loadingDocuments.value = true
      try {
        const data = await documentService.getDocuments()
        documents.value = data.documents || []
      } catch (error) {
        console.error('取得文件清單失敗:', error)
        errors.value.documents = {
          message: '無法載入文件清單',
          detail: error.response?.data?.detail || error.message,
          code: error.response?.status || 'NETWORK_ERROR'
        }
        documents.value = []
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
        console.log('🔧 [Generate] 準備模板資料 - selectedTemplate:', selectedTemplate.value)
        console.log('📋 [Generate] selectedTemplate.params 詳情:', {
          params: selectedTemplate.value.params,
          hasParams: !!selectedTemplate.value.params,
          paramsType: typeof selectedTemplate.value.params,
          paramsKeys: selectedTemplate.value.params ? Object.keys(selectedTemplate.value.params) : [],
          paramsContent: JSON.stringify(selectedTemplate.value.params, null, 2)
        })
        
        const templateData = {
          id: selectedTemplate.value.id,
          name: selectedTemplate.value.name,
          content: selectedTemplate.value.content,
          subject: selectedTemplate.value.subject,
          params: selectedTemplate.value.params || {},
          created_at: selectedTemplate.value.created_at,
          updated_at: selectedTemplate.value.updated_at
        }
        
        console.log('📦 [Generate] 組裝好的 templateData:', templateData)
        console.log('🎛️ [Generate] templateData.params 詳情:', {
          params: templateData.params,
          hasParams: !!templateData.params,
          paramsType: typeof templateData.params,
          paramsKeys: Object.keys(templateData.params || {}),
          paramsContent: JSON.stringify(templateData.params, null, 2)
        })
        
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
          question_type: selectedQuestionType.value || null,
          temperature: 0.7,
          max_tokens: 2000,
          model: 'claude-3-5-sonnet-20241022'
        }
        
        console.log('使用完整模板資訊生成請求:', requestData)
        console.log('模板參數:', templateData.params)
        
        // 呼叫 Enhanced Template 驅動生成 API
        const response = await generateQuestionsByTemplateEnhanced(requestData)
        
        if (response.data && response.data.items) {
          generatedQuestions.value = response.data.items
          console.log('Enhanced Template 生成完成，生成題目數量:', response.data.items.length)
          console.log('使用的模板資訊:', response.data.template_info)
          console.log('實際使用的參數:', response.data.params_used)
        } else {
          throw new Error('API 回應格式不正確')
        }
        
      } catch (error) {
        console.error('Enhanced Template 生成失敗:', error)
        
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
            const fullPrompt = templateContent.replace('{{context}}', documentContent)
            
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
        alert(isEnglish.value ? 'No questions to save!' : '沒有題目可儲存！')
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
        console.log("souece="+sourceContent)
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
          alert(isEnglish.value 
            ? `Successfully saved all ${totalQuestions} questions!` 
            : `成功儲存全部 ${totalQuestions} 道題目！`)
        } else if (successCount > 0) {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.question} (${f.error})`).join('\n')
          alert(isEnglish.value
            ? `Saved ${successCount}/${totalQuestions} questions.\n\nFailed questions:\n${failedDetails}`
            : `儲存了 ${successCount}/${totalQuestions} 道題目。\n\n失敗的題目：\n${failedDetails}`)
        } else {
          const failedDetails = results.failed.map(f => `第${f.index}題: ${f.error}`).join('\n')
          alert(isEnglish.value
            ? `Failed to save any questions.\n\nErrors:\n${failedDetails}`
            : `所有題目儲存失敗。\n\n錯誤詳情：\n${failedDetails}`)
        }

      } catch (error) {
        console.error('儲存問題時發生未預期的錯誤:', error)
        alert(isEnglish.value 
          ? 'An unexpected error occurred while saving questions.' 
          : '儲存問題時發生未預期的錯誤。')
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

    const getSubjectColor = (subject) => {
      const colors = {
        '健康': 'bg-green-100 text-green-800',
        '英文': 'bg-blue-100 text-blue-800',
        '歷史': 'bg-yellow-100 text-yellow-800',
        'Health': 'bg-green-100 text-green-800',
        'English': 'bg-blue-100 text-blue-800',
        'History': 'bg-yellow-100 text-yellow-800'
      }
      return colors[subject] || 'bg-gray-100 text-gray-800'
    }

    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || '未知'
      
      const labelKeys = {
        'single_choice': 'generate.singleChoice',
        'cloze': 'generate.cloze',
        'short_answer': 'generate.shortAnswer',
        'auto': 'generate.auto'
      }
      
      const labelKey = labelKeys[type]
      if (labelKey) {
        return t(labelKey)
      }
      return type
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

    // 新的文件-模板配對方法
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
        console.log('✅ 成功新增配對:', newPairing)
        console.log('📋 當前所有配對:', documentTemplatePairings.value)
        console.log('📊 canGenerateBatch 狀態:', canGenerateBatch.value)
      } else {
        console.log('⚠️ 配對已存在，跳過')
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
    }

    const getSelectedDocument = () => {
      if (!selectedPairing.value) return null
      return selectedDocuments.value.find(d => d.id === selectedPairing.value.document_id)
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
      
      return template.content.replace('{context}', contextContent)
    }

    const getTotalPairings = () => {
      return documentTemplatePairings.value.length
    }

    const getTotalQuestions = () => {
      return documentTemplatePairings.value.reduce((sum, pairing) => sum + pairing.count, 0)
    }

    const generateBatchQuestions = async () => {
      console.log('🎯 批次生成被調用')
      console.log('📊 canGenerateBatch:', canGenerateBatch.value)
      console.log('📋 documentTemplatePairings:', documentTemplatePairings.value)
      console.log('📂 batchSelectedDocuments:', batchSelectedDocuments.value)
      console.log('🔢 總配對數量:', documentTemplatePairings.value.length)
      console.log('🔢 有效配對數量:', documentTemplatePairings.value.filter(p => p.count > 0).length)
      
      if (!canGenerateBatch.value) {
        console.log('❌ 批次生成條件不滿足，退出')
        console.log('   - 配對數量:', documentTemplatePairings.value.length)
        console.log('   - 有count>0的配對數量:', documentTemplatePairings.value.filter(p => p.count > 0).length)
        alert('請先選擇文件並為它們添加模板配對，並確保配對數量大於0')
        return
      }

      generating.value = true
      batchGeneratedQuestions.value = []  // 清空之前的結果
      
      try {
        console.log('🚀 開始批次配對生成題目')
        console.log('📋 文件配對詳情:', documentTemplatePairings.value)
        
        const allBatchQuestions = []
        
        // 逐個處理每個文件-模板配對
        for (const pairing of documentTemplatePairings.value) {
          const template = getTemplate(pairing.template_id)
          const document = batchSelectedDocuments.value.find(d => d.id === pairing.document_id)
          
          if (!template || !document) continue
          
          try {
            console.log(`處理配對: 文件"${document.title}" × 模板"${template.name}"`)
            
            // 使用統一的 Prompt 組合函數
            const completePrompt = buildPrompt(template, [document], pairing.count)

            console.log(`發送 prompt 給配對 ${document.id}-${template.id}:`, completePrompt.substring(0, 200) + '...')
            
            // 呼叫單次生成 API
            const response = await generateQuestionsByPrompt({
              prompt: completePrompt,
              count: pairing.count,
              temperature: 0.7,
              max_tokens: 4000,
              model: 'claude-3-5-sonnet-20241022'
            })
            
            if (response.data.items) {
              // 為每個題目標記來源元數據
              const questionsWithMeta = response.data.items.map(item => ({
                ...item,
                _meta: {
                  documentName: document.title,
                  templateName: template.name,
                  documentId: document.id,
                  templateId: template.id
                }
              }))
              allBatchQuestions.push(...questionsWithMeta)
              console.log(`配對 ${document.title} × ${template.name} 生成成功，題目數量:`, questionsWithMeta.length)
            }
          } catch (pairError) {
            console.error(`配對 ${document.title} × ${template.name} 生成失敗:`, pairError)
          }
        }
        
        batchGeneratedQuestions.value = allBatchQuestions
        console.log('批次配對生成完成，總題目數量:', allBatchQuestions.length)
        
      } catch (error) {
        console.error('批次配對生成失敗:', error)
        
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
        alert(t('generate.noResults') || '沒有可匯出的結果')
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
        alert(t('generate.noResults') || '沒有可儲存的結果')
        return
      }
      
      saving.value = true
      try {
        console.log('開始儲存批次生成結果到資料庫')
        
        // 準備批次儲存的 sourceInfo
        const batchSourceInfo = {
          documentId: null, // 批次生成不指定單一文件
          content: '批次生成',
          subject: 'General',
          chapter: null
        }
        
        // 為批次問題增加 meta 資訊到 sourceInfo
        const questionsWithSourceInfo = batchGeneratedQuestions.value.map(question => {
          const sourceInfo = {
            documentId: question._meta?.documentId || null,
            content: question._meta ? `${question._meta.documentName} + ${question._meta.templateName}` : '批次生成',
            subject: question.subject || 'General',
            chapter: null
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
          alert(`批次儲存完成！成功儲存全部 ${totalQuestions} 道題目`)
        } else {
          alert(`批次儲存完成！成功 ${successCount} 題，失敗 ${failedCount} 題`)
        }
        
      } catch (error) {
        console.error('批次儲存過程中發生錯誤:', error)
        alert('批次儲存失敗，請查看控制台了解詳情')
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
      selectedQuestionType.value = ''
      
      // 重置新的配對系統和批次文件選擇
      batchSelectedDocuments.value = []
      batchDocumentSearchQuery.value = ''
      documentTemplatePairings.value = []
      selectedPairing.value = null
      
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
      templates,
      subjects,
      selectedSubject,
      selectedTemplate,
      selectedTemplates,
      documents,
      selectedDocuments,
      documentSearchQuery,
      traditionalCount,
      selectedQuestionType,
      questionTypes,
      generatedQuestions,
      batchGeneratedQuestions,
      
      // 新的配對系統狀態
      documentTemplatePairings,
      selectedPairing,
      
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
      getQuestionTypeLabel,
      
      // 新的配對系統方法
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
      clearError
    }
  }
}
</script>