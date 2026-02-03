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
    }
    
    // 驗證 payload 結構
    if (options.validate !== false) {
      const eventName = this._getEventNameFromType(eventType)
      if (eventName && !validateEventPayload(eventName, payload)) {
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
      }
      
      try {
        handler(data)
      } catch (error) {
      }
    }
    
    this.emitter.on(eventType, wrappedHandler)
    
    if (this.debug) {
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