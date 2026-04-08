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
