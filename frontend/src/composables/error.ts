import { AxiosError } from 'axios'

interface IResponseError {
  error: string
  error_i18n: string
  info: string
  key: string
}

export function useError() {
  function getResponseErrorMessage(error: AxiosError) {
    const data = error.response?.data as IResponseError
    const result = { isI18n: false, message: '', key: '' }
    // Format error message
    if (data.error) {
      result.message = data.error
    } else {
      result.message = error.message
    }
    // Format error info
    if (data.info) result.message += ` (${data.info})`
    // Format error key
    if (data.key) result.key = data.key
    return result
  }

  return {
    getResponseErrorMessage,
  }
}
