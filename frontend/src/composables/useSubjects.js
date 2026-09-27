import { computed, ref } from 'vue'
import subjectService from '@/api/subjectService.js'
import { useLanguage } from '@/composables/useLanguage.js'
import { gradeLabel, gradeSortIndex } from '@/constants/grades.js'
import { getTextColor } from '@/utils/subjectUtils.js'
import { getSubjectColor as getSubjectColorDefault } from '@/utils/formatters.js'

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

  // 指定科目的年級清單；不信任後端回傳順序，一律以 gradeSortIndex（ESL → Grade Level →
  // Junior Class → ALL → 未知值排最後）重新排序，確保跨科目一致。
  const gradesFor = (name) => {
    const node = findNode(name)
    if (!node) return []
    return node.grades
      .map(g => g.grade)
      .sort((a, b) => gradeSortIndex(a) - gradeSortIndex(b))
  }

  const getColor = (name) => findNode(name)?.color || '#3B82F6'
  // 科目標籤顏色(全站一致):優先用科目管理設定的顏色,樹還沒載入或找不到科目才退回固定配色
  const subjectBadgeStyle = (name) => {
    const color = findNode(name)?.color
    if (!color) return null
    return { backgroundColor: color, color: getTextColor(color) }
  }
  const subjectBadgeClass = (name) => (findNode(name)?.color ? '' : getSubjectColorDefault(name))

  // canonical key → i18n 中文顯示名；使用者自建科目 fallback 原字串
  const getDisplayName = (name) => {
    if (!name) return ''
    const key = `subjects.${name}`
    const translated = t(key)
    return translated === key ? name : translated
  }

  // 年級顯示：ALL → 全年級、'' → 未分級，其餘交由 grades.js 單一來源轉換
  // （例如 JR4 → Jr. G4；未知舊資料字串原樣顯示）
  const getGradeLabel = (grade) => {
    if (grade === 'ALL') return t('subjects.allGrades')
    if (!grade) return t('subjects.noGrade')
    return gradeLabel(grade)
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
    subjectBadgeStyle,
    subjectBadgeClass,
    getDisplayName,
    getGradeLabel
  }
}
