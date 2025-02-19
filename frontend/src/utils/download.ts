import axios from 'axios'

import { getTokenHeader } from './auth'

export const downloadFileFromURL = (url: string, filename: string) => {
  const link = document.createElement('a')
  link.download = filename
  link.href = url
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  // Delete the link
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const getFileToDownload = async (keyword: string, fileType: string) => {
  // Get pre-signed URL
  const params = { params: { keyword: keyword, file_type: fileType } }
  const result = await axios.get('/encoder/s3', getTokenHeader(params))
  // Download file
  const downloadingResult = await axios.get(result.data.url, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([downloadingResult.data]))
  return { url, filename: result.data.file_name }
}

export const formatFileSize = (sizeGB: number | null | undefined) => {
  if (!sizeGB) return ''
  return `${sizeGB.toFixed(2)} GB`
}
