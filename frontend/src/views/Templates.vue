<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- 頁面標題與操作按鈕 -->
    <div class="px-4 py-6 sm:px-0">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">模板管理</h1>
          <p class="mt-2 text-sm text-gray-600">管理不同科目的題目生成模板</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="initializeDefaults"
            :disabled="loading"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            初始化預設模板
          </button>
          <button
            @click="showCreateModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            + 新增模板
          </button>
        </div>
      </div>

      <!-- 篩選器 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">科目篩選</label>
              <select
                v-model="selectedSubject"
                @change="fetchTemplates"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">全部科目</option>
                <option v-for="subject in subjects" :key="subject" :value="subject">
                  {{ subject }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">每頁顯示</label>
              <select
                v-model="pageSize"
                @change="fetchTemplates"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option :value="10">10 筆</option>
                <option :value="20">20 筆</option>
                <option :value="50">50 筆</option>
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
            <p class="text-lg mb-2">尚未建立任何模板</p>
            <p class="text-sm">點擊「新增模板」來建立第一個模板</p>
          </div>
        </div>

        <ul v-else class="divide-y divide-gray-200">
          <li v-for="template in templates" :key="template.id" class="px-6 py-4 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <span :class="getSubjectColor(template.subject)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                      {{ template.subject }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <h3 class="text-lg font-medium text-gray-900">{{ template.name }}</h3>
                    <div class="flex items-center mt-1 text-sm text-gray-500">
                      <span>版本 {{ template.version }}</span>
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
                  檢視
                </button>
                <button
                  @click="editTemplate(template)"
                  class="text-green-600 hover:text-green-800 text-sm font-medium"
                >
                  編輯
                </button>
                <button
                  @click="deleteTemplate(template.id)"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  刪除
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
            上一頁
          </button>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            下一頁
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              顯示
              <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
              到
              <span class="font-medium">{{ Math.min(currentPage * pageSize, totalTemplates) }}</span>
              筆，共
              <span class="font-medium">{{ totalTemplates }}</span>
              筆結果
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                上一頁
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
                下一頁
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
      :subjects="subjects"
      @close="closeModal"
      @save="saveTemplate"
    />

    <!-- 檢視模板 Modal -->
    <TemplateViewModal
      :show="showViewModal"
      :template="viewingTemplate"
      @close="showViewModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import templateService from '../api/templateService.js'
import TemplateModal from '../components/TemplateModal.vue'
import TemplateViewModal from '../components/TemplateViewModal.vue'

export default {
  name: 'Templates',
  components: {
    TemplateModal,
    TemplateViewModal
  },
  setup() {
    const loading = ref(false)
    const templates = ref([])
    const subjects = ref([])
    const selectedSubject = ref('')
    const pageSize = ref(20)
    const currentPage = ref(1)
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
        const data = await templateService.getTemplates(params)
        templates.value = data.templates || []
        totalTemplates.value = data.total || 0
      } catch (error) {
        console.error('取得模板清單失敗:', error)
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
        console.error('取得科目清單失敗:', error)
      }
    }

    // 初始化預設模板
    const initializeDefaults = async () => {
      loading.value = true
      try {
        await templateService.initializeDefaults()
        await fetchTemplates()
        await fetchSubjects()
        alert('預設模板初始化完成！')
      } catch (error) {
        console.error('初始化預設模板失敗:', error)
        alert('初始化失敗，請稍後再試')
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
      if (!confirm('確定要刪除這個模板嗎？')) {
        return
      }

      try {
        await templateService.deleteTemplate(templateId)
        await fetchTemplates()
        alert('模板刪除成功！')
      } catch (error) {
        console.error('刪除模板失敗:', error)
        alert('刪除失敗，請稍後再試')
      }
    }

    const saveTemplate = async (templateData) => {
      try {
        if (editingTemplate.value?.id) {
          // 更新
          await templateService.updateTemplate(editingTemplate.value.id, templateData)
        } else {
          // 新增
          await templateService.createTemplate(templateData)
        }
        
        await fetchTemplates()
        await fetchSubjects()
        closeModal()
        alert(editingTemplate.value?.id ? '模板更新成功！' : '模板建立成功！')
      } catch (error) {
        console.error('儲存模板失敗:', error)
        alert('儲存失敗，請稍後再試')
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
      const colors = {
        '國文': 'bg-red-100 text-red-800',
        '英文': 'bg-blue-100 text-blue-800', 
        '數學': 'bg-green-100 text-green-800',
        '歷史': 'bg-yellow-100 text-yellow-800',
        '地理': 'bg-purple-100 text-purple-800'
      }
      return colors[subject] || 'bg-gray-100 text-gray-800'
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

    // 初始化
    onMounted(async () => {
      await fetchSubjects()
      await fetchTemplates()
    })

    return {
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
      formatDate
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