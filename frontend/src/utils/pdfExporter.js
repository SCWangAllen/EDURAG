/**
 * PDF 匯出工具
 * 提供考券 PDF 匯出功能，支援圖片題目和增強答案券
 * 支援即時預覽（blob URL）和下載
 */
import {
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE,
  QUESTION_TYPE_MAPPING,
  SECTION_INSTRUCTIONS,
  DEFAULT_TYPOGRAPHY_ELEMENTS,
  DEFAULT_STUDENT_INFO
} from '../constants/examDefaults.js'

// 圖片載入快取
const imageCache = new Map()

/**
 * 內部函數：建構 PDF 文件（共用邏輯）
 * @param {Object} examData - 考券資料
 * @returns {Promise<jsPDF>} jsPDF 文件物件
 */
async function buildPDFDocument(examData) {
  // 動態載入 jsPDF
  const { jsPDF } = await import('jspdf')
  await import('jspdf/dist/jspdf.es.min.js')

  // 判斷是否為答案卷模式
  const isAnswerSheet = examData.config?.isAnswerSheet === true

  // 解構 typography 設定（字體大小、行距、圖片大小）
  const typography = examData.config?.typography || {}
  const baseFontSize = typography.fontSize || 11
  const lineHeight = typography.lineHeight || 1.4
  const imageSize = typography.imageSize || 'medium'

  // 圖片大小對照 (mm)
  // 注意：CSS 預覽使用 px (small=120, medium=200, large=300)
  // PDF 輸出使用 mm，此處值經過測試以產生視覺一致的結果
  const IMAGE_SIZE_MM = { small: 80, medium: 120, large: 180 }
  const maxImageHeight = IMAGE_SIZE_MM[imageSize] || 120

  // 行距因子（用於計算行間距）
  // 以標準行距 1.4 為基準，計算相對倍率
  const BASE_LINE_HEIGHT = 1.4
  const lineSpacingFactor = lineHeight / BASE_LINE_HEIGHT

  // 創建 PDF 文件 (A4 尺寸)
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  })

  // 設定中文字型 (如果需要)
  // pdf.addFont('path/to/chinese-font.ttf', 'chinese', 'normal')
  // pdf.setFont('chinese')

  // 設定基本樣式（使用配置的字體大小）
  pdf.setFontSize(baseFontSize)
  let yPosition = 15

  // 提取元素級別設定
  const elements = examData.config?.typography?.elements || DEFAULT_TYPOGRAPHY_ELEMENTS

  // 判斷是否為 Weekly Test 模式
  const isWeeklyTest = examData.config?.isWeeklyTest === true
  const subjects = examData.config?.subjects || []

  // 頁眉
  if (examData.config.header?.enabled !== false) {
    let title = examData.config.header?.titlePrefix || DEFAULT_EXAM_TITLE
    const schoolName = examData.config.header?.schoolName || DEFAULT_SCHOOL_NAME
    let subtitle = examData.config.header?.subtitle || DEFAULT_EXAM_SUBTITLE
    const pageWidth = 210 // A4 寬度

    // Weekly Test 模式：自動生成標題
    if (isWeeklyTest && subjects.length > 0) {
      const grade = examData.config?.grade || ''
      title = `${grade} Weekly Test`
      subtitle = subjects.join(', ')
    }

    // 左上角家長簽名框
    if (examData.config?.parentSignature?.enabled) {
      const sigStyle = elements.parentSignature || { fontSize: 10, fontWeight: 'bold' }
      pdf.setFontSize(sigStyle.fontSize)
      pdf.setFont('times', sigStyle.fontWeight === 'bold' ? 'bold' : 'normal')
      const sigLabel = examData.config.parentSignature?.label || 'Parent Signature'
      pdf.text(`${sigLabel}:`, 15, yPosition)
      // 畫長方框（與預覽一致的尺寸）
      pdf.setDrawColor(0, 0, 0)
      pdf.rect(15, yPosition + 2, 30, 12)  // x, y, width, height
    }

    // 學校名稱 - 使用元素設定（支援新舊 key 名稱）
    const schoolNameStyle = elements.school || elements.schoolName || { fontSize: 16, fontWeight: 'bold' }
    pdf.setFontSize(schoolNameStyle.fontSize)
    pdf.setFont('times', schoolNameStyle.fontWeight === 'bold' ? 'bold' : 'normal')
    const schoolWidth = pdf.getTextWidth(schoolName)
    pdf.text(schoolName, (pageWidth - schoolWidth) / 2, yPosition)
    yPosition += 7

    // 考試標題
    pdf.setFontSize(13)
    pdf.setFont('times', 'bold')
    const displayTitle = isAnswerSheet ? `${title} - Answer Key` : title
    const titleWidth = pdf.getTextWidth(displayTitle)
    pdf.text(displayTitle, (pageWidth - titleWidth) / 2, yPosition)
    yPosition += 6

    // 副標題/範圍 - 使用元素設定（支援新舊 key 名稱）
    const scopeStyle = elements.range || elements.examScope || { fontSize: 10, fontWeight: 'normal' }
    pdf.setFontSize(scopeStyle.fontSize)
    pdf.setFont('times', scopeStyle.fontWeight === 'bold' ? 'bold' : 'normal')
    const subtitleWidth = pdf.getTextWidth(subtitle)
    pdf.text(subtitle, (pageWidth - subtitleWidth) / 2, yPosition)
    yPosition += 10
  }

  // 學生資訊區 - 兩行佈局
  if (examData.config?.studentInfo?.enabled) {
    const studentInfoStyle = elements.studentInfo || { fontSize: 14, fontWeight: 'bold' }
    pdf.setFontSize(studentInfoStyle.fontSize)
    pdf.setFont('times', studentInfoStyle.fontWeight === 'bold' ? 'bold' : 'normal')

    const topFields = examData.config.studentInfo?.topFields || DEFAULT_STUDENT_INFO.topFields
    const bottomField = examData.config.studentInfo?.bottomField || DEFAULT_STUDENT_INFO.bottomField

    const pageWidth = 210

    // 第一行：Name, Class, Date（橫向排列置中）
    const topFieldCount = topFields.length
    const topFieldWidth = 55
    const totalTopWidth = topFieldCount * topFieldWidth
    let xPosition = (pageWidth - totalTopWidth) / 2

    topFields.forEach(field => {
      const fieldLabel = typeof field === 'string' ? field : field.label
      pdf.text(`${fieldLabel}: ______________`, xPosition, yPosition)
      xPosition += topFieldWidth
    })
    yPosition += 7

    // 第二行：Score（置中）
    const scoreLabel = typeof bottomField === 'string' ? bottomField : bottomField.label
    const scoreText = `${scoreLabel}: ______________`
    const scoreWidth = pdf.getTextWidth(scoreText)
    pdf.text(scoreText, (pageWidth - scoreWidth) / 2, yPosition)
    yPosition += 10
  }

  // 題目內容
  const orderedTypes = examData.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching', 'sequence', 'image_question']
  // 取得自定義題型設定
  const questionTypeSettings = examData.config?.questionTypeSettings || {}

  // Weekly Test 模式：按科目分組渲染
  if (isWeeklyTest && subjects.length > 0) {
    for (const subject of subjects) {
      // 科目區塊標題
      if (yPosition > 250) {
        pdf.addPage()
        yPosition = 20
      }

      pdf.setFontSize(14)
      pdf.setFont('times', 'bold')
      const subjectHeader = `【${subject} Section】`
      pdf.text(subjectHeader, 15, yPosition)
      yPosition += 8 * lineSpacingFactor

      // 過濾該科目的題目
      const subjectQuestions = examData.questions.filter(q => q.subject === subject)
      const questionsByType = groupQuestionsByType(subjectQuestions)

      let sectionNumber = 1
      for (const questionType of orderedTypes) {
        const questions = questionsByType[questionType]
        if (!questions || questions.length === 0) continue

        yPosition = await renderQuestionSection(
          pdf, questions, questionType, sectionNumber,
          yPosition, elements, questionTypeSettings,
          lineSpacingFactor, isAnswerSheet, examData.config, maxImageHeight
        )
        sectionNumber++
      }

      yPosition += 10 * lineSpacingFactor // 科目間距
    }
  } else {
    // 標準模式：按題型分組渲染
    const questionsByType = groupQuestionsByType(examData.questions)
    let sectionNumber = 1

    for (const questionType of orderedTypes) {
      const questions = questionsByType[questionType]
      if (!questions || questions.length === 0) continue

      yPosition = await renderQuestionSection(
        pdf, questions, questionType, sectionNumber,
        yPosition, elements, questionTypeSettings,
        lineSpacingFactor, isAnswerSheet, examData.config, maxImageHeight
      )
      sectionNumber++
    }
  }

  return pdf
}

/**
 * 渲染題目區塊（提取為獨立函數以支援多科目模式）
 */
async function renderQuestionSection(
  pdf, questions, questionType, sectionNumber,
  yPosition, elements, questionTypeSettings,
  lineSpacingFactor, isAnswerSheet, config, maxImageHeight
) {
  if (!questions || questions.length === 0) return yPosition

  // 檢查頁面空間
  if (yPosition > 250) {
    pdf.addPage()
    yPosition = 20
  }

  // 區塊標題（使用元素級別設定，支援新舊 key 名稱）
  const sectionTitleStyle = elements.questionType || elements.sectionTitle || { fontSize: 14, fontWeight: 'bold' }
  pdf.setFontSize(sectionTitleStyle.fontSize)
  pdf.setFont('times', sectionTitleStyle.fontWeight === 'bold' ? 'bold' : 'normal')
  const sectionTitle = getSectionTitle(questionType, sectionNumber, questionTypeSettings)
  pdf.text(sectionTitle, 15, yPosition)
  yPosition += 5 * lineSpacingFactor

  // 添加指導文字（使用元素級別設定，支援新舊 key 名稱）
  const instructionStyle = elements.instructions || elements.sectionInstruction || { fontSize: 12, fontWeight: 'bold' }
  pdf.setFontSize(instructionStyle.fontSize)
  // 題目指示使用 bold + italic 組合
  pdf.setFont('times', instructionStyle.fontWeight === 'bold' ? 'bolditalic' : 'italic')
  const instruction = getSectionInstruction(questionType, questionTypeSettings)
  pdf.text(instruction, 15, yPosition)
  yPosition += 6 * lineSpacingFactor

  // 題目內容字體（使用元素級別設定）
  const questionStyle = elements.questionContent || { fontSize: 12, fontWeight: 'normal' }
  pdf.setFont('times', questionStyle.fontWeight === 'bold' ? 'bold' : 'normal')
  pdf.setFontSize(questionStyle.fontSize)

  // 題目
  for (let index = 0; index < questions.length; index++) {
    const question = questions[index]
    const questionNumber = `${index + 1}.`
    let questionText = question.content || question.prompt || 'Question text'

    // 填空題：處理空白符號，統一轉換為 ________
    if (questionType === 'cloze') {
      questionText = normalizeClozeBlank(questionText)
    }

    // 檢查頁面空間（圖片題需要更多空間）
    const requiredSpace = questionType === 'image_question' ? 100 : 30
    if (yPosition > (297 - requiredSpace)) {
      pdf.addPage()
      yPosition = 20
    }

    // 計算行間距（基於配置的行距）
    const lineGap = 4 * lineSpacingFactor

    // 計算題號寬度，讓題目文字緊跟在題號後面
    let questionNumberEndX = 15
    const questionNumWidth = pdf.getTextWidth(questionNumber)

    // 是非題、選擇題（答案券模式）特殊處理：答案在題號前
    if (questionType === 'true_false' || (questionType === 'single_choice' && isAnswerSheet)) {
      if (isAnswerSheet) {
        // 答案卷：答案區域(15~25) + 題號 + 題目
        // 題號渲染在答案區域之後
        pdf.text(questionNumber, 26, yPosition)
        questionNumberEndX = 26 + questionNumWidth + 1
      } else {
        // 題目卷（僅是非題）：底線 + 題號 + 題目
        pdf.text('____', 15, yPosition)
        pdf.text(questionNumber, 26, yPosition)
        questionNumberEndX = 26 + questionNumWidth + 1
      }
    } else {
      pdf.text(questionNumber, 15, yPosition)
      questionNumberEndX = 15 + questionNumWidth + 1
    }

    // 答案卷模式：簡潔顯示題號和答案
    if (isAnswerSheet) {
      yPosition = await renderAnswerSheetQuestion(pdf, question, questionType, yPosition, config, lineSpacingFactor, questionStyle, questionNumberEndX)
      // 重置字體設定（renderAnswerSheetQuestion 會改變字體）
      pdf.setFont('times', questionStyle.fontWeight === 'bold' ? 'bold' : 'normal')
      pdf.setFontSize(questionStyle.fontSize)
    } else {
      // 試題卷模式：完整題目內容
      if (questionType === 'image_question') {
        // 圖片題目渲染（傳入圖片大小配置）
        yPosition = await renderImageQuestion(pdf, question, yPosition, questionText, maxImageHeight, lineSpacingFactor)
      } else if (questionType === 'matching') {
        // 配對題渲染
        yPosition = renderMatchingQuestion(pdf, question, yPosition, questionText, lineSpacingFactor)
      } else if (questionType === 'sequence') {
        // 排序題渲染
        yPosition = renderSequenceQuestion(pdf, question, yPosition, questionText, lineSpacingFactor)
      } else {
        // 處理長文本換行
        // 題目文字緊跟在題號後面
        const textStartX = questionNumberEndX
        const textMaxWidth = 195 - textStartX  // 右邊界固定在 195
        const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
        textLines.forEach((line, lineIndex) => {
          // 第一行緊跟題號，後續行從固定位置開始
          const xPos = lineIndex === 0 ? textStartX : 20
          pdf.text(line, xPos, yPosition + (lineIndex * lineGap))
        })

        yPosition += textLines.length * lineGap + 1.5 * lineSpacingFactor

        // 根據題型添加特定格式
        if (questionType === 'single_choice' && question.options) {
          question.options.forEach((option, optIndex) => {
            // 統一使用小寫字母標籤，移除原有標籤（如有）
            const optionLabel = String.fromCharCode(97 + optIndex) + '.'  // a. b. c. d.
            const optionContent = option.toString().trim().replace(/^[a-zA-Z][.\)\]]\s*/, '')
            const optionText = `${optionLabel} ${optionContent}`

            const optionLines = pdf.splitTextToSize(optionText, 155)
            optionLines.forEach((line, lineIndex) => {
              pdf.text(line, 25, yPosition + (lineIndex * lineGap))
            })
            yPosition += optionLines.length * lineGap + 0.5 * lineSpacingFactor
          })
          yPosition += 1 * lineSpacingFactor
        } else if (questionType === 'short_answer') {
          // 簡答題答題線（與題目起始位置對齊）
          const answerLineGap = 5 * lineSpacingFactor
          for (let i = 0; i < 2; i++) {
            pdf.line(20, yPosition + (i * answerLineGap), 185, yPosition + (i * answerLineGap))
          }
          yPosition += 10 * lineSpacingFactor
        } else if (questionType === 'true_false') {
          // 是非題題目卷：題目內容需要右移以配合題號前的底線
          // T / F 選項已移至題號前的底線區域，這裡不再顯示
          yPosition += 1 * lineSpacingFactor
        }
      }
    }

    yPosition += 2 * lineSpacingFactor // 題目間距
  }

  yPosition += 3 * lineSpacingFactor // 區塊間距
  return yPosition
}

/**
 * 生成 PDF 預覽用的 blob URL
 * @param {Object} examData - 考券資料
 * @returns {Promise<{success: boolean, blobUrl?: string, message?: string}>}
 */
export async function generatePDFPreview(examData) {
  try {
    const pdf = await buildPDFDocument(examData)
    const blobUrl = pdf.output('bloburl')
    return { success: true, blobUrl }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

/**
 * 匯出考券為 PDF（下載）
 * @param {Object} examData - 考券資料
 * @param {Array} examData.questions - 題目列表
 * @param {Object} examData.config - 考券配置
 * @param {Array} examData.questionTypeOrder - 題型順序
 * @param {Object} examData.questionTypeConfig - 題型配置（用於答案卷計分）
 * @param {string} filename - 檔案名稱
 */
export async function exportToPDF(examData, filename = 'exam.pdf') {
  try {
    const pdf = await buildPDFDocument(examData)
    pdf.save(filename)

    return {
      success: true,
      message: 'PDF 匯出成功'
    }

  } catch (error) {
    return {
      success: false,
      message: `PDF 匯出失敗: ${error.message}`
    }
  }
}

/**
 * 渲染圖片題目到 PDF（試題卷模式）
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {Object} question - 題目資料
 * @param {number} yPosition - 當前 Y 位置
 * @param {string} questionText - 題目文字
 * @param {number} maxImageHeight - 最大圖片高度 (mm)
 * @param {number} lineSpacingFactor - 行距因子
 * @returns {number} 更新後的 Y 位置
 */
async function renderImageQuestion(pdf, question, yPosition, questionText, maxImageHeight = 120, lineSpacingFactor = 1) {
  const margin = 20
  const contentWidth = 170
  const lineGap = 5 * lineSpacingFactor

  // 題目描述
  if (questionText && questionText !== '圖片題') {
    const textLines = pdf.splitTextToSize(questionText, contentWidth - 10)
    textLines.forEach((line, lineIndex) => {
      pdf.text(line, margin + 10, yPosition + (lineIndex * lineGap))
    })
    yPosition += textLines.length * lineGap + 5 * lineSpacingFactor
  }

  // 嵌入問題圖片（支持 _url 和 _path 兩種屬性）
  const questionImageUrl = question.question_image_url || question.question_image_path
  if (questionImageUrl) {
    try {
      const imageBase64 = await loadImageAsBase64(questionImageUrl)
      if (imageBase64) {
        // 計算合適的圖片尺寸（使用配置的最大高度）
        const maxWidth = 160
        const imgDimensions = await getImageDimensions(questionImageUrl)
        const { width, height } = calculateFitDimensions(imgDimensions.width, imgDimensions.height, maxWidth, maxImageHeight)

        pdf.addImage(imageBase64, 'JPEG', margin + 10, yPosition, width, height)
        yPosition += height + 5 * lineSpacingFactor
      } else {
        // 圖片載入失敗，顯示佔位符
        renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image || 'Image')
        yPosition += 45 * lineSpacingFactor
      }
    } catch (error) {
      // 圖片載入失敗，顯示佔位符
      renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image || 'Image')
      yPosition += 45 * lineSpacingFactor
    }
  } else if (question.question_image) {
    // 沒有 URL 但有圖片名稱，顯示佔位符
    renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image)
    yPosition += 45 * lineSpacingFactor
  }

  // 答題線
  const answerLineGap = 8 * lineSpacingFactor
  for (let i = 0; i < 3; i++) {
    pdf.line(margin + 10, yPosition + (i * answerLineGap), margin + contentWidth, yPosition + (i * answerLineGap))
  }
  yPosition += 25 * lineSpacingFactor

  return yPosition
}

/**
 * 渲染答案券中的題目（增強版，支援答案圖片和解釋）
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {Object} question - 題目資料
 * @param {string} questionType - 題型
 * @param {number} yPosition - 當前 Y 位置
 * @param {Object} config - 配置選項
 * @param {number} lineSpacingFactor - 行距因子
 * @returns {number} 更新後的 Y 位置
 */
async function renderAnswerSheetQuestion(pdf, question, questionType, yPosition, config = {}, lineSpacingFactor = 1, questionStyle = {}, textStartX = 20) {
  const showAnswerImages = config.showAnswerImages !== false
  const showExplanations = config.showExplanations !== false
  // 使用傳入的 questionStyle 計算行間距
  const fontSize = questionStyle.fontSize || 12
  const lineGap = fontSize * 0.35 * lineSpacingFactor
  const textMaxWidth = 195 - textStartX  // 右邊界固定在 195

  // 一般題目答案（同時顯示題目內容與答案）
  if (questionType !== 'image_question') {
    const answer = question.correct_answer || question.answer || 'N/A'
    const questionText = question.content || question.prompt || ''

    // 填空題特殊處理：答案直接嵌入空白位置（粗體+底線）
    if (questionType === 'cloze') {
      yPosition = renderClozeWithInlineAnswer(
        pdf, questionText, answer, textStartX, yPosition, fontSize, lineGap, textMaxWidth
      )
      yPosition += 1 * lineSpacingFactor
      return yPosition
    }

    // 是非題特殊處理：答案顯示在題號前（粗體+底線）
    if (questionType === 'true_false') {
      // 判斷答案是 T 或 F
      const answerStr = String(answer).toUpperCase().trim()
      const tfAnswer = answerStr.startsWith('T') || answerStr === 'TRUE' ? 'T' : 'F'

      // 渲染粗體答案 + 底線（置中於底線區域 15~25）
      pdf.setFont('times', 'bold')
      pdf.setFontSize(fontSize)
      const ansWidth = pdf.getTextWidth(tfAnswer)
      const ansX = 15 + (10 - ansWidth) / 2  // 置中於 15~25 區域
      pdf.text(tfAnswer, ansX, yPosition)
      pdf.setLineWidth(0.3)
      pdf.line(15, yPosition + 1, 25, yPosition + 1)

      // 題目內容（緊跟在題號後面）
      pdf.setFont('times', 'normal')
      pdf.setFontSize(fontSize)
      const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
      textLines.forEach((line, lineIndex) => {
        // 第一行緊跟題號，後續行從固定位置開始
        const xPos = lineIndex === 0 ? textStartX : 20
        pdf.text(line, xPos, yPosition + lineIndex * lineGap)
      })
      yPosition += textLines.length * lineGap + 1 * lineSpacingFactor
      return yPosition
    }

    // 選擇題特殊處理：答案顯示在題號前（小寫粗體+底線）
    if (questionType === 'single_choice') {
      // 解析答案字母（支援 "A"、"a"、"1"、數字索引等格式）
      const answerRaw = String(answer).trim()
      let answerLetter = 'a'
      if (/^[a-dA-D]$/.test(answerRaw)) {
        // 直接是字母
        answerLetter = answerRaw.toLowerCase()
      } else if (/^[1-4]$/.test(answerRaw)) {
        // 數字 1-4 轉為 a-d
        answerLetter = String.fromCharCode(96 + parseInt(answerRaw))
      } else if (/^[0-3]$/.test(answerRaw)) {
        // 數字索引 0-3 轉為 a-d
        answerLetter = String.fromCharCode(97 + parseInt(answerRaw))
      }

      // 渲染粗體答案 + 底線（置中於底線區域 15~25）
      pdf.setFont('times', 'bold')
      pdf.setFontSize(fontSize)
      const ansWidth = pdf.getTextWidth(answerLetter)
      const ansX = 15 + (10 - ansWidth) / 2  // 置中於 15~25 區域
      pdf.text(answerLetter, ansX, yPosition)
      pdf.setLineWidth(0.3)
      pdf.line(15, yPosition + 1, 25, yPosition + 1)

      // 題目內容（緊跟在題號後面）
      pdf.setFont('times', 'normal')
      pdf.setFontSize(fontSize)
      const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
      textLines.forEach((line, lineIndex) => {
        const xPos = lineIndex === 0 ? textStartX : 20
        pdf.text(line, xPos, yPosition + lineIndex * lineGap)
      })
      yPosition += textLines.length * lineGap + 1 * lineSpacingFactor

      // 顯示選項
      if (question.options && Array.isArray(question.options)) {
        question.options.forEach((option, optIndex) => {
          // 統一使用小寫字母標籤，移除原有標籤（如有）
          const optionLabel = String.fromCharCode(97 + optIndex) + '.'  // a. b. c. d.
          const optionContent = option.toString().trim().replace(/^[a-zA-Z][.\)\]]\s*/, '')
          const optionText = `${optionLabel} ${optionContent}`
          pdf.text(optionText, 25, yPosition)
          yPosition += lineGap
        })
        yPosition += 1 * lineSpacingFactor
      }

      return yPosition
    }

    // 其他題型：顯示題目內容
    if (questionText) {
      const fontWeight = questionStyle.fontWeight || 'normal'
      pdf.setFont('times', fontWeight === 'bold' ? 'bold' : 'normal')
      pdf.setFontSize(fontSize)
      const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
      textLines.forEach((line, lineIndex) => {
        // 第一行緊跟題號，後續行從固定位置開始
        const xPos = lineIndex === 0 ? textStartX : 20
        pdf.text(line, xPos, yPosition + lineIndex * lineGap)
      })
      yPosition += textLines.length * lineGap + 1 * lineSpacingFactor
    }

    // 2. 顯示選項（選擇題）- 統一使用小寫字母標籤 (a. b. c. d.)
    if (questionType === 'single_choice' && question.options && Array.isArray(question.options)) {
      question.options.forEach((option, optIndex) => {
        // 統一使用小寫字母標籤，移除原有標籤（如有）
        const optionLabel = String.fromCharCode(97 + optIndex) + '.'  // a. b. c. d.
        const optionContent = option.toString().trim().replace(/^[a-zA-Z][.\)\]]\s*/, '')
        const optionText = `${optionLabel} ${optionContent}`
        pdf.text(optionText, 25, yPosition)
        yPosition += lineGap
      })
      yPosition += 1 * lineSpacingFactor
    }

    // 3. 顯示答案（粗體標示，支援長答案換行）
    pdf.setFont('times', 'bold')

    // 配對題特殊處理：格式化顯示配對結果
    if (questionType === 'matching') {
      const qd = question.question_data || {}
      const leftItems = qd.left_items || []
      const rightItems = qd.right_items || []

      if (leftItems.length > 0 && rightItems.length > 0) {
        pdf.text('Answer:', 20, yPosition)
        yPosition += lineGap
        pdf.setFont('times', 'normal')

        // 嘗試解析答案配對
        const answerStr = String(answer)
        const pairs = answerStr.split(/[,;]/).map(p => p.trim())

        pairs.forEach((pair, idx) => {
          const pairText = `  ${String.fromCharCode(65 + idx)}. ${pair}`
          pdf.text(pairText, 20, yPosition)
          yPosition += lineGap
        })
        yPosition += 1 * lineSpacingFactor
      } else {
        // 長答案換行處理
        const answerText = `Answer: ${formatAnswerText(answer)}`
        const answerLines = pdf.splitTextToSize(answerText, 163)
        answerLines.forEach((line, lineIndex) => {
          pdf.text(line, 20, yPosition + lineIndex * lineGap)
        })
        pdf.setFont('times', 'normal')
        yPosition += answerLines.length * lineGap + 1 * lineSpacingFactor
      }
    } else {
      // 長答案換行處理
      const answerText = `Answer: ${formatAnswerText(answer)}`
      const answerLines = pdf.splitTextToSize(answerText, 163)
      answerLines.forEach((line, lineIndex) => {
        pdf.text(line, 20, yPosition + lineIndex * lineGap)
      })
      pdf.setFont('times', 'normal')
      yPosition += answerLines.length * lineGap + 1 * lineSpacingFactor
    }

    return yPosition
  }

  // 圖片題目答案（與其他題型格式一致）
  const questionText = question.content || question.prompt || ''

  // 1. 先渲染題目內容（緊跟在題號後面，與其他題型一致）
  if (questionText && questionText !== '圖片題') {
    const fontWeight = questionStyle.fontWeight || 'normal'
    pdf.setFont('times', fontWeight === 'bold' ? 'bold' : 'normal')
    pdf.setFontSize(fontSize)
    const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
    textLines.forEach((line, lineIndex) => {
      const xPos = lineIndex === 0 ? textStartX : 20
      pdf.text(line, xPos, yPosition + lineIndex * lineGap)
    })
    yPosition += textLines.length * lineGap + 1 * lineSpacingFactor
  }

  // 2. 顯示答案圖片（如果有且啟用）
  const answerImageUrl = question.answer_image_url || question.answer_image_path
  if (showAnswerImages && answerImageUrl) {
    try {
      const imageBase64 = await loadImageAsBase64(answerImageUrl)
      if (imageBase64) {
        // 檢查是否需要換頁
        if (yPosition > 200) {
          pdf.addPage()
          yPosition = 20
        }

        pdf.setFont('times', 'bold')
        pdf.text('Answer:', 20, yPosition)
        yPosition += 6

        const maxWidth = 120
        const maxHeight = 60
        const imgDimensions = await getImageDimensions(answerImageUrl)
        const { width, height } = calculateFitDimensions(imgDimensions.width, imgDimensions.height, maxWidth, maxHeight)

        pdf.addImage(imageBase64, 'JPEG', 20, yPosition, width, height)
        yPosition += height + 5
      }
    } catch (error) {
      // 答案圖片載入失敗，顯示文字
      pdf.setFont('times', 'bold')
      pdf.text(`Answer: [Image: ${question.answer_image || 'N/A'}]`, 20, yPosition)
      pdf.setFont('times', 'normal')
      yPosition += 8
    }
  } else if (question.answer_image) {
    // 有答案圖片但未啟用顯示
    pdf.setFont('times', 'bold')
    pdf.text(`Answer: [See answer image: ${question.answer_image}]`, 20, yPosition)
    pdf.setFont('times', 'normal')
    yPosition += 8
  }

  // 3. 顯示解釋說明（如果有且啟用）
  if (showExplanations && question.explanation) {
    pdf.setFont('times', 'italic')
    pdf.setFontSize(9)
    const explanationLines = pdf.splitTextToSize(`Explanation: ${question.explanation}`, 160)
    explanationLines.forEach((line, lineIndex) => {
      pdf.text(line, 20, yPosition + (lineIndex * 4))
    })
    yPosition += explanationLines.length * 4 + 3
    pdf.setFont('times', 'normal')
    pdf.setFontSize(fontSize)
  }

  return yPosition
}

/**
 * 正規化填空題空白符號
 * 將各種空白符號統一轉換為 ________
 * @param {string} text - 題目文字
 * @returns {string} 正規化後的文字
 */
function normalizeClozeBlank(text) {
  // 處理各種空白符號格式：___+, [ ], ( ), 【 】, （ ）
  return text
    .replace(/_{3,}/g, '________')           // 3個以上底線
    .replace(/\[\s*\]/g, '________')         // [ ] 或 []
    .replace(/\(\s*\)/g, '________')         // ( ) 或 ()
    .replace(/【\s*】/g, '________')          // 【 】 或 【】
    .replace(/（\s*）/g, '________')          // （ ） 或 （）
    .replace(/\{\s*\}/g, '________')         // { } 或 {}
    .replace(/_blank_/gi, '________')        // _blank_ 標記
}

/**
 * 渲染填空題答案嵌入版（答案卷專用）
 * 將答案直接嵌入題目的空白位置，粗體 + 底線
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {string} questionText - 題目文字
 * @param {string|Array} answer - 答案
 * @param {number} xStart - 起始 X 座標
 * @param {number} yPosition - Y 座標
 * @param {number} fontSize - 字體大小
 * @param {number} lineGap - 行間距
 * @param {number} maxWidth - 最大寬度
 * @returns {number} 更新後的 Y 位置
 */
function renderClozeWithInlineAnswer(pdf, questionText, answer, xStart, yPosition, fontSize, lineGap, maxWidth = 160) {
  const answers = Array.isArray(answer) ? answer : [answer]
  let answerIndex = 0

  // 分割題目，找出空白位置
  const blankPattern = /_{3,}|\[\s*\]|\(\s*\)|【\s*】|（\s*）|\{\s*\}|_blank_/gi

  // 構建包含答案的文字片段陣列
  const parts = questionText.split(blankPattern)
  const segments = []

  parts.forEach((part, index) => {
    if (part) {
      segments.push({ text: part, isAnswer: false })
    }
    // 除了最後一個 part 之外，每個 part 後面都有一個空白（已被 split 移除）
    if (index < parts.length - 1) {
      // 當空白數量超過答案數量時，顯示佔位符底線
      const ans = answerIndex < answers.length
        ? String(answers[answerIndex])
        : '____'
      answerIndex++
      segments.push({ text: ans, isAnswer: answerIndex <= answers.length })
    }
  })

  // 計算每行可容納的內容，處理換行
  let currentX = xStart
  let currentY = yPosition
  const lineEndX = xStart + maxWidth

  segments.forEach((segment) => {
    const text = segment.text
    if (!text) return

    // 設定字體
    if (segment.isAnswer) {
      pdf.setFont('times', 'bold')
    } else {
      pdf.setFont('times', 'normal')
    }
    pdf.setFontSize(fontSize)

    // 檢查是否需要換行（簡化處理：按字元逐步渲染）
    const textWidth = pdf.getTextWidth(text)

    if (currentX + textWidth > lineEndX) {
      // 需要處理文字換行
      let remainingText = text
      while (remainingText.length > 0) {
        // 計算這一行還能放多少字元
        let fitChars = 0
        for (let i = 1; i <= remainingText.length; i++) {
          const testText = remainingText.substring(0, i)
          if (currentX + pdf.getTextWidth(testText) > lineEndX) {
            break
          }
          fitChars = i
        }

        if (fitChars === 0) {
          // 需要換行
          currentX = xStart
          currentY += lineGap
          continue
        }

        const linePart = remainingText.substring(0, fitChars)
        remainingText = remainingText.substring(fitChars)

        // 渲染文字
        pdf.text(linePart, currentX, currentY)

        // 如果是答案，加底線
        if (segment.isAnswer) {
          const partWidth = pdf.getTextWidth(linePart)
          pdf.setLineWidth(0.3)
          pdf.line(currentX, currentY + 1, currentX + partWidth, currentY + 1)
        }

        currentX += pdf.getTextWidth(linePart)

        // 如果還有剩餘文字，換行
        if (remainingText.length > 0) {
          currentX = xStart
          currentY += lineGap
        }
      }
    } else {
      // 不需要換行，直接渲染
      pdf.text(text, currentX, currentY)

      // 如果是答案，加底線
      if (segment.isAnswer) {
        pdf.setLineWidth(0.3)
        pdf.line(currentX, currentY + 1, currentX + textWidth, currentY + 1)
      }

      currentX += textWidth
    }
  })

  // 重置字體
  pdf.setFont('times', 'normal')

  return currentY + lineGap
}

/**
 * 渲染配對題到 PDF
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {Object} question - 題目資料
 * @param {number} yPosition - 當前 Y 位置
 * @param {string} questionText - 題目文字
 * @param {number} lineSpacingFactor - 行距因子
 * @returns {number} 更新後的 Y 位置
 */
function renderMatchingQuestion(pdf, question, yPosition, questionText, lineSpacingFactor = 1) {
  const margin = 20
  const leftColX = margin + 10
  const rightColX = margin + 90
  const lineGap = 5 * lineSpacingFactor

  // 題目說明
  const textLines = pdf.splitTextToSize(questionText, 160)
  textLines.forEach((line, lineIndex) => {
    pdf.text(line, margin + 10, yPosition + (lineIndex * lineGap))
  })
  yPosition += textLines.length * lineGap + 5 * lineSpacingFactor

  // 取得配對項目
  const questionData = question.question_data || {}
  let leftItems = questionData.left_items || []
  let rightItems = questionData.right_items || []

  // 如果沒有結構化資料，嘗試從 answer 解析
  const answerText = question.correct_answer || question.answer || ''
  if (leftItems.length === 0 && answerText) {
    // 嘗試解析 JSON 格式
    try {
      const parsed = JSON.parse(answerText)
      if (parsed.left_items && parsed.right_items) {
        leftItems = parsed.left_items
        rightItems = parsed.right_items
      } else if (Array.isArray(parsed)) {
        // 可能是配對陣列格式 [["A", "1"], ["B", "2"]]
        parsed.forEach(pair => {
          if (Array.isArray(pair) && pair.length >= 2) {
            leftItems.push(pair[0])
            rightItems.push(pair[1])
          }
        })
      }
    } catch {
      // 不是 JSON，嘗試文字解析
      // answer 格式可能是 "Item1-Match1, Item2-Match2" 之類的
      const pairs = String(answerText).split(/[,;，；]/).map(p => p.trim()).filter(Boolean)
      const parsedLeft = []
      const parsedRight = []
      pairs.forEach((pair) => {
        // 支援多種分隔符：-, :, =, →, ：
        const parts = pair.split(/[-:=→：]/).map(p => p.trim())
        if (parts.length >= 2) {
          parsedLeft.push(parts[0])
          parsedRight.push(parts[1])
        }
      })
      if (parsedLeft.length > 0) {
        leftItems = parsedLeft
        rightItems = parsedRight
      }
    }
  }

  // 如果仍然沒有數據，顯示提示
  if (leftItems.length === 0) {
    console.warn('Matching question has no items:', question.id, question.content?.substring(0, 50))
  }

  // 繪製左右兩欄標題
  pdf.setFont('times', 'bold')
  pdf.text('Items', leftColX, yPosition)
  pdf.text('Matches', rightColX, yPosition)
  pdf.setFont('times', 'normal')
  yPosition += 6 * lineSpacingFactor

  // 繪製配對項目
  const maxItems = Math.max(leftItems.length, rightItems.length)
  for (let i = 0; i < maxItems; i++) {
    const leftLabel = String.fromCharCode(65 + i) + '.'  // A. B. C.
    const rightLabel = String(i + 1) + '.'              // 1. 2. 3.

    // 左欄
    if (leftItems[i]) {
      pdf.text(`${leftLabel} ${leftItems[i]}`, leftColX, yPosition)
    }

    // 右欄
    if (rightItems[i]) {
      pdf.text(`${rightLabel} ${rightItems[i]}`, rightColX, yPosition)
    }

    yPosition += 6 * lineSpacingFactor
  }

  // 答題區：畫線讓學生寫配對結果
  yPosition += 5 * lineSpacingFactor
  pdf.text('Answers: ', leftColX, yPosition)
  for (let i = 0; i < leftItems.length; i++) {
    const label = String.fromCharCode(65 + i)
    pdf.text(`${label}: ____`, leftColX + 30 + (i * 25), yPosition)
  }
  yPosition += 10 * lineSpacingFactor

  return yPosition
}

/**
 * 渲染排序題到 PDF
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {Object} question - 題目資料
 * @param {number} yPosition - 當前 Y 位置
 * @param {string} questionText - 題目文字
 * @param {number} lineSpacingFactor - 行距因子
 * @returns {number} 更新後的 Y 位置
 */
function renderSequenceQuestion(pdf, question, yPosition, questionText, lineSpacingFactor = 1) {
  const margin = 20
  const lineGap = 5 * lineSpacingFactor

  // 題目說明
  const textLines = pdf.splitTextToSize(questionText, 160)
  textLines.forEach((line, lineIndex) => {
    pdf.text(line, margin + 10, yPosition + (lineIndex * lineGap))
  })
  yPosition += textLines.length * lineGap + 5 * lineSpacingFactor

  // 取得排序項目
  const items = question.items || question.question_data?.items || []

  // 繪製項目（打亂顯示，學生需排序）
  for (let i = 0; i < items.length; i++) {
    const itemLabel = `____ ${String.fromCharCode(65 + i)}. ${items[i]}`
    const itemLines = pdf.splitTextToSize(itemLabel, 150)
    itemLines.forEach((line, lineIndex) => {
      pdf.text(line, margin + 15, yPosition + (lineIndex * lineGap))
    })
    yPosition += itemLines.length * lineGap + 2 * lineSpacingFactor
  }

  yPosition += 5 * lineSpacingFactor

  return yPosition
}

/**
 * 渲染圖片佔位符
 */
function renderImagePlaceholder(pdf, x, y, imageName) {
  pdf.setDrawColor(200, 200, 200)
  pdf.setFillColor(248, 248, 248)
  pdf.rect(x, y, 100, 40, 'FD')

  pdf.setFontSize(9)
  pdf.setTextColor(128, 128, 128)
  const text = `[${imageName}]`
  const textWidth = pdf.getTextWidth(text)
  pdf.text(text, x + (100 - textWidth) / 2, y + 22)
  pdf.setTextColor(0, 0, 0)
  pdf.setFontSize(10)
}

/**
 * 格式化答案文字
 */
function formatAnswerText(answer) {
  if (Array.isArray(answer)) {
    return answer.join(', ')
  }
  if (typeof answer === 'object') {
    return JSON.stringify(answer)
  }
  return String(answer)
}

/**
 * 取得圖片尺寸
 * 使用 fetch + blob URL 方式繞過 CORS 限制
 */
async function getImageDimensions(imageUrl) {
  try {
    const response = await fetch(imageUrl)
    if (!response.ok) {
      return { width: 100, height: 60 }
    }
    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)

    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        URL.revokeObjectURL(blobUrl)
        resolve({ width: img.width, height: img.height })
      }
      img.onerror = () => {
        URL.revokeObjectURL(blobUrl)
        resolve({ width: 100, height: 60 })
      }
      img.src = blobUrl
    })
  } catch {
    return { width: 100, height: 60 }
  }
}

/**
 * 計算適合的圖片尺寸（保持比例）
 */
function calculateFitDimensions(origWidth, origHeight, maxWidth, maxHeight) {
  const ratio = Math.min(maxWidth / origWidth, maxHeight / origHeight)
  return {
    width: origWidth * ratio,
    height: origHeight * ratio
  }
}

/**
 * 依題型分組題目
 */
function groupQuestionsByType(questions) {
  const grouped = {}
  questions.forEach(q => {
    if (!grouped[q.type]) {
      grouped[q.type] = []
    }
    grouped[q.type].push(q)
  })
  return grouped
}

/**
 * 取得區塊標題（使用動態字母，根據實際順序）
 * @param {string} questionType - 題型
 * @param {number} sectionNumber - 區塊編號（1-based）
 * @param {Object} customSettings - 自定義題型設定
 */
function getSectionTitle(questionType, sectionNumber, customSettings = {}) {
  const config = QUESTION_TYPE_MAPPING[questionType] || { name: questionType, points: 0 }
  // 優先使用自定義名稱
  const name = customSettings[questionType]?.name || config.name
  // 使用動態字母（A=1, B=2, C=3...），而非固定字母
  const dynamicLetter = String.fromCharCode(64 + sectionNumber) // 65='A', 所以 64+1='A'
  return `${dynamicLetter}. ${name} _____/${config.points}`
}

/**
 * 取得區塊指導文字
 * @param {string} questionType - 題型
 * @param {Object} customSettings - 自定義題型設定
 */
function getSectionInstruction(questionType, customSettings = {}) {
  // 優先使用自定義說明
  return customSettings[questionType]?.instruction ||
         SECTION_INSTRUCTIONS[questionType] ||
         'Complete the following questions.'
}

/**
 * 匯出圖片題目為 PDF
 * @param {Array} imageQuestions - 圖片題目列表
 * @param {Object} config - 配置選項
 * @param {string} filename - 檔案名稱
 */
export async function exportImageQuestionsToPDF(imageQuestions, config = {}, filename = 'image_exam.pdf') {
  try {
    const { jsPDF } = await import('jspdf')

    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const pageWidth = 210
    const pageHeight = 297
    const margin = 20
    const contentWidth = pageWidth - margin * 2
    let yPosition = margin

    // 頁眉
    if (config.header?.enabled !== false) {
      pdf.setFontSize(16)
      pdf.setFont('times', 'bold')

      const schoolName = config.header?.schoolName || DEFAULT_SCHOOL_NAME
      const title = config.header?.titlePrefix || 'Image Questions'

      const schoolWidth = pdf.getTextWidth(schoolName)
      pdf.text(schoolName, (pageWidth - schoolWidth) / 2, yPosition)
      yPosition += 10

      const titleWidth = pdf.getTextWidth(title)
      pdf.text(title, (pageWidth - titleWidth) / 2, yPosition)
      yPosition += 15
    }

    // 渲染每個圖片題目
    for (let i = 0; i < imageQuestions.length; i++) {
      const question = imageQuestions[i]

      // 檢查是否需要換頁
      if (yPosition > pageHeight - 100) {
        pdf.addPage()
        yPosition = margin
      }

      // 題目編號和描述
      pdf.setFontSize(12)
      pdf.setFont('times', 'bold')
      const questionHeader = `Q${i + 1}. ${question.question_description || ''}`
      pdf.text(questionHeader, margin, yPosition)
      yPosition += 8

      // 元數據（科目、章節、頁碼）
      pdf.setFontSize(9)
      pdf.setFont('times', 'italic')
      const metadata = [
        question.subject,
        question.chapter,
        question.page ? `P.${question.page}` : null
      ].filter(Boolean).join(' | ')
      pdf.text(metadata, margin, yPosition)
      yPosition += 10

      // 圖片佔位符（實際圖片需要從伺服器載入）
      // 在實際應用中，您需要先將圖片轉換為 base64 或使用 addImage
      pdf.setDrawColor(200, 200, 200)
      pdf.setFillColor(248, 248, 248)
      pdf.rect(margin, yPosition, contentWidth, 60, 'FD')

      pdf.setFontSize(10)
      pdf.setFont('times', 'normal')
      pdf.setTextColor(128, 128, 128)
      const imgText = `[${question.question_image_path || question.question_image}]`
      const imgTextWidth = pdf.getTextWidth(imgText)
      pdf.text(imgText, margin + (contentWidth - imgTextWidth) / 2, yPosition + 30)
      pdf.setTextColor(0, 0, 0)

      yPosition += 70

      // 如果有答案圖片
      if (question.answer_image && config.includeAnswerImages !== false) {
        pdf.setFontSize(10)
        pdf.setFont('times', 'bold')
        pdf.text('Answer:', margin, yPosition)
        yPosition += 6

        pdf.setDrawColor(200, 200, 200)
        pdf.setFillColor(248, 248, 248)
        pdf.rect(margin, yPosition, contentWidth, 50, 'FD')

        pdf.setFontSize(10)
        pdf.setFont('times', 'normal')
        pdf.setTextColor(128, 128, 128)
        const ansText = `[${question.answer_image_path || question.answer_image}]`
        const ansTextWidth = pdf.getTextWidth(ansText)
        pdf.text(ansText, margin + (contentWidth - ansTextWidth) / 2, yPosition + 25)
        pdf.setTextColor(0, 0, 0)

        yPosition += 55
      }

      yPosition += 10 // 題目間距
    }

    pdf.save(filename)

    return {
      success: true,
      message: `已匯出 ${imageQuestions.length} 道圖片題目`
    }

  } catch (error) {
    return {
      success: false,
      message: `PDF 匯出失敗: ${error.message}`
    }
  }
}

/**
 * 載入圖片並轉換為 base64（用於 PDF 嵌入）
 * 使用 fetch + blob URL 方式繞過 CORS 限制
 * @param {string} imageUrl - 圖片 URL
 * @returns {Promise<string|null>} base64 編碼的圖片或 null
 */
export async function loadImageAsBase64(imageUrl) {
  // 檢查快取
  if (imageCache.has(imageUrl)) {
    return imageCache.get(imageUrl)
  }

  try {
    // 1. 使用 fetch 獲取圖片 blob（通過 Vite 代理或同源請求）
    const response = await fetch(imageUrl)
    if (!response.ok) {
      console.error('[PDF Export] Failed to fetch image:', imageUrl, response.status)
      return null
    }
    const blob = await response.blob()

    // 2. 創建本地 blob URL（同源，不會有 CORS 問題）
    const blobUrl = URL.createObjectURL(blob)

    // 3. 使用 Image 元素載入 blob URL
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0)

        // 釋放 blob URL
        URL.revokeObjectURL(blobUrl)

        try {
          const base64 = canvas.toDataURL('image/jpeg', 0.8)
          imageCache.set(imageUrl, base64)
          resolve(base64)
        } catch (e) {
          console.error('[PDF Export] Failed to convert image to base64:', e)
          resolve(null)
        }
      }
      img.onerror = () => {
        URL.revokeObjectURL(blobUrl)
        console.error('[PDF Export] Failed to load blob image:', imageUrl)
        resolve(null)
      }
      img.src = blobUrl
    })
  } catch (error) {
    console.error('[PDF Export] Failed to fetch image:', imageUrl, error)
    return null
  }
}

/**
 * 匯出為 Word 格式 (未來實作)
 */
export async function exportToWord(examData, filename = 'exam.docx') {
  // TODO: 實作 Word 匯出
  return {
    success: false,
    message: 'Word 匯出功能尚未實作'
  }
}

/**
 * 匯出為純文字格式
 */
export function exportToText(examData, filename = 'exam.txt') {
  try {
    let content = ''
    
    // 頁眉
    if (examData.config.header?.enabled !== false) {
      const schoolName = examData.config.header?.schoolName || 'School Name'
      const title = examData.config.header?.titlePrefix || 'Examination'
      const duration = examData.config.header?.duration || '90 minutes'
      const totalScore = examData.config.header?.totalScore || '100 points'
      
      content += `${schoolName}\n`
      content += `${title}\n`
      content += `${'='.repeat(50)}\n`
      content += `Time: ${duration}    Total: ${totalScore}    Date: ___________\n\n`
    }
    
    // 學生資訊
    if (examData.config.studentInfo?.enabled !== false) {
      const fields = examData.config.studentInfo?.fields || ['Class', 'Number', 'Name', 'Score']
      const fieldTexts = fields.map(field => {
        const fieldName = typeof field === 'string' ? field : field.label
        return `${fieldName}: ________________`
      })
      content += fieldTexts.join('    ') + '\n\n'
    }
    
    // 題目內容
    const orderedTypes = examData.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
    const questionsByType = groupQuestionsByType(examData.questions)
    
    let sectionNumber = 1
    for (const questionType of orderedTypes) {
      const questions = questionsByType[questionType]
      if (!questions || questions.length === 0) continue
      
      // 區塊標題
      const sectionTitle = getSectionTitle(questionType, sectionNumber)
      content += `${sectionTitle}\n`
      content += `${'-'.repeat(40)}\n`
      
      // 題目
      questions.forEach((question, index) => {
        const questionNumber = `${index + 1}.`
        const questionText = question.content || question.prompt || 'Question text'
        
        content += `${questionNumber} ${questionText}\n`
        
        // 根據題型添加特定格式
        if (questionType === 'single_choice' && question.options) {
          question.options.forEach((option, optIndex) => {
            // 統一使用小寫字母標籤，移除原有標籤（如有）
            const optionLabel = String.fromCharCode(97 + optIndex)  // a, b, c, d
            const optionContent = option.toString().trim().replace(/^[a-zA-Z][.\)\]]\s*/, '')
            content += `   ${optionLabel}. ${optionContent}\n`
          })
        } else if (questionType === 'short_answer') {
          content += '   Answer:\n'
          content += '   ________________________________\n'
          content += '   ________________________________\n'
          content += '   ________________________________\n'
        } else if (questionType === 'true_false') {
          content += '   T / F\n'
        }
        
        content += '\n'
      })
      
      sectionNumber++
      content += '\n'
    }
    
    // 下載文字檔
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
    
    return {
      success: true,
      message: '文字檔匯出成功'
    }
    
  } catch (error) {
    return {
      success: false,
      message: `文字檔匯出失敗: ${error.message}`
    }
  }
}