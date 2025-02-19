import { computed, ref, watch } from 'vue'
import { onBeforeRouteUpdate, onBeforeRouteLeave, useRoute, NavigationGuardNext } from 'vue-router'

export function useDirty() {
  const route = useRoute()

  const isDirty = ref(false)
  const cancelKey = ref(0)

  const isCurrentRouteDirty = computed(() => route.meta.dirty)

  watch(
    () => route.meta.dirty,
    (value) => (isDirty.value = !!value)
  )

  // Check `isDirty` before leaving the page
  // * If `isDirty` is true, ask the user if they want to leave the page
  // * If the user confirms, clear `isDirty` and leave the page
  // * If the user cancels, stay on the page
  function checkDirty(next: NavigationGuardNext) {
    if (!isDirty.value || route.meta.bypass) {
      return next()
    }
    if (window.confirm('You have unsaved changes. Are you sure you want to leave?')) {
      clearDirty()
      return next()
    }
    cancelKey.value++
    return next(false)
  }

  onBeforeRouteLeave((_, __, next) => checkDirty(next))
  onBeforeRouteUpdate((_, __, next) => checkDirty(next))

  // Ask confirmation
  function askConfirmation() {
    if (!route.meta.dirty) return true
    return window.confirm('You have unsaved changes. Are you sure you want to leave?')
  }

  // Set `isDirty` to true when the user changes the form
  function setDirty() {
    isDirty.value = true
    route.meta.dirty = true
    window.onbeforeunload = () => true
  }

  // Clear `isDirty` when the user submits the form
  function clearDirty() {
    isDirty.value = false
    route.meta.dirty = false
    window.onbeforeunload = null
  }

  return { isDirty, setDirty, clearDirty, isCurrentRouteDirty, askConfirmation, cancelKey }
}
