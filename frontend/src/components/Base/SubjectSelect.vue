<template>
  <div ref="rootEl" class="relative">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
    <button
      ref="buttonEl"
      type="button"
      :disabled="disabled"
      role="combobox"
      aria-haspopup="listbox"
      :aria-expanded="open"
      :class="[
        'w-full flex items-center justify-between gap-2 border rounded-md shadow-sm bg-white',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        sizeClasses,
        disabled ? 'bg-gray-100 cursor-not-allowed text-gray-400 border-gray-200' : 'border-gray-300 text-gray-900'
      ]"
      @click="toggle"
      @keydown="onKeydown"
    >
      <span class="flex items-center gap-2 min-w-0 flex-1">
        <template v-if="modelValue">
          <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: currentColor }"></span>
          <span class="truncate">{{ currentLabel }}</span>
        </template>
        <span v-else class="truncate text-gray-400">{{ placeholderText }}</span>
      </span>
      <svg class="w-4 h-4 text-gray-400 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path
          fill-rule="evenodd"
          d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.25a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z"
          clip-rule="evenodd"
        />
      </svg>
    </button>

    <ul
      v-if="open"
      ref="panelEl"
      role="listbox"
      class="absolute z-50 mt-1 w-full min-w-[12rem] max-h-64 overflow-auto bg-white border border-gray-200 rounded-md shadow-lg py-1"
    >
      <li
        v-for="(row, idx) in rows"
        :key="row.value || '__empty__'"
        role="option"
        :aria-selected="row.value === modelValue"
        :class="[
          'flex items-center gap-2 px-3 py-2 text-sm cursor-pointer',
          row.value === modelValue ? 'bg-primary-50 text-primary-700' : 'text-gray-900',
          idx === highlightedIndex && row.value !== modelValue ? 'bg-gray-100' : ''
        ]"
        @mousemove="highlightedIndex = idx"
        @click="selectIndex(idx)"
      >
        <span
          class="w-2.5 h-2.5 rounded-full shrink-0"
          :class="row.color ? '' : 'border border-gray-300 bg-white'"
          :style="row.color ? { backgroundColor: row.color } : {}"
        ></span>
        <span class="truncate">{{ row.label }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  label: { type: String, default: '' },
  options: { type: Array, default: null },
  allowEmpty: { type: Boolean, default: true },
  disabled: { type: Boolean, default: false },
  size: { type: String, default: 'md' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const { t } = useLanguage()
const { subjectNames, getDisplayName, getColor, ensureLoaded } = useSubjects()

const rootEl = ref(null)
const buttonEl = ref(null)
const panelEl = ref(null)
const open = ref(false)
const highlightedIndex = ref(-1)

const placeholderText = computed(() => props.placeholder || t('subjects.all'))
const sizeClasses = computed(() => (props.size === 'sm' ? 'px-2 py-1.5 text-sm' : 'px-3 py-2 text-sm'))

// 未指定 options 時使用全部科目;options 傳入(即使是空陣列)代表限定清單
const optionNames = computed(() => (props.options !== null ? props.options : subjectNames.value))

const rows = computed(() => {
  const list = optionNames.value.map(name => ({
    value: name,
    label: getDisplayName(name),
    color: getColor(name)
  }))
  if (props.allowEmpty) {
    list.unshift({ value: '', label: placeholderText.value, color: null })
  }
  return list
})

const currentLabel = computed(() => getDisplayName(props.modelValue))
const currentColor = computed(() => getColor(props.modelValue))

const handleOutsideClick = (event) => {
  if (rootEl.value && !rootEl.value.contains(event.target)) {
    closePanel()
  }
}

const openPanel = () => {
  if (props.disabled) return
  open.value = true
  const idx = rows.value.findIndex(row => row.value === props.modelValue)
  highlightedIndex.value = idx >= 0 ? idx : 0
  document.addEventListener('mousedown', handleOutsideClick)
}

const closePanel = () => {
  if (!open.value) return
  open.value = false
  document.removeEventListener('mousedown', handleOutsideClick)
}

const toggle = () => {
  if (props.disabled) return
  if (open.value) closePanel()
  else openPanel()
}

const selectIndex = (idx) => {
  const row = rows.value[idx]
  if (!row) return
  if (row.value !== props.modelValue) {
    emit('update:modelValue', row.value)
    emit('change', row.value)
  }
  closePanel()
  buttonEl.value?.focus()
}

const onKeydown = (event) => {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!open.value) {
        openPanel()
      } else {
        highlightedIndex.value = Math.min(highlightedIndex.value + 1, rows.value.length - 1)
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      if (!open.value) {
        openPanel()
      } else {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
      }
      break
    case 'Home':
      if (open.value) {
        event.preventDefault()
        highlightedIndex.value = 0
      }
      break
    case 'End':
      if (open.value) {
        event.preventDefault()
        highlightedIndex.value = rows.value.length - 1
      }
      break
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (open.value) {
        selectIndex(highlightedIndex.value)
      } else {
        openPanel()
      }
      break
    case 'Escape':
      if (open.value) {
        event.preventDefault()
        closePanel()
        buttonEl.value?.focus()
      }
      break
  }
}

watch(highlightedIndex, async (idx) => {
  if (idx < 0 || !open.value) return
  await nextTick()
  const el = panelEl.value?.children?.[idx]
  el?.scrollIntoView({ block: 'nearest' })
})

onMounted(ensureLoaded)

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
})
</script>
