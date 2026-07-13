import { computed, ref } from 'vue'
import subjectService from '@/api/subjectService.js'
import { useLanguage } from '@/composables/useLanguage.js'

// module 級單例快取：全 app 共用同一棵「科目→年級」樹
const tree = ref([])
const loading = ref(false)
const loaded = ref(false)
let pendingPromise = null

async function fetchTree() {
  loading.value = true
  try {
    const data = await subjectService.getSubjectTree()
    tree.value = data.subjects || []
    loaded.value = true
  } finally {
    loading.value = false
  }
  return tree.value
}

/**
 * 科目資料的唯一前端來源。
 * 樹狀結構：[{ name, color, grades: [{ id, grade }] }]
 * grade 'ALL' = 全年級通用；'' = 未指定年級。
 */
export function useSubjects() {
  const { t } = useLanguage()

  // 首次呼叫觸發載入；重複呼叫共用同一個請求
  const ensureLoaded = () => {
    if (loaded.value) return Promise.resolve(tree.value)
    if (!pendingPromise) {
      pendingPromise = fetchTree().finally(() => {
        pendingPromise = null
      })
    }
    return pendingPromise
  }

  // 科目增刪改後呼叫，強制重新抓取
  const refresh = () => {
    loaded.value = false
    pendingPromise = null
    return ensureLoaded()
  }

  const subjectNames = computed(() => tree.value.map(node => node.name))

  const findNode = (name) => tree.value.find(node => node.name === name)

  // 指定科目的年級清單（依 ALL, G1..G6, 自訂 排序，由後端保證）
  const gradesFor = (name) => {
    const node = findNode(name)
    return node ? node.grades.map(g => g.grade) : []
  }

  const getColor = (name) => findNode(name)?.color || '#3B82F6'

  // canonical key → i18n 中文顯示名；使用者自建科目 fallback 原字串
  const getDisplayName = (name) => {
    if (!name) return ''
    const key = `subjects.${name}`
    const translated = t(key)
    return translated === key ? name : translated
  }

  // 年級顯示：ALL → 全年級、'' → 未分級
  const getGradeLabel = (grade) => {
    if (grade === 'ALL') return t('subjects.allGrades')
    if (!grade) return t('subjects.noGrade')
    return grade
  }

  return {
    tree,
    loading,
    loaded,
    subjectNames,
    ensureLoaded,
    refresh,
    gradesFor,
    getColor,
    getDisplayName,
    getGradeLabel
  }
}
