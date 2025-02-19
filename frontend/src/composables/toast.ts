import { ToastMessageOptions } from 'primevue/toast'
import { useToast as usePrimeVueToast } from 'primevue/usetoast'

export function useToast() {
  const toast = usePrimeVueToast()

  function showToast(
    severity: ToastMessageOptions['severity'],
    summary: string,
    detail?: string,
    group?: string
  ) {
    toast.add({
      severity: severity,
      summary: summary,
      detail: detail,
      life: 10000,
      group: group,
    })
  }

  return {
    showToast,
  }
}
