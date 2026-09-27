import eventBus from '@/utils/eventBus.js'
import { UI_EVENTS } from '@/utils/eventTypes.js'

export function useToast() {
  const showSuccess = (message, operation = '') => {
    eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, { message, operation })
  }

  // title 為選填:大多數呼叫端沿用既有的通用「操作失敗」標題;
  // 需要更具體標題時(如「更新科目失敗」)可傳入,不影響其他既有呼叫
  const showError = (message, operation = '', error = undefined, title = undefined) => {
    const payload = { message, operation }
    if (error !== undefined) {
      payload.error = error
    }
    if (title) {
      payload.title = title
    }
    eventBus.emit(UI_EVENTS.ERROR_OCCURRED, payload)
  }

  const showInfo = (message, operation = '') => {
    eventBus.emit(UI_EVENTS.INFO_MESSAGE, { message, operation })
  }

  return { showSuccess, showError, showInfo }
}
