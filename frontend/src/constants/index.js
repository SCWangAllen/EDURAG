/**
 * Shared constants used across multiple Vue components.
 * Centralizes hardcoded values that were previously duplicated
 * in Documents.vue, Questions.vue, Generate.vue, Templates.vue,
 * TemplateViewModal.vue, and SelectPanel.vue.
 */

export const QUESTION_TYPES = [
  { value: 'single_choice', labelKey: 'questions.single_choice', order: 1 },
  { value: 'cloze', labelKey: 'questions.cloze', order: 2 },
  { value: 'short_answer', labelKey: 'questions.short_answer', order: 3 },
  { value: 'true_false', labelKey: 'questions.true_false', order: 4 },
  { value: 'matching', labelKey: 'questions.matching', order: 5 },
  { value: 'sequence', labelKey: 'questions.sequence', order: 6 },
  { value: 'enumeration', labelKey: 'questions.enumeration', order: 7 },
  { value: 'symbol_identification', labelKey: 'questions.symbol_identification', order: 8 },
  { value: 'image_question', labelKey: 'questions.image_question', order: 9 },
  { value: 'mixed', labelKey: 'questions.mixed', order: 10 },
  { value: 'auto', labelKey: 'questions.auto', order: 11 }
]

export const GRADE_OPTIONS = [
  { value: 'G1', label: 'G1' },
  { value: 'G2', label: 'G2' },
  { value: 'G3', label: 'G3' },
  { value: 'G4', label: 'G4' },
  { value: 'G5', label: 'G5' },
  { value: 'G6', label: 'G6' },
  { value: 'ALL', label: 'ALL' }
]

export const SUBJECT_COLORS = {
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
