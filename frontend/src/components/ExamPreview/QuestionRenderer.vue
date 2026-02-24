<template>
  <div class="question-item" :class="questionClass">
    <div class="question-number">{{ questionNumber }}</div>
    <div class="question-body">
      <!-- 選擇題 -->
      <template v-if="questionType === 'single_choice'">
        <div class="question-text">{{ question.content || question.prompt }}</div>
        <div v-if="question.options && question.options.length > 0" class="question-options" :class="optionsLayoutClass">
          <div
            v-for="(option, optIndex) in question.options"
            :key="`opt-${optIndex}`"
            class="option"
          >
            <span v-if="!hasOptionLabel(option)" class="option-label">{{ getOptionLabel(optIndex) }}</span>
            <span class="option-text">{{ option }}</span>
          </div>
        </div>
      </template>

      <!-- 填空題 -->
      <template v-else-if="questionType === 'cloze'">
        <div class="question-text" v-html="processClozeBlanks(question.content || question.prompt)"></div>
      </template>

      <!-- 簡答題 -->
      <template v-else-if="questionType === 'short_answer'">
        <div class="question-text">{{ question.content || question.prompt }}</div>
        <div class="answer-area">
          <div
            v-for="line in answerLines"
            :key="`line-${line}`"
            class="answer-line"
            :class="answerLineStyle"
          ></div>
        </div>
      </template>

      <!-- 是非題 -->
      <template v-else-if="questionType === 'true_false'">
        <div class="question-text">{{ question.content || question.prompt }}</div>
        <div class="tf-options">
          {{ trueFalseOptions }}
        </div>
      </template>

      <!-- 配對題 -->
      <template v-else-if="questionType === 'matching'">
        <div class="question-text">{{ question.content || question.prompt }}</div>
        <div class="matching-area">
          <div class="matching-columns">
            <!-- 左欄：待配對項目 -->
            <div class="matching-column left-column">
              <div class="column-header">Items</div>
              <div
                v-for="(item, idx) in matchingLeftItems"
                :key="`left-${idx}`"
                class="matching-item"
              >
                <span class="item-label">{{ String.fromCharCode(65 + idx) }}.</span>
                <span class="item-text">{{ item }}</span>
              </div>
            </div>
            <!-- 右欄：配對選項 -->
            <div class="matching-column right-column">
              <div class="column-header">Matches</div>
              <div
                v-for="(item, idx) in matchingRightItems"
                :key="`right-${idx}`"
                class="matching-item"
              >
                <span class="item-label">{{ idx + 1 }}.</span>
                <span class="item-text">{{ item }}</span>
              </div>
            </div>
          </div>
          <!-- 答題區 -->
          <div class="matching-answer-area">
            <span class="answer-label">Answers:</span>
            <span
              v-for="(_, idx) in matchingLeftItems"
              :key="`ans-${idx}`"
              class="answer-blank"
            >{{ String.fromCharCode(65 + idx) }}: ____</span>
          </div>
        </div>
      </template>

      <!-- 圖片題 -->
      <template v-else-if="questionType === 'image_question'">
        <div class="image-question-container">
          <div v-if="question.content" class="question-text">{{ question.content }}</div>
          <div class="image-display">
            <img
              v-if="question.question_image_url"
              :src="question.question_image_url"
              :alt="question.content || 'Question Image'"
              class="question-image"
              @error="handleImageError"
            />
            <div v-else class="image-placeholder-box">
              <span class="placeholder-icon">🖼️</span>
              <span class="placeholder-text">{{ question.question_image || 'Image' }}</span>
            </div>
          </div>
          <div class="image-question-answer-area">
            <div
              v-for="line in 3"
              :key="`img-line-${line}`"
              class="answer-line line-solid"
            ></div>
          </div>
        </div>
      </template>

      <!-- 其他題型 fallback -->
      <template v-else>
        <div class="question-text">{{ question.content || question.prompt }}</div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  questionType: {
    type: String,
    required: true
  },
  config: {
    type: Object,
    default: () => ({})
  }
})

const questionStyles = computed(() => props.config.questionStyles?.[props.questionType])

const questionNumber = computed(() => {
  const style = questionStyles.value?.numberStyle
  const num = props.index + 1

  switch (style) {
    case 'bracket': return `${num})`
    case 'circle': return ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'][props.index] || `${num}.`
    case 'square': return `[${num}]`
    default: return `${num}.`
  }
})

const questionClass = computed(() => {
  const styles = questionStyles.value
  if (!styles?.enabled) return ''

  const classes = []
  if (styles.backgroundColor) classes.push('has-bg')
  if (styles.borderStyle !== 'none') classes.push('has-border')
  return classes.join(' ')
})

const optionsLayoutClass = computed(() => {
  const layout = props.config.questionStyles?.single_choice?.optionLayout
  return `options-${layout || 'vertical'}`
})

const answerLines = computed(() => {
  const count = props.config.questionStyles?.short_answer?.lineCount || 3
  return Array.from({ length: count }, (_, i) => i + 1)
})

const answerLineStyle = computed(() => {
  const style = props.config.questionStyles?.short_answer?.answerStyle
  return `line-${style || 'solid'}`
})

const trueFalseOptions = computed(() => {
  const style = props.config.questionStyles?.true_false?.labelStyle
  switch (style) {
    case 'full': return 'True / False'
    case 'yn': return 'Yes / No'
    case 'ox': return 'O / X'
    case 'checkbox': return '☐ True  ☐ False'
    default: return 'T / F'
  }
})

const getOptionLabel = (index) => {
  const style = props.config.questionStyles?.single_choice?.optionPrefix
  const letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

  switch (style) {
    case 'circle': return ['Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ'][index]
    case 'square': return `[${letters[index]}]`
    case 'dot': return '•'
    default: return `${letters[index]}.`
  }
}

const hasOptionLabel = (option) => {
  const labelPattern = /^[a-zA-Z][.\)\]][\s]/
  return labelPattern.test(option.toString().trim())
}

const processClozeBlanks = (text) => {
  const style = props.config.questionStyles?.cloze?.blankStyle

  // 使用 CSS border-bottom 作為底線，不使用底線字符
  let blankContent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'  // 空白佔位

  switch (style) {
    case 'box': blankContent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'; break
    case 'parentheses': blankContent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'; break
    case 'dotted': blankContent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'; break
    default: blankContent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
  }

  // 匹配各種空白格式並替換為帶底線的 span
  return text.replace(/_{3,}|\[\s*\]|\(\s*\)|【\s*】|（\s*）/g, `<span class="blank blank-${style || 'underline'}">${blankContent}</span>`)
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const container = event.target.parentNode
  const placeholder = document.createElement('div')
  placeholder.className = 'image-placeholder-box'
  placeholder.innerHTML = '<span class="placeholder-icon">🖼️</span><span class="placeholder-text">圖片載入失敗</span>'
  container.appendChild(placeholder)
}

// 解析配對答案字串為左右兩欄
const parseMatchingAnswer = (answerText) => {
  const left = []
  const right = []
  if (!answerText) return { left, right }

  // 嘗試解析 JSON 格式
  try {
    const parsed = JSON.parse(answerText)
    if (parsed.left_items && parsed.right_items) {
      return { left: parsed.left_items, right: parsed.right_items }
    } else if (Array.isArray(parsed)) {
      // 可能是配對陣列格式 [["A", "1"], ["B", "2"]]
      parsed.forEach(pair => {
        if (Array.isArray(pair) && pair.length >= 2) {
          left.push(pair[0])
          right.push(pair[1])
        }
      })
      if (left.length > 0) return { left, right }
    }
  } catch {
    // 不是 JSON，繼續文字解析
  }

  // 支援多種格式：A-1, B-2 或 Item:Match 或 Term=Definition
  const pairs = String(answerText).split(/[,;，；]/).map(p => p.trim()).filter(Boolean)
  pairs.forEach(pair => {
    // 支援多種分隔符：-, :, =, →, ：
    const parts = pair.split(/[-:=→：]/).map(p => p.trim())
    if (parts.length >= 2) {
      left.push(parts[0])
      right.push(parts[1])
    }
  })
  return { left, right }
}

// 配對題：取得左欄項目
const matchingLeftItems = computed(() => {
  const qd = props.question.question_data
  if (qd?.left_items && Array.isArray(qd.left_items) && qd.left_items.length > 0) {
    return qd.left_items
  }
  // 容錯：嘗試從 answer 解析
  const answer = props.question.correct_answer || props.question.answer || ''
  return parseMatchingAnswer(answer).left
})

// 配對題：取得右欄項目
const matchingRightItems = computed(() => {
  const qd = props.question.question_data
  if (qd?.right_items && Array.isArray(qd.right_items) && qd.right_items.length > 0) {
    return qd.right_items
  }
  // 容錯：嘗試從 answer 解析
  const answer = props.question.correct_answer || props.question.answer || ''
  return parseMatchingAnswer(answer).right
})
</script>

<style scoped>
.question-item {
  margin-bottom: 10px;
  padding: 5px;
}

.question-item.has-bg {
  background: #f9f9f9;
}

.question-item.has-border {
  border: 1px solid #ddd;
  border-radius: 4px;
}

.question-number {
  display: inline-block;
  font-weight: bold;
  margin-right: 10px;
  min-width: 30px;
}

.question-body {
  display: inline;
}

.question-text {
  display: inline-block;
  margin-bottom: 5px;
}

.question-options {
  margin-left: 30px;
  margin-top: 5px;
}

.options-vertical .option {
  display: block;
  margin-bottom: 3px;
}

.options-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.options-compact {
  display: flex;
  gap: 15px;
}

.option-label {
  font-weight: bold;
  margin-right: 8px;
}

:deep(.blank) {
  display: inline-block;
  min-width: 80px;
  text-align: center;
  margin: 0 3px;
}

:deep(.blank-underline) {
  border-bottom: 1px solid #000;
}

:deep(.blank-box) {
  border: 1px solid #000;
  padding: 2px 4px;
}

:deep(.blank-parentheses)::before {
  content: '(';
}

:deep(.blank-parentheses)::after {
  content: ')';
}

:deep(.blank-dotted) {
  border-bottom: 1px dotted #000;
}

.answer-area {
  margin-left: 30px;
  margin-top: 5px;
}

.answer-line {
  height: 18px;
  margin-bottom: 3px;
}

.answer-line.line-solid {
  border-bottom: 1px solid #333;
}

.answer-line.line-dotted {
  border-bottom: 1px dotted #333;
}

.answer-line.line-dashed {
  border-bottom: 1px dashed #333;
}

.tf-options {
  margin-left: 40px;
  margin-top: 5px;
  font-weight: bold;
}

.matching-area {
  margin-left: 30px;
  margin-top: 10px;
}

.matching-columns {
  display: flex;
  gap: 40px;
  margin-bottom: 15px;
}

.matching-column {
  flex: 1;
  min-width: 120px;
}

.column-header {
  font-weight: bold;
  font-size: 11pt;
  margin-bottom: 8px;
  border-bottom: 1px solid #333;
  padding-bottom: 4px;
}

.matching-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 6px;
  font-size: 10pt;
}

.matching-item .item-label {
  font-weight: bold;
  min-width: 20px;
  margin-right: 5px;
}

.matching-item .item-text {
  flex: 1;
}

.matching-answer-area {
  margin-top: 10px;
  font-size: 10pt;
}

.matching-answer-area .answer-label {
  font-weight: bold;
  margin-right: 10px;
}

.matching-answer-area .answer-blank {
  margin-right: 15px;
}

/* 圖片題樣式 */
.image-question-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-display {
  margin: 10px 0;
  max-width: 100%;
}

.question-image {
  max-width: 100%;
  max-height: var(--exam-image-max-height, 200px);
  object-fit: contain;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.image-placeholder-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 120px;
  background: #f9f9f9;
  border: 2px dashed #ddd;
  border-radius: 4px;
  color: #999;
}

.placeholder-icon {
  font-size: 2rem;
  margin-bottom: 5px;
}

.placeholder-text {
  font-size: 0.75rem;
  text-align: center;
}

.image-question-answer-area {
  margin-left: 40px;
  margin-top: 10px;
}
</style>
