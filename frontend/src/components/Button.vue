<template>
  <Button
    v-if="type == 'light'"
    :label="label"
    :icon="isLoading ? 'pi pi-spin pi-spinner' : icon"
    :badge="badge"
    :severity="severity"
    class="tw-justify-center"
    :class="{ 'tw-cursor-not-allowed': disabled }"
    :isLoading="isLoading"
    :disabled="disabled"
    outlined
  />
  <Button
    v-else
    :label="label"
    :icon="isLoading ? 'pi pi-spin pi-spinner' : icon"
    :badge="badge"
    :severity="severity"
    class="tw-justify-center disabled:tw-cursor-not-allowed"
    :class="{
      'tw-bg-slate-300 tw-border-0': disabled && !isLoading,
      'tw-cursor-not-allowed': disabled,
    }"
    :isLoading="isLoading"
    :disabled="disabled"
  />
</template>

<script lang="ts" setup>
import { PropType, computed } from 'vue'

import Button from 'primevue/button'

const props = defineProps({
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  badge: { type: String, default: '' },
  type: { type: String as PropType<'default' | 'light'>, default: 'default' },
  severity: { type: String, default: 'primary' },
  disabled: { type: Boolean },
  isLoading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:state'])

const isLoading = computed({
  get() {
    return props.isLoading
  },
  set(value) {
    emit('update:state', value)
  },
})
</script>
