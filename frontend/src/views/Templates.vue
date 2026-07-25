<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- 頁面標題與操作按鈕 -->
    <div class="px-4 py-6 sm:px-0">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 whitespace-pre-wrap">{{ t('templates.title') }}</h1>
        </div>
        <div class="flex space-x-3">
          <BaseButton variant="secondary" @click="showSubjectManager = true">
            {{ t('templates.subjectManagement') }}
          </BaseButton>
          <BaseButton variant="secondary" :disabled="loading" @click="initializeDefaults">
            {{ t('templates.initializeDefaults') }}
          </BaseButton>
          <BaseButton variant="primary" @click="showCreateModal = true">
            + {{ t('templates.createTemplate') }}
          </BaseButton>
        </div>
      </div>

      <!-- 依題型建立範本(每個題型都有正確起始範本,老師照填就不會生成失敗) -->
      <div v-if="questionTypeStarters.length" class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-1">{{ t('templates.starterGalleryTitle') }}</h2>
          <p class="text-sm text-gray-500 mb-4">{{ t('templates.starterGalleryHint') }}</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            <button
              v-for="s in questionTypeStarters"
              :key="s.question_type"
              type="button"
              @click="createFromType(s.question_type)"
              class="text-left p-4 rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <div class="text-base font-medium text-gray-900">{{ s.label }}</div>
              <div class="mt-2 text-xs font-medium text-primary-600">{{ t('templates.useStarter') }} →</div>
            </button>
          </div>
        </div>
      </div>

      <!-- 篩選器 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <FormSelect
              v-model="selectedSubject"
              :label="t('templates.filterBySubject')"
              @change="fetchTemplates"
            >
              <option value="">{{ t('templates.allSubjects') }}</option>
              <option v-for="subject in subjectNames" :key="subject" :value="subject">
                {{ getDisplayName(subject) }}
              </option>
            </FormSelect>
            <FormSelect
              v-model="selectedGrade"
              :label="t('templates.filterByGrade')"
              @change="fetchTemplates"
            >
              <option value="">{{ t('templates.allGrades') }}</option>
              <option v-for="g in gradeOptions" :key="g.value" :value="g.value">
                {{ getGradeLabel(g.value) }}
              </option>
            </FormSelect>
            <FormSelect
              v-model="pageSize"
              :label="t('templates.itemsPerPage')"
              @change="fetchTemplates"
            >
              <option :value="10">10 {{ t('templates.items') }}</option>
              <option :value="20">20 {{ t('templates.items') }}</option>
              <option :value="50">50 {{ t('templates.items') }}</option>
            </FormSelect>
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

        <EmptyState
          v-else-if="templates.length === 0"
          icon="📋"
          :title="t('templates.noTemplates')"
          :description="t('templates.clickToCreate')"
        />

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
                      {{ getDisplayName(template.subject) }}
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
                  class="text-primary-600 hover:text-blue-800 text-sm font-medium"
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
                    ? 'z-10 bg-blue-50 border-blue-500 text-primary-600'
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
      :preset-type="presetType"
      @close="closeModal"
      @save="saveTemplate"
      @subject-created="handleSubjectCreated"
    />

    <!-- 檢視模板 Modal -->
    <TemplateViewModal
      :show="showViewModal"
      :template="viewingTemplate"
      :subject-list="subjectList"
      @close="viewModal.close()"
    />

    <!-- 科目管理 Modal -->
    <SubjectManagerModal
      :visible="showSubjectManager"
      @close="showSubjectManager = false"
      @subjects-changed="handleSubjectsChanged"
      ref="subjectManagerRef"
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
import SubjectManagerModal from '../components/Templates/SubjectManagerModal.vue'
import Toast from '../components/Toast.vue'
import BaseButton from '../components/Base/BaseButton.vue'
import FormSelect from '../components/Base/FormSelect.vue'
import EmptyState from '../components/Base/EmptyState.vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '../composables/useToast.js'
import { useModal } from '../composables/useModal.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import { getSubjectColor as getSubjectColorDefault, formatDateTime, getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'
import { getTextColor } from '@/utils/subjectUtils.js'

export default {
  name: 'Templates',
  components: {
    TemplateModal,
    TemplateViewModal,
    SubjectManagerModal,
    Toast,
    BaseButton,
    FormSelect,
    EmptyState
  },
  setup() {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目/年級唯一來源
    const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded, refresh } = useSubjects()

    const loading = ref(false)
    const templates = ref([])
    const selectedSubject = ref('')
    const selectedGrade = ref('')
    const pageSize = ref(20)
    const currentPage = ref(1)
    const totalTemplates = ref(0)
    const subjectManagerRef = ref(null)

    // 科目清單（用於模板顯示顏色）
    const subjectList = ref([])
    const showSubjectManager = ref(false)

    // Modal 狀態
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingTemplate = ref(null)
    const presetType = ref('') // 由題型範本庫帶入的預選題型

    // 題型範本庫(單一真實來源,後端 /templates/question-types)
    const questionTypeStarters = ref([])

    // View modal using useModal composable
    const viewModal = useModal()
    const showViewModal = viewModal.isOpen
    const viewingTemplate = viewModal.data

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
          grade: selectedGrade.value || undefined,
          page: currentPage.value,
          size: pageSize.value
        }
        const data = await templateService.getTemplates(params)

        templates.value = data.templates || []
        totalTemplates.value = data.total || 0
      } catch (error) {
      } finally {
        loading.value = false
      }
    }

    // 取得科目詳細清單（用於顏色顯示）
    const fetchSubjectList = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectList.value = data.subjects || []
      } catch (error) {
      }
    }

    // 初始化預設模板
    const initializeDefaults = async () => {
      if (!confirm(t('templates.initializeConfirm'))) {
        return
      }
      loading.value = true
      try {
        await templateService.initializeDefaults()
        await fetchTemplates()
        await refresh()
        await fetchSubjectList()

        showSuccess(t('templates.initializeDefaultsSuccess'), '模板初始化')
      } catch (error) {

        toastError(t('templates.initializeDefaultsFailed'), '模板初始化', error)
      } finally {
        loading.value = false
      }
    }

    // 題型範本庫:載入 + 依題型開啟建立(自動帶入該題型起始範本)
    const fetchQuestionTypeStarters = async () => {
      try {
        const data = await templateService.getQuestionTypes()
        questionTypeStarters.value = data.question_types || []
      } catch (error) {
        questionTypeStarters.value = []
      }
    }
    const createFromType = (questionType) => {
      editingTemplate.value = null
      presetType.value = questionType
      showCreateModal.value = true
    }

    // Modal 操作
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingTemplate.value = null
      presetType.value = ''
    }

    const editTemplate = (template) => {
      editingTemplate.value = { ...template }
      showEditModal.value = true
    }

    const viewTemplate = (template) => {
      viewModal.open(template)
    }

    const deleteTemplate = async (templateId) => {
      if (!confirm(t('templates.confirmDeleteTemplate'))) {
        return
      }

      try {
        await templateService.deleteTemplate(templateId)
        await fetchTemplates()

        showSuccess(t('templates.templateDeleteSuccess'), '模板刪除')
      } catch (error) {

        toastError(t('templates.templateDeleteFailed'), '模板刪除', error)
      }
    }

    const saveTemplate = async (templateData) => {
      try {

        if (editingTemplate.value?.id) {
          await templateService.updateTemplate(editingTemplate.value.id, templateData)
        } else {
          await templateService.createTemplate(templateData)
        }

        await fetchTemplates()
        await refresh()
        await fetchSubjectList()

        showSuccess(
          editingTemplate.value?.id ? t('templates.templateUpdateSuccess') : t('templates.templateCreateSuccess'),
          editingTemplate.value?.id ? '模板更新' : '模板創建'
        )

        closeModal()
      } catch (error) {

        toastError(
          error.response?.data?.detail || error.message || t('templates.templateSaveFailed'),
          editingTemplate.value?.id ? '模板更新' : '模板創建',
          error
        )
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
      const subjectData = subjectList.value.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return 'text-white'
      }
      return getSubjectColorDefault(subject)
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

    const formatDate = (dateString) => formatDateTime(dateString)

    const getQuestionTypeLabel = (questionType) => getQuestionTypeLabelUtil(questionType, t)

    // 處理科目變更事件（來自 SubjectManagerModal）
    const handleSubjectsChanged = async () => {
      await fetchSubjectList()
      await refresh()
      await fetchTemplates()
    }

    // 處理從 TemplateModal 建立新科目的事件
    const handleSubjectCreated = async () => {
      await fetchSubjectList()
      await refresh()
    }

    // 初始化
    onMounted(async () => {
      await ensureLoaded()
      await fetchTemplates()
      await fetchSubjectList()
      await fetchQuestionTypeStarters()
    })

    return {
      t,
      getDisplayName,
      getGradeLabel,
      loading,
      templates,
      subjectNames,
      selectedSubject,
      selectedGrade,
      gradeOptions: GRADE_OPTIONS,
      pageSize,
      currentPage,
      totalTemplates,
      totalPages,
      visiblePages,
      showCreateModal,
      showEditModal,
      showViewModal,
      editingTemplate,
      presetType,
      questionTypeStarters,
      createFromType,
      viewingTemplate,
      subjectList,
      subjectManagerRef,
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
      formatDate,
      getQuestionTypeLabel,

      // 科目管理
      showSubjectManager,
      handleSubjectsChanged,
      handleSubjectCreated,

      // View modal
      viewModal
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
