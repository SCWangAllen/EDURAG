import api from './axios'

const documentService = {
  // 取得文件清單
  async getDocuments(params = {}) {
    const { data } = await api.get('/api/documents/', { params })
    // 統一欄位映射：page_number → page
    if (data.documents) {
      data.documents = data.documents.map(doc => ({
        ...doc,
        page: doc.page_number || doc.page  // 優先使用 page_number，向後兼容 page
      }))
    }
    return data
  },

  // 取得單一文件詳情
  async getDocument(documentId) {
    const { data } = await api.get(`/api/documents/${documentId}`)
    // 統一欄位映射
    if (data) {
      data.page = data.page_number || data.page
    }
    return data
  },

  // 搜尋文件
  async searchDocuments(query, params = {}) {
    const { data } = await api.get('/api/documents/search', {
      params: { q: query, ...params }
    })
    // 統一欄位映射
    if (data.documents) {
      data.documents = data.documents.map(doc => ({
        ...doc,
        page: doc.page_number || doc.page
      }))
    }
    return data
  },

  // 取得文件統計
  async getDocumentStats() {
    const { data } = await api.get('/api/documents/stats')
    return data
  },

  // 取得文件的章節清單
  async getDocumentChapters(documentId) {
    const { data } = await api.get(`/api/documents/${documentId}/chapters`)
    return data
  },

  // 更新文件
  async updateDocument(documentId, updateData) {
    const { data } = await api.put(`/api/documents/${documentId}`, updateData)
    return data
  },

  // 檢查文件引用
  async checkDocumentReferences(documentId) {
    const { data } = await api.get(`/api/documents/${documentId}/references`)
    return data
  },

  // 刪除文件
  async deleteDocument(documentId, force = false) {
    const { data } = await api.delete(`/api/documents/${documentId}`, {
      params: { force }
    })
    return data
  },

  // 取得科目清單
  async getSubjects() {
    const { data } = await api.get('/api/documents/subjects')
    return data
  }
}

export default documentService