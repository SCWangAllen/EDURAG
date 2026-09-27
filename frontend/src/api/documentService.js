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

  // 批次刪除文件
  async batchDeleteDocuments(ids, force = false) {
    const { data } = await api.post('/api/documents/batch-delete', {
      document_ids: ids,
      force
    })
    return data
  },

  // 複製文件到其他年級(例如 G4-G6 教材複製給對應的國中先修班使用)
  // → { created, skipped_count, created_ids, skipped_items: [{document_id, grade, reason}] }
  async copyDocumentsToGrades(documentIds, targetGrades) {
    const { data } = await api.post('/api/documents/copy', {
      document_ids: documentIds,
      target_grades: targetGrades
    })
    return data
  },

  // 取得科目清單
  async getSubjects() {
    const { data } = await api.get('/api/documents/subjects')
    return data
  },

  // 取得上傳來源檔案清單(用於文件列表的「上傳檔案」篩選)
  async getDocumentSources() {
    const { data } = await api.get('/api/documents/sources')
    return data
  }
}

export default documentService