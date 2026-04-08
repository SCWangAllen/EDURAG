/**
 * 考券樣式模板配置
 * 定義不同類型的考券樣式和格式
 */

export const examTemplates = {
  // 標準模板
  standard: {
    header: {
      titlePrefix: '',
      schoolName: '○○學校',
      duration: '90',
      totalScore: '100',
      showMetadata: true,
      instructions: '1. 請仔細閱讀每題題目\n2. 選擇題請在答案卡上作答\n3. 填充題請將答案填入空格中\n4. 簡答題請條理清楚地回答\n5. 考試時間內不得使用參考資料',
      instructionsTitle: '考試說明'
    },
    questionOptions: {
      showSingleChoice: true,
      showCloze: true,
      showShortAnswer: true,
      showAuto: true,
      singleChoiceTitle: 'Part I: Multiple Choice Questions',
      clozeTitle: 'Part II: Fill in the Blanks',
      shortAnswerTitle: 'Part III: Short Answer Questions',
      autoTitle: 'Part IV: Additional Questions'
    },
    footer: {
      content: '※ 請將答案寫在指定的答案欄內，字跡清晰，保持卷面整潔。',
      answerSheetTitle: 'Answer Sheet'
    },
    exportOptions: {
      questionsOnly: false,
      answerSheetOnly: false,
      completeExam: true
    }
  },

  // 學術型模板
  academic: {
    header: {
      titlePrefix: 'Academic',
      schoolName: '○○大學',
      duration: '120',
      totalScore: '100',
      showMetadata: true,
      instructions: '1. This examination consists of multiple sections\n2. Read all questions carefully before answering\n3. Show your work for full credit\n4. Use only approved materials during the exam\n5. Submit your answer sheet before time expires',
      instructionsTitle: 'Examination Instructions'
    },
    questionOptions: {
      showSingleChoice: true,
      showCloze: true,
      showShortAnswer: true,
      showAuto: true,
      singleChoiceTitle: 'Section A: Multiple Choice',
      clozeTitle: 'Section B: Fill in the Blanks',
      shortAnswerTitle: 'Section C: Short Answer',
      autoTitle: 'Section D: Comprehensive Questions'
    },
    footer: {
      content: '※ All answers must be provided in the designated answer areas. Maintain neat handwriting throughout.',
      answerSheetTitle: 'Answer Sheet'
    },
    exportOptions: {
      questionsOnly: false,
      answerSheetOnly: false,
      completeExam: true
    }
  },

  // 簡潔型模板
  minimal: {
    header: {
      titlePrefix: '',
      schoolName: '',
      duration: '60',
      totalScore: '100',
      showMetadata: false,
      instructions: '',
      instructionsTitle: ''
    },
    questionOptions: {
      showSingleChoice: true,
      showCloze: true,
      showShortAnswer: true,
      showAuto: true,
      singleChoiceTitle: '選擇題',
      clozeTitle: '填空題',
      shortAnswerTitle: '簡答題',
      autoTitle: '其他題型'
    },
    footer: {
      content: '',
      answerSheetTitle: '答案欄'
    },
    exportOptions: {
      questionsOnly: false,
      answerSheetOnly: false,
      completeExam: true
    }
  },

  // 正式考試模板
  formal: {
    header: {
      titlePrefix: 'Official',
      schoolName: '○○教育機構',
      duration: '150',
      totalScore: '150',
      showMetadata: true,
      instructions: '【重要提醒】\n1. 考試開始前，請先檢查試卷完整性\n2. 答案必須使用藍色或黑色原子筆書寫\n3. 修改答案時請劃清楚原答案再重寫\n4. 考試結束鈴響後立即停筆\n5. 違反考試規則將依規定處理',
      instructionsTitle: '考試注意事項'
    },
    questionOptions: {
      showSingleChoice: true,
      showCloze: true,
      showShortAnswer: true,
      showAuto: true,
      singleChoiceTitle: '第一部分：選擇題',
      clozeTitle: '第二部分：填空題',
      shortAnswerTitle: '第三部分：簡答題',
      autoTitle: '第四部分：綜合題'
    },
    footer: {
      content: '※ 本試卷共 __ 頁，請確認試卷完整。考試時間結束請立即停筆，將試卷翻面放置。',
      answerSheetTitle: '答案欄'
    },
    exportOptions: {
      questionsOnly: false,
      answerSheetOnly: false,
      completeExam: true
    }
  }
}

/**
 * 獲取模板列表
 * @returns {Array} 模板選項列表
 */
export const getTemplateOptions = () => [
  { value: 'standard', label: '標準模板', description: '適合一般考試使用' },
  { value: 'academic', label: '學術模板', description: '適合大學或學術機構' },
  { value: 'minimal', label: '簡潔模板', description: '簡潔清爽的設計' },
  { value: 'formal', label: '正式模板', description: '適合正式考試場合' }
]

/**
 * 獲取指定模板
 * @param {string} templateName - 模板名稱
 * @returns {Object} 模板配置
 */
export const getTemplate = (templateName) => {
  return examTemplates[templateName] || examTemplates.standard
}

/**
 * 深度複製模板（用於避免修改原始模板）
 * @param {string} templateName - 模板名稱
 * @returns {Object} 模板配置的深拷貝
 */
export const cloneTemplate = (templateName) => {
  const template = getTemplate(templateName)
  return JSON.parse(JSON.stringify(template))
}