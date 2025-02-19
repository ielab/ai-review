import axios from 'axios'
import Cookies from 'js-cookie'

import { IAccountAuthStore } from '@/types/auth'

const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY

export function getTokenHeader(otherConfig = {}, otherHeaders = {}) {
  return {
    headers: {
      Authorization: `Token ${Cookies.get(TOKEN_KEY)}`,
      ...otherHeaders,
    },
    ...otherConfig,
  }
}

export function storeToken(token: string) {
  Cookies.set(TOKEN_KEY, token)
}

// Get account info of current user
export async function getAccountInfo() {
  try {
    // Getting account info
    return (await axios.get('/auth/current', getTokenHeader())).data as IAccountAuthStore
  } catch (error) {
    return null
  }
}
