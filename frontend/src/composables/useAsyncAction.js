import { ElMessage } from 'element-plus'

export const useAsyncAction = () => {
  const runAsync = async (action, options = {}) => {
    const {
      loadingRef = null,
      errorMessage = '',
      onError = null,
      onFinally = null,
      rethrow = false,
    } = options

    if (loadingRef) {
      loadingRef.value = true
    }

    try {
      return await action()
    } catch (error) {
      if (typeof onError === 'function') {
        onError(error)
      } else if (errorMessage) {
        ElMessage.error(error?.response?.data?.detail || errorMessage)
      }

      if (rethrow) {
        throw error
      }
      return null
    } finally {
      if (loadingRef) {
        loadingRef.value = false
      }
      if (typeof onFinally === 'function') {
        onFinally()
      }
    }
  }

  return {
    runAsync,
  }
}