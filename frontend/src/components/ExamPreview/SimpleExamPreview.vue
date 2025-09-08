<template>
  <div class="exam-preview">
    <!-- 考券容器 -->
    <div class="exam-paper">
      <!-- 頁眉區 - 使用 Abraham Academy 標準格式 -->
      <header v-if="config.header?.enabled !== false" class="exam-header">
        <!-- 編輯模式提示 -->
        <div v-if="isEditable" class="edit-hint">
          ✏️ 點擊標題即可編輯
        </div>
        
        <h1 class="school-name editable-title" 
            :class="{ 'editable-active': isEditable }"
            :contenteditable="isEditable" 
            @blur="updateTitle('schoolName', $event)"
            @keydown.enter.prevent="$event.target.blur()"
            :title="isEditable ? '點擊編輯學校名稱' : ''">
          {{ config.header?.schoolName || 'Abraham Academy' }}
        </h1>
        <h2 class="exam-title editable-title" 
            :class="{ 'editable-active': isEditable }"
            :contenteditable="isEditable" 
            @blur="updateTitle('titlePrefix', $event)"
            @keydown.enter.prevent="$event.target.blur()"
            :title="isEditable ? '點擊編輯考試標題' : ''">
          {{ config.header?.titlePrefix || '2024 Semester 2 G4 Science Midterm Exam' }}
        </h2>
        <h3 class="exam-subtitle editable-title" 
            :class="{ 'editable-active': isEditable }"
            :contenteditable="isEditable" 
            @blur="updateTitle('subtitle', $event)"
            @keydown.enter.prevent="$event.target.blur()"
            :title="isEditable ? '點擊編輯副標題' : ''">
          {{ config.header?.subtitle || '(Understanding God\'s World pp. 115-171)' }}
        </h3>
      </header>

      <!-- 學生資訊區
      <section v-if="config.studentInfo?.enabled !== false" class="student-info">
        <div class="info-field" v-for="field in studentFields" :key="field">
          <label>{{ field }}:</label>
          <span class="blank-line">_________________</span>
        </div>
      </section> -->

      <!-- 題目內容區 -->
      <main class="exam-content">
        <!-- 動態題目區塊，依照使用者設定的順序 -->
        <section 
          v-for="(questionType, sectionIndex) in orderedQuestionTypes" 
          :key="questionType"
          v-show="hasQuestionType(questionType)" 
          class="question-section"
        >
          <h3 class="section-title">{{ getSectionTitle(questionType, sectionIndex + 1) }}</h3>
          <p class="section-instruction">{{ getSectionInstruction(questionType) }}</p>
          
          <!-- 選擇題 -->
          <template v-if="questionType === 'single_choice'">
            <div 
              v-for="(q, index) in getQuestionsByType('single_choice')" 
              :key="`mc-${index}`"
              class="question-item"
              :class="getQuestionClass('single_choice')"
            >
              <div class="question-number">{{ getQuestionNumber(index, 'single_choice') }}</div>
              <div class="question-text">{{ q.content || q.prompt }}</div>
              <!-- 如果題目已經包含選項格式，就直接顯示，否則使用 options 陣列 -->
              <div v-if="q.options && q.options.length > 0" class="question-options" :class="getOptionsLayout()">
                <div 
                  v-for="(option, optIndex) in q.options" 
                  :key="`opt-${optIndex}`"
                  class="option"
                >
                  <!-- 檢查選項是否已經有標籤格式，如果有就不加，如果沒有就加 -->
                  <span v-if="!hasOptionLabel(option)" class="option-label">{{ getOptionLabel(optIndex) }}</span>
                  <span class="option-text">{{ option }}</span>
                </div>
              </div>
            </div>
          </template>

          <!-- 填空題 -->
          <template v-if="questionType === 'cloze'">
            <div 
              v-for="(q, index) in getQuestionsByType('cloze')" 
              :key="`cloze-${index}`"
              class="question-item"
              :class="getQuestionClass('cloze')"
            >
              <div class="question-number">{{ getQuestionNumber(index, 'cloze') }}</div>
              <div class="question-text" v-html="processClozeBlanks(q.content || q.prompt)"></div>
            </div>
          </template>

          <!-- 簡答題 -->
          <template v-if="questionType === 'short_answer'">
            <div 
              v-for="(q, index) in getQuestionsByType('short_answer')" 
              :key="`sa-${index}`"
              class="question-item"
              :class="getQuestionClass('short_answer')"
            >
              <div class="question-number">{{ getQuestionNumber(index, 'short_answer') }}</div>
              <div class="question-text">{{ q.content || q.prompt }}</div>
              <div class="answer-area">
                <div 
                  v-for="line in getAnswerLines()" 
                  :key="`line-${line}`"
                  class="answer-line"
                  :class="getAnswerLineStyle()"
                ></div>
              </div>
            </div>
          </template>

          <!-- 是非題 -->
          <template v-if="questionType === 'true_false'">
            <div 
              v-for="(q, index) in getQuestionsByType('true_false')" 
              :key="`tf-${index}`"
              class="question-item"
              :class="getQuestionClass('true_false')"
            >
              <div class="question-number">{{ getQuestionNumber(index, 'true_false') }}</div>
              <div class="question-text">{{ q.content || q.prompt }}</div>
              <div class="tf-options">
                {{ getTrueFalseOptions() }}
              </div>
            </div>
          </template>

          <!-- 配對題 -->
          <template v-if="questionType === 'matching'">
            <div 
              v-for="(q, index) in getQuestionsByType('matching')" 
              :key="`match-${index}`"
              class="question-item"
              :class="getQuestionClass('matching')"
            >
              <div class="question-number">{{ getQuestionNumber(index, 'matching') }}</div>
              <div class="question-text">{{ q.content || q.prompt }}</div>
              <div class="matching-area">
                <div class="matching-instructions">請將左右兩欄進行配對</div>
              </div>
            </div>
          </template>
        </section>
      </main>

      <!-- 答案欄 (如果啟用) -->
      <section v-if="config.answerSheet?.enabled" class="answer-sheet">
        <h3 class="answer-sheet-title">Answer Sheet</h3>
        <div class="answer-grid">
          <div 
            v-for="n in totalQuestions" 
            :key="`ans-${n}`"
            class="answer-item"
          >
            <span class="ans-number">{{ n }}.</span>
            <span class="ans-blank">____</span>
          </div>
        </div>
      </section>

      <!-- 頁尾 -->
      <footer v-if="config.footer?.enabled !== false" class="exam-footer">
        <div class="page-number">Page 1 of 1</div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  config: {
    type: Object,
    default: () => ({})
  },
  questionTypeOrder: {
    type: Array,
    default: () => ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
  },
  editable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update-config'])

// 編輯功能
const isEditable = computed(() => props.editable)

const updateTitle = (field, event) => {
  if (!isEditable.value) return
  
  const newValue = event.target.textContent.trim()
  const updatedConfig = { 
    ...props.config,
    header: {
      ...props.config.header,
      [field]: newValue
    }
  }
  emit('update-config', updatedConfig)
}

// 計算屬性
const totalQuestions = computed(() => props.questions.length)

const studentFields = computed(() => {
  const defaultFields = ['Class', 'Number', 'Name', 'Score']
  if (props.config.studentInfo?.fields) {
    return props.config.studentInfo.fields.map(f => 
      typeof f === 'string' ? f : f.label
    )
  }
  return defaultFields
})

const questionsByType = computed(() => {
  const grouped = {}
  props.questions.forEach(q => {
    if (!grouped[q.type]) {
      grouped[q.type] = []
    }
    grouped[q.type].push(q)
  })
  return grouped
})

const orderedQuestionTypes = computed(() => {
  return props.questionTypeOrder.filter(type => hasQuestionType(type))
})

// 方法
const hasQuestionType = (type) => {
  return questionsByType.value[type]?.length > 0
}

const getQuestionsByType = (type) => {
  return questionsByType.value[type] || []
}

const getQuestionNumber = (index, type) => {
  const style = props.config.questionStyles?.[type]?.numberStyle
  const num = index + 1
  
  switch (style) {
    case 'bracket': return `${num})`
    case 'circle': return ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'][index] || `${num}.`
    case 'square': return `[${num}]`
    default: return `${num}.`
  }
}

const getQuestionClass = (type) => {
  const styles = props.config.questionStyles?.[type]
  if (!styles?.enabled) return ''
  
  const classes = []
  if (styles.backgroundColor) classes.push('has-bg')
  if (styles.borderStyle !== 'none') classes.push('has-border')
  return classes.join(' ')
}

const getOptionsLayout = () => {
  const layout = props.config.questionStyles?.single_choice?.optionLayout
  return `options-${layout || 'vertical'}`
}

const getOptionLabel = (index) => {
  const style = props.config.questionStyles?.single_choice?.optionPrefix
  const letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  // 使用小寫符合 Abraham Academy 格式
  
  switch (style) {
    case 'circle': return ['Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ'][index]
    case 'square': return `[${letters[index]}]`
    case 'dot': return '•'
    default: return `${letters[index]}.`
  }
}

const hasOptionLabel = (option) => {
  // 檢查選項是否已經包含標籤格式（如 "a.", "b.", "A.", "B." 等）
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
  
  // 替換文本中的空格標記
  return text.replace(/___+|\[\s*\]|\(\s*\)/g, `<span class="blank">${blank}</span>`)
}

const getAnswerLines = () => {
  const count = props.config.questionStyles?.short_answer?.lineCount || 3
  return Array.from({ length: count }, (_, i) => i + 1)
}

const getAnswerLineStyle = () => {
  const style = props.config.questionStyles?.short_answer?.answerStyle
  return `line-${style || 'solid'}`
}

const getTrueFalseOptions = () => {
  const style = props.config.questionStyles?.true_false?.labelStyle
  switch (style) {
    case 'full': return 'True / False'
    case 'yn': return 'Yes / No'
    case 'ox': return 'O / X'
    case 'checkbox': return '☐ True  ☐ False'
    default: return 'T / F'
  }
}

const getSectionTitle = (questionType, sectionNumber) => {
  // 使用 Abraham Academy 標準格式
  const typeMapping = {
    matching: { letter: 'A', name: 'Matching', points: 10 },
    multiple_choice: { letter: 'B', name: 'Multiple Choice', points: 10 },
    single_choice: { letter: 'B', name: 'Multiple Choice', points: 10 },
    cloze: { letter: 'C', name: 'Fill in the Blanks', points: 26 },
    fill_in_blank: { letter: 'C', name: 'Fill in the Blanks', points: 26 },
    true_false: { letter: 'D', name: 'True or False', points: 12 },
    short_answer: { letter: 'F', name: 'Questions and Answers', points: 24 },
    essay: { letter: 'G', name: 'Paragraph Writing', points: 12 }
  }
  
  const config = typeMapping[questionType] || { letter: String.fromCharCode(65 + sectionNumber), name: questionType, points: 0 }
  return `${config.letter}. ${config.name} _____/${config.points}`
}

const getSectionInstruction = (questionType) => {
  // Abraham Academy 標準指導文字
  const instructions = {
    matching: 'Write the answer that best fits the description on the line. (1 pt each)',
    multiple_choice: 'Write the correct answer in the blank before each number. (1 pt each)',
    single_choice: 'Write the correct answer in the blank before each number. (1 pt each)',
    cloze: 'Write the answer that best fits the description on the line. (2 pts each)',
    fill_in_blank: 'Write the answer that best fits the description on the line. (2 pts each)',
    true_false: 'Circle T for true or F for false. (1 pt each)',
    short_answer: 'Answer in a complete sentence unless it says "List."',
    essay: 'Write in complete paragraphs with proper structure.'
  }
  
  return instructions[questionType] || 'Complete the following questions.'
}
</script>

<style scoped>
/* 基礎樣式 */
.exam-preview {
  width: 100%;
  height: 100%;
  overflow: auto;
  background: #f5f5f5;
  padding: 20px;
}

.exam-paper {
  max-width: 210mm;
  min-height: 297mm;
  margin: 0 auto;
  background: white;
  padding: 20mm;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-family: 'Times New Roman', 'SimSun', serif;
  font-size: 12pt;
  line-height: 1.6;
}

/* Abraham Academy 標準頁眉樣式 */
.exam-header {
  text-align: center;
  margin-bottom: 30px;
}

.school-name {
  font-size: 24pt;
  font-weight: bold;
  margin: 0 0 8px 0;
}

.exam-title {
  font-size: 18pt;
  font-weight: bold;
  margin: 0 0 5px 0;
}

.exam-subtitle {
  font-size: 16pt;
  margin: 0 0 20px 0;
  color: #333;
}

/* 編輯模式樣式 */
.edit-hint {
  background: #e3f2fd;
  border: 1px solid #2196f3;
  color: #1976d2;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 11pt;
  text-align: center;
  animation: fadeIn 0.3s ease-in;
}

.editable-title {
  position: relative;
  transition: all 0.2s ease;
}

.editable-active {
  cursor: text;
  padding: 4px 8px;
  border-radius: 4px;
}

.editable-active:hover {
  background-color: #f8f9fa;
  box-shadow: 0 0 0 2px #e3f2fd;
}

.editable-active:focus {
  outline: none;
  background-color: #fff;
  box-shadow: 0 0 0 2px #2196f3;
}

.editable-active::before {
  content: "✏️";
  position: absolute;
  right: -25px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.7;
  font-size: 12px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 題型區塊樣式 */
.question-section {
  margin-bottom: 30px;
  page-break-inside: avoid;
}

.section-title {
  font-size: 14pt;
  font-weight: bold;
  margin: 0 0 8px 0;
}

.section-instruction {
  font-size: 11pt;
  margin: 0 0 15px 0;
  font-style: italic;
  color: #444;
}

.exam-info {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 10px;
  font-size: 11pt;
}

/* 學生資訊樣式 */
.student-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 10px 0;
}

.info-field {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-field label {
  font-weight: bold;
}

.blank-line {
  display: inline-block;
  min-width: 100px;
  border-bottom: 1px solid #000;
}

/* 題目內容樣式 */
.exam-content {
  margin: 20px 0;
}

.question-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 14pt;
  font-weight: bold;
  margin: 20px 0 15px 0;
  padding-bottom: 5px;
  border-bottom: 1px solid #333;
}

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

.question-text {
  display: inline-block;
  margin-bottom: 10px;
}

/* 選項樣式 */
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

/* 填空題樣式 */
.blank {
  display: inline-block;
  min-width: 60px;
  text-align: center;
  border-bottom: 1px solid #000;
  margin: 0 5px;
}

/* 簡答題樣式 */
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

/* 是非題樣式 */
.tf-options {
  margin-left: 40px;
  margin-top: 5px;
  font-weight: bold;
}

/* 配對題樣式 */
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

/* 答案欄樣式 */
.answer-sheet {
  margin-top: 40px;
  padding: 20px;
  border: 2px solid #000;
  page-break-before: always;
}

.answer-sheet-title {
  font-size: 14pt;
  font-weight: bold;
  text-align: center;
  margin-bottom: 15px;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.ans-number {
  font-weight: bold;
}

.ans-blank {
  border-bottom: 1px solid #333;
  min-width: 40px;
}

/* 頁尾樣式 */
.exam-footer {
  margin-top: 40px;
  padding-top: 10px;
  border-top: 1px solid #333;
  text-align: center;
  font-size: 10pt;
}


/* 列印樣式 */
@media print {
  .exam-preview {
    background: white;
    padding: 0;
  }
  
  .exam-paper {
    box-shadow: none;
    margin: 0;
    padding: 15mm;
  }
  
  .question-section {
    page-break-inside: avoid;
  }
  
  .answer-sheet {
    page-break-before: always;
  }
}
</style>