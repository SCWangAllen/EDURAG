/**
 * 教材頁碼是自由文字("71"、"100-101"、"10.0"、"pp. 115-171"、"xxii"),
 * 這裡把它解析成 [起始頁, 結束頁](與後端 core/page_range.py 同一套規則):
 * - 去掉數字後面的小數部分("10.0" → 10;"p.12" 仍是 12),全形數字 / 破折號換成半形
 * - 取出所有整數:第一個當起始、最後一個當結束;顛倒就交換;單一數字 → [n, n]
 * - 沒有數字(羅馬數字等)→ null,頁碼篩選時略過這筆
 */
const FULLWIDTH_DIGITS = /[０-９]/g
const DASHES = /[－—–～~]/g

export function parsePageRange(value) {
  if (value === null || value === undefined) return null
  let text = String(value).trim()
  if (!text) return null
  text = text
    .replace(FULLWIDTH_DIGITS, ch => String.fromCharCode(ch.charCodeAt(0) - 0xff10 + 0x30))
    .replace(DASHES, '-')
    // 只去掉「數字後面」的小數(10.0 → 10);「p.12」的點前面不是數字,要保留 12
    // (不用 lookbehind:舊版 Safari 不支援,整個 chunk 會解析失敗)
    .replace(/(\d)\.\d+/g, '$1')
  const nums = (text.match(/\d+/g) || []).map(n => parseInt(n, 10)).filter(n => Number.isFinite(n))
  if (nums.length === 0) return null
  let start = nums[0]
  let end = nums[nums.length - 1]
  if (end < start) [start, end] = [end, start]
  return [start, end]
}

/**
 * 老師輸入的起迄 → 整數、>=1 才算有填、顛倒就交換(輸入 171 再輸入 115 不會變成「沒有資料」)。
 * 回傳 { from, to },沒填的那一邊是 0。三個選教材的地方與送後端的參數都用這個。
 */
export const PAGE_BOUND_MAX = 1000000
export function normalizeBounds(from, to) {
  const clean = (v) => {
    const n = Math.floor(Number(v))
    return Number.isFinite(n) && n >= 1 ? Math.min(n, PAGE_BOUND_MAX) : 0
  }
  let lo = clean(from)
  let hi = clean(to)
  if (lo && hi && lo > hi) [lo, hi] = [hi, lo]
  return { from: lo, to: hi }
}

/** 一筆教材是否落在 from–to 的範圍(區間有重疊就算);沒給範圍一律通過,解析不出頁碼的在有範圍時排除 */
export function pageInRange(value, from, to) {
  const { from: lo, to: hi } = normalizeBounds(from, to)
  if (!lo && !hi) return true
  const r = parsePageRange(value)
  if (!r) return false
  if (lo && r[1] < lo) return false
  if (hi && r[0] > hi) return false
  return true
}

/**
 * 一組教材的頁碼範圍 { from, to };全部解析不出來回 null。
 * 超過 PAGE_BOUND_MAX 的數字(頁碼欄填了 ISBN 之類)視同解析不出來,否則存題時會撞到
 * 後端的範圍上限(1,000,000),整批題目存不進去。
 */
export function selectionPageRange(docs) {
  let from = Infinity
  let to = -Infinity
  ;(docs || []).forEach(doc => {
    const r = parsePageRange(doc && (doc.page ?? doc.page_number))
    if (!r || r[1] > PAGE_BOUND_MAX || r[0] < 1) return
    from = Math.min(from, r[0])
    to = Math.max(to, r[1])
  })
  return Number.isFinite(from) && Number.isFinite(to) ? { from, to } : null
}

/** 副標用:"pp. 115–171"(單頁 "p. 71") */
export function formatPageRangeLabel(range) {
  if (!range) return ''
  return range.from === range.to ? `p. ${range.from}` : `pp. ${range.from}–${range.to}`
}

/** 卡片顯示用:原文照印,前面加 P. */
export function formatPage(value) {
  const text = value === null || value === undefined ? '' : String(value).trim()
  return text ? `P.${text}` : ''
}

/**
 * 範圍跨幾頁(inclusive);沒有範圍回 0。
 * 超過 PAGE_SPAN_WARN 頁時只提醒老師範圍偏大,不阻擋 —— 複習卷 / 月考範圍本來就可能整本書都算,
 * 這種情況照樣能生成,只是之後用頁碼篩選不容易精準找到這批題目。
 */
export const PAGE_SPAN_WARN = 20
export function pageSpan(range) {
  return range ? range.to - range.from + 1 : 0
}
export function isWidePageRange(range) {
  return pageSpan(range) > PAGE_SPAN_WARN
}
