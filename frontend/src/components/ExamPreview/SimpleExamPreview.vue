<template>
  <div class="exam-preview" :style="cssVariables">
    <!-- 考券容器 -->
    <div class="exam-paper">
      <!-- 頁眉區 - 含家長簽名框和標題 -->
      <header v-if="config.header?.enabled !== false" class="exam-header-area">
        <!-- 左上角家長簽名框 -->
        <div v-if="config.parentSignature?.enabled" class="parent-signature-box">
          <label class="signature-label">{{ config.parentSignature?.label || '家長簽名' }}:</label>
          <div class="signature-box"></div>
        </div>

        <!-- 中央標題區 -->
        <div class="header-center">
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
        </div>
      </header>

      <!-- 學生資訊區 - 兩行佈局 -->
      <section v-if="config.studentInfo?.enabled" class="student-info">
        <!-- 第一行：Name, Class, Date -->
        <div class="info-fields-row">
          <div v-for="field in studentInfoTopFields" :key="field.key" class="info-field">
            <span class="field-label">{{ field.label }}:</span>
            <span class="field-underline"></span>
          </div>
        </div>
        <!-- 第二行：Score -->
        <div class="info-score-row">
          <div class="info-field">
            <span class="field-label">{{ studentInfoBottomField.label }}:</span>
            <span class="field-underline"></span>
          </div>
        </div>
      </section>

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
import {
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE,
  DEFAULT_TYPOGRAPHY_ELEMENTS,
  DEFAULT_STUDENT_INFO
} from '@/constants/examDefaults.js'

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

// CSS Variables 計算屬性（用於動態樣式套用）
const cssVariables = computed(() => {
  const typo = props.config.typography || {}
  const elements = typo.elements || DEFAULT_TYPOGRAPHY_ELEMENTS
  const imageSizeMap = { small: '120px', medium: '200px', large: '300px' }

  return {
    // 全域設定
    '--exam-font-size': `${typo.fontSize || 11}pt`,
    '--exam-line-height': typo.lineHeight || 1.4,
    '--exam-image-max-height': imageSizeMap[typo.imageSize] || '200px',

    // 元素級別設定 - 校名
    '--exam-school-name-size': `${elements.schoolName?.fontSize || 16}pt`,
    '--exam-school-name-weight': elements.schoolName?.fontWeight || 'bold',
    '--exam-school-name-align': elements.schoolName?.textAlign || 'center',

    // 大題標題
    '--exam-section-title-size': `${elements.sectionTitle?.fontSize || 14}pt`,
    '--exam-section-title-weight': elements.sectionTitle?.fontWeight || 'bold',
    '--exam-section-title-align': elements.sectionTitle?.textAlign || 'left',

    // 題目指示
    '--exam-section-instruction-size': `${elements.sectionInstruction?.fontSize || 12}pt`,
    '--exam-section-instruction-weight': elements.sectionInstruction?.fontWeight || 'bold',
    '--exam-section-instruction-align': elements.sectionInstruction?.textAlign || 'left',

    // 學生資訊
    '--exam-student-info-size': `${elements.studentInfo?.fontSize || 14}pt`,
    '--exam-student-info-weight': elements.studentInfo?.fontWeight || 'bold',
    '--exam-student-info-align': elements.studentInfo?.textAlign || 'center',

    // 家長簽名
    '--exam-parent-signature-size': `${elements.parentSignature?.fontSize || 10}pt`,
    '--exam-parent-signature-weight': elements.parentSignature?.fontWeight || 'bold',

    // 題目內容
    '--exam-question-size': `${elements.questionContent?.fontSize || 12}pt`,
    '--exam-question-weight': elements.questionContent?.fontWeight || 'normal',
    '--exam-question-align': elements.questionContent?.textAlign || 'left',

    // 範圍/副標題
    '--exam-scope-size': `${elements.examScope?.fontSize || 10}pt`,
    '--exam-scope-weight': elements.examScope?.fontWeight || 'normal',
    '--exam-scope-align': elements.examScope?.textAlign || 'center'
  }
})

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

// 學生資訊欄位 - 第一行（Name, Class, Date）
const studentInfoTopFields = computed(() => {
  if (props.config.studentInfo?.topFields && Array.isArray(props.config.studentInfo.topFields)) {
    return props.config.studentInfo.topFields
  }
  return DEFAULT_STUDENT_INFO.topFields
})

// 學生資訊欄位 - 第二行（Score）
const studentInfoBottomField = computed(() => {
  if (props.config.studentInfo?.bottomField) {
    return props.config.studentInfo.bottomField
  }
  return DEFAULT_STUDENT_INFO.bottomField
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
  padding: 15mm;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-family: 'Times New Roman', 'SimSun', serif;
  font-size: var(--exam-font-size, 11pt);
  line-height: var(--exam-line-height, 1.4);
}

/* 頁眉區域 - 含家長簽名和標題 */
.exam-header-area {
  position: relative;
  text-align: center;
  padding-top: 3px;
  min-height: 55px;
  margin-bottom: 5px;
}

/* 左上角家長簽名框 - absolute 定位與 PDF 一致 */
.parent-signature-box {
  position: absolute;
  left: 0;
  top: 3px;
  font-size: var(--exam-parent-signature-size, 10pt);
  font-weight: var(--exam-parent-signature-weight, bold);
}

.signature-label {
  display: block;
  margin-bottom: 2px;
}

.signature-box {
  width: 80px;
  height: 30px;
  border: 1px solid #000;
}

/* 中央標題區 */
.header-center {
  text-align: center;
}

/* 校名 - 使用 CSS variable */
.school-name {
  font-size: var(--exam-school-name-size, 16pt);
  font-weight: var(--exam-school-name-weight, bold);
  text-align: center;
  margin: 0 0 3px 0;
}

/* 考試標題 */
.exam-title {
  font-size: 13pt;
  font-weight: bold;
  margin: 0 0 2px 0;
}

/* 範圍/副標題 - 使用 CSS variable */
.exam-subtitle {
  font-size: var(--exam-scope-size, 10pt);
  font-weight: var(--exam-scope-weight, normal);
  text-align: center;
  margin: 0;
  color: #333;
}

/* 學生資訊區 - 兩行佈局，與 PDF 一致 */
.student-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: var(--exam-student-info-size, 14pt);
  font-weight: var(--exam-student-info-weight, bold);
  margin: 8px 0 8px 0;
  gap: 4px;
}

/* 第一行：Name, Class, Date */
.info-fields-row {
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 第二行：Score */
.info-score-row {
  display: flex;
  justify-content: center;
}

.info-field {
  display: flex;
  align-items: baseline;
}

.field-label {
  margin-right: 2px;
}

.field-underline {
  display: inline-block;
  width: 70px;
  border-bottom: 1px solid #000;
  height: 0.9em;
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
  margin-bottom: 15px;
  page-break-inside: avoid;
}

/* 大題標題 - 使用 CSS variable */
.section-title {
  font-size: var(--exam-section-title-size, 14pt);
  font-weight: var(--exam-section-title-weight, bold);
  text-align: var(--exam-section-title-align, left);
  margin: 0 0 4px 0;
}

/* 題目指示 - 使用 CSS variable */
.section-instruction {
  font-size: var(--exam-section-instruction-size, 12pt);
  font-weight: var(--exam-section-instruction-weight, bold);
  text-align: var(--exam-section-instruction-align, left);
  margin: 0 0 8px 0;
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

/* 題目內容樣式 */
.exam-content {
  margin: 20px 0;
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