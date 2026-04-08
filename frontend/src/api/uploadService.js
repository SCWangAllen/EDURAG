import api from './axios'

const uploadService = {
  // 上傳 Excel 文件並預覽
  async uploadExcel(file, previewOnly = true) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('preview_only', previewOnly)
    
    const { data } = await api.post('/api/upload/excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  // 下載 Excel 範本
  async downloadTemplate() {
    const response = await api.get('/api/upload/template', {
      responseType: 'blob',
    })
    
    // 創建下載連結
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'document_template.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    return response
  },

  // 確認儲存預覽的文件
  async confirmSave(file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('preview_only', false)
    
    const { data } = await api.post('/api/upload/excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  }
}

export default uploadService