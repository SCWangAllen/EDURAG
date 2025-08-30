<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click="$emit('close')">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <!-- Modal 內容 -->
      <div
        class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"
        @click.stop
      >
        <form @submit.prevent="handleSubmit">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-6">
                  {{ template ? '編輯模板' : '新增模板' }}
                </h3>

                <div class="space-y-6">
                  <!-- 基本資訊 -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                        模板名稱 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="name"
                        v-model="form.name"
                        type="text"
                        required
                        maxlength="100"
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="例：健康單選題預設模板"
                      />
                    </div>

                    <div>
                      <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
                        科目 <span class="text-red-500">*</span>
                      </label>
                      <div class="relative">
                        <select
                          id="subject"
                          v-model="selectedSubjectOption"
                          @change="handleSubjectChange"
                          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">請選擇科目</option>
                          <option v-for="subject in availableSubjects" :key="subject" :value="subject">
                            {{ subject }}
                          </option>
                          <option value="__custom__">+ 新增其他科目</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <!-- 自訂科目輸入框 -->
                  <div v-if="showCustomSubjectInput" class="grid grid-cols-1">
                    <div>
                      <label for="customSubject" class="block text-sm font-medium text-gray-700 mb-2">
                        自訂科目名稱 <span class="text-red-500">*</span>
                      </label>
                      <div class="flex space-x-2">
                        <input
                          id="customSubject"
                          v-model="customSubjectInput"
                          type="text"
                          required
                          maxlength="50"
                          class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="例：物理、化學、生物..."
                          @keyup.enter="addCustomSubject"
                        />
                        <button
                          type="button"
                          @click="addCustomSubject"
                          :disabled="!customSubjectInput.trim()"
                          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          新增
                        </button>
                        <button
                          type="button"
                          @click="cancelCustomSubject"
                          class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                        >
                          取消
                        </button>
                      </div>
                      <p class="text-xs text-gray-500 mt-1">輸入後按 Enter 或點擊「新增」按鈕</p>
                    </div>
                  </div>

                  <!-- Prompt 模板 -->
                  <div>
                    <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
                      Prompt 模板 <span class="text-red-500">*</span>
                    </label>
                    <div class="mb-2">
                      <p class="text-xs text-gray-500">
                        使用 {context} 作為文章內容的替換標記。支援 Markdown 格式。
                      </p>
                    </div>
                    <textarea
                      id="content"
                      v-model="form.content"
                      required
                      rows="12"
                      class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                      placeholder="請根據以下文章內容，生成一道單選題。&#10;&#10;文章內容：&#10;{context}&#10;&#10;請生成一道關於此文章的單選題..."
                    ></textarea>
                  </div>

                  <!-- 參數設定 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">LLM 參數設定</h4>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label for="temperature" class="block text-sm font-medium text-gray-700 mb-2">
                          溫度 (Temperature)
                        </label>
                        <div class="flex items-center space-x-2">
                          <input
                            id="temperature"
                            v-model.number="form.params.temperature"
                            type="range"
                            min="0"
                            max="2"
                            step="0.1"
                            class="flex-1"
                          />
                          <span class="text-sm text-gray-600 min-w-[3rem]">
                            {{ form.params.temperature }}
                          </span>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">控制回答的創意性和隨機性</p>
                      </div>

                      <div>
                        <label for="maxTokens" class="block text-sm font-medium text-gray-700 mb-2">
                          最大字數 (Max Tokens)
                        </label>
                        <input
                          id="maxTokens"
                          v-model.number="form.params.max_tokens"
                          type="number"
                          min="100"
                          max="10000"
                          step="100"
                          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                        <p class="text-xs text-gray-500 mt-1">生成內容的最大長度</p>
                      </div>

                      <div>
                        <label for="topP" class="block text-sm font-medium text-gray-700 mb-2">
                          Top P
                        </label>
                        <div class="flex items-center space-x-2">
                          <input
                            id="topP"
                            v-model.number="form.params.top_p"
                            type="range"
                            min="0"
                            max="1"
                            step="0.05"
                            class="flex-1"
                          />
                          <span class="text-sm text-gray-600 min-w-[3rem]">
                            {{ form.params.top_p }}
                          </span>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">控制詞彙選擇的多樣性</p>
                      </div>

                      <div>
                        <label for="frequencyPenalty" class="block text-sm font-medium text-gray-700 mb-2">
                          頻率懲罰 (Frequency Penalty)
                        </label>
                        <div class="flex items-center space-x-2">
                          <input
                            id="frequencyPenalty"
                            v-model.number="form.params.frequency_penalty"
                            type="range"
                            min="0"
                            max="2"
                            step="0.1"
                            class="flex-1"
                          />
                          <span class="text-sm text-gray-600 min-w-[3rem]">
                            {{ form.params.frequency_penalty }}
                          </span>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">減少重複內容的傾向</p>
                      </div>
                    </div>
                  </div>

                  <!-- 預覽區域 -->
                  <div v-if="form.content" class="bg-blue-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">預覽</h4>
                    <div class="text-sm text-gray-700 whitespace-pre-wrap">
                      {{ previewContent }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="submit"
              :disabled="saving"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ saving ? '儲存中...' : '儲存' }}
            </button>
            <button
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'

export default {
  name: 'TemplateModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    template: {
      type: Object,
      default: null
    },
    subjects: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const saving = ref(false)
    const customSubjects = ref([]) // 儲存用戶新增的自訂科目
    const selectedSubjectOption = ref('') // 目前選中的選項
    const customSubjectInput = ref('') // 自訂科目輸入框
    const showCustomSubjectInput = ref(false) // 是否顯示自訂科目輸入框
    
    const form = reactive({
      name: '',
      subject: '', // 實際要提交的科目
      content: '',
      params: {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
    })

    // 合併原有科目和自訂科目
    const availableSubjects = computed(() => {
      const allSubjects = [...(props.subjects || []), ...customSubjects.value]
      // 去重
      return [...new Set(allSubjects)].sort()
    })

    const resetForm = () => {
      form.name = ''
      form.subject = ''
      form.content = ''
      form.params = {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
      selectedSubjectOption.value = ''
      customSubjectInput.value = ''
      showCustomSubjectInput.value = false
    }

    const previewContent = computed(() => {
      return form.content.replace('{context}', '這裡是文章內容...')
    })

    // 處理科目選擇變化
    const handleSubjectChange = () => {
      if (selectedSubjectOption.value === '__custom__') {
        showCustomSubjectInput.value = true
        form.subject = '' // 清空實際科目，等待用戶輸入
      } else {
        showCustomSubjectInput.value = false
        form.subject = selectedSubjectOption.value
        customSubjectInput.value = ''
      }
    }

    // 新增自訂科目
    const addCustomSubject = () => {
      const newSubject = customSubjectInput.value.trim()
      if (!newSubject) return

      // 檢查是否已存在
      if (availableSubjects.value.includes(newSubject)) {
        alert('此科目已存在！')
        return
      }

      // 新增到自訂科目清單
      customSubjects.value.push(newSubject)
      
      // 設定為當前選中的科目
      form.subject = newSubject
      selectedSubjectOption.value = newSubject
      
      // 隱藏輸入框並清空
      showCustomSubjectInput.value = false
      customSubjectInput.value = ''
    }

    // 取消新增自訂科目
    const cancelCustomSubject = () => {
      showCustomSubjectInput.value = false
      customSubjectInput.value = ''
      selectedSubjectOption.value = form.subject || '' // 恢復到之前的選擇
    }

    // 監聽 template prop 變化來填充表單
    watch(() => props.template, (newTemplate) => {
      if (newTemplate) {
        form.name = newTemplate.name || ''
        form.subject = newTemplate.subject || ''
        form.content = newTemplate.content || ''
        form.params = {
          temperature: 0.7,
          max_tokens: 1000,
          top_p: 1.0,
          frequency_penalty: 0.0,
          ...newTemplate.params
        }
        
        // 設定科目選擇器
        selectedSubjectOption.value = newTemplate.subject || ''
        showCustomSubjectInput.value = false
        
        // 如果是編輯模板且科目不在現有清單中，加入到自訂科目
        if (newTemplate.subject && 
            !props.subjects.includes(newTemplate.subject) && 
            !customSubjects.value.includes(newTemplate.subject)) {
          customSubjects.value.push(newTemplate.subject)
        }
      } else {
        resetForm()
      }
    }, { immediate: true })

    // 監聽 modal 關閉，重置自訂科目輸入狀態
    watch(() => props.show, (newShow) => {
      if (!newShow) {
        showCustomSubjectInput.value = false
        customSubjectInput.value = ''
      }
    })

    const handleSubmit = async () => {
      // 驗證科目是否已設定
      if (!form.subject.trim()) {
        alert('請選擇或新增科目！')
        return
      }

      saving.value = true
      
      try {
        const templateData = {
          name: form.name,
          subject: form.subject,
          content: form.content,
          params: form.params
        }
        
        emit('save', templateData)
      } catch (error) {
        console.error('儲存模板失敗:', error)
      } finally {
        saving.value = false
      }
    }

    return {
      saving,
      form,
      availableSubjects,
      selectedSubjectOption,
      customSubjectInput,
      showCustomSubjectInput,
      previewContent,
      handleSubjectChange,
      addCustomSubject,
      cancelCustomSubject,
      handleSubmit
    }
  }
}
</script>