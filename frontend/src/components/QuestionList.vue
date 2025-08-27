<template>
  <section class="grid gap-6 max-w-4xl">
   
    <div v-for="(q, idx) in questions" :key="idx"
         class="bg-white p-6 rounded-xl shadow cursor-pointer hover:ring-2 hover:ring-blue-200 transition-all"
         @click="$emit('open-drawer', q.context)">
      
      <!-- 題型標籤 -->
      <div class="flex items-center gap-2 mb-3">
        <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
          {{ getTypeLabel(q.type) }}
        </span>
        <span class="text-sm text-gray-500">第 {{ idx+1 }} 題</span>
      </div>
      
      <!-- 題目內容 -->
      <h3 class="font-semibold mb-3 text-gray-800">{{ q.question }}</h3>
      
      <!-- 選項（僅單選題顯示） -->
      <div v-if="q.options && q.options.length > 0" class="mb-3 pl-4 space-y-1">
        <p v-for="(opt, k) in q.options" :key="k" class="text-gray-700">
          {{ opt }}
        </p>
      </div>
      
      <!-- 答案和解釋 -->
      <div class="mt-4 pt-3 border-t border-gray-100">
        <p class="text-sm text-green-700 font-medium mb-2">
          <span class="font-semibold">答案：</span>{{ q.answer }}
        </p>
        <p v-if="q.explanation" class="text-sm text-gray-600">
          <span class="font-semibold">解釋：</span>{{ q.explanation }}
        </p>
      </div>
      
      <!-- 來源提示 -->
      <div class="mt-3 pt-2 border-t border-gray-50">
        <p class="text-xs text-gray-400">
          點擊查看來源文件段落
        </p>
      </div>
    </div>
    
    <!-- 空狀態 -->
    <div v-if="questions.length === 0" 
         class="text-center py-12 text-gray-500">
      <p class="text-lg mb-2">尚未生成題目</p>
      <p class="text-sm">請在左側設定題型和數量，然後點擊「生成題目」</p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'QuestionList',
  props: {
    questions: { type: Array, required: true }
  },
  emits: ['open-drawer'],
  methods: {
    getTypeLabel(type) {
      const typeMap = {
        'single_choice': '單選題',
        'cloze': '填空題',
        'short_answer': '簡答題'
      }
      return typeMap[type] || type
    }
  }
}
</script>

