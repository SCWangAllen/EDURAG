import { ref, computed } from 'vue'
import { languages } from '../i18n/languages.js'

// 鎖定為中文，不再讀取 localStorage
const currentLanguage = ref('zh')

export function useLanguage() {
  const t = (key) => {
    if (!key || typeof key !== 'string') {
      return key || ''
    }
    
    const keys = key.split('.')
    let value = languages[currentLanguage.value]
    
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k]
      } else {
        return key // 如果找不到翻譯，返回原始 key
      }
    }
    
    return value || key
  }

  // 語言已鎖定為中文，此函數保留但不執行任何操作
  const setLanguage = (lang) => {
    // 不再切換語言
  }

  const isEnglish = computed(() => currentLanguage.value === 'en')
  const isChinese = computed(() => currentLanguage.value === 'zh')

  return {
    currentLanguage: computed(() => currentLanguage.value),
    t,
    setLanguage,
    isEnglish,
    isChinese
  }
}