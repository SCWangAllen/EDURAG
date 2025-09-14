import mitt from 'mitt'
import { ALL_EVENTS, validateEventPayload } from './eventTypes.js'

/**
 * 全域事件匯流排系統
 * 提供型別安全的事件發送和監聽功能
 * 支援 debug 模式與詳細日誌追蹤
 */
class EventBus {
  constructor() {
    this.emitter = mitt()
    this.debug = process.env.NODE_ENV === 'development'
    this.eventHistory = []
    this.maxHistorySize = 100
    
    if (this.debug) {
      console.log('[EventBus] 初始化事件匯流排系統')
    }
  }
  
  /**
   * 發送事件
   * @param {string} eventType - 事件類型
   * @param {object} payload - 事件資料
   * @param {object} options - 發送選項
   */
  emit(eventType, payload = {}, options = {}) {
    const timestamp = new Date().toISOString()
    
    // 驗證事件類型
    if (!this._isValidEventType(eventType)) {
      console.warn(`[EventBus] 未知的事件類型: ${eventType}`)
    }
    
    // 驗證 payload 結構
    if (options.validate !== false) {
      const eventName = this._getEventNameFromType(eventType)
      if (eventName && !validateEventPayload(eventName, payload)) {
        console.warn(`[EventBus] Payload 驗證失敗: ${eventType}`)
      }
    }
    
    // 記錄事件歷史
    this._recordEvent('emit', eventType, payload, timestamp)
    
    // 發送事件
    this.emitter.emit(eventType, {
      ...payload,
      timestamp,
      eventType
    })
    
    if (this.debug) {
      console.log(`[EventBus] 發送事件: ${eventType}`, payload)
    }
  }
  
  /**
   * 監聽事件
   * @param {string} eventType - 事件類型
   * @param {function} handler - 事件處理器
   */
  on(eventType, handler) {
    if (typeof handler !== 'function') {
      throw new Error('[EventBus] 事件處理器必須是函數')
    }
    
    // 包裝處理器以提供額外功能
    const wrappedHandler = (data) => {
      const timestamp = new Date().toISOString()
      this._recordEvent('receive', eventType, data, timestamp)
      
      if (this.debug) {
        console.log(`[EventBus] 接收事件: ${eventType}`, data)
      }
      
      try {
        handler(data)
      } catch (error) {
        console.error(`[EventBus] 事件處理器執行失敗 [${eventType}]:`, error)
      }
    }
    
    this.emitter.on(eventType, wrappedHandler)
    
    if (this.debug) {
      console.log(`[EventBus] 註冊監聽器: ${eventType}`)
    }
    
    // 返回取消監聽的函數
    return () => this.off(eventType, wrappedHandler)
  }
  
  /**
   * 單次監聽事件
   * @param {string} eventType - 事件類型
   * @param {function} handler - 事件處理器
   */
  once(eventType, handler) {
    const unsubscribe = this.on(eventType, (data) => {
      handler(data)
      unsubscribe()
    })
    return unsubscribe
  }
  
  /**
   * 取消監聽事件
   * @param {string} eventType - 事件類型
   * @param {function} handler - 事件處理器
   */
  off(eventType, handler) {
    this.emitter.off(eventType, handler)
    
    if (this.debug) {
      console.log(`[EventBus] 取消監聽: ${eventType}`)
    }
  }
  
  /**
   * 清除所有監聽器
   * @param {string} eventType - 特定事件類型，不提供則清除所有
   */
  clear(eventType) {
    if (eventType) {
      this.emitter.off(eventType)
    } else {
      this.emitter.all.clear()
    }
    
    if (this.debug) {
      console.log(`[EventBus] 清除監聽器: ${eventType || '所有事件'}`)
    }
  }
  
  /**
   * 取得事件歷史記錄
   * @param {number} limit - 限制返回數量
   */
  getHistory(limit = 50) {
    return this.eventHistory.slice(-limit)
  }
  
  /**
   * 清除事件歷史
   */
  clearHistory() {
    this.eventHistory = []
    if (this.debug) {
      console.log('[EventBus] 清除事件歷史')
    }
  }
  
  /**
   * 取得目前所有活躍的監聽器
   */
  getActiveListeners() {
    const listeners = {}
    for (const [eventType, handlers] of this.emitter.all) {
      listeners[eventType] = handlers.length
    }
    return listeners
  }
  
  /**
   * 設定 debug 模式
   * @param {boolean} enabled - 是否啟用 debug
   */
  setDebug(enabled) {
    this.debug = enabled
    console.log(`[EventBus] Debug 模式: ${enabled ? '啟用' : '關閉'}`)
  }
  
  /**
   * 私有方法：驗證事件類型
   */
  _isValidEventType(eventType) {
    return Object.values(ALL_EVENTS).includes(eventType)
  }
  
  /**
   * 私有方法：從事件類型取得事件名稱
   */
  _getEventNameFromType(eventType) {
    // 將 'template:updated' 轉換為 'TemplateUpdated'
    const parts = eventType.split(':')
    if (parts.length === 2) {
      const [category, action] = parts
      return category.charAt(0).toUpperCase() + category.slice(1) +
             action.charAt(0).toUpperCase() + action.slice(1)
    }
    return null
  }
  
  /**
   * 私有方法：記錄事件歷史
   */
  _recordEvent(action, eventType, payload, timestamp) {
    this.eventHistory.push({
      action,
      eventType,
      payload: JSON.parse(JSON.stringify(payload)), // 深拷貝
      timestamp
    })
    
    // 限制歷史記錄大小
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift()
    }
  }
}

// 建立全域實例
const eventBus = new EventBus()

// 導出常用事件類型以便使用
export { ALL_EVENTS, TEMPLATE_EVENTS, SUBJECT_EVENTS, DOCUMENT_EVENTS, QUESTION_EVENTS, UI_EVENTS, SYSTEM_EVENTS } from './eventTypes.js'

// 導出事件匯流排實例
export default eventBus

// 導出便利函數
export const {
  emit,
  on,
  once,
  off,
  clear
} = eventBus

/**
 * 高階組件：提供事件監聽的 Vue 混入
 */
export const EventBusMixin = {
  data() {
    return {
      eventUnsubscribers: []
    }
  },
  
  methods: {
    /**
     * 組件內事件監聽（自動清理）
     */
    $listenTo(eventType, handler) {
      const unsubscribe = eventBus.on(eventType, handler)
      this.eventUnsubscribers.push(unsubscribe)
      return unsubscribe
    },
    
    /**
     * 組件內事件發送
     */
    $emitEvent(eventType, payload, options) {
      eventBus.emit(eventType, payload, options)
    }
  },
  
  beforeUnmount() {
    // 自動清理所有事件監聽器
    this.eventUnsubscribers.forEach(unsubscribe => {
      if (typeof unsubscribe === 'function') {
        unsubscribe()
      }
    })
    this.eventUnsubscribers = []
  }
}

/**
 * Vue 3 Composition API 支援
 */
export function useEventBus() {
  const listeners = []
  
  const listenTo = (eventType, handler) => {
    const unsubscribe = eventBus.on(eventType, handler)
    listeners.push(unsubscribe)
    return unsubscribe
  }
  
  const emitEvent = (eventType, payload, options) => {
    eventBus.emit(eventType, payload, options)
  }
  
  const cleanup = () => {
    listeners.forEach(unsubscribe => {
      if (typeof unsubscribe === 'function') {
        unsubscribe()
      }
    })
    listeners.length = 0
  }
  
  // 在組件卸載時自動清理
  if (typeof window !== 'undefined' && window.vue) {
    const { onUnmounted } = window.vue
    if (onUnmounted) {
      onUnmounted(cleanup)
    }
  }
  
  return {
    listenTo,
    emitEvent,
    cleanup,
    eventBus
  }
}