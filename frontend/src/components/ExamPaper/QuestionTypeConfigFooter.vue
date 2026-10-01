<template>
  <div>
    <!-- 統計資訊與儲存按鈕 -->
    <div class="grid grid-cols-[1fr_1fr_1fr_auto] gap-4 mt-6 items-center">
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">{{ mode === 'select' ? t('ui.ed_selected_types_label') : t('ui.ed_enabled_types_label') }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ enabledTypeCount }} {{ t('ui.ed_types_unit') }}</div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">{{ mode === 'select' ? t('ui.ed_selected_count_label') : t('ui.ed_total_questions_label') }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ totalQuestions }} {{ t('ui.ed_questions_unit') }}</div>
      </div>
      <div class="bg-primary-50 border border-primary-500 rounded-lg p-4 text-center">
        <div class="text-sm text-gray-500 mb-2">{{ t('ui.ed_total_score_label') }}</div>
        <div class="text-2xl font-bold text-primary-500">{{ totalPoints }} {{ t('ui.ed_points_unit') }}</div>
        <!-- 目標總分與差距:老師填想出幾分,系統算出目前差多少 -->
        <div class="mt-2 flex items-center justify-center gap-1 text-xs text-gray-500">
          <span>{{ t('ui.ed_target_total_label') }}</span>
          <input
            :value="targetTotal"
            type="number"
            min="10"
            max="500"
            class="w-16 px-1 py-0.5 border border-gray-300 rounded text-xs text-center bg-white focus:outline-none focus:border-primary-500"
            @input="$emit('update:targetTotal', $event.target.value)"
          />
          <span v-if="targetGap !== null" :class="targetGap === 0 ? 'text-emerald-600 font-semibold' : 'text-amber-600 font-semibold'">
            {{ targetGap === 0 ? t('ui.ed_target_met') : (targetGap > 0 ? t('ui.ed_target_short').replace('{n}', targetGap) : t('ui.ed_target_over').replace('{n}', -targetGap)) }}
          </span>
        </div>
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
        <span class="font-semibold">{{ hasUnsavedChanges ? t('ui.ed_save_settings_cta') : t('ui.ed_saved_label') }}</span>
      </button>
    </div>

    <!-- 快速配置按鈕（AI生成模式才顯示） -->
    <div v-if="mode !== 'select'" class="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <p class="text-sm font-semibold text-gray-700 mb-3">💡 {{ t('ui.ed_quick_config_label') }}</p>
      <div class="flex flex-wrap gap-2">
        <button @click="$emit('apply-preset', 'standard')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          📋 {{ t('ui.ed_preset_standard') }}
        </button>
        <button @click="$emit('apply-preset', 'simple')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          ✏️ {{ t('ui.ed_preset_simple') }}
        </button>
        <button @click="$emit('apply-preset', 'comprehensive')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-gray-400">
          📚 {{ t('ui.ed_preset_comprehensive') }}
        </button>
        <button @click="$emit('reset')" class="px-4 py-2 bg-white border border-red-300 rounded-md text-sm font-medium text-danger-600 cursor-pointer transition-all duration-200 hover:bg-danger-50 hover:border-red-400">
          🔄 {{ t('ui.ed_reset_all') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
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
  },
  targetTotal: {
    type: [Number, String],
    default: ''
  }
})

defineEmits(['save', 'apply-preset', 'reset', 'update:targetTotal'])

// 目標總分 − 目前總分;沒填目標回 null(不顯示)
const targetGap = computed(() => {
  const target = Number(props.targetTotal)
  if (props.targetTotal === '' || props.targetTotal === null || !Number.isFinite(target) || target <= 0) return null
  return Math.round((target - Number(props.totalPoints || 0)) * 100) / 100
})
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
