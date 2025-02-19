import { reactive } from 'vue'
import { IAccountAuthStore } from '@/types/auth'
import { DEFAULT_ACCOUNT_AUTH_STORE } from '@/defaults/auth'

export const accountAuthStore: IAccountAuthStore = reactive({
  ...DEFAULT_ACCOUNT_AUTH_STORE,
})

export function cleanAccountAuthStore() {
  Object.assign(accountAuthStore, DEFAULT_ACCOUNT_AUTH_STORE)
}
