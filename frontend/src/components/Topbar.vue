<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <button class="lg:hidden text-2xl" @click="$emit('toggle-sidebar')">☰</button>
    <h1 class="text-lg font-medium">
      <slot>{{ t('topbar.title') }}</slot>
    </h1>
    
    <div class="flex items-center space-x-4">
      <!-- 語言選擇器 -->
      <div class="relative">
        <label class="text-sm text-gray-500 mr-2">{{ t('language') }}:</label>
        <select 
          :value="currentLanguage"
          @change="handleLanguageChange"
          class="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </div>
      
      <!-- API 狀態 -->
      <div class="text-sm text-gray-500">
        {{ t('topbar.apiStatus') }}:
        <span :class="apiOnline ? 'text-green-600' : 'text-red-600'">
          ● {{ apiOnline ? t('topbar.online') : t('topbar.offline') }}
        </span>
      </div>
    </div>
  </header>
</template>

<script>
import { useLanguage } from '../composables/useLanguage.js'

export default {
  name: 'Topbar',
  props: {
    apiOnline: { type: Boolean, default: true }
  },
  setup() {
    const { currentLanguage, t, setLanguage } = useLanguage()

    const handleLanguageChange = (event) => {
      setLanguage(event.target.value)
    }

    return {
      currentLanguage,
      t,
      setLanguage,
      handleLanguageChange
    }
  }
}
</script>