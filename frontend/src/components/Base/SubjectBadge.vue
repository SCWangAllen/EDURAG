<template>
  <span
    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
    :style="{ backgroundColor: color, color: textColor }"
  >
    {{ getDisplayName(subject) }}<template v-if="grade"> · {{ getGradeLabel(grade) }}</template>
  </span>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useSubjects } from '@/composables/useSubjects.js'
import { getTextColor } from '@/utils/subjectUtils.js'

const props = defineProps({
  subject: { type: String, required: true },
  grade: { type: String, default: '' }
})

const { getColor, getDisplayName, getGradeLabel, ensureLoaded } = useSubjects()

const color = computed(() => getColor(props.subject))
const textColor = computed(() => getTextColor(color.value))

onMounted(ensureLoaded)
</script>
