// src/api/questionService.js
import api from './axios'  // 之前設定好的 axios 實例

export function generateQuestions(payload) {
  // 使用統一的API端點，後端會根據Mock模式自動選擇實現
  return api.post('/api/generate/', payload)
}

export function ingestDocument(payload) {
  // 文件攝取API
  return api.post('/api/ingest/', payload)
}

export function getHealth() {
  // 健康檢查API
  return api.get('/health')
}

export function fetchHistory(userId) {
  return api.get(`/users/${userId}/history`)
}

// 將其他題目相關、或不同領域的 API 都拆在這個檔案或同級的其他 service
