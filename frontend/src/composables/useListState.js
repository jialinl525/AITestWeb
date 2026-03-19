import { ref } from 'vue'

const cloneShallow = (value) => ({ ...(value || {}) })

export const useFilterState = (initialFilters = {}) => {
  const defaults = cloneShallow(initialFilters)
  const filters = ref(cloneShallow(defaults))

  const resetFilters = () => {
    filters.value = cloneShallow(defaults)
  }

  return {
    filters,
    resetFilters
  }
}

export const usePaginationState = (initialPagination = {}) => {
  const defaults = {
    page: 1,
    pageSize: 30,
    total: 0,
    ...cloneShallow(initialPagination)
  }
  const pagination = ref(cloneShallow(defaults))

  const resetPage = () => {
    pagination.value.page = 1
  }

  const setPage = (page) => {
    pagination.value.page = Number(page || 1)
  }

  const setPageSize = (size, resetToFirstPage = true) => {
    pagination.value.pageSize = Number(size || defaults.pageSize)
    if (resetToFirstPage) {
      resetPage()
    }
  }

  const setTotal = (total) => {
    pagination.value.total = Number(total || 0)
  }

  return {
    pagination,
    resetPage,
    setPage,
    setPageSize,
    setTotal
  }
}