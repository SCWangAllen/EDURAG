<template>
  <select
    :value="modelValue"
    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
    @change="$emit('update:modelValue', $event.target.value)"
  >
    <option value="">{{ placeholder || t('subjects.all') }}</option>
    <option v-for="name in subjectNames" :key="name" :value="name">
      {{ getDisplayName(name) }}
    </option>
  </select>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' }
})

defineEmits(['update:modelValue'])

const { t } = useLanguage()
const { subjectNames, getDisplayName, ensureLoaded } = useSubjects()

onMounted(ensureLoaded)
</script>
