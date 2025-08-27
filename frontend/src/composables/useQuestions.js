// src/composables/useQuestions.js
import { ref } from 'vue'
import { generateQuestions, ingestDocument } from '../api/questionService'

// 轉換前端友好的科目名稱到後端API格式
function normalizeSubject(frontendSubject) {
  const subjectMap = {
    'Chinese': 'chinese',
    'English': 'english', 
    'Math': 'math',
    // 也支持已經是小寫的情況
    'chinese': 'chinese',
    'english': 'english',
    'math': 'math'
  }
  
  return subjectMap[frontendSubject] || frontendSubject.toLowerCase()
}

export function useQuestions() {
  const questions = ref([])
  const loading   = ref(false)
  const error     = ref(null)
  const output    = ref(null)

  async function load(payload) {
    loading.value = true
    error.value   = null
    output.value  = null // Reset output on new load
    
    try {
      // 步驟1: 攝取文件（如果包含text）
      let documentId = payload.document_id
      
      if (!documentId && payload.text) {
        const apiSubject = normalizeSubject(payload.subject)
        
        console.log('Ingesting document...', payload.subject, '→', apiSubject, payload.text.substring(0, 50))
        const ingestRes = await ingestDocument({
          subject: apiSubject,
          text: payload.text,
          title: payload.title || '用戶輸入的文件'
        })
        
        if (ingestRes.data && ingestRes.data.document_id) {
          documentId = ingestRes.data.document_id
          console.log('Document ingested with ID:', documentId)
        } else {
          throw new Error('文件攝取失敗：無法獲取document_id')
        }
      }
      
      if (!documentId) {
        throw new Error('缺少document_id，無法生成題目')
      }
      
      // 步驟2: 轉換題型格式
      const typesDict = {}
      if (payload.types && Array.isArray(payload.types)) {
        // 舊格式: [{ type: "single_choice", num: 2 }]
        payload.types.forEach(typeInfo => {
          if (typeInfo.num > 0) {
            typesDict[typeInfo.type] = typeInfo.num
          }
        })
      } else if (payload.types && typeof payload.types === 'object') {
        // 新格式: { single_choice: 2, cloze: 1 }
        Object.assign(typesDict, payload.types)
      }
      
      if (Object.keys(typesDict).length === 0) {
        throw new Error('未指定題型或所有題型數量為0')
      }
      
      // 步驟3: 生成題目
      const generatePayload = {
        subject: normalizeSubject(payload.subject),
        document_id: documentId,
        types: typesDict
      }
      
      console.log('Generating questions...', generatePayload)
      const res = await generateQuestions(generatePayload)
      console.log('API Success Response:', res)
      
      // 轉換API回應格式以匹配前端期望
      const apiData = res.data
      if (apiData && apiData.items) {
        // 轉換每個問題項目的格式
        questions.value = apiData.items.map(item => ({
          question: item.prompt,        // prompt -> question
          options: item.options,        // options 保持不變
          answer: item.answer,          // answer 保持不變
          explanation: item.explanation, // 新增解釋欄位
          type: item.type,              // 新增問題類型
          context: item.source?.chunk_text || '', // source.chunk_text -> context
          source: item.source           // 保留完整來源信息
        }))
        
        // 儲存原始回應用於顯示
        output.value = {
          questions: questions.value,
          total_count: apiData.total_count,
          generation_time: apiData.generation_time,
          document_id: documentId
        }
      } else {
        console.warn('API response missing items array:', apiData)
        questions.value = []
        output.value = apiData
      }
      
      return true // Indicate success
    } catch (err) {
      console.error('API Error:', err) // Log error object
      
      // 處理更友好的錯誤訊息
      let errorMessage = '系統錯誤，請稍後再試'
      
      if (err.response) {
        const status = err.response.status
        const data = err.response.data
        
        if (status === 422 && data.detail) {
          // 驗證錯誤
          const validationErrors = data.detail
          const messages = validationErrors.map(e => {
            if (e.loc && e.loc.includes('text') && e.type === 'string_too_short') {
              return '文件內容太短，至少需要3個字符'
            } else if (e.loc && e.loc.includes('subject')) {
              if (e.type === 'enum') {
                return '請選擇有效的科目（國文/英文/數學）'
              }
              return '請選擇有效的科目'
            } else if (e.loc && e.loc.includes('types')) {
              return '請至少選擇一種題型且數量大於0'
            } else if (e.type === 'enum') {
              return `選項值無效: ${e.input}`
            }
            return e.msg || '輸入格式錯誤'
          })
          errorMessage = messages.join('、')
        } else if (status === 404) {
          errorMessage = '找不到相關文件或資源'
        } else if (status >= 500) {
          errorMessage = '服務器錯誤，請稍後再試'
        } else if (data.detail) {
          errorMessage = typeof data.detail === 'string' ? data.detail : '請求處理失敗'
        }
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        errorMessage = '網絡連接錯誤，請檢查後端服務是否正常運行'
      }
      
      // 建立友好的錯誤對象
      error.value = {
        ...err,
        friendlyMessage: errorMessage
      }
      questions.value = [] // Clear questions on error
      return false // Indicate failure
    } finally {
      loading.value = false
    }
  }

  return { questions, loading, error, output, load }
}
