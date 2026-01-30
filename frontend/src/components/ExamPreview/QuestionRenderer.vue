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
          <div class="matching-instructions">請將左右兩欄進行配對</div>
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
  let blank = '________'

  switch (style) {
    case 'box': blank = '[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]'; break
    case 'parentheses': blank = '(&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)'; break
    case 'dotted': blank = '········'; break
    default: blank = '________'
  }

  return text.replace(/___+|\[\s*\]|\(\s*\)/g, `<span class="blank">${blank}</span>`)
}
</script>

<style scoped>
.question-item {
  margin-bottom: 20px;
  padding: 10px;
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
  margin-bottom: 10px;
}

.question-options {
  margin-left: 40px;
  margin-top: 10px;
}

.options-vertical .option {
  display: block;
  margin-bottom: 5px;
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
  min-width: 60px;
  text-align: center;
  border-bottom: 1px solid #000;
  margin: 0 5px;
}

.answer-area {
  margin-left: 40px;
  margin-top: 10px;
}

.answer-line {
  height: 25px;
  margin-bottom: 5px;
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
  margin-left: 40px;
  margin-top: 10px;
}

.matching-instructions {
  font-size: 11pt;
  color: #666;
  font-style: italic;
  margin-bottom: 10px;
}
</style>
