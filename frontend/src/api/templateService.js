import axios from './axios.js'

const templateService = {
  // 取得模板清單
  async getTemplates(params = {}) {
    try {
      const response = await axios.get('/templates', { params })
      return response.data
    } catch (error) {
      console.error('取得模板清單失敗:', error)
      throw error
    }
  },

  // 取得單一模板
  async getTemplate(templateId) {
    try {
      const response = await axios.get(`/templates/${templateId}`)
      return response.data
    } catch (error) {
      console.error('取得模板失敗:', error)
      throw error
    }
  },

  // 建立模板
  async createTemplate(templateData) {
    try {
      const response = await axios.post('/templates', templateData)
      return response.data
    } catch (error) {
      console.error('建立模板失敗:', error)
      throw error
    }
  },

  // 更新模板
  async updateTemplate(templateId, templateData) {
    try {
      const response = await axios.put(`/templates/${templateId}`, templateData)
      return response.data
    } catch (error) {
      console.error('更新模板失敗:', error)
      throw error
    }
  },

  // 刪除模板
  async deleteTemplate(templateId) {
    try {
      const response = await axios.delete(`/templates/${templateId}`)
      return response.data
    } catch (error) {
      console.error('刪除模板失敗:', error)
      throw error
    }
  },

  // 取得科目清單
  async getSubjects() {
    try {
      const response = await axios.get('/templates/subjects')
      return response.data
    } catch (error) {
      console.error('取得科目清單失敗:', error)
      throw error
    }
  },

  // 初始化預設模板
  async initializeDefaults() {
    try {
      const response = await axios.post('/templates/initialize-defaults')
      return response.data
    } catch (error) {
      console.error('初始化預設模板失敗:', error)
      throw error
    }
  }
}

export default templateService