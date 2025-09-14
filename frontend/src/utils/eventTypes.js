/**
 * 事件類型常數定義
 * 集中管理所有事件類型，確保一致性與型別安全
 */

// 模板相關事件
export const TEMPLATE_EVENTS = {
  UPDATED: 'template:updated',
  DELETED: 'template:deleted',
  CREATED: 'template:created',
  SELECTED: 'template:selected',
  PARAMETERS_CHANGED: 'template:parameters_changed'
}

// 科目相關事件
export const SUBJECT_EVENTS = {
  UPDATED: 'subject:updated',
  DELETED: 'subject:deleted',
  CREATED: 'subject:created',
  SELECTED: 'subject:selected'
}

// 文件相關事件
export const DOCUMENT_EVENTS = {
  UPLOADED: 'document:uploaded',
  DELETED: 'document:deleted',
  UPDATED: 'document:updated',
  SELECTED: 'document:selected'
}

// 題目相關事件
export const QUESTION_EVENTS = {
  GENERATED: 'question:generated',
  DELETED: 'question:deleted',
  EXPORTED: 'question:exported'
}

// UI 相關事件
export const UI_EVENTS = {
  LOADING_START: 'ui:loading_start',
  LOADING_END: 'ui:loading_end',
  ERROR_OCCURRED: 'ui:error_occurred',
  SUCCESS_MESSAGE: 'ui:success_message',
  MODAL_OPEN: 'ui:modal_open',
  MODAL_CLOSE: 'ui:modal_close'
}

// 系統相關事件
export const SYSTEM_EVENTS = {
  RELOAD_DATA: 'system:reload_data',
  CLEAR_CACHE: 'system:clear_cache',
  MODE_CHANGED: 'system:mode_changed'
}

// 合併所有事件類型
export const ALL_EVENTS = {
  ...TEMPLATE_EVENTS,
  ...SUBJECT_EVENTS,
  ...DOCUMENT_EVENTS,
  ...QUESTION_EVENTS,
  ...UI_EVENTS,
  ...SYSTEM_EVENTS
}

/**
 * 事件 Payload 資料結構定義
 */
export const EventPayloadTypes = {
  // 模板事件 payload
  TemplateUpdated: {
    id: 'number',
    name: 'string',
    subject: 'string',
    content: 'string',
    params: 'object'
  },
  
  TemplateDeleted: {
    id: 'number',
    name: 'string'
  },
  
  TemplateCreated: {
    id: 'number',
    name: 'string',
    subject: 'string'
  },
  
  TemplateSelected: {
    template: 'object'
  },
  
  TemplateParametersChanged: {
    templateId: 'number',
    params: 'object'
  },
  
  // 科目事件 payload
  SubjectUpdated: {
    id: 'number',
    name: 'string',
    description: 'string',
    color: 'string'
  },
  
  SubjectDeleted: {
    id: 'number',
    name: 'string'
  },
  
  SubjectCreated: {
    id: 'number',
    name: 'string'
  },
  
  SubjectSelected: {
    subject: 'object'
  },
  
  // 文件事件 payload
  DocumentUploaded: {
    id: 'number',
    title: 'string',
    subject: 'string'
  },
  
  DocumentDeleted: {
    id: 'number',
    title: 'string'
  },
  
  DocumentSelected: {
    documents: 'array'
  },
  
  // 題目事件 payload
  QuestionGenerated: {
    questions: 'array',
    count: 'number',
    templateUsed: 'string'
  },
  
  QuestionDeleted: {
    id: 'number'
  },
  
  QuestionExported: {
    format: 'string',
    count: 'number',
    filename: 'string'
  },
  
  // UI 事件 payload
  LoadingStart: {
    operation: 'string',
    message: 'string'
  },
  
  LoadingEnd: {
    operation: 'string'
  },
  
  ErrorOccurred: {
    error: 'object',
    operation: 'string',
    message: 'string'
  },
  
  SuccessMessage: {
    message: 'string',
    operation: 'string'
  },
  
  ModalOpen: {
    modalId: 'string',
    data: 'object'
  },
  
  ModalClose: {
    modalId: 'string'
  },
  
  // 系統事件 payload
  ReloadData: {
    scope: 'string'
  },
  
  ClearCache: {
    cacheType: 'string'
  },
  
  ModeChanged: {
    oldMode: 'string',
    newMode: 'string'
  }
}

/**
 * 事件驗證工具
 * 驗證事件 payload 是否符合預期結構
 */
export function validateEventPayload(eventType, payload) {
  const expectedStructure = EventPayloadTypes[eventType]
  if (!expectedStructure) {
    console.warn(`[EventBus] Unknown event type: ${eventType}`)
    return true // 未知事件類型，不進行驗證
  }
  
  for (const [key, expectedType] of Object.entries(expectedStructure)) {
    if (!(key in payload)) {
      console.warn(`[EventBus] Missing required field '${key}' in ${eventType} payload`)
      return false
    }
    
    const actualType = Array.isArray(payload[key]) ? 'array' : typeof payload[key]
    if (actualType !== expectedType && payload[key] !== null && payload[key] !== undefined) {
      console.warn(`[EventBus] Field '${key}' should be ${expectedType}, got ${actualType} in ${eventType} payload`)
      return false
    }
  }
  
  return true
}