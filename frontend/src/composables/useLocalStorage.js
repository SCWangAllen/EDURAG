/**
 * Composable for reading/writing JSON values from localStorage.
 *
 * @param {string} key - localStorage key
 * @param {*} defaultValue - Default value when key is missing or parse fails
 * @returns {{ load: () => *, save: (value: *) => void, remove: () => void }}
 */
export function useLocalStorage(key, defaultValue = null) {
  const load = () => {
    try {
      const raw = localStorage.getItem(key)
      return raw !== null ? JSON.parse(raw) : defaultValue
    } catch {
      return defaultValue
    }
  }

  const save = (value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch {
      // quota exceeded or other storage error — silently ignore
    }
  }

  const remove = () => {
    localStorage.removeItem(key)
  }

  return { load, save, remove }
}
