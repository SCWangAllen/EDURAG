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
                          v-model="selectedSubjectId"
                          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">請選擇科目</option>
                          <option v-for="subject in subjectOptions" :key="subject.id" :value="subject.id">
                            <span :style="{ color: subject.color }">●</span>
                            {{ subject.name }}
                          </option>
                        </select>
                      </div>
                      <p class="text-xs text-gray-500 mt-1">
                        如需新增科目，請先到模板頁面的「📋 科目管理」建立
                      </p>
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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import subjectService from '../api/subjectService.js'

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
  emits: ['close', 'save', 'subject-created'],
  setup(props, { emit }) {
    const saving = ref(false)
    const subjectOptions = ref([]) // 科目選項清單
    const selectedSubjectId = ref(null) // 目前選中的科目ID
    
    const form = reactive({
      name: '',
      subject_id: null, // 科目ID
      content: '',
      params: {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
    })

    // 載入科目清單
    const loadSubjects = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectOptions.value = data.subjects || []
        console.log('📋 載入科目選項:', subjectOptions.value)
      } catch (error) {
        console.error('載入科目清單失敗:', error)
        subjectOptions.value = []
      }
    }

    // 監聽 subjects prop 變化
    watch(() => props.subjects, (newSubjects) => {
      if (newSubjects && newSubjects.length > 0) {
        subjectOptions.value = newSubjects
        console.log('📋 更新科目選項 (從 props):', subjectOptions.value)
      }
    }, { immediate: true })

    const handleLegacySubject = async (subjectName) => {
      try {
        // 優先使用 props 中的科目清單，如果沒有才重新載入
        if (subjectOptions.value.length === 0) {
          if (props.subjects && props.subjects.length > 0) {
            subjectOptions.value = props.subjects
          } else {
            await loadSubjects()
          }
        }
        
        // 查找是否已有對應的科目
        const existingSubject = subjectOptions.value.find(s => s.name === subjectName)
        
        if (existingSubject) {
          // 科目已存在，直接使用其ID
          form.subject_id = existingSubject.id
          selectedSubjectId.value = existingSubject.id
          console.log(`✅ 找到對應科目: ${subjectName} (ID: ${existingSubject.id})`)
        } else {
          // 科目不存在，自動建立
          console.log(`🔄 建立新科目: ${subjectName}`)
          const newSubject = await subjectService.createSubject({
            name: subjectName,
            description: `自動從模板建立的科目`,
            color: '#3B82F6'  // 使用預設藍色
          })
          
          // 發出事件通知父組件重新載入科目
          emit('subject-created', newSubject.subject)
          
          // 設定為新建立的科目
          form.subject_id = newSubject.subject.id
          selectedSubjectId.value = newSubject.subject.id
          console.log(`✅ 成功建立新科目: ${subjectName} (ID: ${newSubject.subject.id})`)
        }
      } catch (error) {
        console.error('處理舊科目資料失敗:', error)
        // 失敗時設為空，讓使用者手動選擇
        form.subject_id = null
        selectedSubjectId.value = null
      }
    }

    const resetForm = () => {
      form.name = ''
      form.subject_id = null
      form.content = ''
      selectedSubjectId.value = null
      form.params = {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0
      }
    }

    const previewContent = computed(() => {
      return form.content.replace('{context}', '這裡是文章內容...')
    })


    // 監聽 template prop 變化來填充表單
    watch(() => props.template, async (newTemplate) => {
      if (newTemplate) {
        form.name = newTemplate.name || ''
        form.content = newTemplate.content || ''
        form.params = {
          temperature: 0.7,
          max_tokens: 1000,
          top_p: 1.0,
          frequency_penalty: 0.0,
          ...newTemplate.params
        }
        
        // 處理科目ID設定
        if (newTemplate.subject_id) {
          // 如果已有 subject_id，直接使用
          form.subject_id = newTemplate.subject_id
          selectedSubjectId.value = newTemplate.subject_id
        } else if (newTemplate.subject) {
          // 如果沒有 subject_id 但有 subject 名稱，需要查找或建立對應的科目
          await handleLegacySubject(newTemplate.subject)
        } else {
          // 都沒有的話設為空
          form.subject_id = null
          selectedSubjectId.value = null
        }
      } else {
        resetForm()
      }
    }, { immediate: true })

    // 監聽科目ID變化，同步到 form
    watch(selectedSubjectId, (newSubjectId) => {
      form.subject_id = newSubjectId
    })

    const handleSubmit = async () => {
      // 驗證科目是否已選擇
      if (!form.subject_id) {
        alert('請選擇科目！')
        return
      }

      saving.value = true
      
      try {
        const templateData = {
          name: form.name,
          subject_id: form.subject_id,
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

    // 載入科目清單
    onMounted(async () => {
      await loadSubjects()
    })

    return {
      saving,
      form,
      subjectOptions,
      selectedSubjectId,
      previewContent,
      loadSubjects,
      handleLegacySubject,
      handleSubmit
    }
  }
}
</script>