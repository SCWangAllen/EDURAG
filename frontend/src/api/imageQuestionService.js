// src/api/imageQuestionService.js
// 圖片題目管理 API 服務

import api from './axios'

/**
 * 上傳 Excel 檔案匯入圖片題目
 * @param {File} file - Excel 檔案
 * @param {boolean} previewOnly - 是否僅預覽（true = 只預覽，false = 預覽並儲存）
 * @returns {Promise} 預覽結果
 */
export function uploadExcel(file, previewOnly = true) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('preview_only', previewOnly)

  return api.post('/api/image-questions/upload/excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 取得圖片題目清單
 * @param {Object} params - 查詢參數
 * @param {string} [params.subject] - 科目篩選
 * @param {string} [params.grade] - 年級篩選
 * @param {string} [params.chapter] - 章節篩選
 * @param {boolean} [params.verified] - 圖片驗證狀態
 * @param {string} [params.search] - 搜尋關鍵字
 * @param {number} [params.page=1] - 頁碼
 * @param {number} [params.size=20] - 每頁數量
 * @returns {Promise} 題目清單
 */
export function getImageQuestions(params = {}) {
  return api.get('/api/image-questions/', { params })
}

/**
 * 取得圖片題目統計
 * @returns {Promise} 統計資訊
 */
export function getImageQuestionStats() {
  return api.get('/api/image-questions/stats')
}

/**
 * 取得單一圖片題目
 * @param {number} questionId - 題目 ID
 * @returns {Promise} 題目詳情
 */
export function getImageQuestion(questionId) {
  return api.get(`/api/image-questions/${questionId}`)
}

/**
 * 更新圖片題目
 * @param {number} questionId - 題目 ID
 * @param {Object} data - 更新資料
 * @returns {Promise} 更新後的題目
 */
export function updateImageQuestion(questionId, data) {
  return api.put(`/api/image-questions/${questionId}`, data)
}

/**
 * 刪除圖片題目
 * @param {number} questionId - 題目 ID
 * @returns {Promise} 刪除結果
 */
export function deleteImageQuestion(questionId) {
  return api.delete(`/api/image-questions/${questionId}`)
}

/**
 * 驗證圖片是否存在
 * @param {number[]} questionIds - 要驗證的題目 ID 列表
 * @returns {Promise} 驗證結果
 */
export function verifyImages(questionIds) {
  return api.post('/api/image-questions/verify-images', {
    question_ids: questionIds,
  })
}

/**
 * 取得問題圖片 URL
 * @param {string} filename - 圖片檔名（含或不含副檔名）
 * @returns {string} 完整圖片 URL
 */
export function getQuestionImageUrl(filename) {
  if (!filename) return null
  // 使用相對路徑，讓 Vite 代理處理，避免 CORS 問題
  return `/api/images/questions/${filename}`
}

/**
 * 取得答案圖片 URL
 * @param {string} filename - 圖片檔名（含或不含副檔名）
 * @returns {string} 完整圖片 URL
 */
export function getAnswerImageUrl(filename) {
  if (!filename) return null
  // 使用相對路徑，讓 Vite 代理處理，避免 CORS 問題
  return `/api/images/answers/${filename}`
}

/**
 * 取得圖片 URL（通用，根據類型選擇目錄）
 * @param {string} filename - 圖片檔名（含或不含副檔名）
 * @param {string} imageType - 'questions' 或 'answers'
 * @returns {string} 完整圖片 URL
 */
export function getImageUrl(filename, imageType = 'questions') {
  if (!filename) return null
  const baseUrl = api.defaults.baseURL || ''
  return `${baseUrl}/api/images/${imageType}/${filename}`
}

/**
 * 檢查圖片是否存在
 * @param {string} filename - 圖片檔名
 * @param {string} imageType - 'questions' 或 'answers'
 * @returns {Promise} 檢查結果
 */
export function checkImageExists(filename, imageType = 'questions') {
  return api.get(`/api/images/check/${imageType}/${filename}`)
}

/**
 * 列出可用圖片
 * @param {string} imageType - 'questions' 或 'answers'
 * @param {Object} params - 查詢參數
 * @param {string} [params.search] - 搜尋關鍵字
 * @param {number} [params.limit=50] - 返回數量限制
 * @returns {Promise} 圖片列表
 */
export function listImages(imageType, params = {}) {
  return api.get(`/api/images/list/${imageType}`, { params })
}

/**
 * 查詢圖片引用
 * @param {string} imageType - 圖片類型 ('questions' 或 'answers')
 * @param {string} imageName - 圖片名稱（不含副檔名）
 * @returns {Promise} 引用此圖片的題目列表
 * @example
 * {
 *   image_name: "g4_health_ch1",
 *   image_type: "questions",
 *   references: [
 *     { id: 1, subject: "Health", grade: "G4", chapter: "Chapter 1", ... }
 *   ],
 *   total: 1
 * }
 */
export function getImageReferences(imageType, imageName) {
  return api.get(`/api/images/references/${imageType}/${imageName}`)
}

/**
 * 重命名圖片
 * @param {string} imageType - 圖片類型 ('questions' 或 'answers')
 * @param {string} oldName - 舊圖片名稱（不含副檔名）
 * @param {string} newName - 新圖片名稱（不含副檔名）
 * @param {boolean} [updateQuestions=true] - 是否同步更新引用此圖片的題目
 * @returns {Promise} 重命名結果
 * @example
 * {
 *   success: true,
 *   old_name: "old_image",
 *   new_name: "new_image",
 *   affected_questions: 3,
 *   message: "圖片重命名成功，已更新 3 筆題目"
 * }
 */
export function renameImage(imageType, oldName, newName, updateQuestions = true) {
  return api.put(`/api/images/rename/${imageType}`, {
    old_name: oldName,
    new_name: newName,
    update_questions: updateQuestions,
  })
}

/**
 * 創建單一圖片題目
 * @param {Object} data - 題目資料
 * @param {string} data.question_image - 問題圖片名稱
 * @param {string} data.subject - 科目
 * @param {string} [data.answer_image] - 答案圖片名稱
 * @param {string} [data.question_description] - 題目描述
 * @param {string} [data.grade] - 年級
 * @param {string} [data.chapter] - 章節
 * @param {string} [data.page] - 頁碼
 * @returns {Promise} 創建的題目
 */
export function createImageQuestion(data) {
  return api.post('/api/image-questions/', data)
}

/**
 * 取得所有缺失圖片的題目清單
 * @returns {Promise} 缺失圖片清單
 * @example
 * {
 *   missing_question_images: [{ id, image_name, image_type, subject, grade, chapter }],
 *   missing_answer_images: [{ id, image_name, image_type, subject, grade, chapter }],
 *   total_missing: 5
 * }
 */
export function getMissingImages() {
  return api.get('/api/image-questions/missing-images')
}

/**
 * 上傳圖片檔案
 * @param {string} imageType - 圖片類型 ('questions' 或 'answers')
 * @param {File} file - 要上傳的圖片檔案
 * @param {string} [customName] - 可選的自訂檔案名稱（不含副檔名）
 * @returns {Promise} 上傳結果
 * @example
 * {
 *   success: true,
 *   filename: "g4_question_health.jpg",
 *   name: "g4_question_health",
 *   extension: "jpg",
 *   image_type: "questions",
 *   path: "/api/images/questions/g4_question_health.jpg",
 *   message: "圖片上傳成功"
 * }
 */
export function uploadImage(imageType, file, customName = null) {
  const formData = new FormData()
  formData.append('file', file)
  if (customName) {
    formData.append('custom_name', customName)
  }

  return api.post(`/api/images/upload/${imageType}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export default {
  uploadExcel,
  getImageQuestions,
  getImageQuestionStats,
  getImageQuestion,
  updateImageQuestion,
  deleteImageQuestion,
  verifyImages,
  getImageUrl,
  getQuestionImageUrl,
  getAnswerImageUrl,
  checkImageExists,
  listImages,
  createImageQuestion,
  getMissingImages,
  uploadImage,
  getImageReferences,
  renameImage,
}
