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
  }
}

export default settingsService
