<template>
  <div class="fixed top-4 right-4 z-50 max-w-sm w-full">
    <transition-group name="toast" tag="div" class="space-y-2">
      <div
        v-for="toast in visibleToasts"
        :key="toast.id"
        :class="[
          'bg-white shadow-lg rounded-lg border-l-4 p-4 flex items-start',
          getToastClass(toast.type)
        ]"
      >
        <div :class="['flex-shrink-0 mr-3', getIconClass(toast.type)]">
          <!-- 成功圖標 -->
          <svg v-if="toast.type === 'success'" class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <!-- 錯誤圖標 -->
          <svg v-else-if="toast.type === 'error'" class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <!-- 警告圖標 -->
          <svg v-else-if="toast.type === 'warning'" class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <!-- 資訊圖標 -->
          <svg v-else class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="flex-1">
          <p :class="['text-sm font-medium', getTextClass(toast.type)]">
            {{ toast.title }}
          </p>
          <p v-if="toast.message" class="text-sm text-gray-600 mt-1">
            {{ toast.message }}
          </p>
        </div>
        <button
          @click="removeToast(toast.id)"
          class="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-600"
        >
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import eventBus, { UI_EVENTS } from '@/utils/eventBus.js'
import { useLanguage } from '../composables/useLanguage.js'

export default {
  name: 'Toast',
  setup() {
    const { t } = useLanguage()
    const toasts = ref([])
    let nextId = 1

    const visibleToasts = computed(() => {
      return toasts.value.filter(toast => toast.visible)
    })

    // 監聽事件匯流排的通知事件
    eventBus.on(UI_EVENTS.SUCCESS_MESSAGE, ({ message, operation }) => {
      const completedMsg = operation ? t('toast.operationCompleted').replace('{operation}', operation) : message
      showToast('success', t('toast.operationSuccess'), message || completedMsg)
    })

    eventBus.on(UI_EVENTS.ERROR_OCCURRED, ({ message, operation, error }) => {
      const errorMsg = error?.response?.data?.detail || error?.message || message || t('toast.unknownError')
      showToast('error', t('toast.operationFailed'), errorMsg)
    })

    const showToast = (type, title, message, duration = 5000) => {
      const toast = {
        id: nextId++,
        type,
        title,
        message,
        visible: true
      }

      toasts.value.push(toast)

      // 自動移除
      setTimeout(() => {
        removeToast(toast.id)
      }, duration)
    }

    const removeToast = (id) => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index > -1) {
        toasts.value[index].visible = false
        setTimeout(() => {
          toasts.value.splice(index, 1)
        }, 300) // 等待動畫完成
      }
    }

    const getToastClass = (type) => {
      switch (type) {
        case 'success': return 'border-green-400'
        case 'error': return 'border-red-400'
        case 'warning': return 'border-yellow-400'
        case 'info': return 'border-blue-400'
        default: return 'border-gray-400'
      }
    }

    const getIconClass = (type) => {
      switch (type) {
        case 'success': return 'text-green-400'
        case 'error': return 'text-red-400'
        case 'warning': return 'text-yellow-400'
        case 'info': return 'text-blue-400'
        default: return 'text-gray-400'
      }
    }

    const getTextClass = (type) => {
      switch (type) {
        case 'success': return 'text-green-800'
        case 'error': return 'text-red-800'
        case 'warning': return 'text-yellow-800'
        case 'info': return 'text-blue-800'
        default: return 'text-gray-800'
      }
    }


    // 提供程式化調用方法
    const toast = {
      success: (title, message) => showToast('success', title, message),
      error: (title, message) => showToast('error', title, message),
      warning: (title, message) => showToast('warning', title, message),
      info: (title, message) => showToast('info', title, message)
    }

    return {
      t,
      visibleToasts,
      removeToast,
      getToastClass,
      getIconClass,
      getTextClass,
      toast
    }
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>