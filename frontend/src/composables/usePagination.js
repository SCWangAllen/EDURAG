/**
 * Shared pagination composable.
 * Replaces duplicated pagination state, computed properties, and methods
 * found in Documents.vue, Questions.vue, Templates.vue, and SelectPanel.vue.
 */

import { ref, computed } from 'vue'

export function usePagination(fetchFn, defaultPageSize = 20) {
  const currentPage = ref(1)
  const pageSize = ref(defaultPageSize)
  const totalItems = ref(0)

  const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

  const pageNumbers = computed(() => {
    const pages = []
    const start = Math.max(1, currentPage.value - 2)
    const end = Math.min(totalPages.value, currentPage.value + 2)
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    return pages
  })

  const changePage = (page) => {
    if (page < 1 || page > totalPages.value) return
    currentPage.value = page
    if (fetchFn) fetchFn()
  }

  const resetPage = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    pageSize,
    totalItems,
    totalPages,
    pageNumbers,
    changePage,
    resetPage
  }
}
