/**
 * Shared formatting functions used across multiple Vue components.
 * Replaces duplicated getSubjectColor, getDifficultyColor, formatDate,
 * and getQuestionTypeLabel found in Documents.vue, Questions.vue,
 * Templates.vue, Generate.vue, and TemplateViewModal.vue.
 */

import { SUBJECT_COLORS, DIFFICULTY_COLORS, QUESTION_TYPES } from '@/constants/index.js'

const DEFAULT_COLOR = 'bg-gray-100 text-gray-800'

export function getSubjectColor(subject) {
  return SUBJECT_COLORS[subject] || DEFAULT_COLOR
}

export function getDifficultyColor(difficulty) {
  return DIFFICULTY_COLORS[difficulty] || DEFAULT_COLOR
}

export function formatDate(dateString, options) {
  if (!dateString) return ''
  const defaults = { year: 'numeric', month: '2-digit', day: '2-digit' }
  return new Date(dateString).toLocaleDateString('zh-TW', options || defaults)
}

export function formatDateTime(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatDateTimeFull(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export function getQuestionTypeLabel(type, t) {
  if (!type) return ''
  if (t) {
    const translationKey = `questions.${type}`
    const translation = t(translationKey)
    if (translation !== translationKey) return translation
  }
  const found = QUESTION_TYPES.find(qt => qt.value === type)
  return found ? type : type
}
