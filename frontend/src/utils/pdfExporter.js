/**
 * PDF 匯出工具
 * 提供考券 PDF 匯出功能，支援圖片題目和增強答案券
 */
import {
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE,
  QUESTION_TYPE_MAPPING,
  SECTION_INSTRUCTIONS
} from '../constants/examDefaults.js'

// 圖片載入快取
const imageCache = new Map()

/**
 * 匯出考券為 PDF
 * @param {Object} examData - 考券資料
 * @param {Array} examData.questions - 題目列表
 * @param {Object} examData.config - 考券配置
 * @param {Array} examData.questionTypeOrder - 題型順序
 * @param {Object} examData.questionTypeConfig - 題型配置（用於答案卷計分）
 * @param {string} filename - 檔案名稱
 */
export async function exportToPDF(examData, filename = 'exam.pdf') {
  try {
    // 動態載入 jsPDF
    const { jsPDF } = await import('jspdf')
    await import('jspdf/dist/jspdf.es.min.js')

    // 判斷是否為答案卷模式
    const isAnswerSheet = examData.config?.isAnswerSheet === true

    // 創建 PDF 文件 (A4 尺寸)
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    // 設定中文字型 (如果需要)
    // pdf.addFont('path/to/chinese-font.ttf', 'chinese', 'normal')
    // pdf.setFont('chinese')

    // 設定基本樣式
    pdf.setFontSize(12)
    let yPosition = 20

    // 頁眉
    if (examData.config.header?.enabled !== false) {
      pdf.setFontSize(16)
      pdf.setFont('times', 'bold')

      const title = examData.config.header?.titlePrefix || DEFAULT_EXAM_TITLE
      const schoolName = examData.config.header?.schoolName || DEFAULT_SCHOOL_NAME
      const subtitle = examData.config.header?.subtitle || DEFAULT_EXAM_SUBTITLE

      // 置中標題 - Abraham Academy 格式
      const pageWidth = 210 // A4 寬度

      // 學校名稱 (最大)
      pdf.setFontSize(20)
      const schoolWidth = pdf.getTextWidth(schoolName)
      pdf.text(schoolName, (pageWidth - schoolWidth) / 2, yPosition)
      yPosition += 10

      // 考試標題 (中等) - 答案卷標題加入「答案卷」
      pdf.setFontSize(16)
      const displayTitle = isAnswerSheet ? `${title} - Answer Key` : title
      const titleWidth = pdf.getTextWidth(displayTitle)
      pdf.text(displayTitle, (pageWidth - titleWidth) / 2, yPosition)
      yPosition += 8

      // 副標題 (小)
      pdf.setFontSize(14)
      const subtitleWidth = pdf.getTextWidth(subtitle)
      pdf.text(subtitle, (pageWidth - subtitleWidth) / 2, yPosition)
      yPosition += 15
      
      // // 考試資訊
      // pdf.setFontSize(10)
      // pdf.setFont('helvetica', 'normal')
      // const duration = examData.config.header?.duration || '90 minutes'
      // const totalScore = examData.config.header?.totalScore || '100 points'
      
      // pdf.text(`Time: ${duration}`, 20, yPosition)
      // pdf.text(`Total: ${totalScore}`, 100, yPosition)
      // pdf.text('Date: ___________', 150, yPosition)
      // yPosition += 10
      
      // 分隔線
    //   pdf.line(20, yPosition, 190, yPosition)
    //   yPosition += 10
    // }
    
    // // 學生資訊
    // if (examData.config.studentInfo?.enabled !== false) {
    //   pdf.setFontSize(10)
    //   const fields = examData.config.studentInfo?.fields || ['Class', 'Number', 'Name', 'Score']
      
    //   let xPosition = 20
    //   fields.forEach(field => {
    //     const fieldName = typeof field === 'string' ? field : field.label
    //     pdf.text(`${fieldName}: ________________`, xPosition, yPosition)
    //     xPosition += 45
    //   })
    //   yPosition += 15
    }
    
    // 題目內容
    const orderedTypes = examData.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching', 'image_question']
    const questionsByType = groupQuestionsByType(examData.questions)

    let sectionNumber = 1
    for (const questionType of orderedTypes) {
      const questions = questionsByType[questionType]
      if (!questions || questions.length === 0) continue

      // 檢查頁面空間
      if (yPosition > 250) {
        pdf.addPage()
        yPosition = 20
      }

      // 區塊標題
      pdf.setFontSize(12)
      pdf.setFont('times', 'bold')
      const sectionTitle = getSectionTitle(questionType, sectionNumber)
      pdf.text(sectionTitle, 20, yPosition)
      yPosition += 8

      // 添加指導文字
      pdf.setFontSize(10)
      pdf.setFont('times', 'italic')
      const instruction = getSectionInstruction(questionType)
      pdf.text(instruction, 20, yPosition)
      yPosition += 10

      pdf.setFont('times', 'normal')

      // 題目
      for (let index = 0; index < questions.length; index++) {
        const question = questions[index]
        const questionNumber = `${index + 1}.`
        const questionText = question.content || question.prompt || 'Question text'

        // 檢查頁面空間（圖片題需要更多空間）
        const requiredSpace = questionType === 'image_question' ? 100 : 30
        if (yPosition > (297 - requiredSpace)) {
          pdf.addPage()
          yPosition = 20
        }

        // 題目編號和內容
        pdf.text(questionNumber, 20, yPosition)

        // 答案卷模式：簡潔顯示題號和答案
        if (isAnswerSheet) {
          yPosition = await renderAnswerSheetQuestion(pdf, question, questionType, yPosition, examData.config)
        } else {
          // 試題卷模式：完整題目內容
          if (questionType === 'image_question') {
            // 圖片題目渲染
            yPosition = await renderImageQuestion(pdf, question, yPosition, questionText)
          } else {
            // 處理長文本換行
            const textLines = pdf.splitTextToSize(questionText, 160)
            textLines.forEach((line, lineIndex) => {
              pdf.text(line, 30, yPosition + (lineIndex * 5))
            })

            yPosition += textLines.length * 5 + 5

            // 根據題型添加特定格式
            if (questionType === 'single_choice' && question.options) {
              question.options.forEach((option, optIndex) => {
                // 檢查選項是否已經包含標籤格式
                const hasLabel = /^[a-zA-Z][.\)\]][\s]/.test(option.toString().trim())

                let optionText
                if (hasLabel) {
                  // 選項已經有標籤，直接使用
                  optionText = option
                } else {
                  // 選項沒有標籤，加上小寫字母標籤（符合 Abraham Academy 格式）
                  const optionLabel = String.fromCharCode(97 + optIndex) + '.'  // a. b. c. d.
                  optionText = `${optionLabel} ${option}`
                }

                const optionLines = pdf.splitTextToSize(optionText, 140)
                optionLines.forEach((line, lineIndex) => {
                  pdf.text(line, 40, yPosition + (lineIndex * 4))
                })
                yPosition += optionLines.length * 4 + 2
              })
              yPosition += 5
            } else if (questionType === 'short_answer') {
              // 簡答題答題線
              for (let i = 0; i < 3; i++) {
                pdf.line(40, yPosition + (i * 8), 180, yPosition + (i * 8))
              }
              yPosition += 25
            } else if (questionType === 'true_false') {
              pdf.text('T / F', 40, yPosition)
              yPosition += 8
            }
          }
        }

        yPosition += 5 // 題目間距
      }

      sectionNumber++
      yPosition += 10 // 區塊間距
    }
    
    // 儲存 PDF
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
 * @returns {number} 更新後的 Y 位置
 */
async function renderImageQuestion(pdf, question, yPosition, questionText) {
  const margin = 20
  const contentWidth = 170

  // 題目描述
  if (questionText && questionText !== '圖片題') {
    const textLines = pdf.splitTextToSize(questionText, contentWidth - 10)
    textLines.forEach((line, lineIndex) => {
      pdf.text(line, margin + 10, yPosition + (lineIndex * 5))
    })
    yPosition += textLines.length * 5 + 5
  }

  // 嵌入問題圖片（支持 _url 和 _path 兩種屬性）
  const questionImageUrl = question.question_image_url || question.question_image_path
  if (questionImageUrl) {
    try {
      const imageBase64 = await loadImageAsBase64(questionImageUrl)
      if (imageBase64) {
        // 計算合適的圖片尺寸（最大寬度 160mm，最大高度 80mm）
        const maxWidth = 160
        const maxHeight = 80
        const imgDimensions = await getImageDimensions(questionImageUrl)
        const { width, height } = calculateFitDimensions(imgDimensions.width, imgDimensions.height, maxWidth, maxHeight)

        pdf.addImage(imageBase64, 'JPEG', margin + 10, yPosition, width, height)
        yPosition += height + 5
      } else {
        // 圖片載入失敗，顯示佔位符
        renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image || 'Image')
        yPosition += 45
      }
    } catch (error) {
      // 圖片載入失敗，顯示佔位符
      renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image || 'Image')
      yPosition += 45
    }
  } else if (question.question_image) {
    // 沒有 URL 但有圖片名稱，顯示佔位符
    renderImagePlaceholder(pdf, margin + 10, yPosition, question.question_image)
    yPosition += 45
  }

  // 答題線
  for (let i = 0; i < 3; i++) {
    pdf.line(margin + 10, yPosition + (i * 8), margin + contentWidth, yPosition + (i * 8))
  }
  yPosition += 25

  return yPosition
}

/**
 * 渲染答案券中的題目（增強版，支援答案圖片和解釋）
 * @param {jsPDF} pdf - PDF 文件物件
 * @param {Object} question - 題目資料
 * @param {string} questionType - 題型
 * @param {number} yPosition - 當前 Y 位置
 * @param {Object} config - 配置選項
 * @returns {number} 更新後的 Y 位置
 */
async function renderAnswerSheetQuestion(pdf, question, questionType, yPosition, config = {}) {
  const showAnswerImages = config.showAnswerImages !== false
  const showExplanations = config.showExplanations !== false
  const margin = 20

  // 一般題目答案（同時顯示題目內容與答案）
  if (questionType !== 'image_question') {
    const answer = question.correct_answer || question.answer || 'N/A'
    const questionText = question.content || question.prompt || ''

    // 1. 顯示題目內容
    if (questionText) {
      pdf.setFont('times', 'normal')
      const textLines = pdf.splitTextToSize(questionText, 150)
      textLines.forEach((line, lineIndex) => {
        pdf.text(line, 30, yPosition + lineIndex * 5)
      })
      yPosition += textLines.length * 5 + 3
    }

    // 2. 顯示選項（選擇題）
    if (questionType === 'single_choice' && question.options && Array.isArray(question.options)) {
      question.options.forEach((option, optIndex) => {
        const optionLabel = String.fromCharCode(65 + optIndex) + '.'
        const optionText = /^[a-zA-Z][.\)\]]/.test(option.toString().trim())
          ? option
          : `${optionLabel} ${option}`
        pdf.text(optionText, 40, yPosition)
        yPosition += 5
      })
      yPosition += 2
    }

    // 3. 顯示答案（粗體標示）
    pdf.setFont('times', 'bold')
    pdf.text(`Answer: ${formatAnswerText(answer)}`, 30, yPosition)
    pdf.setFont('times', 'normal')
    yPosition += 8

    return yPosition
  }

  // 圖片題目答案（增強版）
  pdf.setFontSize(10)

  // 顯示答案圖片（如果有且啟用，支持 _url 和 _path 兩種屬性）
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
        pdf.text('Answer:', 40, yPosition)
        yPosition += 6

        const maxWidth = 120
        const maxHeight = 60
        const imgDimensions = await getImageDimensions(answerImageUrl)
        const { width, height } = calculateFitDimensions(imgDimensions.width, imgDimensions.height, maxWidth, maxHeight)

        pdf.addImage(imageBase64, 'JPEG', 40, yPosition, width, height)
        yPosition += height + 5
      }
    } catch (error) {
      // 答案圖片載入失敗，顯示文字
      pdf.setFont('times', 'bold')
      pdf.text(`Answer: [Image: ${question.answer_image || 'N/A'}]`, 40, yPosition)
      pdf.setFont('times', 'normal')
      yPosition += 8
    }
  } else if (question.answer_image) {
    // 有答案圖片但未啟用顯示
    pdf.setFont('times', 'bold')
    pdf.text(`Answer: [See answer image: ${question.answer_image}]`, 40, yPosition)
    pdf.setFont('times', 'normal')
    yPosition += 8
  }

  // 顯示解釋說明（如果有且啟用）
  if (showExplanations && (question.explanation || question.content)) {
    const explanationText = question.explanation || question.content
    if (explanationText && explanationText !== '圖片題') {
      pdf.setFont('times', 'italic')
      pdf.setFontSize(9)
      const explanationLines = pdf.splitTextToSize(`Explanation: ${explanationText}`, 140)
      explanationLines.forEach((line, lineIndex) => {
        pdf.text(line, 40, yPosition + (lineIndex * 4))
      })
      yPosition += explanationLines.length * 4 + 3
      pdf.setFont('times', 'normal')
      pdf.setFontSize(10)
    }
  }

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
  const str = String(answer)
  return str.length > 100 ? str.substring(0, 100) + '...' : str
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
 * 取得區塊標題
 */
function getSectionTitle(questionType, sectionNumber) {
  const config = QUESTION_TYPE_MAPPING[questionType] || { letter: sectionNumber, name: questionType, points: 0 }
  return `${config.letter}. ${config.name} _____/${config.points}`
}

/**
 * 取得區塊指導文字
 */
function getSectionInstruction(questionType) {
  return SECTION_INSTRUCTIONS[questionType] || 'Complete the following questions.'
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
            // 檢查選項是否已經包含標籤格式
            const hasLabel = /^[a-zA-Z][.\)\]][\s]/.test(option.toString().trim())
            
            if (hasLabel) {
              // 選項已經有標籤，直接使用
              content += `   ${option}\n`
            } else {
              // 選項沒有標籤，加上小寫字母標籤（符合 Abraham Academy 格式）
              const optionLabel = String.fromCharCode(97 + optIndex)  // a, b, c, d
              content += `   ${optionLabel}. ${option}\n`
            }
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