/**
 * 題目格式檢核(前端版):生成結果列表標示問題、儲存時略過不合格的題目。
 * 規則與後端 core/question_validation.py 對齊;後端存檔時仍會再檢一次。
 * 回傳的是 i18n key(generate.check_*),用 checkLabel() 轉成顯示文字。
 */
const CLOZE_BLANK_RE = /_{2,}|＿+|\[\s*(?:blank)?\s*\]|\(\s*(?:blank)?\s*\)|【\s*】|（\s*）|\{\s*(?:blank)?\s*\}|<\s*blank\s*>|_blank_/i
const LABEL_PREFIX_RE = /^[A-Za-z][.)\]]\s*/

export const CHECK_FALLBACK_TEXT = {
  check_empty_prompt: '題幹為空',
  check_empty_answer: '答案為空',
  check_choice_options: '選擇題選項少於 2 個',
  check_choice_answer: '選擇題答案不在選項中',
  check_tf_answer: '是非題答案不是 true/false',
  check_cloze_no_blank: '填充題沒有空格',
  check_matching_items: '配合題缺少左右項目',
  check_matching_mismatch: '配合題左右項目數不一致',
  check_sequence_items: '排序題缺少項目'
}

/** 選擇題答案 → 大寫字母;對不到選項回 null(接受字母、1 起算數字、選項全文) */
export function resolveChoiceAnswer(answer, options) {
  if (!Array.isArray(options) || options.length < 2) return null
  const raw = String((Array.isArray(answer) ? answer[0] : answer) ?? '').trim()
  if (!raw) return null
  const letter = raw.match(/^([A-Za-z])[.)]?$/)
  if (letter) {
    const idx = letter[1].toUpperCase().charCodeAt(0) - 65
    return idx >= 0 && idx < options.length ? String.fromCharCode(65 + idx) : null
  }
  if (/^\d+$/.test(raw)) {
    const n = parseInt(raw, 10)
    if (n >= 1 && n <= options.length) return String.fromCharCode(64 + n)
    return n === 0 ? 'A' : null
  }
  const lowered = raw.toLowerCase()
  const stripped = raw.replace(LABEL_PREFIX_RE, '').trim().toLowerCase()
  for (let i = 0; i < options.length; i++) {
    const full = String(options[i]).trim().toLowerCase()
    const content = String(options[i]).replace(LABEL_PREFIX_RE, '').trim().toLowerCase()
    if (lowered === full || lowered === content || stripped === content) return String.fromCharCode(65 + i)
  }
  return null
}

/** 回傳問題 key;合格回 null */
export function checkQuestion(q) {
  if (!q) return 'check_empty_prompt'
  const type = q.type || q.question_type
  const prompt = String(q.prompt ?? q.content ?? '').trim()
  const answer = q.answer ?? q.correct_answer
  if (!prompt) return 'check_empty_prompt'
  if (answer === undefined || answer === null || String(answer).trim() === '') return 'check_empty_answer'
  switch (type) {
    case 'single_choice':
      if (!Array.isArray(q.options) || q.options.length < 2) return 'check_choice_options'
      return resolveChoiceAnswer(answer, q.options) ? null : 'check_choice_answer'
    case 'true_false':
      return /^(true|false)$/i.test(String(answer).trim()) ? null : 'check_tf_answer'
    case 'cloze':
      return CLOZE_BLANK_RE.test(prompt) ? null : 'check_cloze_no_blank'
    case 'matching': {
      const qd = q.question_data || {}
      const left = qd.left_items
      const right = qd.right_items
      if (!Array.isArray(left) || !Array.isArray(right) || !left.length || !right.length) return 'check_matching_items'
      return left.length === right.length ? null : 'check_matching_mismatch'
    }
    case 'sequence': {
      const items = q.items || q.question_data?.items
      return Array.isArray(items) && items.length ? null : 'check_sequence_items'
    }
    default:
      return null
  }
}

export function checkLabel(key, t) {
  if (!key) return ''
  const translated = t ? t(`generate.${key}`) : ''
  return (translated && translated !== `generate.${key}`) ? translated : (CHECK_FALLBACK_TEXT[key] || key)
}
