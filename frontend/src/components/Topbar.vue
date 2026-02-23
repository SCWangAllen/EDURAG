<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <button class="lg:hidden text-2xl" @click="$emit('toggle-sidebar')">☰</button>
    <h1 class="text-lg font-medium">
      <slot>{{ t('topbar.title') }}</slot>
    </h1>
    
    <div class="flex items-center space-x-4">
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