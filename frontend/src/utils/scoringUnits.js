/**
 * 計分單位(scoring units):一題裡「可以各自給分的格數」。
 *
 * 配對 = 配對組數、填充 = 題幹空格數、辨識 = 要列舉的項目數、排序 = 項目數、
 * 圖片題 = 圖片題登錄的空格數(blank_count)、其餘題型 = 1。
 *
 * Step 2 的小計/總分、設計器抬頭總分、PDF 大題標題「(2 pts each) _____/N」
 * 全部從這裡算,三個地方才不會各算各的(以前配對題 PDF 用組數、Step 2 用題數)。
 */

// 填充題空格的寫法(與 PDF 產生器共用;用 source 建新 RegExp,避免 g 旗標的 lastIndex 互相干擾)
export const CLOZE_BLANK_PATTERN = /_{2,}|＿+|\[\s*(?:blank)?\s*\]|\(\s*(?:blank)?\s*\)|【\s*】|（\s*）|\{\s*(?:blank)?\s*\}|<\s*blank\s*>|_blank_/gi

/** 可切換「每題 / 每格」計分的題型與預設;不在這裡的題型固定每題計分 */
export const SCORING_BASIS_DEFAULTS = {
  matching: 'unit',
  cloze: 'unit',
  enumeration: 'unit',
  diagram_question: 'unit',
  sequence: 'question'
}

/**
 * 「每題幾格」的預設:Step 2 可改(unitsPerQuestion),估算小計用,AI 生成時也當成生成條件
 * (配對組數 / 填充空格數 / 辨識項目數)。配對 10 = 後端 matching_pairs 的預設值。
 */
export const UNITS_PER_QUESTION_DEFAULTS = {
  matching: 10,
  cloze: 1,
  enumeration: 3,
  diagram_question: 1,
  sequence: 5
}

/** 各題型的「格」叫什麼(Step 3 清單標籤用):pairs / blanks / items;固定每題計分的題型回 null */
export function unitsKind(type) {
  return { matching: 'pairs', cloze: 'blanks', diagram_question: 'blanks', enumeration: 'items', sequence: 'items' }[type] || null
}

/**
 * 每題格數的上下限:與後端生成條件的 schema 一致(matching_pairs 2–20、cloze_blanks 1–5、
 * enumeration_items 2–10),估算、輸入框、送後端三處共用,老師填不出「估得到、生不出來」的數字
 */
export const UNITS_PER_QUESTION_BOUNDS = {
  matching: [2, 20],
  cloze: [1, 5],
  enumeration: [2, 10],
  diagram_question: [1, 50],
  sequence: [2, 10]
}

export function unitsBounds(type) {
  return UNITS_PER_QUESTION_BOUNDS[type] || [1, 50]
}

export function normalizeUnitsPerQuestion(type, value) {
  const [lo, hi] = unitsBounds(type)
  const n = Math.floor(Number(value))
  if (!Number.isFinite(n)) return UNITS_PER_QUESTION_DEFAULTS[type] || lo
  return Math.min(hi, Math.max(lo, n))
}

/**
 * AI 生成時依 Step 2 的「每題幾格」帶給後端的限制條件(後端會逐題檢核、不符就重生成):
 * 配對 → matching_pairs、填充 → cloze_blanks、辨識 → enumeration_items。
 * 每題計分的題型不限制(格數不影響分數),配對例外:組數本來就一直是生成條件。
 */
export function generationUnitParams(type, cfg) {
  const basis = normalizeScoringBasis(type, cfg && cfg.basis)
  const units = normalizeUnitsPerQuestion(type, cfg && cfg.unitsPerQuestion)
  if (type === 'matching') return { matching_pairs: units }
  if (basis !== 'unit') return {}
  if (type === 'cloze') return { cloze_blanks: units }
  if (type === 'enumeration') return { enumeration_items: units }
  // 排序、圖片題沒有生成條件:格數只用來估算
  return {}
}

export function canChooseScoringBasis(type) {
  return Object.prototype.hasOwnProperty.call(SCORING_BASIS_DEFAULTS, type)
}

export function defaultScoringBasis(type) {
  return SCORING_BASIS_DEFAULTS[type] || 'question'
}

/** 舊草稿沒有 basis、或題型不允許切換時,回到預設 */
export function normalizeScoringBasis(type, basis) {
  if (canChooseScoringBasis(type) && (basis === 'unit' || basis === 'question')) return basis
  return defaultScoringBasis(type)
}

function toList(value) {
  if (Array.isArray(value)) return value
  if (value === null || value === undefined) return []
  const text = String(value).trim()
  if (!text) return []
  try {
    const parsed = JSON.parse(text)
    if (Array.isArray(parsed)) return parsed
  } catch {
    // 不是 JSON 就當逗號分隔
  }
  return text.split(/[,;，；\n]/).map(s => s.trim()).filter(Boolean)
}

function matchingPairCount(q) {
  const qd = q.question_data || {}
  if (Array.isArray(qd.left_items) && qd.left_items.length) return qd.left_items.length
  if (Array.isArray(qd.right_items) && qd.right_items.length) return qd.right_items.length
  const answer = q.correct_answer ?? q.answer ?? ''
  const text = typeof answer === 'string' ? answer : ''
  try {
    const parsed = JSON.parse(text)
    if (parsed && Array.isArray(parsed.left_items)) return parsed.left_items.length
    if (Array.isArray(parsed)) return parsed.length
  } catch {
    // 舊格式:"Term-Definition, Term-Definition" 或 "1-b, 2-a"
  }
  return text.split(/[,;，；]/).map(s => s.trim()).filter(s => /[-:=→：]/.test(s)).length
}

function clozeBlankCount(q) {
  const stem = String(q.content ?? q.prompt ?? '')
  const matches = stem.match(new RegExp(CLOZE_BLANK_PATTERN.source, 'gi'))
  if (matches && matches.length) return matches.length
  // 題幹沒有空格記號的舊題:PDF 會把每個答案在題幹裡挖成一格,格數 = 答案數
  return toList(q.correct_answer ?? q.answer).length
}

/** 一題的計分單位數(至少 1) */
export function scoringUnits(q) {
  if (!q) return 1
  switch (q.type) {
    case 'matching':
      return Math.max(1, matchingPairCount(q))
    case 'cloze':
      return Math.max(1, clozeBlankCount(q))
    case 'enumeration': {
      const qd = q.question_data || {}
      const n = toList(q.correct_answer ?? q.answer).length || Number(qd.max_items) || Number(qd.min_items) || 0
      return Math.max(1, n)
    }
    case 'sequence': {
      const items = q.items || (q.question_data && q.question_data.items)
      const n = Array.isArray(items) && items.length ? items.length : toList(q.correct_answer ?? q.answer).length
      return Math.max(1, n)
    }
    case 'diagram_question': {
      const n = Number(q.blank_count)
      return Number.isFinite(n) && n >= 1 ? Math.floor(n) : 1
    }
    default:
      return 1
  }
}

/** 一個大題的計分單位總數:每格計分 = 各題格數加總;每題計分 = 題數 */
export function sectionUnits(questions, basis) {
  const list = Array.isArray(questions) ? questions : []
  return basis === 'unit' ? list.reduce((sum, q) => sum + scoringUnits(q), 0) : list.length
}

export function sectionScore(questions, points, basis) {
  return sectionUnits(questions, basis) * (Number(points) || 0)
}

/**
 * Step 2 的小計。已有實際題目(選到/生成了)就照實際題目算,與設計器抬頭、PDF 大題標題
 * 完全一致;還沒有題目時用 Step 2 的題數估:每題計分 = 題數 × 分數,
 * 每格計分 = 題數 × 估計格數 × 分數(estimated: true,畫面標 ≈)。
 */
export function configSubtotal(type, cfg, actualQuestions) {
  const basis = normalizeScoringBasis(type, cfg && cfg.basis)
  const points = Number(cfg && cfg.points) || 0
  const count = Number(cfg && cfg.count) || 0
  const perQuestion = basis === 'unit' ? normalizeUnitsPerQuestion(type, cfg && cfg.unitsPerQuestion) : 1
  // 預估值:題數 × 每題格數 × 分數(每題計分時每題格數 = 1)
  const estimate = count * perQuestion * points
  const actual = Array.isArray(actualQuestions) ? actualQuestions.length : 0
  if (actual > 0) {
    // 已有實際題目:照實際算;題目還沒選滿目標題數時另附預估值供對照
    return { value: sectionScore(actualQuestions, points, basis), estimated: false, basis, estimate, partial: actual < count }
  }
  return { value: estimate, estimated: basis === 'unit', basis, estimate, partial: false }
}

/**
 * 把 Step 2 的每題分數與計分方式併進 examStyles.questionTypeSettings,給 PDF 大題標題用。
 * 設計器與「直接匯出」(不開設計器)都要走這裡,兩條路才會印出同樣的 _____/N。
 */
export function mergeTypeSettings(questionTypeSettings, questionTypeConfig) {
  const merged = { ...(questionTypeSettings || {}) }
  Object.entries(questionTypeConfig || {}).forEach(([type, cfg]) => {
    if (!cfg) return
    const entry = { ...(merged[type] || {}), basis: normalizeScoringBasis(type, cfg.basis) }
    if (cfg.points !== undefined && cfg.points !== null && cfg.points !== '') entry.points = Number(cfg.points)
    merged[type] = entry
  })
  return merged
}

/** 依題型分組(Step 2 小計與設計器總分共用) */
export function groupByType(questions) {
  const grouped = {}
  ;(questions || []).forEach(q => {
    if (!q || !q.type) return
    if (!grouped[q.type]) grouped[q.type] = []
    grouped[q.type].push(q)
  })
  return grouped
}
