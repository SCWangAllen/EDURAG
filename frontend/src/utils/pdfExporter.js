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
import { SCHOOL_CREST_DATA_URL, SCHOOL_CREST_ASPECT } from '../assets/schoolCrest.js'
import { gradeLabel } from '../constants/grades.js'

// 版面基準(mm),依學校樣張:
//   15  左邊界:大題字母「A.」、作答底線起點
//   23  大題名稱首字;指示句、每一題的題號都對齊這裡(底線在左邊 15~22)
const SECTION_NAME_X = 23
const NUMBER_BLANK_X = 15
const BLANK_SHORT = SECTION_NAME_X - NUMBER_BLANK_X - 1   // 7:題號前底線 15~22(約 3 底線)
const NUMBER_X = SECTION_NAME_X                           // 題號與大題名稱首字對齊
// 全域圖片大小(小 / 中 / 大)對應的最大高度 mm;控制面板顯示「目前尺寸」時也用同一張表
export const IMAGE_SIZE_MM = { small: 80, medium: 120, large: 180 }
// 內容可用的垂直範圍:20mm 起、286mm 止(頁碼基線在 290mm、字頂約 287.5mm,只留 1.5mm 不相碰)
const PAGE_TOP = 20
const PAGE_BOTTOM = 286

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
  const mixMode = examData.config?.weeklyTestMixMode || 'separate'

  // 頁眉
  if (examData.config.header?.enabled !== false) {
    let title = examData.config.header?.titlePrefix || DEFAULT_EXAM_TITLE
    const schoolName = examData.config.header?.schoolName || DEFAULT_SCHOOL_NAME
    let subtitle = examData.config.header?.subtitle || DEFAULT_EXAM_SUBTITLE
    const pageWidth = 210 // A4 寬度

    // Weekly Test 模式：自動生成標題
    if (isWeeklyTest && subjects.length > 0) {
      const grade = examData.config?.grade || ''
      title = `${gradeLabel(grade)} Review Test`
      subtitle = subjects.join(', ')
    }

    // 校徽浮水印：半透明、置中於標題區後方（先畫，文字才會疊在上面）。config.watermark.enabled = false 可關閉
    const watermark = examData.config?.watermark || {}
    if (watermark.enabled !== false) {
      const wmWidth = watermark.width || 34
      const wmHeight = wmWidth * SCHOOL_CREST_ASPECT
      try {
        pdf.saveGraphicsState()
        pdf.setGState(new pdf.GState({ opacity: watermark.opacity ?? 0.12 }))
        pdf.addImage(watermark.dataUrl || SCHOOL_CREST_DATA_URL, 'PNG', (pageWidth - wmWidth) / 2, watermark.y ?? 10, wmWidth, wmHeight)
        pdf.restoreGraphicsState()
      } catch (e) {
        console.warn('Watermark skipped:', e?.message)
      }
    }

    // 左上角家長簽名框
    if (!isAnswerSheet && examData.config?.parentSignature?.enabled) {
      const sigStyle = elements.parentSignature || { fontSize: 10, fontWeight: 'bold' }
      pdf.setFontSize(sigStyle.fontSize)
      pdf.setFont('times', sigStyle.fontWeight === 'bold' ? 'bold' : 'normal')
      const sigLabel = examData.config.parentSignature?.label || 'Parent Signature'
      // 樣張：簽名框在上、標籤在框下方
      pdf.setDrawColor(0, 0, 0)
      pdf.rect(15, yPosition - 4, 32, 12)  // x, y, width, height
      pdf.text(sigLabel, 15, yPosition + 12)
    }

    // 學校名稱 - 使用元素設定（支援新舊 key 名稱）
    const schoolNameStyle = elements.school || elements.schoolName || { fontSize: 16, fontWeight: 'bold' }
    pdf.setFontSize(schoolNameStyle.fontSize)
    pdf.setFont('times', schoolNameStyle.fontWeight === 'bold' ? 'bold' : 'normal')
    const schoolWidth = pdf.getTextWidth(schoolName)
    pdf.text(schoolName, (pageWidth - schoolWidth) / 2, yPosition)
    yPosition += 7

    // 考試標題(年份學期年級科目:粗體 14 置中,依 elements.subject)
    const titleStyle = elements.subject || { fontSize: 14, fontWeight: 'bold' }
    pdf.setFontSize(titleStyle.fontSize)
    pdf.setFont('times', titleStyle.fontWeight === 'bold' ? 'bold' : 'normal')
    const titleWidth = pdf.getTextWidth(title)
    pdf.text(title, (pageWidth - titleWidth) / 2, yPosition)
    yPosition += 6

    // 副標題/範圍 - 使用元素設定（支援新舊 key 名稱）
    const scopeStyle = elements.range || elements.examScope || { fontSize: 10, fontWeight: 'normal' }
    pdf.setFontSize(scopeStyle.fontSize)
    pdf.setFont('times', scopeStyle.fontWeight === 'bold' ? 'bold' : 'normal')
    const subtitleWidth = pdf.getTextWidth(subtitle)
    pdf.text(subtitle, (pageWidth - subtitleWidth) / 2, yPosition)
    yPosition += 8

    // 答案卷:範圍下方獨立一行「Answer Key」粗體 16 置中(答案卷不印家長簽名與學生資訊)
    if (isAnswerSheet) {
      pdf.setFontSize(schoolNameStyle.fontSize)
      pdf.setFont('times', 'bold')
      const keyLabel = 'Answer Key'
      pdf.text(keyLabel, (pageWidth - pdf.getTextWidth(keyLabel)) / 2, yPosition)
      yPosition += 8
    } else {
      yPosition += 2
    }
  }

  // 學生資訊區 - 兩行佈局
  if (!isAnswerSheet && examData.config?.studentInfo?.enabled) {
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
      pdf.text(`${fieldLabel}: _______________`, xPosition, yPosition)  // 15 底線
      xPosition += topFieldWidth
    })
    yPosition += 7

    // 第二行：Grade（置中）
    const gradeLabel = typeof bottomField === 'string' ? bottomField : bottomField.label
    const gradeText = `${gradeLabel}: _______________`  // 15 底線
    const gradeWidth = pdf.getTextWidth(gradeText)
    pdf.text(gradeText, (pageWidth - gradeWidth) / 2, yPosition)
    yPosition += 14  // 與第一大題拉開一點距離
  }

  // 題目內容
  const orderedTypes = examData.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching', 'sequence', 'diagram_question']
  // 取得自定義題型設定
  const questionTypeSettings = examData.config?.questionTypeSettings || {}

  // Weekly Test 模式
  if (isWeeklyTest && subjects.length > 0) {
    if (mixMode === 'mixed') {
      // 混合模式：按題型分節，各科題目混在同一題型區塊內，標註科目來源
      const questionsByType = groupQuestionsByType(examData.questions)
      let sectionNumber = 1

      for (const questionType of orderedTypes) {
        const questions = questionsByType[questionType]
        if (!questions || questions.length === 0) continue

        yPosition = await renderQuestionSection(
          pdf, questions, questionType, sectionNumber,
          yPosition, elements, questionTypeSettings,
          lineSpacingFactor, isAnswerSheet, examData.config, maxImageHeight,
          { showSubjectLabel: true }
        )
        sectionNumber++
      }
    } else {
      // 分區模式：按科目分節，每節內再按題型排列
      for (const subject of subjects) {
        if (yPosition > 250) {
          pdf.addPage()
          yPosition = 20
        }

        // 科目區塊標題（含底線分隔）
        pdf.setFontSize(14)
        pdf.setFont('times', 'bold')
        const subjectQuestions = examData.questions.filter(q => q.subject === subject)
        const subjectHeader = `--- ${subject} Section (${subjectQuestions.length} questions) ---`
        const headerWidth = pdf.getTextWidth(subjectHeader)
        pdf.text(subjectHeader, (210 - headerWidth) / 2, yPosition)
        yPosition += 8 * lineSpacingFactor

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

        yPosition += 10 * lineSpacingFactor
      }
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

  // 頁尾頁碼「-1-」置中
  const pageCount = pdf.internal.getNumberOfPages()
  pdf.setFont('times', 'normal')
  pdf.setFontSize(10)
  for (let p = 1; p <= pageCount; p++) {
    pdf.setPage(p)
    const label = `-${p}-`
    pdf.text(label, (210 - pdf.getTextWidth(label)) / 2, 290)
  }

  return pdf
}

/**
 * 渲染題目區塊（提取為獨立函數以支援多科目模式）
 */
async function renderQuestionSection(
  pdf, questions, questionType, sectionNumber,
  yPosition, elements, questionTypeSettings,
  lineSpacingFactor, isAnswerSheet, config, maxImageHeight,
  options = {}
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
  // 配合題以「配對項目數」計分（2 pts each → 9 項 = 18 分），其他題型以題數計
  const scoredUnits = questionType === 'matching'
    ? questions.reduce((n, q) => n + (getMatchingItems(q).rightItems.length || 1), 0)
    : questions.length
  const sectionTitle = getSectionTitle(questionType, sectionNumber, questionTypeSettings, scoredUnits)
  // 樣張:「A.」靠左,名稱從 SECTION_NAME_X 起;下方指示句對齊名稱第一個字
  const dot = sectionTitle.indexOf('. ')
  if (dot > 0) {
    pdf.text(sectionTitle.slice(0, dot + 1), 15, yPosition)
    pdf.text(sectionTitle.slice(dot + 2), SECTION_NAME_X, yPosition)
  } else {
    pdf.text(sectionTitle, 15, yPosition)
  }
  yPosition += 5 * lineSpacingFactor

  // 添加指導文字（使用元素級別設定，支援新舊 key 名稱）
  const instructionStyle = elements.instructions || elements.sectionInstruction || { fontSize: 12, fontWeight: 'bold' }
  pdf.setFontSize(instructionStyle.fontSize)
  // 題目指示:粗體(不用斜體,依樣張規格)
  pdf.setFont('times', instructionStyle.fontWeight === 'bold' ? 'bold' : 'normal')
  const instruction = getSectionInstruction(questionType, questionTypeSettings)
  pdf.text(instruction, SECTION_NAME_X, yPosition)
  yPosition += 6 * lineSpacingFactor

  // 題目內容字體（使用元素級別設定）
  const questionStyle = elements.questionContent || { fontSize: 12, fontWeight: 'normal' }
  pdf.setFont('times', questionStyle.fontWeight === 'bold' ? 'bold' : 'normal')
  pdf.setFontSize(questionStyle.fontSize)

  const showSubjectLabel = options.showSubjectLabel === true
  // 題號寬度以本大題最寬的題號(最後一題)為準,整大題題目文字同一起點;
  // 否則第 10 題起題號變寬,題目與選項會整體右移
  const maxNumWidth = pdf.getTextWidth(`${questions.length}.`)

  // 題目
  for (let index = 0; index < questions.length; index++) {
    const question = sanitizeQuestionForPdf(questions[index])
    const questionNumber = `${index + 1}.`
    let questionText = question.content || question.prompt || 'Question text'

    // 混合模式：在題目文字後附加科目標註
    if (showSubjectLabel && question.subject) {
      questionText = `${questionText}  [${question.subject}]`
    }

    // 填空題：處理空白符號，統一轉換為 ________
    if (questionType === 'cloze') {
      questionText = prepareClozeText(questionText, question.correct_answer || question.answer).text
    } else {
      // 其他題型題目內的空格統一為 5 底線(樣張規格)
      questionText = questionText.replace(/_{3,}/g, '_____')
    }

    // 先估這一題要多高,放不下就整題換頁(避免題目或圖片壓到頁尾頁碼)
    // 圖片題的圖片高度在 renderImageQuestion 內載圖後精確判斷
    const estimatedHeight = questionType === 'diagram_question'
      ? await measureImageQuestionHeight(pdf, question, questionText, maxImageHeight, lineSpacingFactor, config?.imageOverrides?.[question.id])
      : estimateQuestionHeight(pdf, question, questionType, questionText, 4 * lineSpacingFactor, lineSpacingFactor, { isAnswerSheet })
    if (yPosition > PAGE_TOP && yPosition + estimatedHeight > PAGE_BOTTOM) {
      pdf.addPage()
      yPosition = PAGE_TOP
    }

    // 計算行間距（基於配置的行距）
    const lineGap = 4 * lineSpacingFactor

    // 計算題號寬度，讓題目文字緊跟在題號後面
    let questionNumberEndX = 15
    const questionNumWidth = maxNumWidth

    // 是非題、選擇題：答案寫在題號前（題目卷畫底線；答案卷在同一位置印答案）
    if (questionType === 'true_false' || questionType === 'single_choice') {
      if (isAnswerSheet) {
        // 答案卷：答案印在 15~22 的底線上(見 renderAnswerSheetQuestion),題號接在後面
        pdf.text(questionNumber, NUMBER_X, yPosition)
        questionNumberEndX = NUMBER_X + questionNumWidth + 1
      } else {
        // 題目卷：底線 15~22 + 題號（對齊大題名稱首字）+ 題目
        drawAnswerBlank(pdf, NUMBER_BLANK_X, yPosition, BLANK_SHORT)
        pdf.text(questionNumber, NUMBER_X, yPosition)
        questionNumberEndX = NUMBER_X + questionNumWidth + 1
      }
    } else {
      // 其他題型：題號靠左（與「A.」齊），題號後的題目文字對齊大題名稱與指示句（23mm）
      pdf.text(questionNumber, NUMBER_BLANK_X, yPosition)
      questionNumberEndX = Math.max(SECTION_NAME_X, NUMBER_BLANK_X + questionNumWidth + 1)
    }

    // 答案卷模式：簡潔顯示題號和答案
    if (isAnswerSheet) {
      yPosition = await renderAnswerSheetQuestion(pdf, question, questionType, yPosition, config, lineSpacingFactor, questionStyle, questionNumberEndX)
      // 重置字體設定（renderAnswerSheetQuestion 會改變字體）
      pdf.setFont('times', questionStyle.fontWeight === 'bold' ? 'bold' : 'normal')
      pdf.setFontSize(questionStyle.fontSize)
    } else {
      // 試題卷模式：完整題目內容
      if (questionType === 'diagram_question') {
        // 記下這張圖在第幾頁、離頁頂多少 mm，預覽可以跳到它的位置
        pdf.__imagePositions = pdf.__imagePositions || {}
        pdf.__imagePositions[question.id] = { page: pdf.internal.getCurrentPageInfo().pageNumber, y: yPosition }
        // 圖片題目渲染（傳入圖片大小配置）
        yPosition = await renderImageQuestion(
          pdf, question, yPosition, questionText, maxImageHeight, lineSpacingFactor,
          config?.imageOverrides?.[question.id]
        )
      } else if (questionType === 'matching') {
        // 配對題渲染
        yPosition = renderMatchingQuestion(pdf, question, yPosition, questionText, lineSpacingFactor, { textStartX: questionNumberEndX })
      } else if (questionType === 'sequence') {
        // 排序題渲染
        yPosition = renderSequenceQuestion(pdf, question, yPosition, questionText, lineSpacingFactor, questionNumberEndX)
      } else {
        // 處理長文本換行
        // 題目文字緊跟在題號後面
        const textStartX = questionNumberEndX
        const textMaxWidth = 195 - textStartX  // 右邊界固定在 195
        const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
        textLines.forEach((line, lineIndex) => {
          // 每一行都對齊題目第一個字（懸掛縮排）
          pdf.text(line, textStartX, yPosition + (lineIndex * lineGap))
        })

        yPosition += textLines.length * lineGap + 1.5 * lineSpacingFactor

        // 根據題型添加特定格式
        if (questionType === 'single_choice' && question.options) {
          // 選項與題目第一個字對齊;一列四欄放得下就一列,否則兩欄,再不行直排
          yPosition = renderChoiceOptions(pdf, question.options, questionNumberEndX, yPosition, lineGap, lineSpacingFactor)
        } else if (questionType === 'short_answer') {
          // 簡答題答題線：起點對齊題目第一個字，行距 8mm 留手寫空間
          const answerLineGap = 8 * lineSpacingFactor
          for (let i = 0; i < 2; i++) {
            const lineY = yPosition + 3 + i * answerLineGap
            pdf.line(textStartX, lineY, 195, lineY)
          }
          yPosition += 3 + 2 * answerLineGap
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
    return { success: true, blobUrl, imagePositions: pdf.__imagePositions || {} }
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
async function renderImageQuestion(pdf, question, yPosition, questionText, maxImageHeight = 120, lineSpacingFactor = 1, override = null) {
  const margin = 20
  const contentWidth = 170
  const lineGap = 5 * lineSpacingFactor
  const textX = SECTION_NAME_X  // 題目文字與圖片對齊大題名稱首字

  // 先量:題目文字幾行、圖片多高,整題放不下就換頁,文字與圖片才不會被拆開或壓到頁碼
  const hasText = questionText && questionText !== '圖片題'
  const textLines = hasText ? pdf.splitTextToSize(questionText, 195 - textX) : []
  const textHeight = hasText ? textLines.length * lineGap + 2 * lineSpacingFactor : 0

  const questionImageUrl = question.question_image_url || question.question_image_path
  let imageBase64 = null
  let width = 0
  let height = 0
  if (questionImageUrl) {
    try {
      imageBase64 = await loadImageAsBase64(questionImageUrl)
      if (imageBase64) {
        // 圖片尺寸：有逐題覆寫（config.imageOverrides[id]）就用覆寫，否則依全域最大高度等比縮放
        // （與控制面板顯示的「目前尺寸」用同一個函式，數字一致）
        const imgDimensions = await getImageDimensions(questionImageUrl)
        ;({ width, height } = getEffectiveImageSize(imgDimensions, override, maxImageHeight)
          || { width: 195 - textX, height: maxImageHeight })
        // 比一整頁還高的圖,等比縮到一頁放得下
        const maxFit = PAGE_BOTTOM - PAGE_TOP - textHeight - 3 * lineSpacingFactor
        if (height > maxFit) {
          width = width * (maxFit / height)
          height = maxFit
        }
      }
    } catch (error) {
      imageBase64 = null
    }
  }
  // 換頁由呼叫端在畫題號前依 measureImageQuestionHeight 決定,這裡不再換頁(否則題號會留在上一頁)

  // 題目描述
  if (hasText) {
    textLines.forEach((line, lineIndex) => {
      pdf.text(line, textX, yPosition + (lineIndex * lineGap))
    })
    yPosition += textHeight
  }

  // 嵌入問題圖片（支持 _url 和 _path 兩種屬性）
  if (questionImageUrl) {
    try {
      if (imageBase64) {
        pdf.addImage(imageBase64, 'JPEG', textX, yPosition, width, height)
        yPosition += height + 3 * lineSpacingFactor
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

  // 圖片本身已含作答處，不再畫下方答題線;間距已含在圖後 3mm 內
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
  if (questionType !== 'diagram_question') {
    const answer = question.correct_answer || question.answer || 'N/A'
    let questionText = question.content || question.prompt || ''
    if (questionType !== 'cloze') {
      // 與學生卷一致：題目內的空格統一為 5 底線
      questionText = questionText.replace(/_{3,}/g, '_____')
    }
    let clozeAnswers = answer
    if (questionType === 'cloze') {
      const prepared = prepareClozeText(questionText, answer)
      questionText = prepared.text
      clozeAnswers = prepared.answers
    }

    // 填空題特殊處理：答案直接嵌入空白位置（粗體+底線）
    if (questionType === 'cloze') {
      yPosition = renderClozeWithInlineAnswer(
        pdf, questionText, clozeAnswers, textStartX, yPosition, fontSize, lineGap, textMaxWidth
      )
      yPosition += 1 * lineSpacingFactor
      return yPosition
    }

    // 配合題：與學生卷同版面，正確詞語粗體加底線印在左欄底線上
    if (questionType === 'matching') {
      pdf.setFont('times', 'normal')
      pdf.setFontSize(fontSize)
      return renderMatchingQuestion(pdf, question, yPosition, questionText, lineSpacingFactor, { textStartX, showAnswers: true })
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
      const ansX = 15 + (BLANK_SHORT - ansWidth) / 2  // 置中於底線區域
      pdf.text(tfAnswer, ansX, yPosition)
      pdf.setLineWidth(0.3)
      pdf.line(15, yPosition + 1, 15 + BLANK_SHORT, yPosition + 1)

      // 題目內容（緊跟在題號後面）
      pdf.setFont('times', 'normal')
      pdf.setFontSize(fontSize)
      const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
      textLines.forEach((line, lineIndex) => {
        // 第一行緊跟題號，後續行從固定位置開始
        const xPos = textStartX  // 每一行都對齊題目第一個字
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
      const ansX = 15 + (BLANK_SHORT - ansWidth) / 2  // 置中於底線區域
      pdf.text(answerLetter, ansX, yPosition)
      pdf.setLineWidth(0.3)
      pdf.line(15, yPosition + 1, 15 + BLANK_SHORT, yPosition + 1)

      // 題目內容（緊跟在題號後面）
      pdf.setFont('times', 'normal')
      pdf.setFontSize(fontSize)
      const textLines = pdf.splitTextToSize(questionText, textMaxWidth)
      textLines.forEach((line, lineIndex) => {
        const xPos = textStartX  // 每一行都對齊題目第一個字
        pdf.text(line, xPos, yPosition + lineIndex * lineGap)
      })
      yPosition += textLines.length * lineGap + 1 * lineSpacingFactor

      // 顯示選項
      if (question.options && Array.isArray(question.options)) {
        yPosition = renderChoiceOptions(pdf, question.options, textStartX, yPosition, lineGap, lineSpacingFactor)
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
        const xPos = textStartX  // 每一行都對齊題目第一個字
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

    if (questionType === 'short_answer') {
      // 簡答題答案卷：答案粗體加底線、對齊題目第一個字，不加「Answer:」
      const answerLines = pdf.splitTextToSize(formatAnswerText(answer), 195 - textStartX)
      const answerGap = lineGap + 1.5
      answerLines.forEach((line, lineIndex) => {
        const y = yPosition + lineIndex * answerGap
        pdf.text(line, textStartX, y)
        pdf.line(textStartX, y + 1, textStartX + pdf.getTextWidth(line), y + 1)
      })
      pdf.setFont('times', 'normal')
      yPosition += answerLines.length * answerGap + 2 * lineSpacingFactor
    } else {
      // 其他題型：長答案換行處理（配合題已在前面提早回傳）
      const answerText = `Answer: ${formatAnswerText(answer)}`
      const answerLines = pdf.splitTextToSize(answerText, 195 - textStartX)
      answerLines.forEach((line, lineIndex) => {
        pdf.text(line, textStartX, yPosition + lineIndex * lineGap)
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
      const xPos = textStartX  // 每一行都對齊題目第一個字
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
        const maxWidth = 120
        const maxHeight = 60
        const imgDimensions = await getImageDimensions(answerImageUrl)
        const { width, height } = calculateFitDimensions(imgDimensions.width, imgDimensions.height, maxWidth, maxHeight)

        // 「Answer:」標題 + 圖片放不下就換頁,不壓到頁碼
        if (yPosition > PAGE_TOP && yPosition + 6 + height + 5 > PAGE_BOTTOM) {
          pdf.addPage()
          yPosition = PAGE_TOP
        }

        pdf.setFont('times', 'bold')
        pdf.text('Answer:', 20, yPosition)
        yPosition += 6

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
const HTML_TAG_RE = /<\/?(?:u|b|i|em|strong|br|p|span|sub|sup|mark|s|del|ins|small|div|font)(?:\s[^<>]*)?\s*\/?>/gi
const HTML_ENTITIES = { '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'" }

/**
 * 去掉題目文字裡的 HTML 標籤(模型偶爾輸出 <u>heart</u>,PDF 會原樣印出)。
 * 遞迴處理字串 / 陣列 / 物件,其他型別原樣回傳。
 */
function stripHtml(value) {
  if (typeof value === 'string') {
    // 先解實體再去標籤:被轉義的 &lt;u&gt; 一樣要清掉
    let text = value
    Object.entries(HTML_ENTITIES).forEach(([k, v]) => { text = text.split(k).join(v) })
    return text.replace(HTML_TAG_RE, '').replace(/[ \t]{2,}/g, ' ').trim()
  }
  if (Array.isArray(value)) return value.map(stripHtml)
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, stripHtml(v)]))
  }
  return value
}

/** 匯出前把題目的文字欄位去 HTML(淺拷貝,不動原資料;圖片 data URL 不含標籤不受影響) */
function sanitizeQuestionForPdf(question) {
  if (!question || typeof question !== 'object') return question
  const out = { ...question }
  ;['content', 'prompt', 'answer', 'correct_answer', 'explanation', 'options', 'items', 'question_data']
    .forEach(key => { if (out[key] !== undefined) out[key] = stripHtml(out[key]) })
  return out
}

/**
 * 填充題題幹一定要有空格:先統一各種寫法,沒有標記時把答案挖成空格,
 * 還是沒有就在句尾補一條(舊資料兜底;新資料由後端 normalize_cloze_prompt 保證)。
 */
/** 答案可能是陣列、JSON 字串陣列('["heart","lungs"]',儲存時 JSON.stringify 過)或單一字串 */
function parseAnswerList(answer) {
  if (Array.isArray(answer)) return answer
  const text = String(answer ?? '').trim()
  if (text.startsWith('[')) {
    try {
      const parsed = JSON.parse(text)
      if (Array.isArray(parsed)) return parsed
    } catch { /* 不是 JSON,當一般字串 */ }
  }
  return [answer]
}

/** 答案的可接受詞形:去頭尾標點與冠詞,加單複數變化(與後端 _answer_variants 一致;太短的變體不收) */
function answerVariants(answer) {
  const raw = String(answer ?? '').trim().replace(/[.,;:!?]+$/, '').replace(/^(?:the|a|an)\s+/i, '').trim()
  const base = raw.replace(/^["'()[\]]+|["'()[\]]+$/g, '').trim()
  if (!base) return []
  const lower = base.toLowerCase()
  const variants = new Set([raw, base, base + 's', base + 'es'])
  if (lower.endsWith('ies')) variants.add(base.slice(0, -3) + 'y')
  if (lower.endsWith('es')) variants.add(base.slice(0, -2))
  if (lower.endsWith('s')) variants.add(base.slice(0, -1))
  if (lower.endsWith('y')) variants.add(base.slice(0, -1) + 'ies')
  return [...variants].filter(v => v === raw || v === base || v.length >= 3).sort((a, b) => b.length - a.length)
}

function answerRegex(answer) {
  const variants = answerVariants(answer)
  if (variants.length === 0) return null
  const alternation = variants.map(v => v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  // 整字比對;用「前一字元」分組取代 lookbehind,舊版 Safari 也能跑
  return new RegExp('(^|[^A-Za-z0-9])(?:' + alternation + ')(?![A-Za-z0-9])', 'i')
}

/**
 * 回傳 { text, answers }:text 保證有空格;answers 為答案卷要印的字
 * (題幹本來沒空格、靠答案挖出來的,印句子裡實際挖掉的那個字,例如 lungs 而不是 lung)
 */
function prepareClozeText(text, answer) {
  let out = normalizeClozeBlank(String(text || ''))
  const answers = parseAnswerList(answer)
  if (out.includes('________')) return { text: out, answers }
  const display = []
  answers.forEach((ans) => {
    const re = answerRegex(ans)
    const match = re ? out.match(re) : null
    if (match) {
      out = out.replace(re, '$1________')
      display.push(match[0].slice(match[1].length))
    } else {
      display.push(ans)
    }
  })
  if (!out.includes('________')) out = out.replace(/\s*[.。]?\s*$/, '') + ' ________.'
  return { text: out, answers: display }
}

// 填充題「空格」的各種寫法(與後端 question_sanitize._ALT_BLANK_RE 一致):
// __ / ＿＿ / [ ] / [blank] / ( ) / (blank) / 【 】 / （ ） / { } / {blank} / <blank> / _blank_
const CLOZE_BLANK_PATTERN = /_{2,}|＿+|\[\s*(?:blank)?\s*\]|\(\s*(?:blank)?\s*\)|【\s*】|（\s*）|\{\s*(?:blank)?\s*\}|<\s*blank\s*>|_blank_/gi

function normalizeClozeBlank(text) {
  return String(text || '').replace(CLOZE_BLANK_PATTERN, '________')
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
  // 找出空白位置(與 normalizeClozeBlank 認得的寫法一致)
  const parts = String(questionText || '').split(CLOZE_BLANK_PATTERN)
  const blankCount = parts.length - 1

  // 多個空格但答案是一個字串("heart, arteries")→ 拆開對應
  let answers = parseAnswerList(answer)
  if (answers.length === 1 && blankCount > 1) {
    const pieces = String(answer ?? '').split(/[,;，；、/]/).map(s => s.trim()).filter(Boolean)
    if (pieces.length === blankCount) answers = pieces
  }

  // 依「單字」切 token(保留空白),答案 token 標記 isAnswer;換行只發生在單字邊界,
  // 不會把 "and days" 切成 "an|d days"
  const tokens = []
  const pushWords = (text, isAnswer) => {
    text.split(/(\s+)/).forEach((t) => {
      if (t) tokens.push({ text: t, isAnswer, space: /^\s+$/.test(t) })
    })
  }
  const displayAnswer = (raw, before) => {
    let text = String(raw ?? '').trim().replace(/[.,;:!?]+$/, '')
    if (/(?:^|[^A-Za-z])(?:the|a|an)\s*$/i.test(before)) text = text.replace(/^(?:the|a|an)\s+/i, '')
    return text
  }
  parts.forEach((part, index) => {
    if (part) pushWords(part, false)
    if (index < blankCount) {
      const hasAnswer = index < answers.length
      pushWords(hasAnswer ? displayAnswer(answers[index], part) : '____', hasAnswer)
    }
  })

  const lineEndX = xStart + maxWidth
  let currentX = xStart
  let currentY = yPosition
  const setFont = (isAnswer) => {
    pdf.setFont('times', isAnswer ? 'bold' : 'normal')
    pdf.setFontSize(fontSize)
  }
  const widthOf = (text, isAnswer) => { setFont(isAnswer); return pdf.getTextWidth(text) }
  const newline = () => { currentX = xStart; currentY += lineGap }
  const draw = (text, isAnswer, width) => {
    setFont(isAnswer)
    if (!/^\s+$/.test(text)) pdf.text(text, currentX, currentY)
    if (isAnswer) {
      pdf.setLineWidth(0.3)
      pdf.line(currentX, currentY + 1, currentX + width, currentY + 1)
    }
    currentX += width
  }

  tokens.forEach((tok, i) => {
    const width = widthOf(tok.text, tok.isAnswer)
    if (tok.space) {
      if (currentX === xStart) return                     // 行首不畫空白
      const next = tokens[i + 1]
      const nextWidth = next && !next.space ? widthOf(next.text, next.isAnswer) : 0
      if (currentX + width + nextWidth > lineEndX) { newline(); return }  // 下一個字放不下就換行
      draw(tok.text, tok.isAnswer, width)
      return
    }
    if (currentX + width > lineEndX && currentX > xStart) newline()
    if (width <= maxWidth) { draw(tok.text, tok.isAnswer, width); return }
    // 單一單字比整行還寬(極少見)才逐字切
    let rest = tok.text
    while (rest.length > 0) {
      let fit = 0
      for (let n = 1; n <= rest.length; n++) {
        if (currentX + widthOf(rest.slice(0, n), tok.isAnswer) > lineEndX) break
        fit = n
      }
      if (fit === 0) {
        if (currentX > xStart) { newline(); continue }
        fit = 1
      }
      const piece = rest.slice(0, fit)
      draw(piece, tok.isAnswer, widthOf(piece, tok.isAnswer))
      rest = rest.slice(fit)
      if (rest.length > 0) newline()
    }
  })

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
// 配合題每一列:短底線(與單選題題號前的底線同長,寫字母)+ 題號 + 說明;右欄字母 + 詞語。
// 列縮排到題幹文字的位置(23mm),與其他題型的選項對齊;底線變短後左右兩欄都比以前寬
const MATCH_BLANK_X = SECTION_NAME_X                               // 左欄底線起點(23mm)
const MATCH_BLANK_W = BLANK_SHORT                                  // 底線長度 = 單選題底線(7mm)
const MATCH_NUMBER_X = MATCH_BLANK_X + MATCH_BLANK_W + 1           // 左欄題號 x
const MATCH_RIGHT_COL_X = 145                                      // 右欄字母 x(右欄 50mm)
const MATCH_DESC_MAX_WIDTH = MATCH_RIGHT_COL_X - MATCH_NUMBER_X - 8  // 左欄說明可用寬度(約 100mm)

/**
 * 配合題每列的排版:說明 / 右欄詞語 / 答案卷底線上的詞語各自換行後的行數與列高。
 * 渲染(renderMatchingQuestion)與換頁高度估算(estimateQuestionHeight)共用,
 * 估算才會和實際列高一致,10 組以上或長說明不會被頁尾截掉。
 */
function layoutMatchingRows(pdf, question, lineGap, lineSpacingFactor, showAnswers) {
  const { leftItems, rightItems } = getMatchingItems(question)
  const answerMap = showAnswers
    ? parseMatchingAnswer(question.correct_answer || question.answer, leftItems, rightItems)
    : null
  const rows = []
  const count = Math.max(leftItems.length, rightItems.length)
  for (let i = 0; i < count; i++) {
    const row = { num: `${i + 1}.`, letter: `${String.fromCharCode(97 + i)}.`, descLines: [], termLines: [], keyLines: [] }
    pdf.setFont('times', 'normal')
    if (i < rightItems.length) {
      row.descX = MATCH_NUMBER_X + pdf.getTextWidth(row.num) + 2
      row.descLines = pdf.splitTextToSize(String(rightItems[i]), MATCH_DESC_MAX_WIDTH)
    }
    if (i < leftItems.length) {
      row.termX = MATCH_RIGHT_COL_X + pdf.getTextWidth(row.letter) + 2
      row.termLines = pdf.splitTextToSize(String(leftItems[i]), 195 - row.termX)
    }
    if (answerMap && answerMap[i] !== undefined && i < rightItems.length) {
      // 答案卷:底線上印對應詞語的字母(與單選題答案卷一致;7mm 底線放不下整個詞)
      row.keyLines = [String.fromCharCode(97 + answerMap[i])]
    }
    const lines = Math.max(1, row.descLines.length, row.termLines.length, row.keyLines.length)
    row.height = lines * lineGap + 1.5 * lineSpacingFactor
    rows.push(row)
  }
  return { leftItems, rightItems, rows }
}

function renderMatchingQuestion(pdf, question, yPosition, questionText, lineSpacingFactor = 1, opts = {}) {
  const lineGap = 5 * lineSpacingFactor
  const textX = opts.textStartX || 30

  // 題目說明（接在題號後）
  const textLines = pdf.splitTextToSize(questionText, 195 - textX)
  textLines.forEach((line, i) => pdf.text(line, textX, yPosition + i * lineGap))
  yPosition += textLines.length * lineGap + 3 * lineSpacingFactor

  const { leftItems, rightItems, rows } = layoutMatchingRows(pdf, question, lineGap, lineSpacingFactor, !!opts.showAnswers)
  if (leftItems.length === 0) {
    console.warn('Matching question has no items:', question.id, question.content?.substring(0, 50))
  }

  // 左欄「短底線 + 題號 + 說明」,右欄「字母 + 詞語」;答案卷把字母印在底線上(同單選題)
  const blankX = MATCH_BLANK_X
  rows.forEach((row, i) => {
    if (i < rightItems.length) {
      if (row.keyLines.length > 0) {
        drawKeyAnswerOnBlank(pdf, row.keyLines[0], blankX, yPosition, MATCH_BLANK_W, 'center')
        pdf.setFont('times', 'normal')
      } else {
        drawAnswerBlank(pdf, blankX, yPosition, MATCH_BLANK_W)
      }
      pdf.text(row.num, MATCH_NUMBER_X, yPosition)
      row.descLines.forEach((line, li) => pdf.text(line, row.descX, yPosition + li * lineGap))
    }
    if (i < leftItems.length) {
      pdf.text(row.letter, MATCH_RIGHT_COL_X, yPosition)
      row.termLines.forEach((line, li) => pdf.text(line, row.termX, yPosition + li * lineGap))
    }
    yPosition += row.height
  })

  return yPosition + 3 * lineSpacingFactor
}

/**
 * 取得配合題的左右欄項目：left_items = 詞語（項目），right_items = 說明。
 * 沒有結構化資料時嘗試從 answer 解析（JSON 或 "A-1, B-2" 文字）。
 */
function getMatchingItems(question) {
  const questionData = question.question_data || {}
  let leftItems = questionData.left_items || []
  let rightItems = questionData.right_items || []

  const answerText = question.correct_answer || question.answer || ''
  if (leftItems.length === 0 && answerText) {
    try {
      const parsed = JSON.parse(answerText)
      if (parsed.left_items && parsed.right_items) {
        leftItems = parsed.left_items
        rightItems = parsed.right_items
      } else if (Array.isArray(parsed)) {
        parsed.forEach(pair => {
          if (Array.isArray(pair) && pair.length >= 2) {
            leftItems.push(pair[0])
            rightItems.push(pair[1])
          }
        })
      }
    } catch {
      const pairs = String(answerText).split(/[,;，；]/).map(p => p.trim()).filter(Boolean)
      const parsedLeft = []
      const parsedRight = []
      pairs.forEach((pair) => {
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
  return { leftItems, rightItems }
}

/**
 * 解析配合題答案為 { 說明索引: 詞語索引 }。
 * 每組「X-Y」第一個代號指 left_items（詞語），第二個指 right_items（說明）；
 * 代號可為數字（1 起算）或字母（A 起算），例如 "A-2, B-3" 或 "1-A, 2-B" 或 "1-1"。
 */
function parseMatchingAnswer(answer, leftItems, rightItems) {
  const leftCount = leftItems.length
  const rightCount = rightItems.length
  let text = ''
  if (answer && typeof answer === 'object' && !Array.isArray(answer)) {
    text = Object.entries(answer).map(([k, v]) => `${k} - ${v}`).join('; ')
  } else if (Array.isArray(answer)) {
    text = answer.map(a => (Array.isArray(a) ? a.join(' - ') : String(a))).join('; ')
  } else {
    text = String(answer || '')
  }
  text = text.trim()
  if (!text || !leftCount || !rightCount) return {}

  // 1) 索引形式 "1-b, 2-c":數字 → 說明(right_items)、字母 → 詞語(left_items);
  //    同型("1-1")時退回第一個 = left、第二個 = right
  const tokenIndex = (tok) => {
    const t = String(tok).trim()
    if (/^\d+$/.test(t)) return { kind: 'num', idx: parseInt(t, 10) - 1 }
    if (/^[A-Za-z]$/.test(t)) return { kind: 'alpha', idx: t.toUpperCase().charCodeAt(0) - 65 }
    return null
  }
  const fromIndexForm = () => {
    const map = {}
    for (const pair of text.split(/[,;，；\n]/)) {
      const parts = pair.trim().split(/\s*[-–—:=→：]\s*/).filter(Boolean)
      if (parts.length !== 2) return {}
      const a = tokenIndex(parts[0])
      const b = tokenIndex(parts[1])
      if (!a || !b) return {}
      let li, ri
      if (a.kind === 'num' && b.kind === 'alpha') { ri = a.idx; li = b.idx }
      else if (a.kind === 'alpha' && b.kind === 'num') { li = a.idx; ri = b.idx }
      else { li = a.idx; ri = b.idx }
      if (li < 0 || li >= leftCount || ri < 0 || ri >= rightCount) return {}
      map[ri] = li
    }
    return map
  }

  // 2) 全文形式 "詞語-說明, 詞語-說明"(舊資料):用項目文字在答案裡的出現位置配對,
  //    左右項目相鄰出現即為一組;較長的項目優先,避免子字串誤判
  const fromText = () => {
    const lowered = text.toLowerCase()
    const found = []
    ;[['L', leftItems], ['R', rightItems]].forEach(([side, items]) => {
      items.forEach((item, idx) => {
        const needle = String(item).trim().toLowerCase()
        if (!needle) return
        let start = lowered.indexOf(needle)
        while (start !== -1) {
          found.push({ start, len: needle.length, side, idx })
          start = lowered.indexOf(needle, start + 1)
        }
      })
    })
    found.sort((x, y) => x.start - y.start || y.len - x.len)
    const map = {}
    let pending = null
    let lastEnd = -1
    for (const f of found) {
      if (f.start < lastEnd) continue
      lastEnd = f.start + f.len
      if (pending && pending.side !== f.side) {
        if (f.side === 'L') map[pending.idx] = f.idx
        else map[f.idx] = pending.idx
        pending = null
      } else {
        pending = f
      }
    }
    return map
  }

  let map = fromIndexForm()
  if (Object.keys(map).length < rightCount) {
    const textMap = fromText()
    if (Object.keys(textMap).length > Object.keys(map).length) map = textMap
  }
  return map
}

/**
 * 答案卷：把答案粗體印在底線上。align='center' 置中於底線寬度並畫整條底線（選擇題字母），
 * align='left' 靠左並只在文字下方畫線（配合題詞語）。
 */
function drawKeyAnswerOnBlank(pdf, text, x, y, width = BLANK_SHORT, align = 'center') {
  pdf.setFont('times', 'bold')
  const w = pdf.getTextWidth(text)
  if (align === 'left') {
    pdf.text(text, x, y)
    pdf.line(x, y + 1, x + w, y + 1)
  } else {
    pdf.text(text, x + Math.max(0, (width - w) / 2), y)
    pdf.line(x, y + 1, x + Math.max(width, w + 1), y + 1)
  }
}

// 選擇題選項排版規則（老師規格）：以最長選項的字元數決定
//   ≤ 10 字 → 一列四欄；11–27 字 → 兩欄兩列；28 字以上 → 一個選項一列
const OPTION_SINGLE_ROW_MAX_CHARS = 10
const OPTION_TWO_COLS_MAX_CHARS = 27

/**
 * 選擇題選項排版：依最長選項字數決定欄數（見上方常數）；
 * 字數符合但實際寬度放不下時（例如全大寫）才降級，避免文字重疊。
 * 選項起點與題目第一個字對齊。回傳排完後的 y。
 */
function renderChoiceOptions(pdf, options, startX, yPosition, lineGap, lineSpacingFactor) {
  const rightEdge = 195
  const contents = options.map(option => option.toString().trim().replace(/^[a-zA-Z][.)\]]\s*/, ''))
  const texts = contents.map((content, i) => `${String.fromCharCode(97 + i)}. ${content}`)
  const longest = Math.max(0, ...contents.map(c => c.length))
  const available = rightEdge - startX
  const widths = texts.map(t => pdf.getTextWidth(t))
  const fitsIn = (cols) => widths.every(w => w <= available / cols - 3)

  let cols = longest <= OPTION_SINGLE_ROW_MAX_CHARS ? 4 : (longest <= OPTION_TWO_COLS_MAX_CHARS ? 2 : 1)
  while (cols > 1 && !fitsIn(cols)) cols = cols === 4 ? 2 : 1

  if (cols === 1) {
    texts.forEach(t => {
      const lines = pdf.splitTextToSize(t, available)
      lines.forEach((line, li) => pdf.text(line, startX, yPosition + li * lineGap))
      yPosition += lines.length * lineGap + 0.5 * lineSpacingFactor
    })
  } else {
    const colWidth = available / cols
    for (let i = 0; i < texts.length; i += cols) {
      texts.slice(i, i + cols).forEach((t, c) => pdf.text(t, startX + c * colWidth, yPosition))
      yPosition += lineGap + 0.5 * lineSpacingFactor
    }
  }
  return yPosition + 1 * lineSpacingFactor
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
function renderSequenceQuestion(pdf, question, yPosition, questionText, lineSpacingFactor = 1, textStartX = 30) {
  const margin = 20
  const lineGap = 5 * lineSpacingFactor

  // 題目說明（第一行緊接題號，換行後續行對齊題目起點）
  const textLines = pdf.splitTextToSize(questionText, 195 - textStartX)
  textLines.forEach((line, lineIndex) => {
    pdf.text(line, textStartX, yPosition + (lineIndex * lineGap))
  })
  yPosition += textLines.length * lineGap + 5 * lineSpacingFactor

  // 取得排序項目
  const items = question.items || question.question_data?.items || []

  // 繪製項目（打亂顯示，學生在每項前的底線填順序）
  for (let i = 0; i < items.length; i++) {
    // 項目前的底線從題幹第一個字的位置開始
    const textX = drawAnswerBlank(pdf, textStartX, yPosition)
    const itemLabel = `${String.fromCharCode(65 + i)}. ${items[i]}`
    const itemLines = pdf.splitTextToSize(itemLabel, 195 - textX)
    itemLines.forEach((line, lineIndex) => {
      pdf.text(line, textX, yPosition + (lineIndex * lineGap))
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
// 圖片原始尺寸快取:量高度與實際渲染各會查一次,避免重複下載
const dimensionCache = new Map()

/**
 * 圖片題整塊(題目文字 + 圖片 + 間距)的高度 mm;載不到圖時以佔位框計。
 * 在畫題號之前呼叫,整塊放不下就先換頁。
 */
async function measureImageQuestionHeight(pdf, question, questionText, maxImageHeight = 120, lineSpacingFactor = 1, override = null) {
  const lineGap = 5 * lineSpacingFactor
  const textX = SECTION_NAME_X
  const hasText = questionText && questionText !== '圖片題'
  // 間距刻意縮小(文字→圖 2mm、圖後 3mm),兩張「中」圖(120mm)才能同頁
  const textHeight = hasText ? pdf.splitTextToSize(questionText, 195 - textX).length * lineGap + 2 * lineSpacingFactor : 0
  const url = question.question_image_url || question.question_image_path
  let imageBlock = 45 * lineSpacingFactor
  if (url) {
    try {
      const dims = await getImageDimensions(url)
      const size = getEffectiveImageSize(dims, override, maxImageHeight)
      if (size) {
        const maxFit = PAGE_BOTTOM - PAGE_TOP - textHeight - 3 * lineSpacingFactor
        imageBlock = Math.min(size.height, maxFit) + 3 * lineSpacingFactor
      }
    } catch {
      // 保持佔位框高度
    }
  }
  return textHeight + imageBlock
}

async function getImageDimensions(imageUrl) {
  if (dimensionCache.has(imageUrl)) return dimensionCache.get(imageUrl)
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
        const dims = { width: img.width, height: img.height }
        dimensionCache.set(imageUrl, dims)
        resolve(dims)
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
/**
 * 學生卷作答底線:用畫線而非底線字元。
 * 底線字元會沉到基線下方,和題號高低不齊;畫在基線下 1mm 與答案卷的答案底線同深度。
 * 回傳底線右側加間距後的 x,供接續的文字使用。
 */
function drawAnswerBlank(pdf, x, y, width = BLANK_SHORT, gap = 2) {
  pdf.line(x, y + 1, x + width, y + 1)
  return x + width + gap
}

/**
 * 逐題圖片尺寸覆寫（mm）。只填寬或只填高時依原圖比例算另一邊；兩者都填就照填的畫。
 * 超過頁面可用範圍時等比縮回。
 */
export function applyImageOverride(dims, override, maxWidth = 172, maxHeight = 240) {
  const aspect = dims && dims.width > 0 ? dims.height / dims.width : 1
  let width = Number(override?.width) || 0
  let height = Number(override?.height) || 0
  if (width > 0 && height <= 0) height = width * aspect
  else if (height > 0 && width <= 0) width = height / aspect
  if (width <= 0 || height <= 0) return { width: 0, height: 0 }
  if (width > maxWidth) { height *= maxWidth / width; width = maxWidth }
  if (height > maxHeight) { width *= maxHeight / height; height = maxHeight }
  return { width, height }
}

/**
 * 圖片實際印出的尺寸（mm）：有覆寫用覆寫，否則依全域最大高度等比縮放到頁面可用寬度內。
 * 匯出與控制面板的「目前尺寸」都用這個函式。dims 無效時回傳 null。
 */
export function getEffectiveImageSize(dims, override, maxHeight = 120) {
  if (!dims || !(dims.width > 0) || !(dims.height > 0)) return null
  const maxWidth = 195 - SECTION_NAME_X
  if (override && (override.width > 0 || override.height > 0)) {
    return applyImageOverride(dims, override, maxWidth, 240)
  }
  return calculateFitDimensions(dims.width, dims.height, maxWidth, maxHeight)
}

/**
 * 估算一題在學生卷上的高度(mm),用來決定要不要整題換頁。
 * 圖片題只估文字部分(圖片高度在 renderImageQuestion 內載圖後精確判斷)。
 */
function estimateQuestionHeight(pdf, question, questionType, questionText, lineGap, lineSpacingFactor, opts = {}) {
  const textLines = pdf.splitTextToSize(String(questionText || ''), 195 - (NUMBER_X + 6)).length
  let h = textLines * lineGap + 1.5 * lineSpacingFactor
  switch (questionType) {
    case 'single_choice': {
      const opts = Array.isArray(question.options) ? question.options : []
      const longest = Math.max(0, ...opts.map(o => String(o).replace(/^[a-zA-Z][.)\]]\s*/, '').length))
      const cols = longest <= OPTION_SINGLE_ROW_MAX_CHARS ? 4 : (longest <= OPTION_TWO_COLS_MAX_CHARS ? 2 : 1)
      h += Math.ceil(opts.length / cols) * (lineGap + 0.5 * lineSpacingFactor) + 1 * lineSpacingFactor
      break
    }
    case 'short_answer':
      h += 3 + 2 * 8 * lineSpacingFactor
      break
    case 'matching': {
      // 與 renderMatchingQuestion 同一套排版:題幹行距 5、每列依換行後行數計
      const matchGap = 5 * lineSpacingFactor
      const { rows } = layoutMatchingRows(pdf, question, matchGap, lineSpacingFactor, !!opts.isAnswerSheet)
      h = textLines * matchGap + 3 * lineSpacingFactor
        + rows.reduce((sum, row) => sum + row.height, 0) + 3 * lineSpacingFactor
      break
    }
    case 'sequence': {
      const items = question.items || question.question_data?.items || []
      h += 5 * lineSpacingFactor + items.length * 7 * lineSpacingFactor + 5 * lineSpacingFactor
      break
    }
    case 'diagram_question':
      h += 30
      break
    default:
      h += 4 * lineSpacingFactor
  }
  return h
}

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
function getSectionTitle(questionType, sectionNumber, customSettings = {}, questionCount = 0) {
  const config = QUESTION_TYPE_MAPPING[questionType] || { name: questionType, points: 0 }
  // 優先使用自定義名稱
  const name = customSettings[questionType]?.name || config.name
  // 使用動態字母（A=1, B=2, C=3...），而非固定字母
  const dynamicLetter = String.fromCharCode(64 + sectionNumber) // 65='A', 所以 64+1='A'
  // 有「每題分數」設定時:A. Matching (2 pts each) _____/18,總分 = 每題分數 × 題數
  const perQuestion = Number(customSettings[questionType]?.points)
  if (perQuestion > 0 && questionCount > 0) {
    const unit = perQuestion === 1 ? 'pt' : 'pts'
    return `${dynamicLetter}. ${name} (${perQuestion} ${unit} each) _____/${perQuestion * questionCount}`
  }
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
      const fields = examData.config.studentInfo?.fields || ['Class', 'Number', 'Name', 'Grade']
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