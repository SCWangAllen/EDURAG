import axios from './axios.js'

const templateService = {
  // 取得模板清單
  async getTemplates(params = {}) {
    const response = await axios.get('/templates', { params })
    return response.data
  },

  // 取得單一模板
  async getTemplate(templateId) {
    const response = await axios.get(`/templates/${templateId}`)
    return response.data
  },

  // 建立模板
  async createTemplate(templateData) {
    const response = await axios.post('/templates', templateData)
    return response.data
  },

  // 更新模板
  async updateTemplate(templateId, templateData) {
    const response = await axios.put(`/templates/${templateId}`, templateData)
    return response.data
  },

  // 刪除模板
  async deleteTemplate(templateId) {
    const response = await axios.delete(`/templates/${templateId}`)
    return response.data
  },

  // 取得科目清單
  async getSubjects() {
    const response = await axios.get('/templates/subjects')
    return response.data
  },

  // 初始化預設模板
  async initializeDefaults() {
    const response = await axios.post('/templates/initialize-defaults')
    return response.data
  }
}

export default templateService
