<template>
  <div class="tw-flex tw-w-full tw-min-h-[86vh]">
    <div
      v-if="icon && title"
      class="tw-flex tw-flex-col tw-px-24 tw-py-8 tw-bg-primary-50 tw-gap-y-2"
    >
      <div class="tw-flex tw-items-center tw-gap-2">
        <i
          :class="icon"
          class="fa-2xl tw-text-primary-500"
        />
        <div class="tw-pr-8 tw-text-3xl tw-font-bold">{{ title }}</div>
      </div>
      <slot name="subtitle">
        <p>{{ subtitle }}</p>
      </slot>
    </div>

    <div class="tw-px-24 tw-py-8 tw-w-full"><slot></slot></div>
  </div>
</template>

<script lang="ts" setup>
// const props = defineProps({
//  icon: { type: String },
//  title: { type: String },
// })

defineProps({
  icon: { type: String },
  title: { type: String },
  subtitle: { type: String },
})
</script>
