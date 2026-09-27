<template>
  <BaseModal
    :model-value="show"
    size="md"
    :title="modalTitle"
    @update:model-value="$emit('close')"
  >
    <form id="subjectModalForm" @submit.prevent="handleSubmit">
      <div class="space-y-6">
        <!-- 科目名稱：新增年級模式為唯讀，其餘可編輯 -->
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('subjectModal.subjectName') }}
            <span v-if="mode !== 'addGrade'" class="text-red-500">*</span>
          </label>
          <div
            v-if="mode === 'addGrade'"
            class="flex items-baseline space-x-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-md"
          >
            <span class="text-gray-900 font-medium">{{ getDisplayName(form.name) }}</span>
            <span v-if="getDisplayName(form.name) !== form.name" class="text-xs text-gray-400">({{ form.name }})</span>
          </div>
          <template v-else>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              maxlength="50"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              :placeholder="t('subjectModal.subjectNamePlaceholder')"
            />
            <p
              v-if="mode === 'editGroup' && getDisplayName(form.name) !== form.name"
              class="text-xs text-gray-500 mt-1"
            >
              {{ t('subjectModal.displayNameHint').replace('{name}', getDisplayName(form.name)) }}
            </p>
          </template>
        </div>

        <!-- 科目描述（新增年級模式隱藏，沿用父科目值） -->
        <div v-if="showDescription">
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('subjectModal.subjectDescription') }}
          </label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            maxlength="500"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            :placeholder="t('subjectModal.subjectDescriptionPlaceholder')"
          ></textarea>
        </div>

        <!-- 適用年級（編輯科目資訊模式隱藏，不動各列年級） -->
        <div v-if="showGrade">
          <label for="grade" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('subjectModal.subjectGrade') }} <span class="text-red-500">*</span>
          </label>
          <div class="flex space-x-2">
            <select
              id="gradeSelect"
              v-model="selectedGradePreset"
              @change="handleGradePresetChange"
              class="block w-1/2 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">{{ t('subjectModal.selectGrade') }}</option>
              <optgroup v-for="group in gradeGroups" :key="group.key" :label="t(group.labelKey)">
                <option
                  v-for="grade in group.grades"
                  :key="grade.code"
                  :value="grade.code"
                  :disabled="isGradeExisting(grade.code)"
                >
                  {{ grade.label }}{{ isGradeExisting(grade.code) ? ` (${t('subjectModal.gradeExistsOption')})` : '' }}
                </option>
              </optgroup>
              <option
                :value="allGradeOption.code"
                :disabled="isGradeExisting(allGradeOption.code)"
              >
                {{ allGradeOption.label }}{{ isGradeExisting(allGradeOption.code) ? ` (${t('subjectModal.gradeExistsOption')})` : '' }}
              </option>
              <option value="custom">{{ t('subjectModal.customGrade') }}</option>
            </select>
            <input
              v-if="showCustomGradeInput"
              id="gradeCustom"
              v-model="form.grade"
              type="text"
              required
              maxlength="20"
              class="block w-1/2 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              :placeholder="t('subjectModal.customGradePlaceholder')"
            />
          </div>
          <p v-if="gradeExists" class="text-xs text-red-500 mt-1">
            {{ t('subjectModal.gradeExists').replace('{grade}', getGradeLabel(form.grade)) }}
          </p>
          <p v-else class="text-xs text-gray-500 mt-1">{{ t('subjectModal.gradeHint') }}</p>
        </div>

        <!-- 科目顏色（新增年級模式隱藏，沿用父科目色） -->
        <div v-if="showColor">
          <label for="color" class="block text-sm font-medium text-gray-700 mb-2">
            {{ t('subjectModal.subjectColor') }}
          </label>
          <div class="flex items-center space-x-3">
            <input
              id="color"
              v-model="form.color"
              type="color"
              class="h-10 w-16 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
            <input
              v-model="form.color"
              type="text"
              pattern="^#[0-9A-Fa-f]{6}$"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="#3B82F6"
            />
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ t('subjectModal.colorHint') }}</p>
        </div>

        <!-- 預覽 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('subjectModal.preview') }}</label>
          <div class="p-3 bg-gray-50 rounded-md">
            <span
              :style="{ backgroundColor: form.color, color: getTextColor(form.color) }"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              {{ getDisplayName(form.name) || t('subjectModal.subjectNamePreview') }}
              <span v-if="form.grade" class="ml-1.5 text-xs">{{ getGradeLabel(form.grade) }}</span>
            </span>
          </div>
        </div>
      </div>
    </form>

    <template #footer>
      <button
        type="button"
        @click="$emit('close')"
        class="px-4 py-2 rounded-md border border-gray-300 shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ t('cancel') }}
      </button>
      <button
        type="submit"
        form="subjectModalForm"
        :disabled="submitDisabled"
        class="px-4 py-2 rounded-md border border-transparent shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ submitLabel }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, reactive, watch, computed } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { getTextColor } from '@/utils/subjectUtils.js'
import { GRADE_GROUPS, ALL_GRADE } from '@/constants/grades.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'SubjectModal',
  components: {
    BaseModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    // 既有：編輯單一科目列（含 id/name/grade/...）；null = 新增
    subject: {
      type: Object,
      default: null
    },
    // 新增年級到既有科目：{ name(canonical), color, description?, existingGrades?: [] }
    addGradeParent: {
      type: Object,
      default: null
    },
    // 編輯整組科目資訊：{ name(canonical), color, description, gradeIds: [] }
    editGroup: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'save', 'save-group'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { getDisplayName, getGradeLabel } = useSubjects()

    const form = reactive({
      name: '',
      description: '',
      grade: '',
      color: '#3B82F6'
    })

    const selectedGradePreset = ref('')

    // editGroup > addGrade > default（create/edit）
    const mode = computed(() => {
      if (props.editGroup) return 'editGroup'
      if (props.addGradeParent) return 'addGrade'
      return 'default'
    })

    const showDescription = computed(() => mode.value !== 'addGrade')
    const showGrade = computed(() => mode.value !== 'editGroup')
    const showColor = computed(() => mode.value !== 'addGrade')

    // 該科目已存在的年級（供新增年級模式擋重複）
    const existingGrades = computed(() => props.addGradeParent?.existingGrades || [])
    const isGradeExisting = (value) =>
      mode.value === 'addGrade' && existingGrades.value.includes(value)
    const gradeExists = computed(
      () =>
        mode.value === 'addGrade' &&
        !!form.grade.trim() &&
        existingGrades.value.includes(form.grade.trim())
    )

    const modalTitle = computed(() => {
      if (mode.value === 'editGroup') {
        return t('subjectModal.editGroupTitle').replace('{name}', getDisplayName(props.editGroup.name))
      }
      if (mode.value === 'addGrade') {
        return t('subjectModal.addGradeTitle').replace('{name}', getDisplayName(props.addGradeParent.name))
      }
      return props.subject ? t('subjectModal.editTitle') : t('subjectModal.createTitle')
    })

    const submitLabel = computed(() => {
      if (mode.value === 'editGroup') return t('subjectModal.update')
      if (mode.value === 'addGrade') return t('subjectModal.create')
      return props.subject ? t('subjectModal.update') : t('subjectModal.create')
    })

    const submitDisabled = computed(() => {
      if (mode.value === 'editGroup') return !form.name.trim()
      if (mode.value === 'addGrade') return !form.grade.trim() || gradeExists.value
      return !form.name.trim() || !form.grade.trim()
    })

    // 預設年級選項：單一來源 constants/grades.js（ESL / Grade Level / Junior Class + ALL）
    const gradeGroups = GRADE_GROUPS
    const allGradeOption = ALL_GRADE
    const allGradePresets = [...gradeGroups.flatMap(g => g.grades), allGradeOption]

    // 是否顯示自訂輸入框
    const showCustomGradeInput = computed(() => {
      return selectedGradePreset.value === 'custom'
    })

    // 處理預設年級選擇變化
    const handleGradePresetChange = () => {
      if (selectedGradePreset.value && selectedGradePreset.value !== 'custom') {
        form.grade = selectedGradePreset.value
      } else if (selectedGradePreset.value === 'custom') {
        form.grade = ''
      }
    }

    // 重置表單
    const resetForm = () => {
      form.name = ''
      form.description = ''
      form.grade = ''
      form.color = '#3B82F6'
      selectedGradePreset.value = ''
    }

    // 依模式載入表單資料
    const loadForm = () => {
      if (mode.value === 'editGroup') {
        form.name = props.editGroup.name || ''
        form.description = props.editGroup.description || ''
        form.grade = ''
        form.color = props.editGroup.color || '#3B82F6'
        selectedGradePreset.value = ''
      } else if (mode.value === 'addGrade') {
        form.name = props.addGradeParent.name || ''
        form.description = props.addGradeParent.description || ''
        form.grade = ''
        form.color = props.addGradeParent.color || '#3B82F6'
        selectedGradePreset.value = ''
      } else if (props.subject) {
        form.name = props.subject.name || ''
        form.description = props.subject.description || ''
        form.grade = props.subject.grade || ''
        form.color = props.subject.color || '#3B82F6'

        // 設定年級預設選擇
        const preset = allGradePresets.find(p => p.code === form.grade)
        if (preset) {
          selectedGradePreset.value = form.grade
        } else if (form.grade) {
          selectedGradePreset.value = 'custom'
        } else {
          selectedGradePreset.value = ''
        }
      } else {
        resetForm()
      }
    }

    // 提交表單
    const handleSubmit = () => {
      if (mode.value === 'editGroup') {
        if (!form.name.trim()) {
          return
        }
        emit('save-group', {
          name: form.name.trim(),
          description: form.description.trim() || null,
          color: form.color
        })
        return
      }

      // addGrade 與 default 都需要 grade
      if (!form.grade.trim()) {
        return
      }
      if (mode.value === 'addGrade' && gradeExists.value) {
        return
      }

      const subjectData = {
        name: form.name.trim(),
        description: form.description.trim() || null,
        grade: form.grade.trim(),
        color: form.color
      }

      emit('save', subjectData)
    }

    // 以 mode + 識別碼為 key；只在 Modal 打開或 key 改變時載入，避免覆蓋使用者編輯
    const wasOpen = ref(false)
    const lastKey = ref(null)
    const currentKey = computed(() => {
      if (props.editGroup) return `group:${props.editGroup.name}`
      if (props.addGradeParent) return `addgrade:${props.addGradeParent.name}`
      if (props.subject) return `edit:${props.subject.id}`
      return 'create'
    })

    watch(
      () => [props.show, currentKey.value],
      ([newShow, key]) => {
        const isOpening = newShow && !wasOpen.value
        const keyChanged = key !== lastKey.value

        if (newShow && (isOpening || keyChanged)) {
          loadForm()
          lastKey.value = key
        } else if (!newShow) {
          lastKey.value = null
        }

        wasOpen.value = newShow
      },
      { immediate: true }
    )

    return {
      t,
      form,
      mode,
      gradeGroups,
      allGradeOption,
      selectedGradePreset,
      showCustomGradeInput,
      showDescription,
      showGrade,
      showColor,
      isGradeExisting,
      gradeExists,
      modalTitle,
      submitLabel,
      submitDisabled,
      handleGradePresetChange,
      handleSubmit,
      getTextColor,
      getDisplayName,
      getGradeLabel
    }
  }
}
</script>
