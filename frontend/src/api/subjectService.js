import api from './axios'

export const subjectService = {
  // 取得所有科目
  async getSubjects(includeInactive = false) {
    const response = await api.get('/api/subjects/', {
      params: { include_inactive: includeInactive }
    })
    return response.data
  },

  // 取得單一科目
  async getSubject(subjectId) {
    const response = await api.get(`/api/subjects/${subjectId}`)
    return response.data
  },

  // 建立科目
  async createSubject(subjectData) {
    const response = await api.post('/api/subjects/', subjectData)
    return response.data
  },

  // 更新科目
  async updateSubject(subjectId, updateData) {
    const response = await api.put(`/api/subjects/${subjectId}`, updateData)
    return response.data
  },

  // 刪除科目
  async deleteSubject(subjectId, force = false) {
    const response = await api.delete(`/api/subjects/${subjectId}`, {
      params: { force }
    })
    return response.data
  },

  // 取得科目使用統計
  async getSubjectStats() {
    const response = await api.get('/api/subjects/usage/stats')
    return response.data
  }
}

export default subjectService
