import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    // 強制重新載入模組，避免快取問題
    force: true,
    // 關閉檔案系統快取
    fs: {
      cachedChecks: false
    },
    // HMR 設定（Docker 容器內需要）
    watch: {
      usePolling: true
    },
    // 代理 API 請求到後端，避免 CORS 問題
    // Docker 容器內使用服務名稱 'backend'，本機開發使用 localhost
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://backend:8000',
        changeOrigin: true,
      }
    }
  },
  // 優化配置，避免模組快取問題  
  optimizeDeps: {
    // 強制重建依賴
    force: true
  },
  build: {
    // 添加版本號碼到檔案名，避免瀏覽器快取
    rollupOptions: {
      output: {
        // 為 chunks 添加 hash
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  }
})
