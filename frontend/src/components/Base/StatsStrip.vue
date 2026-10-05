<template>
  <!--
    統計資訊:預設收成一行摘要(數字都在),想看卡片再展開;收合狀態記在瀏覽器。
    老師回饋:統計卡片占很大一塊,但不是每次都要看。
  -->
  <div v-if="items && items.length" class="mb-6">
    <div class="flex items-center justify-between gap-3 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div class="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-gray-600">
        <span v-for="item in items" :key="item.label" class="whitespace-nowrap">
          <span class="font-semibold text-gray-900">{{ item.value }}</span> {{ item.label }}
        </span>
      </div>
      <button
        type="button"
        class="text-xs text-primary-600 hover:text-primary-800 whitespace-nowrap focus:outline-none"
        @click="toggle"
      >
        {{ collapsed ? t('statsShowDetails') : t('statsHideDetails') }} {{ collapsed ? '▾' : '▴' }}
      </button>
    </div>

    <div v-if="!collapsed" class="grid grid-cols-1 md:grid-cols-4 gap-6 mt-3">
      <div v-for="item in items" :key="'card-' + item.label" class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <dl>
            <dt class="text-sm font-medium text-gray-500 truncate">{{ item.label }}</dt>
            <dd class="text-2xl font-semibold text-gray-900">{{ item.value }}</dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useLanguage } from '@/composables/useLanguage.js'
import { useLocalStorage } from '@/composables/useLocalStorage.js'

const props = defineProps({
  // [{ label, value }]
  items: { type: Array, default: () => [] },
  // 每頁一個 key,收合狀態各自記
  storageKey: { type: String, required: true },
  defaultCollapsed: { type: Boolean, default: true }
})

const { t } = useLanguage()
const store = useLocalStorage(props.storageKey, props.defaultCollapsed)
const collapsed = ref(store.load() !== false)
watch(collapsed, (v) => store.save(v))
const toggle = () => { collapsed.value = !collapsed.value }
</script>
