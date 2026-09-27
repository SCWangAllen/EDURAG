<template>
  <BaseModal
    :model-value="visible"
    size="md"
    :title="t('documents.copyToGradesTitle')"
    @update:model-value="handleClose"
  >
    <p class="text-sm text-gray-600 mb-4">
      {{ t('documents.copyToGradesHint').replace('{count}', count) }}
    </p>

    <div class="space-y-4 max-h-80 overflow-y-auto pr-1">
      <div v-for="group in gradeGroups" :key="group.key">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
          {{ t(group.labelKey) }}
        </p>
        <div class="flex flex-wrap gap-2">
          <label
            v-for="grade in group.grades"
            :key="grade.code"
            class="inline-flex items-center px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors"
            :class="selected.includes(grade.code)
              ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
              : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'"
          >
            <input type="checkbox" :value="grade.code" v-model="selected" class="sr-only" />
            {{ grade.label }}
          </label>
        </div>
      </div>

      <div>
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
          {{ t('documents.copyToGradesGeneric') }}
        </p>
        <label
          class="inline-flex items-center px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors"
          :class="selected.includes(allGradeOption.code)
            ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
            : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'"
        >
          <input type="checkbox" :value="allGradeOption.code" v-model="selected" class="sr-only" />
          {{ getGradeLabel(allGradeOption.code) }}
        </label>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        @click="handleClose"
        class="px-4 py-2 rounded-md border border-gray-300 shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ t('cancel') }}
      </button>
      <button
        type="button"
        :disabled="selected.length === 0 || copying"
        @click="confirm"
        class="px-4 py-2 rounded-md border border-transparent shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ copying ? t('documents.copying') : t('documents.copyToGradesConfirm') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, watch } from 'vue'
import BaseModal from '@/components/Base/BaseModal.vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { GRADE_GROUPS, ALL_GRADE } from '@/constants/grades.js'

export default {
  name: 'CopyToGradesModal',
  components: { BaseModal },
  props: {
    visible: { type: Boolean, default: false },
    count: { type: Number, default: 0 },
    copying: { type: Boolean, default: false }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { getGradeLabel } = useSubjects()

    const selected = ref([])

    // 每次開啟時清空已選年級
    watch(() => props.visible, (isVisible) => {
      if (isVisible) selected.value = []
    })

    const handleClose = () => emit('close')

    const confirm = () => {
      if (selected.value.length === 0) return
      emit('confirm', [...selected.value])
    }

    return {
      t,
      getGradeLabel,
      gradeGroups: GRADE_GROUPS,
      allGradeOption: ALL_GRADE,
      selected,
      handleClose,
      confirm
    }
  }
}
</script>
