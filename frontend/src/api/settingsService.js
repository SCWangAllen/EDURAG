import api from './axios'

export const settingsService = {
  // 取得可選的 LLM 模型清單
  async getModels() {
    const response = await api.get('/api/settings/models')
    return response.data
  },

  // 取得目前選中的生成模型
  async getModel() {
    const response = await api.get('/api/settings/model')
    return response.data
  },

  // 設定生成模型
  async setModel(modelId) {
    const response = await api.put('/api/settings/model', { model: modelId })
    return response.data
  },

  // 取得建議模型 ID 清單(使用者自訂,全站共用)
  async getRecommended() {
    const response = await api.get('/api/settings/recommended')
    return response.data
  },

  // 更新建議模型 ID 清單
  async setRecommended(ids) {
    const response = await api.put('/api/settings/recommended', { models: ids })
    return response.data
  }
}

export default settingsService
