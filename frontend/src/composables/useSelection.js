/**
 * Shared multi-selection composable.
 * Replaces duplicated selection state and methods found in
 * Documents.vue, Questions.vue, and SelectPanel.vue.
 */

import { ref, computed } from 'vue'

export function useSelection(idKey = 'id') {
  const selectedItems = ref([])

  const isAllSelected = (allItems) => {
    if (!allItems || allItems.length === 0) return false
    return allItems.every(item => selectedItems.value.some(s => s[idKey] === item[idKey]))
  }

  const isSelected = (item) => {
    const id = typeof item === 'object' ? item[idKey] : item
    return selectedItems.value.some(s => s[idKey] === id)
  }

  const toggleSelection = (item) => {
    const index = selectedItems.value.findIndex(s => s[idKey] === item[idKey])
    if (index > -1) {
      selectedItems.value.splice(index, 1)
    } else {
      selectedItems.value.push(item)
    }
  }

  const toggleSelectAll = (allItems) => {
    const allSelected = isAllSelected(allItems)
    if (allSelected) {
      selectedItems.value = []
    } else {
      selectedItems.value = [...allItems]
    }
  }

  const clearSelection = () => {
    selectedItems.value = []
  }

  return {
    selectedItems,
    isAllSelected,
    isSelected,
    toggleSelection,
    toggleSelectAll,
    clearSelection
  }
}
