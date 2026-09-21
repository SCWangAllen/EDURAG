import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import './assets/tailwind.css'

// 部署新版後,瀏覽器快取的舊頁面會去抓已不存在的舊 chunk(Failed to fetch dynamically imported module)。
// Vite 會發 vite:preloadError,這裡自動重新整理一次拿新版;用 sessionStorage 避免無限重載。
window.addEventListener('vite:preloadError', (event) => {
  event.preventDefault()
  const key = 'edurag:reloaded-for-preload-error'
  if (sessionStorage.getItem(key) === '1') return
  sessionStorage.setItem(key, '1')
  window.location.reload()
})
window.addEventListener('load', () => sessionStorage.removeItem('edurag:reloaded-for-preload-error'))

createApp(App).use(router).mount('#app')
