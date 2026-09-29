import axios from './axios.js'

const templateService = {
  // 取得模板清單
  async getTemplates(params = {}) {
    const response = await axios.get('/api/templates', { params })
    return response.data
  },

  // 取得單一模板
  async getTemplate(templateId) {
    const response = await axios.get(`/api/templates/${templateId}`)
    return response.data
  },

  // 建立模板
  async createTemplate(templateData) {
    const response = await axios.post('/api/templates', templateData)
    return response.data
  },

  // 更新模板
  async updateTemplate(templateId, templateData) {
    const response = await axios.put(`/api/templates/${templateId}`, templateData)
    return response.data
  },

  // 刪除模板
  async deleteTemplate(templateId) {
    const response = await axios.delete(`/api/templates/${templateId}`)
    return response.data
  },

  // 取得科目清單
  async getSubjects() {
    const response = await axios.get('/api/templates/subjects')
    return response.data
  },

  // 初始化預設模板
  async initializeDefaults() {
    const response = await axios.post('/api/templates/initialize-defaults')
    return response.data
  },

  // 取得各題型的起始範本與輸出範例(單一真實來源,供範本庫/自動帶入)
  async getQuestionTypes() {
    const response = await axios.get('/api/templates/question-types')
    return response.data
  },

  // 自訂順序：把模板往上/下移動一格(第一次移動會凍結目前排序,之後需以 sort=manual 重新取得清單)
  async moveTemplate(templateId, direction) {
    const response = await axios.post(`/api/templates/${templateId}/move`, { direction })
    return response.data
  },

  // 拖曳排序：把模板移到任意位置(target 為 { before_id } 或 { after_id },擇一)
  async moveTemplateTo(templateId, target) {
    const response = await axios.post(`/api/templates/${templateId}/move-to`, target)
    return response.data
  }
}

export default templateService
