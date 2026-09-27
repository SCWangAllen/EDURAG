/**
 * 年級單一來源（前端）。
 *
 * 學校現有三個學制分組：
 * - ESL：K1, K2, A1, A2
 * - Grade Level：G1–G6
 * - Junior Class：Jr. G4–Jr. G9（沿用 G4–G6 健康/自然/語文教材，代碼 JR4–JR9）
 * 另有 ALL = 通用（全年級適用），排序永遠在最後。
 *
 * 後端 GET /api/subjects/grades 回傳相同分組（key: 'esl' | 'grade' | 'junior'），
 * 但畫面渲染一律以這份本地常數為準，不依賴該 API 回應。
 */

export const GRADE_GROUPS = [
  {
    key: 'esl',
    labelKey: 'gradeGroups.esl',
    grades: [
      { code: 'K1', label: 'K1' },
      { code: 'K2', label: 'K2' },
      { code: 'A1', label: 'A1' },
      { code: 'A2', label: 'A2' }
    ]
  },
  {
    key: 'grade',
    labelKey: 'gradeGroups.grade',
    grades: [
      { code: 'G1', label: 'G1' },
      { code: 'G2', label: 'G2' },
      { code: 'G3', label: 'G3' },
      { code: 'G4', label: 'G4' },
      { code: 'G5', label: 'G5' },
      { code: 'G6', label: 'G6' }
    ]
  },
  {
    key: 'junior',
    labelKey: 'gradeGroups.junior',
    grades: [
      { code: 'JR4', label: 'Jr. G4' },
      { code: 'JR5', label: 'Jr. G5' },
      { code: 'JR6', label: 'Jr. G6' },
      { code: 'JR7', label: 'Jr. G7' },
      { code: 'JR8', label: 'Jr. G8' },
      { code: 'JR9', label: 'Jr. G9' }
    ]
  }
]

// 通用（全年級適用）；在所有排序清單中永遠排最後
export const ALL_GRADE = { code: 'ALL', label: 'ALL' }

// 標準排序：依三個學制分組依序排列，ALL 排最後
export const GRADE_ORDER = [
  ...GRADE_GROUPS.flatMap(group => group.grades.map(g => g.code)),
  ALL_GRADE.code
]

const LABEL_BY_CODE = Object.fromEntries(
  [...GRADE_GROUPS.flatMap(group => group.grades), ALL_GRADE].map(g => [g.code, g.label])
)

const ORDER_INDEX = Object.fromEntries(GRADE_ORDER.map((code, index) => [code, index]))

/**
 * 代碼 → 顯示標籤。未知值（例如舊資料的自訂年級字串）原樣回傳。
 */
export function gradeLabel(code) {
  if (!code) return code
  return LABEL_BY_CODE[code] !== undefined ? LABEL_BY_CODE[code] : code
}

/**
 * 排序用的索引：依 GRADE_ORDER；未知值排在 ALL 之後（陣列尾端）。
 */
export function gradeSortIndex(code) {
  return ORDER_INDEX[code] !== undefined ? ORDER_INDEX[code] : GRADE_ORDER.length
}
