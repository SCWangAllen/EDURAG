import api from './axios'

export const subjectService = {
  // 取得所有科目
  async getSubjects(includeInactive = false) {
    try {
      const response = await api.get('/api/subjects/', {
        params: { include_inactive: includeInactive }
      })
      return response.data
    } catch (error) {
      console.error('取得科目清單失敗:', error)
      throw error
    }
  },

  // 取得單一科目
  async getSubject(subjectId) {
    try {
      const response = await api.get(`/api/subjects/${subjectId}`)
      return response.data
    } catch (error) {
      console.error('取得科目失敗:', error)
      throw error
    }
  },

  // 建立科目
  async createSubject(subjectData) {
    try {
      const response = await api.post('/api/subjects/', subjectData)
      return response.data
    } catch (error) {
      console.error('建立科目失敗:', error)
      throw error
    }
  },

  // 更新科目
  async updateSubject(subjectId, updateData) {
    try {
      const response = await api.put(`/api/subjects/${subjectId}`, updateData)
      return response.data
    } catch (error) {
      console.error('更新科目失敗:', error)
      throw error
    }
  },

  // 刪除科目
  async deleteSubject(subjectId, force = false) {
    try {
      const response = await api.delete(`/api/subjects/${subjectId}`, {
        params: { force }
      })
      return response.data
    } catch (error) {
      console.error('刪除科目失敗:', error)
      throw error
    }
  },

  // 取得科目使用統計
  async getSubjectStats() {
    try {
      const response = await api.get('/api/subjects/usage/stats')
      return response.data
    } catch (error) {
      console.error('取得科目統計失敗:', error)
      throw error
    }
  }
}

export default subjectService