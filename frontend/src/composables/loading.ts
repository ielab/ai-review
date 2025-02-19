import { ref } from 'vue'

export function useLoading(initState: boolean | undefined = true) {
  const isLoading = ref<boolean>(initState)

  function setLoading(state: boolean) {
    isLoading.value = state
  }

  return { isLoading, setLoading }
}
