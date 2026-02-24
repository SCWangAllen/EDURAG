/**
 * 考券預設值常數
 * 集中管理 Abraham Academy 相關硬編碼值
 */

export const DEFAULT_SCHOOL_NAME = 'Abraham Academy'

export const DEFAULT_EXAM_TITLE = '2024 Semester 2 G4 Science Midterm Exam'

export const DEFAULT_EXAM_SUBTITLE = "(Understanding God's World pp. 115-171)"

/**
 * 題型對照表（用於 PDF/文字匯出區塊標題）
 */
export const QUESTION_TYPE_MAPPING = {
  matching: { letter: 'A', name: 'Matching', points: 10 },
  multiple_choice: { letter: 'B', name: 'Multiple Choice', points: 10 },
  single_choice: { letter: 'B', name: 'Multiple Choice', points: 10 },
  cloze: { letter: 'C', name: 'Fill in the Blanks', points: 26 },
  fill_in_blank: { letter: 'C', name: 'Fill in the Blanks', points: 26 },
  true_false: { letter: 'D', name: 'True or False', points: 10 },
  sequence: { letter: 'E', name: 'Sequence Ordering', points: 10 },
  short_answer: { letter: 'F', name: 'Questions and Answers', points: 24 },
  essay: { letter: 'G', name: 'Paragraph Writing', points: 12 },
  image_question: { letter: 'H', name: 'Image Questions', points: 10 },
  enumeration: { letter: 'I', name: 'Enumeration', points: 10 },
  symbol_identification: { letter: 'J', name: 'Symbol Identification', points: 10 }
}

/**
 * 區塊指導文字（用於 PDF/文字匯出）
 */
export const SECTION_INSTRUCTIONS = {
  matching: 'Write the answer that best fits the description on the line. (1 pt each)',
  multiple_choice: 'Write the correct answer in the blank before each number. (1 pt each)',
  single_choice: 'Write the correct answer in the blank before each number. (1 pt each)',
  cloze: 'Write the answer that best fits the description on the line. (2 pts each)',
  fill_in_blank: 'Write the answer that best fits the description on the line. (2 pts each)',
  true_false: 'Write T for True or F for False in the blank. (1 pt each)',
  sequence: 'Write the correct order number in the blank before each item. (1 pt each)',
  short_answer: 'Answer in a complete sentence unless it says "List."',
  essay: 'Write in complete paragraphs with proper structure.',
  image_question: 'Answer the questions based on the images provided.',
  enumeration: 'List the requested items. (1 pt each)',
  symbol_identification: 'Identify the meaning of each symbol. (1 pt each)'
}

/**
 * 元素級別字體設定預設值
 * 用於考券進階樣式客製化
 */
export const DEFAULT_TYPOGRAPHY_ELEMENTS = {
  schoolName: { fontSize: 16, fontWeight: 'bold', textAlign: 'center' },
  sectionTitle: { fontSize: 14, fontWeight: 'bold', textAlign: 'left' },
  sectionInstruction: { fontSize: 12, fontWeight: 'bold', textAlign: 'left' },
  studentInfo: { fontSize: 14, fontWeight: 'bold', textAlign: 'center' },
  parentSignature: { fontSize: 10, fontWeight: 'bold', textAlign: 'left' },
  questionContent: { fontSize: 12, fontWeight: 'normal', textAlign: 'left' },
  examScope: { fontSize: 10, fontWeight: 'normal', textAlign: 'center' }
}

/**
 * 學生資訊區預設配置
 * 第一行：Name, Class, Date（橫向排列）
 * 第二行：Score（單獨一行，置中）
 */
export const DEFAULT_STUDENT_INFO = {
  enabled: true,
  topFields: [
    { label: 'Name', key: 'name' },
    { label: 'Class', key: 'class' },
    { label: 'Date', key: 'date' }
  ],
  bottomField: { label: 'Score', key: 'score' }
}

/**
 * 家長簽名區預設配置
 */
export const DEFAULT_PARENT_SIGNATURE = {
  enabled: true,
  label: 'Parent Signature',
  position: 'top-left',
  boxStyle: true
}
