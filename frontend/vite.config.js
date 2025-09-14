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
    // 強制重新載入模組，避免快取問題
    force: true,
    // 關閉檔案系統快取
    fs: {
      cachedChecks: false
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
