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

/** 還沒選到實際題目時,每題估計幾格(其餘題型估 1)。配對 10 = 後端生成時的預設組數 matching_pairs */
export const ESTIMATED_UNITS_PER_QUESTION = {
  matching: 10
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
  if (Array.isArray(actualQuestions) && actualQuestions.length > 0) {
    return { value: sectionScore(actualQuestions, points, basis), estimated: false, basis }
  }
  if (basis === 'question') return { value: count * points, estimated: false, basis }
  const perQuestion = ESTIMATED_UNITS_PER_QUESTION[type] || 1
  return { value: count * perQuestion * points, estimated: true, basis }
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
