import api from './axios'

const dashboardService = {
  // 取得儀表板統計資料
  async getStats() {
    const { data } = await api.get('/api/dashboard/stats')
    return data
  }
}

export default dashboardService