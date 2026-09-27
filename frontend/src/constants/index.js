/**
 * Shared constants used across multiple Vue components.
 * Centralizes hardcoded values that were previously duplicated
 * in Documents.vue, Questions.vue, Generate.vue, Templates.vue,
 * TemplateViewModal.vue, and SelectPanel.vue.
 */
import { GRADE_GROUPS, ALL_GRADE } from './grades.js'

// 題型單一來源(前端)。templateType=true 者為「文字模板題型」,由模板生成流程
// 支援、可在 TemplateModal 建立;diagram_question 走圖片題另一條路,非文字模板。
export const QUESTION_TYPES = [
  { value: 'single_choice', labelKey: 'questions.single_choice', order: 1, templateType: true },
  { value: 'cloze', labelKey: 'questions.cloze', order: 2, templateType: true },
  { value: 'short_answer', labelKey: 'questions.short_answer', order: 3, templateType: true },
  { value: 'true_false', labelKey: 'questions.true_false', order: 4, templateType: true },
  { value: 'matching', labelKey: 'questions.matching', order: 5, templateType: true },
  { value: 'sequence', labelKey: 'questions.sequence', order: 6, templateType: true },
  { value: 'enumeration', labelKey: 'questions.enumeration', order: 7, templateType: true },
  { value: 'diagram_question', labelKey: 'questions.diagram_question', order: 8, templateType: false }
]

// 文字模板題型(TemplateModal 題型下拉、生成流程使用)
export const TEMPLATE_QUESTION_TYPES = QUESTION_TYPES.filter(t => t.templateType)

// 單一來源：frontend/src/constants/grades.js（ESL / Grade Level / Junior Class + ALL）
export const GRADE_OPTIONS = [
  ...GRADE_GROUPS.flatMap(group => group.grades.map(g => ({ value: g.code, label: g.label }))),
  { value: ALL_GRADE.code, label: ALL_GRADE.label }
]

// key = canonical 科目 key（與 useSubjects / 後端正規化一致）；保留舊中文/英文名以相容尚未清理的資料
export const SUBJECT_COLORS = {
  health: 'bg-green-100 text-green-800',
  english: 'bg-blue-100 text-blue-800',
  history: 'bg-purple-100 text-purple-800',
  math: 'bg-red-100 text-red-800',
  science: 'bg-teal-100 text-teal-800',
  chinese: 'bg-orange-100 text-orange-800',
  social: 'bg-yellow-100 text-yellow-800',
  '健康': 'bg-green-100 text-green-800',
  '英文': 'bg-blue-100 text-blue-800',
  '歷史': 'bg-purple-100 text-purple-800',
  '國文': 'bg-red-100 text-red-800',
  '數學': 'bg-green-100 text-green-800',
  '地理': 'bg-purple-100 text-purple-800',
  'Health': 'bg-green-100 text-green-800',
  'English': 'bg-blue-100 text-blue-800',
  'History': 'bg-purple-100 text-purple-800'
}

export const DIFFICULTY_COLORS = {
  'easy': 'bg-green-100 text-green-800',
  'medium': 'bg-yellow-100 text-yellow-800',
  'hard': 'bg-red-100 text-red-800'
}
