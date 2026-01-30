import eventBus from '@/utils/eventBus.js'
import { UI_EVENTS } from '@/utils/eventTypes.js'

export function useToast() {
  const showSuccess = (message, operation = '') => {
    eventBus.emit(UI_EVENTS.SUCCESS_MESSAGE, { message, operation })
  }

  const showError = (message, operation = '', error = undefined) => {
    const payload = { message, operation }
    if (error !== undefined) {
      payload.error = error
    }
    eventBus.emit(UI_EVENTS.ERROR_OCCURRED, payload)
  }

  return { showSuccess, showError }
}
