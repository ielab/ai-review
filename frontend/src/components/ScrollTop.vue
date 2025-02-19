<template>
  <ScrollTop
    v-tooltip.top="'Go to the top'"
    unstyled
    :pt="{
      root: 'tw-rounded-full tw-w-[3rem] tw-h-[3rem] tw-border-none tw-cursor-pointer tw-bg-black tw-bg-opacity-50',
      icon: 'tw-text-white',
    }"
  />
</template>

<script setup lang="ts">
import ScrollTop from 'primevue/scrolltop'
</script>
