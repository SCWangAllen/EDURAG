/**
 * 後端生成結果的檢核提醒(question.warnings = [{ code, actual, expected }])→ 顯示文字。
 * 出題頁(GenerationResults)與組卷 AI 模式(GeneratedQuestionList)共用。
 */
const WARNING_KEYS = {
  matching_pairs: 'generate.warn_matching_pairs',
  cloze_blanks: 'generate.warn_cloze_blanks',
  enumeration_items: 'generate.warn_enumeration_items'
}

export function warningText(question, t) {
  const w = (question && question.warnings || [])[0]
  if (!w) return ''
  const key = WARNING_KEYS[w.code]
  const template = key ? t(key) : ''
  const text = template && template !== key ? template : `${w.code}: ${w.actual}/${w.expected}`
  return text.replace('{actual}', w.actual).replace('{expected}', w.expected)
}
