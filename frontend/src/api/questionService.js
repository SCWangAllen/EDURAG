// src/api/questionService.js
import api from './axios'  // 之前設定好的 axios 實例

export function generateQuestions(payload) {
  // 呼叫後端統一的 API 端點進行題目生成
  return api.post('/api/generate/', payload)
}

// 批次生成題目 - 支持不同題型使用不同模板
export function generateQuestionsBatch(payload) {
  return api.post('/api/generate/batch', payload)
}

// 模板驅動題目生成
export function generateQuestionsTemplate(payload) {
  return api.post('/api/generate/template', payload)
}

// 批次模板驅動題目生成
export function generateQuestionsTemplateBatch(payload) {
  return api.post('/api/generate/template/batch', payload)
}

// Prompt 驅動題目生成 (前端組合完整 prompt)
export function generateQuestionsByPrompt(payload) {
  return api.post('/api/generate/prompt', payload)
}

// 完整模板驅動題目生成 (傳送完整模板資訊)
export function generateQuestionsByTemplateEnhanced(payload) {
  console.log('🚀 [API] generateQuestionsByTemplateEnhanced 請求開始')
  console.log('📦 [API] 請求 payload:', payload)
  console.log('📝 [API] 模板資訊:', payload.template)
  console.log('📄 [API] 文件資訊:', payload.documents)
  console.log('🎛️ [API] 參數:', {
    count: payload.count,
    question_type: payload.question_type,
    temperature: payload.temperature,
    max_tokens: payload.max_tokens,
    model: payload.model
  })
  
  return api.post('/api/generate/template-enhanced', payload)
    .then(response => {
      console.log('✅ [API] generateQuestionsByTemplateEnhanced 回應成功')
      console.log('📊 [API] 回應資料:', response.data)
      if (response.data.template_info) {
        console.log('📝 [API] 使用的模板資訊:', response.data.template_info)
      }
      if (response.data.params_used) {
        console.log('🎛️ [API] 實際使用的參數:', response.data.params_used)
      }
      console.log('📈 [API] 生成統計:', {
        count: response.data.count,
        generation_time: response.data.generation_time,
        model_used: response.data.model_used
      })
      return response
    })
    .catch(error => {
      console.error('❌ [API] generateQuestionsByTemplateEnhanced 請求失敗')
      console.error('💥 [API] 錯誤詳情:', error)
      if (error.response) {
        console.error('📡 [API] 伺服器回應:', error.response.data)
        console.error('🔢 [API] 狀態碼:', error.response.status)
      }
      throw error
    })
}

export function ingestDocument(payload) {
  // 文件攝取API
  return api.post('/api/ingest/', payload)
}

export function getHealth() {
  // 健康檢查API
  return api.get('/health')
}

export function fetchHistory(userId) {
  return api.get(`/users/${userId}/history`)
}

// 問題管理相關 API

// 取得問題清單
export function getQuestions(params = {}) {
  return api.get('/api/questions/', { params })
}

// 取得單一問題詳情
export function getQuestion(questionId) {
  return api.get(`/api/questions/${questionId}`)
}

// 創建問題
export function createQuestion(questionData) {
  return api.post('/api/questions/', questionData)
}

// 更新問題
export function updateQuestion(questionId, updateData) {
  return api.put(`/api/questions/${questionId}`, updateData)
}

// 刪除問題
export function deleteQuestion(questionId) {
  return api.delete(`/api/questions/${questionId}`)
}

// 取得問題統計
export function getQuestionStats() {
  return api.get('/api/questions/stats')
}

// 導出問題
export async function exportQuestions(exportData) {
  const response = await api.post('/api/questions/export', exportData, {
    responseType: 'blob',
  })
  
  // 從 response headers 獲取檔名
  const contentDisposition = response.headers['content-disposition']
  let filename = 'questions_export.json'
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename=(.+)/)
    if (filenameMatch) {
      filename = filenameMatch[1]
    }
  }
  
  // 創建下載連結
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  
  return response
}
