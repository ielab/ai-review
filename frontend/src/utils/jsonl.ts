import axios from 'axios'

const axiosInstace = axios.create({ baseURL: '' })

export const readJSONL = async (url: string) => {
  const response = await axiosInstace.get(url)
  const text = response.data
  return text
}

export const parseJSONL = (text: string) => {
  const lines = text.split('\n')
  const data = lines.map((line) => {
    if (line === '') return
    return JSON.parse(line)
  })
  return data
}
