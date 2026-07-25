<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <button class="lg:hidden text-2xl" @click="$emit('toggle-sidebar')">☰</button>
    <h1 class="text-lg font-medium">
      <slot>{{ t('topbar.title') }}</slot>
    </h1>
    
    <div class="flex items-center space-x-4">
      <!-- 語言切換(記住個人選擇) -->
      <div class="flex items-center rounded-md border border-gray-200 overflow-hidden text-sm">
        <button
          type="button"
          class="px-2.5 py-1 focus:outline-none transition-colors"
          :class="currentLanguage === 'en' ? 'bg-primary-600 text-white' : 'text-gray-500 hover:bg-gray-100'"
          @click="setLanguage('en')"
        >EN</button>
        <button
          type="button"
          class="px-2.5 py-1 focus:outline-none transition-colors"
          :class="currentLanguage === 'zh' ? 'bg-primary-600 text-white' : 'text-gray-500 hover:bg-gray-100'"
          @click="setLanguage('zh')"
        >中</button>
      </div>

      <!-- API 狀態 -->
      <div class="text-sm text-gray-500">
        {{ t('topbar.apiStatus') }}:
        <span :class="apiOnline ? 'text-green-600' : 'text-red-600'">
          ● {{ apiOnline ? t('topbar.online') : t('topbar.offline') }}
        </span>
      </div>

      <!-- 設定 -->
      <button
        type="button"
        class="text-gray-400 hover:text-gray-600 focus:outline-none"
        :title="t('settings.title')"
        @click="settingsOpen = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
    </div>

    <SettingsModal v-model="settingsOpen" />
  </header>
</template>

<script>
import { ref } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import SettingsModal from './SettingsModal.vue'

export default {
  name: 'Topbar',
  components: { SettingsModal },
  props: {
    apiOnline: { type: Boolean, default: true }
  },
  setup() {
    const { currentLanguage, t, setLanguage } = useLanguage()

    const settingsOpen = ref(false)

    const handleLanguageChange = (event) => {
      setLanguage(event.target.value)
    }

    return {
      currentLanguage,
      t,
      setLanguage,
      handleLanguageChange,
      settingsOpen
    }
  }
}
</script>