<template>
  <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
    <!-- 摘要統計 -->
    <div class="flex justify-between items-center p-4 bg-gray-50 border-b border-gray-200">
      <div class="flex gap-6">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500">已生成</span>
          <span class="text-xl font-bold text-primary-500">{{ questions.length }}</span>
        </div>
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500">已選 / 應選</span>
          <span
            class="text-xl font-bold"
            :class="{
              'text-gray-400': countStatusClass === 'status-empty',
              'text-amber-500': countStatusClass === 'status-partial',
              'text-emerald-600': countStatusClass === 'status-complete',
              'text-danger-600': countStatusClass === 'status-over'
            }"
          >{{ selectedCount }} / {{ targetCount }}</span>
        </div>
      </div>

      <div class="flex gap-2">
        <button
          v-if="unselectedQuestions.length > 0"
          @click="clearUnselected"
          class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200 bg-white text-gray-500 border border-gray-300 hover:bg-gray-50 hover:border-gray-400"
          title="刪除所有未勾選的題目"
        >
          🗑️ 清空未選用 ({{ unselectedQuestions.length }})
        </button>
        <button
          v-if="questions.length > 0"
          @click="toggleSelectAll"
          class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200 bg-primary-500 text-white hover:bg-primary-600"
        >
          {{ isAllSelected ? '取消全選' : '全選' }}
        </button>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-if="questions.length === 0" class="py-12 px-8 text-center">
      <div class="text-5xl mb-4 opacity-50">📝</div>
      <p class="text-base font-medium text-gray-500 mb-2">尚未生成題目</p>
      <p class="text-sm text-gray-400">點擊上方「生成題目」按鈕開始生成</p>
    </div>

    <!-- 題目列表 -->
    <div v-else class="flex flex-col">
      <div
        v-for="(question, index) in questions"
        :key="question.id || index"
        :class="[
          'flex items-start gap-4 p-4 border-b border-gray-100 transition-colors duration-200 last:border-b-0',
          question.selected ? 'bg-primary-50' : 'opacity-60 hover:bg-gray-50'
        ]"
      >
        <!-- 勾選框 -->
        <div>
          <input
            type="checkbox"
            :checked="question.selected"
            @change="toggleSelection(question)"
            class="w-5 h-5 cursor-pointer"
          />
        </div>

        <!-- 序號 -->
        <div
          class="flex-shrink-0 w-8 h-8 flex items-center justify-center text-white rounded-full text-sm font-semibold"
          :class="question.selected ? 'bg-primary-500' : 'bg-gray-400'"
        >{{ index + 1 }}</div>

        <!-- 題目內容 -->
        <div class="flex-1 min-w-0">
          <!-- 題目文字 -->
          <div class="text-[15px] text-gray-900 leading-[1.6] mb-3 break-words">
            {{ question.content || question.prompt }}
          </div>

          <!-- 選項（如果有） -->
          <div v-if="question.options && question.options.length > 0" class="flex flex-wrap gap-2 mb-3">
            <span v-for="(opt, idx) in question.options" :key="idx" class="px-3 py-1.5 bg-gray-100 border border-gray-200 rounded-md text-sm text-gray-700">
              {{ opt }}
            </span>
          </div>

          <!-- 元數據 -->
          <div class="flex flex-wrap gap-2 text-xs">
            <span v-if="question._meta?.templateName" class="px-2 py-1 rounded font-medium truncate max-w-[250px] bg-primary-100 text-primary-800">
              📋 {{ question._meta.templateName }}
            </span>
            <span v-if="question._meta?.documentNames" class="px-2 py-1 rounded font-medium truncate max-w-[250px] bg-amber-100 text-amber-800" :title="question._meta.documentNames">
              📚 {{ truncateText(question._meta.documentNames, 30) }}
            </span>
            <span v-if="question.saved" class="px-2 py-1 rounded font-medium truncate max-w-[250px] bg-emerald-100 text-emerald-800">
              ✓ 已儲存
            </span>
            <span v-else-if="question.save_error" class="px-2 py-1 rounded font-medium truncate max-w-[250px] bg-red-100 text-red-800 cursor-help" :title="question.save_error">
              ✗ 儲存失敗
            </span>
          </div>
        </div>

        <!-- 操作按鈕 -->
        <div class="flex-shrink-0">
          <button
            @click="removeQuestion(question)"
            class="w-8 h-8 flex items-center justify-center bg-red-100 text-red-800 border border-red-300 rounded-md text-base font-semibold cursor-pointer transition-all duration-200 hover:bg-red-200 hover:border-red-400 hover:scale-105"
            title="刪除此題"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  targetCount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['toggle-selection', 'remove-question', 'clear-unselected'])

const selectedCount = computed(() => {
  return props.questions.filter(q => q.selected).length
})

// 計算已選/應選的狀態 class
const countStatusClass = computed(() => {
  if (selectedCount.value === 0) return 'status-empty'
  if (selectedCount.value < props.targetCount) return 'status-partial'
  if (selectedCount.value === props.targetCount) return 'status-complete'
  return 'status-over' // 超過目標
})

const unselectedQuestions = computed(() => {
  return props.questions.filter(q => !q.selected)
})

const isAllSelected = computed(() => {
  if (props.questions.length === 0) return false
  return props.questions.every(q => q.selected)
})

const toggleSelection = (question) => {
  emit('toggle-selection', question)
}

const removeQuestion = (question) => {
  if (confirm('確定要刪除此題目嗎？')) {
    emit('remove-question', question)
  }
}

const clearUnselected = () => {
  if (confirm(`確定要清空 ${unselectedQuestions.value.length} 道未勾選的題目嗎？`)) {
    emit('clear-unselected')
  }
}

const toggleSelectAll = () => {
  const newState = !isAllSelected.value
  props.questions.forEach(q => {
    if (q.selected !== newState) {
      emit('toggle-selection', q)
    }
  })
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>
