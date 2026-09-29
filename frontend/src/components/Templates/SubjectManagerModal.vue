<template>
  <BaseModal
    :model-value="visible"
    size="2xl"
    @update:model-value="$emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-between w-full pr-3">
        <h3 class="text-lg font-medium text-gray-900">{{ t('templates.subjectManagementTitle') }}</h3>
        <button
          @click="openCreateSubject"
          class="bg-primary-600 hover:bg-primary-700 text-white px-3 py-1 rounded text-sm font-medium"
        >
          + {{ t('templates.addSubject') }}
        </button>
      </div>
    </template>

    <!-- 科目清單（資料夾式：科目 → 年級，預設收合） -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="node in tree"
        :key="node.name"
        class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
      >
        <!-- 科目標題列：展開鈕 + 名稱 + 新增年級 / 編輯科目資訊 -->
        <div class="flex items-center justify-between mb-1">
          <button
            @click="toggleExpand(node.name)"
            class="flex items-center space-x-2 flex-1 min-w-0 text-left focus:outline-none"
          >
            <svg
              :class="['w-4 h-4 text-gray-400 flex-shrink-0 transition-transform', isExpanded(node.name) ? 'rotate-90' : '']"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span
              :style="{ backgroundColor: node.color }"
              class="inline-block w-3.5 h-3.5 rounded-full flex-shrink-0"
            ></span>
            <h4 class="font-medium text-gray-900 truncate flex-1 min-w-0" :title="getDisplayName(node.name)">{{ getDisplayName(node.name) }}</h4>
          </button>
          <div class="flex items-center space-x-1 flex-shrink-0 ml-2">
            <button
              @click="openAddGrade(node)"
              class="text-gray-400 hover:text-primary-600 text-base leading-none px-1"
              :title="t('templates.addGrade')"
            >
              ＋
            </button>
            <button
              @click="openEditGroup(node)"
              class="text-gray-400 hover:text-primary-600 text-sm px-1"
              :title="t('templates.editSubjectInfo')"
            >
              ✏️
            </button>
          </div>
        </div>
        <!-- 年級數 / 範本數放第二行,標題列只留名稱,避免名稱在 4 欄卡片中被擠到 0 寬 -->
        <p class="text-xs text-gray-500 pl-6 mb-2">
          {{ node.grades.length }} {{ t('templates.gradeCount') }} · {{ nodeTemplateCount(node) }} {{ t('templates.templateCount') }}
        </p>

        <!-- 年級列（可收合），依學制分組（ESL / Grade Level / Junior Class）顯示小標題 -->
        <div v-show="isExpanded(node.name)" class="pl-6 space-y-2">
          <div v-for="group in groupedGradesFor(node)" :key="group.key">
            <p v-if="group.labelKey" class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
              {{ t(group.labelKey) }}
            </p>
            <ul class="space-y-1">
              <li
                v-for="g in group.items"
                :key="g.id"
                class="flex justify-between items-center py-1 px-2 rounded hover:bg-gray-50"
              >
                <span class="text-sm text-gray-700">{{ getGradeLabel(g.grade) }}</span>
                <div class="flex space-x-1">
                  <button
                    @click="editSubject(g.id)"
                    class="text-gray-400 hover:text-primary-600 text-sm"
                  >
                    ✏️
                  </button>
                  <button
                    @click="handleDeleteSubject(node, g)"
                    class="text-gray-400 hover:text-red-600 text-sm"
                  >
                    🗑️
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-if="tree.length === 0" class="text-center py-8 text-gray-500">
      <p>{{ t('templates.noSubjects') }}</p>
    </div>
  </BaseModal>

  <!-- 新增/編輯科目 Modal（支援：編輯單列 / 新增年級 / 編輯科目資訊） -->
  <SubjectModal
    :show="showSubjectModal"
    :subject="editingSubject"
    :add-grade-parent="addGradeParent"
    :edit-group="editGroup"
    @close="closeSubjectModal"
    @save="saveSubject"
    @save-group="saveGroup"
  />
</template>

<script>
import { ref, watch } from 'vue'
import SubjectModal from '../SubjectModal.vue'
import subjectService from '../../api/subjectService.js'
import { useLanguage } from '../../composables/useLanguage.js'
import { useToast } from '../../composables/useToast.js'
import { useSubjects } from '@/composables/useSubjects.js'
import eventBus, { SUBJECT_EVENTS } from '@/utils/eventBus.js'
import BaseModal from '@/components/Base/BaseModal.vue'
import { GRADE_GROUPS, gradeSortIndex } from '@/constants/grades.js'

// 代碼 → 學制分組 key，用於把某科目的年級列分組顯示
const GROUP_KEY_BY_CODE = Object.fromEntries(
  GRADE_GROUPS.flatMap(group => group.grades.map(g => [g.code, group.key]))
)

export default {
  name: 'SubjectManagerModal',
  components: {
    SubjectModal,
    BaseModal
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'subjects-changed'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { showSuccess, showError: toastError } = useToast()
    // 科目→年級樹來源；CRUD 後 refresh() 讓全 app 同步
    const { tree, refresh, getDisplayName, getGradeLabel } = useSubjects()

    const subjectStats = ref({})
    const subjectStatsByName = ref({})
    const showSubjectModal = ref(false)
    const editingSubject = ref(null)
    // 新增年級 / 編輯科目資訊模式（與 editingSubject 互斥）
    const addGradeParent = ref(null)
    const editGroup = ref(null)
    const editGroupNode = ref(null)

    // 科目展開狀態；預設收合，refresh 後保留（不因重抓而重置）
    const expandedNodes = ref(new Set())
    const isExpanded = (name) => expandedNodes.value.has(name)
    const toggleExpand = (name) => {
      const next = new Set(expandedNodes.value)
      if (next.has(name)) {
        next.delete(name)
      } else {
        next.add(name)
      }
      expandedNodes.value = next
    }

    const fetchSubjectStats = async () => {
      try {
        const data = await subjectService.getSubjectStats()
        subjectStats.value = data.stats || {}
        subjectStatsByName.value = data.by_name || {}
      } catch (error) {
      }
    }

    const loadData = async () => {
      await Promise.all([refresh(), fetchSubjectStats()])
    }

    // 科目層級的範本數:依名稱統計(含舊的只存名稱範本);沒有時退回各年級列加總
    const nodeTemplateCount = (node) =>
      subjectStatsByName.value[node.name] ??
      (node.grades || []).reduce(
        (sum, g) => sum + (subjectStats.value[g.id]?.template_count || 0),
        0
      )

    // 將某科目的年級列依學制分組（ESL / Grade Level / Junior Class），
    // ALL 與未知舊資料字串歸入無標題的「其他」群組；只回傳非空群組
    const groupedGradesFor = (node) => {
      const buckets = GRADE_GROUPS.map(group => ({ key: group.key, labelKey: group.labelKey, items: [] }))
      const other = { key: 'other', labelKey: 'templates.otherGrades', items: [] }
      ;(node.grades || []).forEach(g => {
        const groupKey = GROUP_KEY_BY_CODE[g.grade]
        const bucket = groupKey ? buckets.find(b => b.key === groupKey) : other
        bucket.items.push(g)
      })
      buckets.forEach(b => b.items.sort((a, b2) => gradeSortIndex(a.grade) - gradeSortIndex(b2.grade)))
      other.items.sort((a, b2) => gradeSortIndex(a.grade) - gradeSortIndex(b2.grade))
      return [...buckets, other].filter(b => b.items.length > 0)
    }

    // 當 modal 打開時載入資料
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        loadData()
      }
    })

    const openCreateSubject = () => {
      editingSubject.value = null
      addGradeParent.value = null
      editGroup.value = null
      editGroupNode.value = null
      showSubjectModal.value = true
    }

    // 年級列僅帶 { id, grade }；用 id 取回完整科目物件供編輯
    const editSubject = async (subjectId) => {
      try {
        addGradeParent.value = null
        editGroup.value = null
        editGroupNode.value = null
        editingSubject.value = await subjectService.getSubject(subjectId)
        showSubjectModal.value = true
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.subjectSaveFailed'),
          t('ui.md_subject_load'),
          error
        )
      }
    }

    // 科目標題列「＋」：對該科目新增一個年級（走 create，同名不同 grade）
    const openAddGrade = (node) => {
      editingSubject.value = null
      editGroup.value = null
      editGroupNode.value = null
      addGradeParent.value = {
        name: node.name,
        color: node.color,
        existingGrades: node.grades.map(g => g.grade)
      }
      showSubjectModal.value = true
    }

    // 科目標題列「✏️」：編輯整組科目資訊（name/color/description），儲存時對全部年級列 PUT
    const openEditGroup = async (node) => {
      editingSubject.value = null
      addGradeParent.value = null
      editGroupNode.value = node

      // description 不在 tree 內，取第一列補上以利編輯；失敗不阻斷
      let description = ''
      try {
        if (node.grades.length) {
          const first = await subjectService.getSubject(node.grades[0].id)
          description = first?.description || ''
        }
      } catch (error) {
      }

      editGroup.value = {
        name: node.name,
        color: node.color,
        description,
        gradeIds: node.grades.map(g => g.id)
      }
      showSubjectModal.value = true
    }

    const closeSubjectModal = () => {
      showSubjectModal.value = false
      editingSubject.value = null
      addGradeParent.value = null
      editGroup.value = null
      editGroupNode.value = null
    }

    const saveSubject = async (subjectData) => {
      const displayName = getDisplayName(subjectData.name)
      try {
        if (editingSubject.value?.id) {
          await subjectService.updateSubject(editingSubject.value.id, subjectData)

          eventBus.emit(SUBJECT_EVENTS.UPDATED, {
            id: editingSubject.value.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })

          showSuccess(t('templates.subjectUpdateSuccess').replace('{name}', displayName), t('ui.md_subject_update'))
        } else {
          const newSubject = await subjectService.createSubject(subjectData)

          eventBus.emit(SUBJECT_EVENTS.CREATED, {
            id: newSubject.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })

          showSuccess(t('templates.subjectCreateSuccess').replace('{name}', displayName), t('ui.md_subject_create'))
        }

        closeSubjectModal()
        await loadData()

        eventBus.emit('system:reload_data', {
          scope: 'subjects'
        })

        emit('subjects-changed')

      } catch (error) {
        let errorMessage = error.response?.data?.detail || error.message || t('templates.subjectSaveFailed')

        // 處理重複科目名稱的錯誤提示
        if (errorMessage.includes('already exists') || errorMessage.includes('已存在') || errorMessage.includes('duplicate')) {
          errorMessage = t('templates.duplicateSubjectName').replace('{name}', displayName)
        }

        toastError(
          errorMessage,
          editingSubject.value?.id ? t('ui.md_subject_update') : t('ui.md_subject_create'),
          error,
          editingSubject.value?.id ? t('templates.subjectUpdateFailedTitle') : t('templates.subjectCreateFailedTitle')
        )
      }
    }

    // 編輯科目資訊：對該科目全部年級列迴圈 PUT（只更新 name/color/description，不動 grade）
    const saveGroup = async (groupData) => {
      const node = editGroupNode.value
      if (!node) {
        return
      }
      const displayName = getDisplayName(groupData.name)
      try {
        for (const g of node.grades) {
          await subjectService.updateSubject(g.id, {
            name: groupData.name,
            description: groupData.description,
            color: groupData.color
          })
        }

        eventBus.emit(SUBJECT_EVENTS.UPDATED, {
          name: groupData.name,
          description: groupData.description,
          color: groupData.color
        })

        showSuccess(t('templates.subjectUpdateSuccess').replace('{name}', displayName), t('ui.md_subject_update'))

        closeSubjectModal()
        await loadData()

        eventBus.emit('system:reload_data', {
          scope: 'subjects'
        })

        emit('subjects-changed')
      } catch (error) {
        let errorMessage = error.response?.data?.detail || error.message || t('templates.subjectSaveFailed')

        if (errorMessage.includes('already exists') || errorMessage.includes('已存在') || errorMessage.includes('duplicate')) {
          errorMessage = t('templates.duplicateSubjectName').replace('{name}', displayName)
        }

        toastError(errorMessage, t('ui.md_subject_update'), error, t('templates.subjectUpdateFailedTitle'))
      }
    }

    const handleDeleteSubject = async (node, gradeRow) => {
      const displayName = getDisplayName(node.name)
      if (!confirm(t('templates.confirmDeleteSubject').replace('{name}', displayName))) {
        return
      }

      try {
        // 統計以科目列 id 為 key;只看這個年級列自己的範本數
        const templateCount = subjectStats.value[gradeRow.id]?.template_count || 0
        const force = templateCount > 0 ? confirm(t('templates.forceDeleteSubjectWithTemplates').replace('{count}', templateCount)) : false

        await subjectService.deleteSubject(gradeRow.id, force)

        eventBus.emit(SUBJECT_EVENTS.DELETED, {
          id: gradeRow.id,
          name: node.name
        })

        showSuccess(t('templates.subjectDeleteSuccess').replace('{name}', displayName), t('ui.md_subject_delete'))

        await loadData()
        emit('subjects-changed')
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.subjectDeleteFailed'),
          t('ui.md_subject_delete'),
          error,
          t('templates.subjectDeleteFailedTitle')
        )
      }
    }

    return {
      t,
      tree,
      subjectStats,
      nodeTemplateCount,
      groupedGradesFor,
      showSubjectModal,
      editingSubject,
      addGradeParent,
      editGroup,
      isExpanded,
      toggleExpand,
      getDisplayName,
      getGradeLabel,
      openCreateSubject,
      editSubject,
      openAddGrade,
      openEditGroup,
      closeSubjectModal,
      saveSubject,
      saveGroup,
      handleDeleteSubject,
      fetchSubjectStats
    }
  }
}
</script>
