<template>
  <div ref="rootEl" class="relative">
    <!-- 觸發按鈕 -->
    <button
      type="button"
      class="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-left text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      @click="open = !open"
    >
      <span :class="modelValue.subject ? 'text-gray-900' : 'text-gray-400'">
        {{ displayLabel }}
      </span>
      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- 下拉面板：科目 → 年級 樹 -->
    <div
      v-if="open"
      class="absolute z-30 mt-1 w-full max-h-72 overflow-y-auto bg-white border border-gray-200 rounded-md shadow-lg"
    >
      <button
        v-if="clearable"
        type="button"
        class="w-full px-3 py-2 text-left text-sm text-gray-500 hover:bg-gray-50"
        @click="selectSubject('')"
      >
        {{ t('subjects.all') }}
      </button>

      <div v-for="node in tree" :key="node.name" class="border-t border-gray-100 first:border-t-0">
        <!-- 科目列：點選 = 該科全年級 -->
        <div class="flex items-center hover:bg-gray-50">
          <button
            type="button"
            class="flex-1 flex items-center gap-2 px-3 py-2 text-left text-sm"
            :class="isSelected(node.name, null) ? 'text-primary-600 font-medium' : 'text-gray-900'"
            @click="selectSubject(node.name)"
          >
            <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: node.color }" />
            {{ getDisplayName(node.name) }}
            <span class="text-xs text-gray-400">{{ t('subjects.allGrades') }}</span>
          </button>
          <button
            v-if="node.grades.length"
            type="button"
            class="px-2 py-2 text-gray-400 hover:text-gray-600"
            @click.stop="toggleExpand(node.name)"
          >
            <svg
              class="w-4 h-4 transition-transform"
              :class="expanded.has(node.name) ? 'rotate-90' : ''"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- 年級子列 -->
        <div v-if="expanded.has(node.name)">
          <button
            v-for="g in node.grades"
            :key="g.id"
            type="button"
            class="w-full pl-9 pr-3 py-1.5 text-left text-sm hover:bg-gray-50"
            :class="isSelected(node.name, g.grade) ? 'text-primary-600 font-medium' : 'text-gray-700'"
            @click="selectGrade(node.name, g.grade)"
          >
            {{ getGradeLabel(g.grade) }}
          </button>
        </div>
      </div>

      <div v-if="!tree.length" class="px-3 py-4 text-sm text-gray-400 text-center">
        {{ loading ? '…' : t('subjects.all') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'

// modelValue: { subject: string, grade: string|null }
// grade null/'' = 該科全年級；subject '' = 不篩選
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ subject: '', grade: null })
  },
  clearable: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useLanguage()
const { tree, loading, getDisplayName, getGradeLabel, ensureLoaded } = useSubjects()

const open = ref(false)
const expanded = ref(new Set())
const rootEl = ref(null)

const displayLabel = computed(() => {
  if (!props.modelValue.subject) return t('subjects.all')
  const name = getDisplayName(props.modelValue.subject)
  const grade = props.modelValue.grade
  return grade ? `${name} / ${getGradeLabel(grade)}` : `${name} / ${t('subjects.allGrades')}`
})

const isSelected = (subject, grade) =>
  props.modelValue.subject === subject && (props.modelValue.grade || null) === (grade || null)

const toggleExpand = (name) => {
  const next = new Set(expanded.value)
  if (next.has(name)) next.delete(name)
  else next.add(name)
  expanded.value = next
}

const selectSubject = (name) => {
  emit('update:modelValue', { subject: name, grade: null })
  open.value = false
}

const selectGrade = (name, grade) => {
  emit('update:modelValue', { subject: name, grade })
  open.value = false
}

const handleClickOutside = (event) => {
  if (rootEl.value && !rootEl.value.contains(event.target)) {
    open.value = false
  }
}

onMounted(() => {
  ensureLoaded()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
