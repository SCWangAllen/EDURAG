<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">{{ t('imageQuestions.batchRetagTitle') }}</h3>
        <button type="button" class="text-gray-400 hover:text-gray-600" @click="$emit('close')">✕</button>
      </div>

      <div class="px-6 py-4 space-y-4">
        <p class="text-sm text-gray-500">
          {{ t('imageQuestions.batchRetagHint').replace('{n}', count) }}
        </p>

        <!-- Subject -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.subject') }}</label>
          <SubjectSelect v-model="form.subject" :placeholder="t('imageQuestions.keepUnchanged')" />
        </div>

        <!-- Grade -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.grade') }}</label>
          <select
            v-model="form.grade"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">{{ t('imageQuestions.keepUnchanged') }}</option>
            <option v-for="g in gradeOptions" :key="g" :value="g">{{ getGradeLabel(g) }}</option>
          </select>
        </div>

        <!-- Chapter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.chapter') }}</label>
          <input
            v-model="form.chapter"
            type="text"
            :placeholder="t('imageQuestions.keepUnchanged')"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-2">
        <button
          type="button"
          class="px-4 py-2 rounded-md border border-gray-300 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          @click="$emit('close')"
        >
          {{ t('cancel') }}
        </button>
        <button
          type="button"
          :disabled="!hasChange || applying"
          class="px-4 py-2 rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
          @click="apply"
        >
          {{ t('imageQuestions.applyRetag') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, computed, watch, onMounted } from 'vue'
import { useEscapeToClose } from '@/composables/useEscapeToClose.js'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import SubjectSelect from '@/components/Base/SubjectSelect.vue'

export default {
  name: 'BatchTagModal',
  components: {
    SubjectSelect
  },
  props: {
    visible: { type: Boolean, default: false },
    count: { type: Number, default: 0 },
    applying: { type: Boolean, default: false },
  },
  emits: ['close', 'apply'],
  setup(props, { emit }) {
    useEscapeToClose(() => props.visible, () => emit('close'))  // Esc 關閉
    const { t } = useLanguage()
    const { tree, subjectNames, gradesFor, getGradeLabel, getDisplayName, ensureLoaded } = useSubjects()

    const form = reactive({ subject: '', grade: '', chapter: '' })

    // 年級選項:選了科目 → 該科目年級;否則 = 所有科目年級的聯集(動態,支援自訂年級)
    const gradeOptions = computed(() => {
      if (form.subject) return gradesFor(form.subject)
      const all = new Set()
      for (const node of tree.value) {
        for (const g of node.grades || []) all.add(g.grade)
      }
      return [...all]
    })

    const hasChange = computed(
      () => !!(form.subject || form.grade || form.chapter.trim())
    )

    // 每次開啟時清空
    watch(
      () => props.visible,
      (v) => {
        if (v) {
          form.subject = ''
          form.grade = ''
          form.chapter = ''
        }
      }
    )

    const apply = () => {
      const fields = {}
      if (form.subject) fields.subject = form.subject
      if (form.grade) fields.grade = form.grade
      if (form.chapter.trim()) fields.chapter = form.chapter.trim()
      emit('apply', fields)
    }

    onMounted(() => ensureLoaded())

    return { t, subjectNames, gradeOptions, getGradeLabel, getDisplayName, form, hasChange, apply }
  },
}
</script>
