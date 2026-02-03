/**
 * PDF 匯出工具
 * 提供考券 PDF 匯出功能
 */
import {
  DEFAULT_SCHOOL_NAME,
  DEFAULT_EXAM_TITLE,
  DEFAULT_EXAM_SUBTITLE,
  QUESTION_TYPE_MAPPING,
  SECTION_INSTRUCTIONS
} from '../constants/examDefaults.js'

/**
 * 匯出考券為 PDF
 * @param {Object} examData - 考券資料
 * @param {Array} examData.questions - 題目列表
 * @param {Object} examData.config - 考券配置
 * @param {Array} examData.questionTypeOrder - 題型順序
 * @param {string} filename - 檔案名稱
 */
export async function exportToPDF(examData, filename = 'exam.pdf') {
  try {
    // 動態載入 jsPDF
    const { jsPDF } = await import('jspdf')
    await import('jspdf/dist/jspdf.es.min.js')
    
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
      
      // 考試標題 (中等)
      pdf.setFontSize(16)
      const titleWidth = pdf.getTextWidth(title)
      pdf.text(title, (pageWidth - titleWidth) / 2, yPosition)
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
    const orderedTypes = examData.questionTypeOrder || ['single_choice', 'cloze', 'short_answer', 'true_false', 'matching']
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
      questions.forEach((question, index) => {
        const questionNumber = `${index + 1}.`
        const questionText = question.content || question.prompt || 'Question text'
        
        // 檢查頁面空間
        if (yPosition > 270) {
          pdf.addPage()
          yPosition = 20
        }
        
        // 題目編號和內容
        pdf.text(questionNumber, 20, yPosition)
        
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
        
        yPosition += 5 // 題目間距
      })
      
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