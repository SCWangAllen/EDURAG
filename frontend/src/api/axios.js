import axios from 'axios'

// 根據環境自動選擇 backend URL
// 1. 明確設定 VITE_API_BASE_URL（非空）時一律尊重之。
//    生產同源部署請設為 '/'：請求走同源 /api/*（由 nginx 反代到 backend，見 nginx.prod.conf）。
//    ⚠️ 用 '/' 而非空字串當同源訊號：Docker build-arg 無法區分「未傳入」與「傳入空字串」，
//       空字串會讓 dev docker build 也誤判為同源；'/' 為非空，可安全與 fallback 區分。
// 2. 未設定且為遠端主機（非 localhost）→ 沿用 http://<hostname>:8988。
// 3. 本機開發 fallback → http://localhost:8988。
const getBaseURL = () => {
  const configured = import.meta.env.VITE_API_BASE_URL
  if (configured) {
    return configured
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
