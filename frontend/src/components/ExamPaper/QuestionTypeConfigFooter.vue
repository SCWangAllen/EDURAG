<template>
  <div>
    <!-- 統計資訊與儲存按鈕 -->
    <div class="grid grid-cols-[1fr_1fr_1fr_auto] gap-4 mt-6 items-center">
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">{{ mode === 'select' ? '已選題型' : '已啟用題型' }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ enabledTypeCount }} 種</div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">{{ mode === 'select' ? '已選題數' : '總題數' }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ totalQuestions }} 題</div>
      </div>
      <div class="bg-primary-50 border border-primary-500 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">總分</div>
        <div class="text-2xl font-bold text-primary-500">{{ totalPoints }} 分</div>
      </div>

      <!-- 儲存設定按鈕 -->
      <button
        @click="$emit('save')"
        class="flex items-center gap-2 px-6 py-3 text-white border-none rounded-lg font-semibold text-sm cursor-pointer transition-all duration-200 whitespace-nowrap enabled:hover:-translate-y-px enabled:hover:shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)] enabled:active:translate-y-0 disabled:bg-gray-300 disabled:text-gray-400 disabled:cursor-not-allowed"
        :class="hasUnsavedChanges
          ? 'bg-warning-500 enabled:hover:bg-warning-600 pulse-animation'
          : 'bg-emerald-500 enabled:hover:bg-emerald-600'"
      >
        <span class="text-lg">💾</span>
        <span class="font-semibold">{{ hasUnsavedChanges ? '儲存設定 *' : '已儲存' }}</span>
      </button>
    </div>

    <!-- 快速配置按鈕（AI生成模式才顯示） -->
    <div v-if="mode !== 'select'" class="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <p class="text-sm font-semibold text-gray-700 mb-3">💡 快速配置：</p>
      <div class="flex flex-wrap gap-2">
        <button @click="$emit('apply-preset', 'standard')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          📋 標準考券 (41題)
        </button>
        <button @click="$emit('apply-preset', 'simple')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          ✏️ 簡易考券 (20題)
        </button>
        <button @click="$emit('apply-preset', 'comprehensive')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          📚 綜合考券 (50題)
        </button>
        <button @click="$emit('reset')" class="px-4 py-2 bg-white border border-red-300 rounded-md text-sm font-medium text-danger-600 cursor-pointer transition-all duration-200 hover:bg-danger-50 hover:border-red-400">
          🔄 全部重置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  enabledTypeCount: {
    type: Number,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  },
  totalPoints: {
    type: Number,
    required: true
  },
  hasUnsavedChanges: {
    type: Boolean,
    required: true
  },
  mode: {
    type: String,
    default: 'generate'
  }
})

defineEmits(['save', 'apply-preset', 'reset'])
</script>

<style scoped>
/* 自訂脈動動畫：Tailwind animate-pulse 的 opacity 曲線（降到 0.5）與此不同（僅降到 0.85），故保留 */
.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}
</style>
