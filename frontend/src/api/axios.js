import axios from 'axios'

// 根據環境自動選擇 backend URL
// 1. 優先使用環境變數 VITE_API_BASE_URL
// 2. 如果是遠端訪問（非 localhost），使用當前 hostname + port 8988
// 3. 最後 fallback 到 localhost:8988
const getBaseURL = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // 如果訪問的不是 localhost，表示是遠端訪問（如 34.80.48.137）
  // 則使用相同的 hostname + backend port
  const hostname = window.location.hostname
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:8988`
  }

  // 本機開發環境，使用 localhost:8988
  return 'http://localhost:8988'
}

const api = axios.create({
  baseURL: getBaseURL(),
  headers: { 'Content-Type': 'application/json' }
})

export default api
