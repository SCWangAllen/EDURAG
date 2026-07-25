import { ref, computed } from 'vue'
import { languages } from '../i18n/languages.js'

const STORAGE_KEY = 'ui_lang'
const SUPPORTED = ['en', 'zh']
// 預設英文(老師為主要使用者);個人選擇記在 localStorage,開發者切一次中文即固定。
const DEFAULT_LANG = 'en'

function initialLang() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && SUPPORTED.includes(saved)) return saved
  } catch (e) {
    // localStorage 不可用(隱私模式等)→ 用預設
  }
  return DEFAULT_LANG
}

// module 級單例:全 app 共用同一個語言狀態(切換即時反映到所有元件)
const currentLanguage = ref(initialLang())

// 在指定語言樹裡解析 dotted key,找不到回 undefined
function resolve(lang, keys) {
  let value = languages[lang]
  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k]
    } else {
      return undefined
    }
  }
  return typeof value === 'string' ? value : (value === undefined ? undefined : value)
}

export function useLanguage() {
  const t = (key) => {
    if (!key || typeof key !== 'string') {
      return key || ''
    }
    const keys = key.split('.')
    // fallback 鏈:目前語言 → 中文(最完整)→ 原始 key
    const primary = resolve(currentLanguage.value, keys)
    if (primary !== undefined) return primary
    const fallback = resolve('zh', keys)
    if (fallback !== undefined) return fallback
    return key
  }

  const setLanguage = (lang) => {
    if (!SUPPORTED.includes(lang)) return
    currentLanguage.value = lang
    try {
      localStorage.setItem(STORAGE_KEY, lang)
    } catch (e) {
      // 無法持久化就只在本次 session 生效
    }
  }

  const toggleLanguage = () => {
    setLanguage(currentLanguage.value === 'en' ? 'zh' : 'en')
  }

  const isEnglish = computed(() => currentLanguage.value === 'en')
  const isChinese = computed(() => currentLanguage.value === 'zh')

  return {
    currentLanguage: computed(() => currentLanguage.value),
    t,
    setLanguage,
    toggleLanguage,
    isEnglish,
    isChinese
  }
}
