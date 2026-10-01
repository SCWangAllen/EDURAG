<template>
  <div class="w-full">
    <!-- 自選模式提示 -->
    <div v-if="mode === 'select'" class="flex items-center gap-3 p-4 mb-6 bg-primary-100 border border-primary-500 rounded-lg text-primary-800">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span class="text-sm font-medium">{{ t('ui.ed_select_mode_hint') }}</span>
    </div>

    <!-- 題型配置表格 -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div class="grid grid-cols-[80px_1fr_80px_120px_120px_100px_100px] gap-4 p-4 bg-gray-50 font-semibold text-sm text-gray-700 border-b-2 border-gray-200">
        <div class="col-order">#</div>
        <div class="col-type">{{ t('ui.ed_type_column_label') }}</div>
        <div class="col-enabled">{{ t('ui.ed_enabled_column_label') }}</div>
        <div class="col-count">{{ t('ui.ed_count_column_label') }}</div>
        <div class="col-points">{{ t('ui.ed_points_column_label') }}</div>
        <div class="col-total">{{ t('ui.ed_subtotal_column_label') }}</div>
        <div class="col-actions">{{ t('ui.ed_actions_column_label') }}</div>
      </div>

      <draggable
        v-model="orderedTypes"
        item-key="type"
        handle=".drag-handle"
        @end="onDragEnd"
        class="flex flex-col"
      >
        <template #item="{ element: typeConfig, index }">
          <QuestionTypeConfigRow
            :typeConfig="typeConfig"
            :actualQuestions="questionsByType[typeConfig.type] || []"
            :index="index"
            :totalCount="orderedTypes.length"
            :mode="mode"
            @enabled-change="onEnabledChange"
            @config-change="onRowConfigChange"
            @move-up="moveUp"
            @move-down="moveDown"
          />
        </template>
      </draggable>
    </div>

    <QuestionTypeConfigFooter
      :enabledTypeCount="enabledTypeCount"
      :totalQuestions="totalQuestions"
      :totalPoints="totalPoints"
      :hasUnsavedChanges="hasUnsavedChanges"
      :mode="mode"
      @save="saveConfigManually"
      @apply-preset="applyPreset"
      @reset="resetAll"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import draggable from 'vuedraggable'
import QuestionTypeConfigRow from './QuestionTypeConfigRow.vue'
import QuestionTypeConfigFooter from './QuestionTypeConfigFooter.vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { configSubtotal } from '@/utils/scoringUnits.js'

const { t } = useLanguage()

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  mode: {
    type: String,
    default: 'generate'
  },
  // 依題型分組的實際題目(選題/生成後),每格計分的小計與總分用實際格數算
  questionsByType: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

// 題型順序陣列（用於拖拽排序）
const orderedTypes = ref([])

// 追蹤是否有未儲存的變更
const hasUnsavedChanges = ref(false)

// 初始化順序陣列
const initOrderedTypes = () => {
  orderedTypes.value = Object.entries(props.modelValue)
    .map(([type, config]) => ({
      type,
      ...config
    }))
    .sort((a, b) => a.order - b.order)
}

initOrderedTypes()

// 父層草稿還原 / 清除草稿 / 預設套用時把新值同步進本地複本(以前只在建立時讀一次,
// 重新整理後 Step 2 會停在預設值,小計與下方總分對不上)。內容相同就不重建,免得輸入中被打斷。
// 遞迴把物件鍵排序後再序列化,不同鍵順序(例如 basis 後加)也能比出「內容相同」
const stableJson = (value) => JSON.stringify(value, (_key, val) =>
  (val && typeof val === 'object' && !Array.isArray(val))
    ? Object.keys(val).sort().reduce((acc, k) => { acc[k] = val[k]; return acc }, {})
    : val
)
const localConfigJson = () => {
  const local = {}
  orderedTypes.value.forEach(item => {
    const { type, ...cfg } = item
    local[type] = cfg
  })
  return stableJson(local)
}
watch(() => props.modelValue, (val) => {
  if (val && stableJson(val) !== localConfigJson()) initOrderedTypes()
}, { deep: true })

// 計算屬性
const enabledTypeCount = computed(() => {
  return orderedTypes.value.filter(t => t.enabled).length
})

const totalQuestions = computed(() => {
  return orderedTypes.value
    .filter(t => t.enabled)
    .reduce((sum, t) => sum + t.count, 0)
})

const totalPoints = computed(() => {
  return orderedTypes.value
    .filter(t => t.enabled)
    .reduce((sum, t) => sum + configSubtotal(t.type, t, props.questionsByType[t.type]).value, 0)
})

// 拖拽結束事件
const onDragEnd = () => {
  orderedTypes.value.forEach((item, index) => {
    item.order = index + 1
  })
  syncToParent()
}

// 啟用狀態變更
const onEnabledChange = (typeConfig) => {
  typeConfig.enabled = !typeConfig.enabled

  if (!typeConfig.enabled) {
    typeConfig.count = 0
  } else {
    if (typeConfig.count === 0) {
      typeConfig.count = 5
    }
  }
  syncToParent() // 即時同步到父層,讓 Step 3 題數立刻反映(不需按 Save Settings)
}

// 子元件配置變更（count 或 points）
const onRowConfigChange = (typeConfig, field, value) => {
  typeConfig[field] = value
  syncToParent() // 即時同步到父層,讓 Step 3 題數立刻反映(不需按 Save Settings)
}

// 向上移動
const moveUp = (index) => {
  if (index > 0) {
    const temp = orderedTypes.value[index]
    orderedTypes.value[index] = orderedTypes.value[index - 1]
    orderedTypes.value[index - 1] = temp
    onDragEnd()
  }
}

// 向下移動
const moveDown = (index) => {
  if (index < orderedTypes.value.length - 1) {
    const temp = orderedTypes.value[index]
    orderedTypes.value[index] = orderedTypes.value[index + 1]
    orderedTypes.value[index + 1] = temp
    onDragEnd()
  }
}

// 手動儲存設定
const saveConfigManually = () => {
  if (!hasUnsavedChanges.value) {
    syncToParent()
    return
  }
  syncToParent()
  hasUnsavedChanges.value = false
}

// 同步到父組件
const syncToParent = () => {
  const newConfig = {}
  orderedTypes.value.forEach(item => {
    const { type, ...config } = item
    newConfig[type] = config
  })
  emit('update:modelValue', newConfig)
}

// 快速配置預設
const applyPreset = (preset) => {
  const presets = {
    standard: {
      single_choice: { count: 10, points: 1, enabled: true },
      cloze: { count: 13, points: 2, enabled: true },
      true_false: { count: 12, points: 1, enabled: true },
      short_answer: { count: 6, points: 4, enabled: true }
    },
    simple: {
      single_choice: { count: 10, points: 2, enabled: true },
      cloze: { count: 5, points: 2, enabled: true },
      short_answer: { count: 5, points: 4, enabled: true }
    },
    comprehensive: {
      single_choice: { count: 15, points: 1, enabled: true },
      cloze: { count: 15, points: 2, enabled: true },
      true_false: { count: 10, points: 1, enabled: true },
      short_answer: { count: 8, points: 3, enabled: true },
      matching: { count: 2, points: 5, enabled: true }
    }
  }

  const config = presets[preset]
  if (config) {
    orderedTypes.value.forEach(item => {
      if (config[item.type]) {
        Object.assign(item, config[item.type])
      } else {
        item.enabled = false
        item.count = 0
      }
    })
    syncToParent()
    hasUnsavedChanges.value = false
  }
}

// 全部重置
const resetAll = () => {
  orderedTypes.value.forEach(item => {
    item.enabled = false
    item.count = 0
    item.points = 2
  })
  syncToParent()
  hasUnsavedChanges.value = false
}
</script>
