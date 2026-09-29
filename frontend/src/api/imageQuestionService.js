// src/api/imageQuestionService.js
// 圖片題目管理 API 服務

import api from './axios'

/**
 * 上傳 Excel 檔案匯入圖片題目
 * @param {File} file - Excel 檔案
 * @param {boolean} previewOnly - 是否僅預覽（true = 只預覽，false = 預覽並儲存）
 * @param {string} [sourceFilename] - 確認儲存時回傳預覽階段拿到的原始檔名，讓後端記錄在匯入批次上
 * @returns {Promise} 預覽結果
 */
export function uploadExcel(file, previewOnly = true, sourceFilename = null) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('preview_only', previewOnly)
  if (sourceFilename) {
    formData.append('source_filename', sourceFilename)
  }

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
 * @param {string} [params.import_batch_id] - 匯入批次篩選
 * @param {number} [params.page=1] - 頁碼
 * @param {number} [params.size=20] - 每頁數量
 * @returns {Promise} 題目清單
 */
export function getImageQuestions(params = {}) {
  return api.get('/api/image-questions/', { params })
}

/**
 * 取得匯入批次清單(最新在前)
 * @returns {Promise} { batches: [{ batch_id, source_filename, imported_at, total, verified, missing }] }
 */
export function getImportBatches() {
  return api.get('/api/image-questions/import-batches')
}

/**
 * 刪除整個匯入批次(該批次匯入的題目全部軟刪)
 * @param {string} batchId - 匯入批次 ID
 * @param {boolean} [deleteOrphanImages=false] - 是否一併刪除未被其他題目引用的圖片檔
 * @returns {Promise} { batch_id, deleted_questions, deleted_images, kept_images }
 */
export function deleteImportBatch(batchId, deleteOrphanImages = false) {
  return api.delete(`/api/image-questions/import-batches/${batchId}`, {
    params: { delete_orphan_images: deleteOrphanImages },
  })
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
 * 批次刪除圖片題目(軟刪)
 * @param {number[]} ids - 要刪除的題目 ID 列表
 * @returns {Promise} { success_count, failed_count, failed_ids }
 */
export function batchDeleteImageQuestions(ids) {
  return api.post('/api/image-questions/batch-delete', { ids })
}

/**
 * 批次改標籤(科目/年級/章節;只帶要更新的欄位)
 * @param {number[]} ids - 要更新的題目 ID 列表
 * @param {Object} fields - { subject?, grade?, chapter? }
 * @returns {Promise} { success_count, failed_count, failed_ids }
 */
export function batchUpdateImageQuestions(ids, fields = {}) {
  return api.post('/api/image-questions/batch-update', { ids, ...fields })
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
/**
 * 把原圖 URL 換成縮圖 URL(/api/images/thumb/...),清單與圖片庫用,原圖只在放大預覽時載入
 */
export function toThumbUrl(url) {
  if (!url) return url
  return url.replace(/\/api\/images\/(questions|answers)\//, '/api/images/thumb/$1/')
}

export function getImageUrl(filename, imageType = 'questions') {
  if (!filename) return null
  // 去掉結尾斜線:同源模式 baseURL 為 '/',直接串接會變成 '//api/...'(協定相對網址,指向錯誤主機)
  const baseUrl = (api.defaults.baseURL || '').replace(/\/+$/, '')
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
 * 刪除圖片
 * @param {string} imageType - 圖片類型 ('questions' 或 'answers')
 * @param {string} imageName - 圖片名稱（可含或不含副檔名）
 * @param {boolean} [force=false] - 是否強制刪除（即使有題目引用）
 * @returns {Promise} 刪除結果
 * @example
 * {
 *   message: "圖片 'g4_health_ch1' 已刪除",
 *   deleted: "g4_health_ch1",
 *   references_cleared: 2
 * }
 */
export function deleteImage(imageType, imageName, force = false) {
  return api.delete(`/api/images/${imageType}/${imageName}`, {
    params: { force },
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
  getImportBatches,
  deleteImportBatch,
  getImageQuestionStats,
  getImageQuestion,
  updateImageQuestion,
  deleteImageQuestion,
  batchDeleteImageQuestions,
  batchUpdateImageQuestions,
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
  deleteImage,
}
