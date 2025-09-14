<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- 頁面標題與操作按鈕 -->
    <div class="px-4 py-6 sm:px-0">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ t('templates.title') }}</h1>
          <p class="mt-2 text-sm text-gray-600">{{ t('templates.subtitle') }}</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="showSubjectManager = true"
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ t('templates.subjectManagement') }}
          </button>
          <button
            @click="initializeDefaults"
            :disabled="loading"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {{ t('templates.initializeDefaults') }}
          </button>
          <button
            @click="showCreateModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            + {{ t('templates.createTemplate') }}
          </button>
        </div>
      </div>

      <!-- 篩選器 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('templates.filterBySubject') }}</label>
              <select
                v-model="selectedSubject"
                @change="fetchTemplates"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ t('templates.allSubjects') }}</option>
                <option v-for="subject in subjects" :key="subject" :value="subject">
                  {{ subject }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('templates.itemsPerPage') }}</label>
              <select
                v-model="pageSize"
                @change="fetchTemplates"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option :value="10">10 {{ t('templates.items') }}</option>
                <option :value="20">20 {{ t('templates.items') }}</option>
                <option :value="50">50 {{ t('templates.items') }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 模板清單 -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-pulse">
            <div class="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-4"></div>
            <div class="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
          </div>
        </div>

        <div v-else-if="templates.length === 0" class="p-8 text-center">
          <div class="text-gray-500">
            <p class="text-lg mb-2">{{ t('templates.noTemplates') }}</p>
            <p class="text-sm">{{ t('templates.clickToCreate') }}</p>
          </div>
        </div>

        <ul v-else class="divide-y divide-gray-200">
          <li v-for="template in templates" :key="template.id" class="px-6 py-4 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <span 
                      :class="getSubjectStyle(template.subject) ? '' : getSubjectColor(template.subject)"
                      :style="getSubjectStyle(template.subject)" 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                      {{ template.subject }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <h3 class="text-lg font-medium text-gray-900">{{ template.name }}</h3>
                    <div class="flex items-center mt-1 text-sm text-gray-500">
                      <span>{{ t('templates.version') }} {{ template.version }}</span>
                      <span class="mx-2">•</span>
                      <span>{{ getQuestionTypeLabel(template.question_type) }}</span>
                      <span class="mx-2">•</span>
                      <span>{{ formatDate(template.updated_at) }}</span>
                    </div>
                  </div>
                </div>
                <div class="mt-2">
                  <p class="text-sm text-gray-600 line-clamp-2">
                    {{ template.content.substring(0, 150) }}{{ template.content.length > 150 ? '...' : '' }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="viewTemplate(template)"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {{ t('view') }}
                </button>
                <button
                  @click="editTemplate(template)"
                  class="text-green-600 hover:text-green-800 text-sm font-medium"
                >
                  {{ t('templates.edit') }}
                </button>
                <button
                  @click="deleteTemplate(template.id)"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  {{ t('templates.delete') }}
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="prevPage"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            {{ t('templates.prevPage') }}
          </button>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            {{ t('templates.nextPage') }}
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              {{ t('templates.showing') }}
              <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
              {{ t('templates.to') }}
              <span class="font-medium">{{ Math.min(currentPage * pageSize, totalTemplates) }}</span>
              {{ t('templates.of') }}
              <span class="font-medium">{{ totalTemplates }}</span>
              {{ t('templates.results') }}
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                {{ t('templates.prevPage') }}
              </button>
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  page === currentPage
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                ]"
              >
                {{ page }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                {{ t('templates.nextPage') }}
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- 建立/編輯模板 Modal -->
    <TemplateModal
      :show="showCreateModal || showEditModal"
      :template="editingTemplate"
      :subjects="subjectList"
      @close="closeModal"
      @save="saveTemplate"
      @subject-created="handleSubjectCreated"
    />

    <!-- 檢視模板 Modal -->
    <TemplateViewModal
      :show="showViewModal"
      :template="viewingTemplate"
      @close="showViewModal = false"
    />

    <!-- 科目管理 Modal -->
    <div v-if="showSubjectManager" class="fixed inset-0 z-50 overflow-y-auto" @click="showSubjectManager = false">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"
          @click.stop
        >
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-lg font-medium text-gray-900">{{ t('templates.subjectManagementTitle') }}</h3>
              <div class="flex space-x-3">
                <button
                  @click="showSubjectModal = true"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium"
                >
                  + {{ t('templates.addSubject') }}
                </button>
                <button @click="showSubjectManager = false" class="text-gray-400 hover:text-gray-600">
                  ×
                </button>
              </div>
            </div>

            <!-- 科目清單 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="subject in subjectList"
                :key="subject.id"
                class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center space-x-2">
                    <span
                      :style="{ backgroundColor: subject.color }"
                      class="inline-block w-4 h-4 rounded-full"
                    ></span>
                    <h4 class="font-medium text-gray-900">{{ subject.name }}</h4>
                  </div>
                  <div class="flex space-x-1">
                    <button
                      @click="editSubject(subject)"
                      class="text-gray-400 hover:text-blue-600 text-sm"
                    >
                      ✏️
                    </button>
                    <button
                      @click="deleteSubject(subject)"
                      class="text-gray-400 hover:text-red-600 text-sm"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <p v-if="subject.description" class="text-sm text-gray-600 mb-2">
                  {{ subject.description }}
                </p>
                <div class="text-xs text-gray-500">
                  {{ subjectStats[subject.name]?.template_count || 0 }} {{ t('templates.templateCount') }}
                </div>
              </div>
            </div>

            <!-- 空狀態 -->
            <div v-if="subjectList.length === 0" class="text-center py-8 text-gray-500">
              <p>{{ t('templates.noSubjects') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/編輯科目 Modal -->
    <SubjectModal
      :show="showSubjectModal"
      :subject="editingSubject"
      @close="closeSubjectModal"
      @save="saveSubject"
    />
    
    <!-- Toast 通知組件 -->
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import templateService from '../api/templateService.js'
import subjectService from '../api/subjectService.js'
import TemplateModal from '../components/TemplateModal.vue'
import TemplateViewModal from '../components/TemplateViewModal.vue'
import SubjectModal from '../components/SubjectModal.vue'
import Toast from '../components/Toast.vue'
import { useLanguage } from '../composables/useLanguage.js'
import eventBus, { SUBJECT_EVENTS, UI_EVENTS } from '@/utils/eventBus.js'

export default {
  name: 'Templates',
  components: {
    TemplateModal,
    TemplateViewModal,
    SubjectModal,
    Toast
  },
  setup() {
    const { t } = useLanguage()
    
    const loading = ref(false)
    const templates = ref([])
    const subjects = ref([])
    const selectedSubject = ref('')
    const pageSize = ref(20)
    const currentPage = ref(1)
    
    // 科目管理相關狀態
    const showSubjectManager = ref(false)
    const showSubjectModal = ref(false)
    const subjectList = ref([])
    const subjectStats = ref({})
    const editingSubject = ref(null)
    const totalTemplates = ref(0)
    
    // Modal 狀態
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    const editingTemplate = ref(null)
    const viewingTemplate = ref(null)

    const totalPages = computed(() => {
      return Math.ceil(totalTemplates.value / pageSize.value)
    })

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    // 取得模板清單
    const fetchTemplates = async () => {
      loading.value = true
      try {
        const params = {
          subject: selectedSubject.value || undefined,
          page: currentPage.value,
          size: pageSize.value
        }
        console.log('🔎 載入模板清單，參數:', params)
        const data = await templateService.getTemplates(params)
        console.log('📝 收到模板資料:', data.templates?.map(t => ({ id: t.id, name: t.name, subject: t.subject })))
        
        templates.value = data.templates || []
        totalTemplates.value = data.total || 0
      } catch (error) {
        console.error('❌ 載入模板失敗:', error)
      } finally {
        loading.value = false
      }
    }

    // 取得科目清單
    const fetchSubjects = async () => {
      try {
        const data = await templateService.getSubjects()
        subjects.value = data.subjects || []
      } catch (error) {
        console.error('Failed to fetch subjects:', error)
      }
    }

    // 初始化預設模板
    const initializeDefaults = async () => {
      loading.value = true
      try {
        await templateService.initializeDefaults()
        await fetchTemplates()
        await fetchSubjects()
        
        // 發送成功事件
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('templates.initializeDefaultsSuccess'),
          operation: '模板初始化'
        })
      } catch (error) {
        console.error('Failed to initialize default templates:', error)
        
        // 發送錯誤事件
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          error,
          message: t('templates.initializeDefaultsFailed'),
          operation: '模板初始化'
        })
      } finally {
        loading.value = false
      }
    }

    // Modal 操作
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingTemplate.value = null
    }

    const editTemplate = (template) => {
      editingTemplate.value = { ...template }
      showEditModal.value = true
    }

    const viewTemplate = (template) => {
      viewingTemplate.value = template
      showViewModal.value = true
    }

    const deleteTemplate = async (templateId) => {
      if (!confirm(t('templates.confirmDeleteTemplate'))) {
        return
      }

      try {
        await templateService.deleteTemplate(templateId)
        await fetchTemplates()
        
        // 發送成功事件
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('templates.templateDeleteSuccess'),
          operation: '模板刪除'
        })
      } catch (error) {
        console.error('Failed to delete template:', error)
        
        // 發送錯誤事件
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          error,
          message: t('templates.templateDeleteFailed'),
          operation: '模板刪除'
        })
      }
    }

    const saveTemplate = async (templateData) => {
      try {
        console.log('🔄 開始儲存模板:', templateData)
        
        if (editingTemplate.value?.id) {
          // 更新
          console.log('🔄 更新模板 ID:', editingTemplate.value.id)
          const result = await templateService.updateTemplate(editingTemplate.value.id, templateData)
          console.log('✅ 更新結果:', result)
        } else {
          // 新增
          console.log('➕ 建立新模板')
          const result = await templateService.createTemplate(templateData)
          console.log('✅ 建立結果:', result)
        }
        
        console.log('🔄 重新載入模板清單...')
        await fetchTemplates()
        console.log('🔄 重新載入科目清單...')
        await fetchSubjects()
        
        console.log('✅ 模板儲存完成，新的模板清單:', templates.value.map(t => ({ id: t.id, name: t.name, subject: t.subject })))
        
        // 發送成功事件
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: editingTemplate.value?.id ? t('templates.templateUpdateSuccess') : t('templates.templateCreateSuccess'),
          operation: editingTemplate.value?.id ? '模板更新' : '模板創建'
        })
        
        closeModal()
      } catch (error) {
        console.error('❌ 儲存模板失敗:', error)
        
        // 發送錯誤事件
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          error,
          operation: editingTemplate.value?.id ? '模板更新' : '模板創建',
          message: error.response?.data?.detail || error.message || t('templates.templateSaveFailed')
        })
      }
    }

    // 分頁操作
    const goToPage = (page) => {
      currentPage.value = page
      fetchTemplates()
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        goToPage(currentPage.value - 1)
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        goToPage(currentPage.value + 1)
      }
    }

    // 工具函數
    const getSubjectColor = (subject) => {
      // 從科目清單中查找對應的科目顏色
      const subjectData = subjectList.value.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return `text-white`
      }
      // 備用顏色方案
      const colors = {
        '健康': 'bg-green-100 text-green-800',
        '英文': 'bg-blue-100 text-blue-800', 
        '歷史': 'bg-yellow-100 text-yellow-800'
      }
      return colors[subject] || 'bg-gray-100 text-gray-800'
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

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 科目管理方法
    const fetchSubjectList = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectList.value = data.subjects || []
        console.log('📝 載入科目清單:', subjectList.value)
      } catch (error) {
        console.error(t('templates.fetchSubjectsFailed') + ':', error)
      }
    }
    
    const fetchSubjectStats = async () => {
      try {
        const data = await subjectService.getSubjectStats()
        subjectStats.value = data.stats || {}
        console.log('📈 載入科目統計:', subjectStats.value)
      } catch (error) {
        console.error(t('templates.fetchSubjectStatsFailed') + ':', error)
      }
    }
    
    const editSubject = (subject) => {
      editingSubject.value = { ...subject }
      showSubjectModal.value = true
    }
    
    const closeSubjectModal = () => {
      showSubjectModal.value = false
      editingSubject.value = null
    }
    
    const saveSubject = async (subjectData) => {
      try {
        if (editingSubject.value?.id) {
          // 更新科目
          await subjectService.updateSubject(editingSubject.value.id, subjectData)
          
          // 發送科目更新事件
          eventBus.emit(SUBJECT_EVENTS.UPDATED, {
            id: editingSubject.value.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })
          
          // 發送成功訊息事件
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: t('templates.subjectUpdateSuccess').replace('{name}', subjectData.name),
            operation: '科目更新'
          })
        } else {
          // 新增科目
          const newSubject = await subjectService.createSubject(subjectData)
          
          // 發送科目創建事件
          eventBus.emit(SUBJECT_EVENTS.CREATED, {
            id: newSubject.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })
          
          // 發送成功訊息事件
          eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
            message: t('templates.subjectCreateSuccess').replace('{name}', subjectData.name),
            operation: '科目創建'
          })
        }
        
        closeSubjectModal()
        await fetchSubjectList()
        await fetchSubjects() // 更新模板使用的科目清單
        await fetchTemplates() // 重新載入模板
        
        // 發送資料重新載入事件
        eventBus.emit('system:reload_data', {
          scope: 'subjects'
        })
        
      } catch (error) {
        console.error(t('templates.subjectSaveFailed') + ':', error)
        
        // 發送錯誤事件
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          error,
          operation: editingSubject.value?.id ? '科目更新' : '科目創建',
          message: error.response?.data?.detail || error.message || t('templates.subjectSaveFailed')
        })
      }
    }
    
    const deleteSubject = async (subject) => {
      if (!confirm(t('templates.confirmDeleteSubject').replace('{name}', subject.name))) {
        return
      }
      
      try {
        const templateCount = subjectStats.value[subject.name]?.template_count || 0
        const force = templateCount > 0 ? confirm(t('templates.forceDeleteSubjectWithTemplates').replace('{count}', templateCount)) : false
        
        await subjectService.deleteSubject(subject.id, force)
        
        // 發送科目刪除事件
        eventBus.emit(SUBJECT_EVENTS.DELETED, {
          id: subject.id,
          name: subject.name
        })
        
        // 發送成功訊息事件
        eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, {
          message: t('templates.subjectDeleteSuccess').replace('{name}', subject.name),
          operation: '科目刪除'
        })
        
        await fetchSubjectList()
        await fetchSubjects()
        await fetchTemplates()
      } catch (error) {
        console.error(t('templates.subjectDeleteFailed') + ':', error)
        
        // 發送錯誤事件
        eventBus.emit(UI_EVENTS.ERROR_OCCURRED, {
          error,
          message: error.response?.data?.detail || error.message || t('templates.subjectDeleteFailed'),
          operation: '科目刪除'
        })
      }
    }

    // 處理從 TemplateModal 建立新科目的事件
    const handleSubjectCreated = async (newSubject) => {
      console.log('🎉 收到新建科目事件:', newSubject)
      // 重新載入科目清單以包含新科目
      await fetchSubjectList()
      await fetchSubjectStats()
    }

    // 取得問題類型標籤
    const getQuestionTypeLabel = (questionType) => {
      if (!questionType) return ''
      
      // 使用 i18n 翻譯系統
      const translationKey = `questions.${questionType}`
      const translation = t(translationKey)
      
      // 如果有翻譯就用，沒有就顯示原始值
      return translation !== translationKey ? translation : questionType
    }

    // 初始化
    onMounted(async () => {
      await fetchSubjects()
      await fetchTemplates()
      await fetchSubjectList()
      await fetchSubjectStats()
    })

    return {
      t,
      loading,
      templates,
      subjects,
      selectedSubject,
      pageSize,
      currentPage,
      totalTemplates,
      totalPages,
      visiblePages,
      showCreateModal,
      showEditModal,
      showViewModal,
      editingTemplate,
      viewingTemplate,
      fetchTemplates,
      initializeDefaults,
      closeModal,
      editTemplate,
      viewTemplate,
      deleteTemplate,
      saveTemplate,
      goToPage,
      prevPage,
      nextPage,
      getSubjectColor,
      getSubjectStyle,
      getTextColor,
      formatDate,
      getQuestionTypeLabel,
      
      // 科目管理
      showSubjectManager,
      showSubjectModal,
      subjectList,
      subjectStats,
      editingSubject,
      editSubject,
      closeSubjectModal,
      saveSubject,
      deleteSubject,
      handleSubjectCreated
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>