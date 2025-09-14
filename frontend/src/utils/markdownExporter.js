/**
 * Markdown 匯出工具
 * 負責將考券內容匯出為 Markdown 檔案
 */

export const downloadMarkdownFile = (content, filename) => {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  
  link.href = url
  link.download = `${filename}.md`
  link.style.display = 'none'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  // 清理 URL 物件
  window.URL.revokeObjectURL(url)
}

export const exportQuestionsAsJson = (questions, filename) => {
  const exportData = questions.map(q => ({
    id: q.id,
    type: q.type,
    subject: q.subject,
    content: q.content || q.prompt,
    options: q.options || [],
    correct_answer: q.correct_answer,
    difficulty: q.difficulty,
    source_document: q.source_document ? {
      title: q.source_document.title,
      id: q.source_document.id
    } : null,
    created_at: q.created_at
  }))

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
    type: 'application/json;charset=utf-8' 
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  
  a.href = url
  a.download = `${filename}.json`
  a.style.display = 'none'
  
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  
  URL.revokeObjectURL(url)
}

/**
 * 生成檔案名稱
 * @param {string} title - 考券標題
 * @param {string} suffix - 檔案後綴
 * @returns {string} 清理後的檔案名稱
 */
export const generateFilename = (title, suffix = '') => {
  const cleanTitle = title.replace(/[^a-zA-Z0-9\-_\s\u4e00-\u9fff]/g, '_')
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', '_').replace(/:/g, '-')
  return `${cleanTitle}_${timestamp}${suffix}`
}