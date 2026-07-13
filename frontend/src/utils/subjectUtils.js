/**
 * Compute a readable text color (black/white) for the given background color.
 * 單一出口：取代散落於各元件的重複實作。
 *
 * @param {string} backgroundColor - Hex color like "#3B82F6"
 * @returns {string} "#000000" or "#FFFFFF"
 */
export function getTextColor(backgroundColor) {
  const hex = (backgroundColor || '#3B82F6').replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
  return brightness > 155 ? '#000000' : '#FFFFFF'
}

/**
 * Get subject display name with optional grade info.
 * Works with both a template object (has subject/subject_id) and a plain subject name string.
 *
 * @param {string|object} subjectOrTemplate - Subject name string or template/object with subject/subject_id
 * @param {Array} subjectList - Array of subject objects with { id, name, grade, ... }
 * @returns {string} Display name like "Health (Grade 7)" or just "Health"
 */
export function getSubjectDisplayName(subjectOrTemplate, subjectList) {
  let subjectName = subjectOrTemplate
  let subjectId = null

  if (typeof subjectOrTemplate === 'object' && subjectOrTemplate !== null) {
    subjectId = subjectOrTemplate.subject_id
    subjectName = subjectOrTemplate.subject
  }

  const list = subjectList || []

  // Prefer lookup by subject_id
  if (subjectId) {
    const found = list.find(s => s.id === subjectId)
    if (found) {
      return found.grade ? `${found.name} (${found.grade})` : found.name
    }
  }

  // Fallback: lookup by subject name
  if (subjectName) {
    const found = list.find(s => s.name === subjectName)
    if (found && found.grade) {
      return `${subjectName} (${found.grade})`
    }
  }

  return subjectName || 'Unknown'
}
