import { ref, computed } from 'vue'
import { languages } from '../i18n/languages.js'

const currentLanguage = ref(localStorage.getItem('language') || 'zh')

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

  const setLanguage = (lang) => {
    currentLanguage.value = lang
    localStorage.setItem('language', lang)
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