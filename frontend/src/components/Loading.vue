<template>
  <div
  :class="severity === 'primary' ? 'tw-text-primary-500' : 'tw-text-white'"
    class="tw-gap-2 tw-flex tw-flex-col tw-absolute tw-z-[100] tw-left-1/2 tw-top-1/2 tw-translate-x-[-50%] tw-translate-y-[-50%]"
  >
    <i class="pi pi-spin pi-spinner tw-mx-auto tw-text-[5rem]" />
  </div>
</template>

<script lang="ts" setup>
defineProps({
 severity: { type: String },
})
</script>