<template>
  <div class="flex flex-col gap-6">
    <!-- 篩選器區域 -->
    <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h3 class="text-base font-semibold text-gray-900 mb-4">🔍 篩選條件</h3>

      <div class="flex gap-3 flex-wrap">
        <div class="flex flex-col gap-1 min-w-[150px]">
          <label class="text-xs font-medium text-gray-500">科目</label>
          <select v-model="filters.subject" class="p-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]">
            <option value="">全部</option>
            <option v-for="subject in subjects" :key="subject" :value="subject">
              {{ getDisplayName(subject) }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-1 min-w-[150px]">
          <label class="text-xs font-medium text-gray-500">年級</label>
          <select v-model="filters.grade" class="p-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]">
            <option value="">全部</option>
            <option v-for="grade in grades" :key="grade" :value="grade">{{ getGradeLabel(grade) }}</option>
          </select>
        </div>

        <div class="flex flex-col gap-1 min-w-[150px]">
          <label class="text-xs font-medium text-gray-500">題型</label>
          <select v-model="filters.questionType" class="p-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]">
            <option value="">全部</option>
            <option v-for="qt in selectableQuestionTypes" :key="qt.value" :value="qt.value">{{ t(qt.labelKey) }}</option>
          </select>
        </div>

        <div class="flex flex-col gap-1 flex-1 min-w-[200px]">
          <label class="text-xs font-medium text-gray-500">搜尋</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="搜尋題目內容..."
            class="p-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)]"
          >
        </div>

        <div class="flex flex-col gap-1 min-w-[150px]">
          <label class="text-xs font-medium text-gray-500">&nbsp;</label>
          <button @click="resetFilters" class="px-3 py-2 bg-gray-500 text-white rounded-md text-sm cursor-pointer hover:bg-gray-600">
            🔄 重置
          </button>
        </div>
      </div>

      <!-- 快速隨機選題按鈕 -->
      <div class="mt-4 pt-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600">
            <span class="font-medium">🎲 快速選題：</span>
            {{ isWeeklyTestMode
              ? '根據每科設定的題數，自動隨機選取各科目題目'
              : '根據題型配置自動隨機選取符合篩選條件的題目' }}
          </div>
          <button
            @click="isWeeklyTestMode ? weeklyTestQuickSelect() : quickRandomSelect()"
            :disabled="randomSelecting || (!isWeeklyTestMode && !hasEnabledTypes) || (isWeeklyTestMode && !hasWeeklyTestSubjects)"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <span v-if="randomSelecting" class="animate-spin">⏳</span>
            <span v-else>🎲</span>
            {{ randomSelecting ? '選題中...' : '快速隨機選題' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 題型分頁 Tabs -->
    <QuestionTypeTabs
      v-model="currentTab"
      :types="enabledTypes"
      :stats="tabStats"
      @update:modelValue="onTabChange"
      class="mb-4"
    />

    <!-- 已選摘要 -->
    <SelectedQuestionsSummary
      :selected-count="selectedQuestions.length"
      :type-stats="typeStats"
      :question-type-config="questionTypeConfig"
      @clear="clearSelection"
    />

    <!-- 題目列表（含 Loading、空狀態、分頁） -->
    <QuestionSelectionList
      :questions="questions"
      :loading="loading"
      :total-questions="totalQuestions"
      :current-page="currentPage"
      :total-pages="totalPages"
      :page-numbers="pageNumbers"
      :selected-ids="selectedIdSet"
      :is-all-selected="isAllCurrentPageSelected"
      @toggle-selection="toggleSelection"
      @toggle-select-all="toggleSelectAllCurrentPage"
      @change-page="changePage"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { getQuestions } from '@/api/questionService.js'
import { getImageQuestions, getQuestionImageUrl, getAnswerImageUrl } from '@/api/imageQuestionService.js'
import { useToast } from '@/composables/useToast.js'
import { QUESTION_TYPES, GRADE_OPTIONS } from '@/constants/index.js'
import QuestionTypeTabs from './QuestionTypeTabs.vue'
import SelectedQuestionsSummary from './SelectedQuestionsSummary.vue'
import QuestionSelectionList from './QuestionSelectionList.vue'

const { t } = useLanguage()
const { showSuccess, showError: toastError } = useToast()
// 科目/年級唯一來源
const { subjectNames: subjects, getDisplayName, getGradeLabel, ensureLoaded } = useSubjects()
const grades = GRADE_OPTIONS.map(g => g.value)

const props = defineProps({
  examInfo: {
    type: Object,
    required: true
  },
  questionTypeConfig: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['questions-loaded', 'questions-updated', 'sync-config'])

// ==================== 狀態 ====================

const questions = ref([])
const selectedQuestions = ref([])
const loading = ref(false)
const randomSelecting = ref(false)  // 快速選題中
const currentTab = ref('')  // 當前選中的題型 Tab（空字串表示「全部」）

const filters = ref({
  subject: '',
  grade: '',
  questionType: '',
  search: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const totalQuestions = ref(0)

// 篩選用的題型（排除 mixed/auto）
const selectableQuestionTypes = computed(() =>
  QUESTION_TYPES.filter(qt => qt.value !== 'mixed' && qt.value !== 'auto')
)

// ==================== 計算屬性 ====================

const totalPages = computed(() => {
  return Math.ceil(totalQuestions.value / pageSize.value)
})

const pageNumbers = computed(() => {
  const pages = []
  const maxVisible = 5
  const total = totalPages.value

  if (total <= maxVisible) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      for (let i = 1; i <= maxVisible; i++) {
        pages.push(i)
      }
    } else if (currentPage.value >= total - 2) {
      for (let i = total - maxVisible + 1; i <= total; i++) {
        pages.push(i)
      }
    } else {
      for (let i = currentPage.value - 2; i <= currentPage.value + 2; i++) {
        pages.push(i)
      }
    }
  }

  return pages
})

const typeStats = computed(() => {
  const stats = {}
  selectedQuestions.value.forEach(q => {
    const type = q.type  // ✅ 統一使用 'type' 欄位（後端回傳的欄位名）
    if (type) {
      stats[type] = (stats[type] || 0) + 1
    }
  })
  return stats
})

// 從父組件傳入的 questionTypeConfig 獲取已啟用的題型
const enabledTypes = computed(() => {
  return Object.keys(props.questionTypeConfig)
    .filter(type => props.questionTypeConfig[type].enabled)
    .map(type => ({
      type: type,
      count: props.questionTypeConfig[type].count
    }))
})

// 是否有啟用的題型且有需要選取的題目數量
const hasEnabledTypes = computed(() => {
  return enabledTypes.value.some(t => t.count > 0)
})

// Weekly Test 模式判斷
const isWeeklyTestMode = computed(() => {
  return props.examInfo.isWeeklyTest === true
})

// 是否有 Weekly Test 科目可選
const hasWeeklyTestSubjects = computed(() => {
  const subjects = props.examInfo.subjects || []
  const counts = props.examInfo.weeklyTestSubjectCounts || {}
  return subjects.length > 0 && subjects.some(sub => (counts[sub] || 0) > 0)
})

// 為 QuestionTypeTabs 準備統計資料
const tabStats = computed(() => {
  const stats = {}
  Object.keys(typeStats.value).forEach(type => {
    stats[type] = {
      selected: typeStats.value[type],  // 已選數量
      generated: 0,  // 自選模式不適用
    }
  })
  return stats
})

const selectedIdSet = computed(() => {
  return new Set(selectedQuestions.value.map(q => q.id))
})

const isAllCurrentPageSelected = computed(() => {
  if (questions.value.length === 0) return false
  return questions.value.every(q => selectedIdSet.value.has(q.id))
})

// ==================== 方法 ====================

const loadQuestions = async () => {
  try {
    loading.value = true

    const params = {
      page: currentPage.value,
      size: pageSize.value
    }

    // 優先使用 Tab 篩選（如果有選中特定題型）
    const activeFilter = currentTab.value || filters.value.questionType

    // 圖片題目使用獨立 API
    if (activeFilter === 'diagram_question') {
      await loadImageQuestions()
      return
    }

    if (activeFilter) params.question_type = activeFilter

    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.grade) params.grade = filters.value.grade
    if (filters.value.search) params.search = filters.value.search


    const response = await getQuestions(params)

    questions.value = response.data.questions || []
    totalQuestions.value = response.data.total || 0


  } catch (error) {
    toastError('載入題目失敗', '載入題目列表')
  } finally {
    loading.value = false
  }
}

// 載入圖片題目
const loadImageQuestions = async () => {
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      verified: true  // 只載入已驗證的圖片題目
    }

    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.grade) params.grade = filters.value.grade
    if (filters.value.search) params.search = filters.value.search

    const response = await getImageQuestions(params)
    const imageQuestionsData = response.data.questions || response.data.diagram_questions || []

    // 轉換 ImageQuestion 為與 Question 相容的格式
    questions.value = imageQuestionsData.map(iq => ({
      id: `img_${iq.id}`,  // 前綴區分
      _originalId: iq.id,
      type: 'diagram_question',
      content: iq.question_description || '圖片題',
      question_image: iq.question_image,
      question_image_ext: iq.question_image_ext,
      answer_image: iq.answer_image,
      answer_image_ext: iq.answer_image_ext,
      subject: iq.subject,
      grade: iq.grade,
      chapter: iq.chapter,
      page: iq.page,
      explanation: iq.question_description,
      images_verified: iq.images_verified,
      // 提供完整圖片 URL
      question_image_url: getQuestionImageUrl(
        iq.question_image + (iq.question_image_ext ? `.${iq.question_image_ext}` : '')
      ),
      answer_image_url: iq.answer_image ? getAnswerImageUrl(
        iq.answer_image + (iq.answer_image_ext ? `.${iq.answer_image_ext}` : '')
      ) : null
    }))

    totalQuestions.value = response.data.total || 0

  } catch (error) {
    toastError('載入圖片題目失敗', '載入圖片題目')
  } finally {
    loading.value = false
  }
}

const toggleSelection = (question) => {
  const index = selectedQuestions.value.findIndex(q => q.id === question.id)

  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(question)
  }

  emit('questions-updated', { questions: selectedQuestions.value })

  // ✅ 自動同步配置
  autoSyncConfig()
}

const toggleSelectAllCurrentPage = () => {
  if (isAllCurrentPageSelected.value) {
    // 取消選擇本頁所有題目
    questions.value.forEach(q => {
      const index = selectedQuestions.value.findIndex(sq => sq.id === q.id)
      if (index > -1) {
        selectedQuestions.value.splice(index, 1)
      }
    })
  } else {
    // 選擇本頁所有題目
    questions.value.forEach(q => {
      if (!selectedIdSet.value.has(q.id)) {
        selectedQuestions.value.push(q)
      }
    })
  }

  emit('questions-updated', { questions: selectedQuestions.value })

  // ✅ 自動同步配置
  autoSyncConfig()
}

const clearSelection = () => {
  selectedQuestions.value = []
  emit('questions-updated', { questions: [] })

  // ✅ 自動同步配置
  autoSyncConfig()

  showSuccess('已清空選擇', '清空題目')
}

// ✅ 自動同步配置到父組件
const autoSyncConfig = () => {
  emit('sync-config', { typeStats: typeStats.value })
}

// Tab 切換方法
const onTabChange = (questionType) => {
  currentTab.value = questionType
  currentPage.value = 1  // 重置到第一頁
  loadQuestions()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadQuestions()
}

const resetFilters = () => {
  filters.value = {
    subject: '',
    grade: '',
    questionType: '',
    search: ''
  }
  currentPage.value = 1
}

// 題型名稱（使用 i18n）
const getTypeName = (type) => {
  return t(`generate.${type}`) || type
}

// 快速隨機選題
const quickRandomSelect = async () => {
  if (randomSelecting.value) return

  // 獲取需要選取的題型和數量
  const typesToSelect = Object.entries(props.questionTypeConfig)
    .filter(([_, config]) => config.enabled && config.count > 0)
    .map(([type, config]) => ({ type, count: config.count }))

  if (typesToSelect.length === 0) {
    toastError('請先在題型配置中設定需要的題目數量', '快速選題')
    return
  }

  randomSelecting.value = true

  try {
    // 清空現有選擇
    selectedQuestions.value = []

    const allSelectedQuestions = []
    const failedTypes = []
    const insufficientTypes = []  // 記錄數量不足的題型

    // 針對每個題型分別獲取題目
    for (const { type, count } of typesToSelect) {
      try {
        // 圖片題目使用獨立 API
        if (type === 'diagram_question') {
          const response = await getImageQuestions({
            page: 1,
            size: count * 3, // 獲取多一些以便隨機選取
            verified: true,
            subject: filters.value.subject || undefined,
            grade: filters.value.grade || undefined
          })

          const imageQuestionsData = response.data.questions || response.data.diagram_questions || []
          const formattedQuestions = imageQuestionsData.map(iq => ({
            id: `img_${iq.id}`,
            _originalId: iq.id,
            type: 'diagram_question',
            content: iq.question_description || '圖片題',
            question_image: iq.question_image,
            question_image_ext: iq.question_image_ext,
            answer_image: iq.answer_image,
            answer_image_ext: iq.answer_image_ext,
            subject: iq.subject,
            grade: iq.grade,
            chapter: iq.chapter,
            page: iq.page,
            explanation: iq.question_description,
            images_verified: iq.images_verified,
            question_image_url: getQuestionImageUrl(
              iq.question_image + (iq.question_image_ext ? `.${iq.question_image_ext}` : '')
            ),
            answer_image_url: iq.answer_image ? getAnswerImageUrl(
              iq.answer_image + (iq.answer_image_ext ? `.${iq.answer_image_ext}` : '')
            ) : null
          }))

          // 隨機選取指定數量
          const shuffled = formattedQuestions.sort(() => Math.random() - 0.5)
          const selectedForType = shuffled.slice(0, count)
          allSelectedQuestions.push(...selectedForType)

          // 檢查數量是否足夠
          if (selectedForType.length < count) {
            insufficientTypes.push({
              type,
              typeName: getTypeName(type),
              expected: count,
              actual: selectedForType.length
            })
          }
        } else {
          // 一般題目
          const response = await getQuestions({
            page: 1,
            size: count * 3, // 獲取多一些以便隨機選取
            question_type: type,
            subject: filters.value.subject || undefined,
            grade: filters.value.grade || undefined
          })

          const questionsData = response.data.questions || []

          // 隨機選取指定數量
          const shuffled = questionsData.sort(() => Math.random() - 0.5)
          const selectedForType = shuffled.slice(0, count)
          allSelectedQuestions.push(...selectedForType)

          // 檢查數量是否足夠
          if (selectedForType.length < count) {
            insufficientTypes.push({
              type,
              typeName: getTypeName(type),
              expected: count,
              actual: selectedForType.length
            })
          }
        }
      } catch (error) {
        failedTypes.push(type)
      }
    }

    // 更新選擇
    selectedQuestions.value = allSelectedQuestions

    // 通知父組件
    emit('questions-updated', { questions: allSelectedQuestions })
    autoSyncConfig()

    // 顯示結果
    const totalSelected = allSelectedQuestions.length

    // 顯示數量不足警告
    if (insufficientTypes.length > 0) {
      const details = insufficientTypes
        .map(t => `• ${t.typeName}：需要 ${t.expected} 題，僅找到 ${t.actual} 題`)
        .join('\n')

      const filterInfo = (filters.value.subject || filters.value.grade)
        ? `\n\n目前篩選條件：${[filters.value.subject, filters.value.grade].filter(Boolean).join(' / ')}`
        : ''

      toastError(
        `部分題型在篩選範圍內數量不足：\n${details}${filterInfo}\n\n請調整篩選條件或減少題目數量。`,
        '題目數量不足'
      )
    }

    if (failedTypes.length > 0) {
      showSuccess(
        `已隨機選取 ${totalSelected} 題（部分題型獲取失敗：${failedTypes.map(t => getTypeName(t)).join(', ')}）`,
        '快速選題'
      )
    } else if (insufficientTypes.length === 0) {
      showSuccess(`已隨機選取 ${totalSelected} 題`, '快速選題')
    } else {
      // 有數量不足但仍選取了部分題目
      showSuccess(`已隨機選取 ${totalSelected} 題（部分題型數量不足）`, '快速選題')
    }

  } catch (error) {
    toastError('快速選題失敗: ' + error.message, '快速選題')
  } finally {
    randomSelecting.value = false
  }
}

// Weekly Test 快速選題：按科目分別抓題
const weeklyTestQuickSelect = async () => {
  if (randomSelecting.value) return

  const subjects = props.examInfo.subjects || []
  const subjectCounts = props.examInfo.weeklyTestSubjectCounts || {}
  const grade = props.examInfo.grade || ''

  if (subjects.length === 0) {
    toastError('請先選擇科目', '快速選題')
    return
  }

  randomSelecting.value = true

  try {
    selectedQuestions.value = []
    const allSelectedQuestions = []
    const insufficientSubjects = []

    for (const subject of subjects) {
      const targetCount = subjectCounts[subject] || 10

      try {
        // 對每個科目獲取題目
        const response = await getQuestions({
          page: 1,
          size: targetCount * 3,
          subject: subject,
          grade: grade || undefined
        })

        const questionsData = response.data.questions || []

        // 隨機選取指定數量
        const shuffled = [...questionsData].sort(() => Math.random() - 0.5)
        const selectedForSubject = shuffled.slice(0, targetCount)
        allSelectedQuestions.push(...selectedForSubject)

        if (selectedForSubject.length < targetCount) {
          insufficientSubjects.push({
            subject,
            expected: targetCount,
            actual: selectedForSubject.length
          })
        }
      } catch (error) {
        insufficientSubjects.push({
          subject,
          expected: targetCount,
          actual: 0
        })
      }
    }

    // 更新選擇
    selectedQuestions.value = allSelectedQuestions
    emit('questions-updated', { questions: allSelectedQuestions })
    autoSyncConfig()

    // 顯示結果
    if (insufficientSubjects.length > 0) {
      const details = insufficientSubjects
        .map(s => `• ${s.subject}：需要 ${s.expected} 題，僅找到 ${s.actual} 題`)
        .join('\n')
      toastError(`部分科目題目數量不足：\n${details}`, '題目數量不足')
    }

    showSuccess(
      `已隨機選取 ${allSelectedQuestions.length} 題（共 ${subjects.length} 科）`,
      '快速選題'
    )
  } catch (error) {
    toastError('快速選題失敗: ' + error.message, '快速選題')
  } finally {
    randomSelecting.value = false
  }
}

// ==================== 監聽 ====================

watch(filters, () => {
  currentPage.value = 1
  loadQuestions()
}, { deep: true })

// 監聯 examInfo 變化，同步更新篩選條件（批次更新避免多次觸發）
watch(() => props.examInfo, (newInfo) => {
  if (!newInfo) return

  const updates = {}
  // Weekly Test 模式下不自動設定 subject 篩選（因為多科目）
  if (!newInfo.isWeeklyTest && newInfo.subject && newInfo.subject !== filters.value.subject) {
    updates.subject = newInfo.subject
  }
  if (newInfo.grade && newInfo.grade !== filters.value.grade) {
    updates.grade = newInfo.grade
  }

  // 一次性更新，只觸發一次 filters watch
  if (Object.keys(updates).length > 0) {
    filters.value = { ...filters.value, ...updates }
  }
}, { deep: true })

// ==================== 生命週期 ====================

onMounted(() => {
  // 載入科目/年級樹
  ensureLoaded()

  // 不再自動從 examInfo 設定篩選器，讓使用者自行選擇「全部」或特定篩選條件
  // 篩選器預設值為空字串（全部）
  loadQuestions()
})
</script>
