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
      <!-- 有範本之後預設收成一行(老師不用每次捲過 300px 才看到清單),狀態記在瀏覽器 -->
      <div v-if="questionTypeStarters.length" class="bg-white shadow rounded-lg mb-6">
        <button
          type="button"
          class="w-full flex items-center justify-between px-4 py-3 sm:px-6 text-left focus:outline-none"
          @click="starterCollapsed = !starterCollapsed"
        >
          <span class="text-base font-semibold text-gray-900">
            {{ t('templates.starterGalleryTitle') }}
            <span class="ml-2 text-xs font-normal text-gray-400">{{ questionTypeStarters.length }} {{ t('templates.starterTypesUnit') }}</span>
          </span>
          <span class="text-xs text-primary-600 whitespace-nowrap">{{ starterCollapsed ? t('templates.starterGalleryShow') + ' ▾' : t('templates.starterGalleryHide') + ' ▴' }}</span>
        </button>
        <div v-show="!starterCollapsed" class="px-4 pb-5 sm:px-6">
          <p class="text-sm text-gray-500 mb-4">{{ t('templates.starterGalleryHint') }}</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            <button
              v-for="s in questionTypeStarters"
              :key="s.question_type"
              type="button"
              @click="createFromType(s.question_type)"
              class="text-left p-4 rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <div class="text-base font-medium text-gray-900">{{ t('questions.' + s.question_type) }}</div>
              <div class="mt-2 text-xs font-medium text-primary-600">{{ t('templates.useStarter') }} →</div>
            </button>
          </div>
        </div>
      </div>

      <!-- 篩選器 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
            <FormInput
              v-model="searchQuery"
              :label="t('templates.search')"
              :placeholder="t('templates.searchPlaceholder')"
              @keyup.enter="handleSearchEnter"
              @input="handleSearchInput"
            />
            <SubjectSelect
              v-model="selectedSubject"
              :label="t('templates.filterBySubject')"
              :placeholder="t('templates.allSubjects')"
              @change="fetchTemplates"
            />
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
              v-model="sortBy"
              :label="t('templates.sortBy')"
              @change="handleSortChange"
            >
              <option value="grade">{{ t('templates.sortByGrade') }}</option>
              <option value="newest">{{ t('templates.sortByNewest') }}</option>
              <option value="manual">{{ t('templates.sortByManual') }}</option>
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

      <!-- 排序非「自訂順序」時提示怎麼切換 -->
      <p v-if="sortBy !== 'manual'" class="text-xs text-gray-500 mb-2">
        {{ t('templates.manualOrderHint') }}
      </p>
        <p v-if="sortBy === 'manual' && !canReorder" class="text-xs text-amber-600 mb-2">{{ t('templates.manualOrderFilterHint') }}</p>
      <p v-if="canReorder" class="text-xs text-gray-500 mb-2">{{ t('templates.dragHint') }}</p>

      <!-- 模板清單 -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <!-- 上方翻頁(老師需求:不用捲到最下面才能換頁) -->
        <div v-if="!loading && templates.length > 0 && totalPages > 1" class="px-6 py-2 border-b border-gray-200 flex items-center justify-end gap-2 text-sm text-gray-600">
          <button type="button" @click="prevPage" :disabled="currentPage === 1" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50">{{ t('templates.prevPage') }}</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button type="button" @click="nextPage" :disabled="currentPage === totalPages" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50">{{ t('templates.nextPage') }}</button>
        </div>
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
          <li
            v-for="template in templates"
            :key="template.id"
            :draggable="canReorder"
            @dragstart="onDragStart($event, template)"
            @dragover="onDragOver($event, template)"
            @dragleave="onDragLeave(template)"
            @drop="onDrop($event, template)"
            @dragend="onDragEnd"
            class="px-6 py-4 hover:bg-gray-50 border-t-2 border-b-2"
            :class="[
              draggingId === template.id ? 'opacity-50' : '',
              dropTarget && dropTarget.id === template.id && dropTarget.position === 'before' ? 'border-t-primary-500' : 'border-t-transparent',
              dropTarget && dropTarget.id === template.id && dropTarget.position === 'after' ? 'border-b-primary-500' : 'border-b-transparent'
            ]"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center flex-1 min-w-0">
                <span
                  v-if="canReorder"
                  class="flex-shrink-0 mr-3 text-gray-400 cursor-grab select-none text-lg leading-none"
                  :title="t('templates.dragToReorder')"
                >⠿</span>
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
              </div>
              <div class="flex items-center space-x-2">
                <template v-if="canReorder">
                  <button
                    type="button"
                    @click="moveTemplate(template, 'up')"
                    :title="t('templates.moveUp')"
                    :disabled="moving"
                    class="text-gray-400 hover:text-primary-600 text-sm leading-none px-1 disabled:opacity-40"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    @click="moveTemplate(template, 'down')"
                    :title="t('templates.moveDown')"
                    :disabled="moving"
                    class="text-gray-400 hover:text-primary-600 text-sm leading-none px-1 disabled:opacity-40"
                  >
                    ▼
                  </button>
                </template>
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
                  @click="copyTemplate(template)"
                  class="text-gray-600 hover:text-gray-800 text-sm font-medium"
                >
                  {{ t('templates.copy') }}
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

      <!-- 分頁:摘要列常駐(只有一頁時也要看得到「共 N 筆」),翻頁鍵多頁才顯示 -->
      <div v-if="totalTemplates > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div v-if="totalPages > 1" class="flex-1 flex justify-between sm:hidden">
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
          <div v-if="totalPages > 1">
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
import { ref, onMounted, onActivated, computed, watch } from 'vue'
import templateService from '../api/templateService.js'
import subjectService from '../api/subjectService.js'
import TemplateModal from '../components/TemplateModal.vue'
import TemplateViewModal from '../components/TemplateViewModal.vue'
import SubjectManagerModal from '../components/Templates/SubjectManagerModal.vue'
import Toast from '../components/Toast.vue'
import BaseButton from '../components/Base/BaseButton.vue'
import FormSelect from '../components/Base/FormSelect.vue'
import FormInput from '../components/Base/FormInput.vue'
import SubjectSelect from '../components/Base/SubjectSelect.vue'
import EmptyState from '../components/Base/EmptyState.vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useToast } from '../composables/useToast.js'
import { useModal } from '../composables/useModal.js'
import { useLocalStorage } from '../composables/useLocalStorage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { GRADE_OPTIONS } from '@/constants/index.js'
import { formatDateTime, getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'

export default {
  name: 'Templates',
  components: {
    TemplateModal,
    TemplateViewModal,
    SubjectManagerModal,
    Toast,
    BaseButton,
    FormSelect,
    FormInput,
    SubjectSelect,
    EmptyState
  },
  setup() {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError, showInfo } = useToast()
    // 科目/年級唯一來源
    const { subjectNames, getDisplayName, getGradeLabel, ensureLoaded, refresh, subjectBadgeClass, subjectBadgeStyle } = useSubjects()

    // 排序方式記在 localStorage:老師切到「自訂順序」後,下次進來維持該選擇
    const SORT_STORAGE_KEY = 'edurag:templatesSort'
    const VALID_SORTS = ['grade', 'newest', 'manual']
    const { load: loadSortPref, save: saveSortPref } = useLocalStorage(SORT_STORAGE_KEY, 'grade')

    const loading = ref(false)
    const templates = ref([])
    const searchQuery = ref('')
    const initialSort = loadSortPref()
    const sortBy = ref(VALID_SORTS.includes(initialSort) ? initialSort : 'grade')
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
    // 起始範本區塊收合狀態:沒存過偏好時,有範本就收、沒範本就展開(第一次使用需要它)
    const starterCollapsedStore = useLocalStorage('edurag:starterGalleryCollapsed', null)
    const starterCollapsed = ref(starterCollapsedStore.load() === true)
    let starterPrefTouched = starterCollapsedStore.load() !== null
    watch(starterCollapsed, (v) => { starterPrefTouched = true; starterCollapsedStore.save(v) })
    watch(templates, (list) => {
      if (!starterPrefTouched && list && list.length > 0) starterCollapsed.value = true
    })

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
          search: searchQuery.value || undefined,
          sort: sortBy.value || undefined,
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

    // 搜尋:Enter 立即觸發,輸入時 300ms 防抖;皆重置到第 1 頁
    let searchDebounceTimer = null
    const handleSearchEnter = () => {
      if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer)
        searchDebounceTimer = null
      }
      currentPage.value = 1
      fetchTemplates()
    }
    const handleSearchInput = () => {
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
      searchDebounceTimer = setTimeout(() => {
        currentPage.value = 1
        fetchTemplates()
      }, 300)
    }
    const handleSortChange = () => {
      currentPage.value = 1
      saveSortPref(sortBy.value)
      fetchTemplates()
    }

    // 自訂順序:上/下移動一格;第一次移動會在後端凍結目前排序,故移動後一律以 sort=manual 重新取得清單
    // 只有「自訂順序」且沒有任何篩選時才能上下移動:後端是對全部模板排序,
    // 篩選中移動會和看不見的模板對調,畫面上像沒反應
    const canReorder = computed(() =>
      sortBy.value === 'manual' && !selectedSubject.value && !selectedGrade.value && !searchQuery.value
    )
    const moving = ref(false)
    const moveTemplate = async (template, direction) => {
      if (moving.value) return  // 連點兩下會送出兩個互相打架的請求
      moving.value = true
      try {
        const result = await templateService.moveTemplate(template.id, direction)
        if (result && result.moved === false) {
          showInfo(t('templates.moveAtEdge'))
        }
        await fetchTemplates()
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.moveFailed'),
          'templates.move',
          error,
          t('templates.sortByManual')
        )
      } finally {
        moving.value = false
      }
    }

    // 拖曳排序：把模板拖到任意位置(canReorder 為 true 時才啟用,見上方 moveTemplate 註解)
    // draggingId：正被拖曳的模板 id；dropTarget：{ id, position } 目前指向的插入點
    // (position 為 'before' 代表插到該列上半部即該列之前，'after' 為下半部即之後)
    const draggingId = ref(null)
    const dropTarget = ref(null)

    const onDragStart = (event, template) => {
      if (!canReorder.value) return
      draggingId.value = template.id
      event.dataTransfer.effectAllowed = 'move'
      try {
        event.dataTransfer.setData('text/plain', String(template.id))
      } catch (e) {
        // 部分瀏覽器（極少數）setData 會丟例外，不影響拖曳本身，忽略即可
      }
    }

    const onDragOver = (event, template) => {
      if (!canReorder.value || draggingId.value === null) return
      event.preventDefault()
      if (draggingId.value === template.id) {
        dropTarget.value = null
        return
      }
      const rect = event.currentTarget.getBoundingClientRect()
      const position = event.clientY - rect.top < rect.height / 2 ? 'before' : 'after'
      dropTarget.value = { id: template.id, position }
    }

    const onDragLeave = (template) => {
      if (dropTarget.value && dropTarget.value.id === template.id) {
        dropTarget.value = null
      }
    }

    const onDrop = async (event, template) => {
      if (!canReorder.value) return
      event.preventDefault()
      const sourceId = draggingId.value
      const position = dropTarget.value && dropTarget.value.id === template.id ? dropTarget.value.position : null
      draggingId.value = null
      dropTarget.value = null

      // 丟到自己身上，或沒有有效的插入點(沒先觸發 dragover)：不送出請求
      if (!sourceId || sourceId === template.id || !position || moving.value) return

      moving.value = true
      try {
        const target = position === 'before' ? { before_id: template.id } : { after_id: template.id }
        await templateService.moveTemplateTo(sourceId, target)
        await fetchTemplates()
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.moveFailed'),
          'templates.move',
          error,
          t('templates.sortByManual')
        )
      } finally {
        moving.value = false
      }
    }

    const onDragEnd = () => {
      draggingId.value = null
      dropTarget.value = null
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

    // 複製模板:沿用原內容/科目/年級/題型/參數,名稱加上「（複製）」後綴,建立後直接開編輯
    const copyTemplate = async (template) => {
      const subjectId = template.subject_id ?? subjectList.value.find(s => s.name === template.subject)?.id ?? null
      if (!subjectId) {
        toastError(t('templates.copyFailed'), t('templates.copy'))
        return
      }

      try {
        const payload = {
          name: `${template.name}${t('templates.copySuffix')}`.slice(0, 100),  // TemplateCreate.name max_length=100
          subject_id: subjectId,
          content: template.content,
          question_type: template.question_type,
          grades: [...(template.grades || [])],
          params: { ...(template.params || {}) }
        }
        const created = await templateService.createTemplate(payload)

        await fetchTemplates()
        showSuccess(t('templates.copySuccess'), t('templates.copy'))

        editingTemplate.value = { ...created }
        showEditModal.value = true
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.copyFailed'),
          t('templates.copy'),
          error
        )
      }
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


    // 科目標籤顏色改用全站共用的 useSubjects 取色(科目管理設定的顏色)
    const getSubjectColor = (subject) => subjectBadgeClass(subject)
    const getSubjectStyle = (subject) => subjectBadgeStyle(subject)

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

    // 頁面被 keep-alive 快取後再次切回時,重新整理清單(保留篩選/搜尋/分頁狀態)
    let isFirstActivation = true
    onActivated(() => {
      if (isFirstActivation) {
        isFirstActivation = false
        return
      }
      fetchTemplates()
    })

    return {
      t,
      getDisplayName,
      getGradeLabel,
      loading,
      templates,
      subjectNames,
      searchQuery,
      sortBy,
      handleSearchEnter,
      handleSearchInput,
      handleSortChange,
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
      starterCollapsed,
      createFromType,
      viewingTemplate,
      subjectList,
      subjectManagerRef,
      fetchTemplates,
      initializeDefaults,
      closeModal,
      editTemplate,
      viewTemplate,
      copyTemplate,
      deleteTemplate,
      saveTemplate,
      moveTemplate,
      canReorder,
      moving,
      draggingId,
      dropTarget,
      onDragStart,
      onDragOver,
      onDragLeave,
      onDrop,
      onDragEnd,
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
