<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto" @click="$emit('close')">
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
              <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
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
                  <h4 class="font-medium text-gray-900">
                    {{ subject.name }}{{ subject.grade ? ` (${subject.grade})` : '' }}
                  </h4>
                </div>
                <div class="flex space-x-1">
                  <button
                    @click="editSubject(subject)"
                    class="text-gray-400 hover:text-blue-600 text-sm"
                  >
                    ✏️
                  </button>
                  <button
                    @click="handleDeleteSubject(subject)"
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
</template>

<script>
import { ref, watch } from 'vue'
import SubjectModal from '../SubjectModal.vue'
import subjectService from '../../api/subjectService.js'
import { useLanguage } from '../../composables/useLanguage.js'
import { useToast } from '../../composables/useToast.js'
import eventBus, { SUBJECT_EVENTS } from '@/utils/eventBus.js'

export default {
  name: 'SubjectManagerModal',
  components: {
    SubjectModal
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

    const subjectList = ref([])
    const subjectStats = ref({})
    const showSubjectModal = ref(false)
    const editingSubject = ref(null)

    const fetchSubjectList = async () => {
      try {
        const data = await subjectService.getSubjects()
        subjectList.value = data.subjects || []
      } catch (error) {
      }
    }

    const fetchSubjectStats = async () => {
      try {
        const data = await subjectService.getSubjectStats()
        subjectStats.value = data.stats || {}
      } catch (error) {
      }
    }

    const loadData = async () => {
      await Promise.all([fetchSubjectList(), fetchSubjectStats()])
    }

    // 當 modal 打開時載入資料
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        loadData()
      }
    })

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
          await subjectService.updateSubject(editingSubject.value.id, subjectData)

          eventBus.emit(SUBJECT_EVENTS.UPDATED, {
            id: editingSubject.value.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })

          showSuccess(t('templates.subjectUpdateSuccess').replace('{name}', subjectData.name), '科目更新')
        } else {
          const newSubject = await subjectService.createSubject(subjectData)

          eventBus.emit(SUBJECT_EVENTS.CREATED, {
            id: newSubject.id,
            name: subjectData.name,
            description: subjectData.description,
            color: subjectData.color
          })

          showSuccess(t('templates.subjectCreateSuccess').replace('{name}', subjectData.name), '科目創建')
        }

        closeSubjectModal()
        await loadData()

        eventBus.emit('system:reload_data', {
          scope: 'subjects'
        })

        emit('subjects-changed')

      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.subjectSaveFailed'),
          editingSubject.value?.id ? '科目更新' : '科目創建',
          error
        )
      }
    }

    const handleDeleteSubject = async (subject) => {
      if (!confirm(t('templates.confirmDeleteSubject').replace('{name}', subject.name))) {
        return
      }

      try {
        const templateCount = subjectStats.value[subject.name]?.template_count || 0
        const force = templateCount > 0 ? confirm(t('templates.forceDeleteSubjectWithTemplates').replace('{count}', templateCount)) : false

        await subjectService.deleteSubject(subject.id, force)

        eventBus.emit(SUBJECT_EVENTS.DELETED, {
          id: subject.id,
          name: subject.name
        })

        showSuccess(t('templates.subjectDeleteSuccess').replace('{name}', subject.name), '科目刪除')

        await loadData()
        emit('subjects-changed')
      } catch (error) {
        toastError(
          error.response?.data?.detail || error.message || t('templates.subjectDeleteFailed'),
          '科目刪除',
          error
        )
      }
    }

    return {
      t,
      subjectList,
      subjectStats,
      showSubjectModal,
      editingSubject,
      editSubject,
      closeSubjectModal,
      saveSubject,
      handleDeleteSubject,
      fetchSubjectList,
      fetchSubjectStats
    }
  }
}
</script>
