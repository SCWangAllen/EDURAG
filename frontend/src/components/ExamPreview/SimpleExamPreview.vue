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
          {{ config.header?.schoolName || DEFAULT_SCHOOL_NAME }}
        </h1>
        <h2 class="exam-title editable-title" 
            :class="{ 'editable-active': isEditable }"
            :contenteditable="isEditable" 
            @blur="updateTitle('titlePrefix', $event)"
            @keydown.enter.prevent="$event.target.blur()"
            :title="isEditable ? '點擊編輯考試標題' : ''">
          {{ config.header?.titlePrefix || DEFAULT_EXAM_TITLE }}
        </h2>
        <h3 class="exam-subtitle editable-title" 
            :class="{ 'editable-active': isEditable }"
            :contenteditable="isEditable" 
            @blur="updateTitle('subtitle', $event)"
            @keydown.enter.prevent="$event.target.blur()"
            :title="isEditable ? '點擊編輯副標題' : ''">
          {{ config.header?.subtitle || DEFAULT_EXAM_SUBTITLE }}
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
          
          <QuestionRenderer
            v-for="(q, index) in getQuestionsByType(questionType)"
            :key="`${questionType}-${index}`"
            :question="q"
            :index="index"
            :question-type="questionType"
            :config="config"
          />
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
import QuestionRenderer from './QuestionRenderer.vue'
import { DEFAULT_SCHOOL_NAME, DEFAULT_EXAM_TITLE, DEFAULT_EXAM_SUBTITLE } from '@/constants/examDefaults.js'

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
  },
  questionTypeConfig: {
    type: Object,
    default: () => ({})
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

const getSectionTitle = (questionType, sectionNumber) => {
  // ✅ 動態生成 Section 字母（基於實際順序）
  const letter = String.fromCharCode(65 + sectionNumber - 1)  // 65 = 'A'

  // 題型名稱對照表（保留原有的 Abraham Academy 格式名稱）
  const typeNameMapping = {
    matching: 'Matching',
    multiple_choice: 'Multiple Choice',
    single_choice: 'Multiple Choice',
    cloze: 'Fill in the Blanks',
    fill_in_blank: 'Fill in the Blanks',
    true_false: 'True or False',
    short_answer: 'Questions and Answers',
    essay: 'Paragraph Writing',
    sequence: 'Sequencing',
    enumeration: 'Enumeration',
    symbol_identification: 'Symbol Identification',
    image_question: 'Image Questions'
  }

  const name = typeNameMapping[questionType] || questionType

  // ✅ 從 questionTypeConfig 計算實際總分
  const typeConfig = props.questionTypeConfig[questionType]
  const totalPoints = typeConfig ? (typeConfig.count * typeConfig.points) : 0

  return `${letter}. ${name} _____/${totalPoints}`
}

const getSectionInstruction = (questionType) => {
  // ✅ 從 questionTypeConfig 取得每題配分
  const typeConfig = props.questionTypeConfig[questionType]
  const pointsPerQuestion = typeConfig ? typeConfig.points : 1

  // Abraham Academy 標準指導文字（使用實際配分）
  const baseInstructions = {
    matching: 'Write the answer that best fits the description on the line.',
    multiple_choice: 'Write the correct answer in the blank before each number.',
    single_choice: 'Write the correct answer in the blank before each number.',
    cloze: 'Write the answer that best fits the description on the line.',
    fill_in_blank: 'Write the answer that best fits the description on the line.',
    true_false: 'Circle T for true or F for false.',
    short_answer: 'Answer in a complete sentence unless it says "List."',
    essay: 'Write in complete paragraphs with proper structure.',
    image_question: 'Answer the questions based on the images provided.'
  }

  const baseText = baseInstructions[questionType] || 'Complete the following questions.'

  // 為有配分的題型添加配分說明
  if (typeConfig && ['matching', 'multiple_choice', 'single_choice', 'cloze', 'fill_in_blank', 'true_false', 'image_question'].includes(questionType)) {
    return `${baseText} (${pointsPerQuestion} ${pointsPerQuestion > 1 ? 'pts' : 'pt'} each)`
  }

  return baseText
}
</script>

<style scoped>
/* 基礎樣式 */
.exam-preview {
  width: 100%;
  min-height: 100%;
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