<template>
  <div
    class="tw-flex tw-flex-col tw-items-center tw-justify-center tw-text-center tw-gap-x-2"
  >
    <div
      :class="'tw-bg-' + props.color + '-200'"
      class="tw-w-[2.5rem] tw-h-[2.5rem] tw-rounded-lg tw-flex tw-justify-center"
    >
      <div
        class="tw-w-[1.5rem] tw-h-[1.5rem] tw-rounded tw-mt-[0.3rem] tw-flex tw-justify-center"
        :class="
          props.secondary ? 'tw-bg-white' : 'tw-bg-' + props.color + '-500'
        "
      >
        <p
          v-if="!props.keyIcon"
          class="tw-font-bold tw-text-white tw-text-xs"
        >
          {{ props.keyLabel }}
        </p>
        <i
          v-if="props.keyIcon !== 'Option'"
          class="tw-text-xs"
          :class="[
            props.keyIcon,
            props.secondary
              ? 'tw-text-' + props.color + '-500'
              : 'tw-text-white',
          ]"
        ></i>

        <img
          v-else
          :src="optionIcon"
          class="tw-h-[0.6rem] tw-mt-1"
        />
      </div>
    </div>
    <div class="tw-font-medium tw-text-sm">
      <p v-if="props.event">
        {{ props.event }}:
        <span
          :class="'tw-text-' + props.color + '-500'"
          class="tw-font-bold"
          >{{ props.keyLabel }}</span
        >
      </p>
      <p>{{ props.for }}</p>
      <i :class="props.forIcon"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  color: string
  keyLabel?: string
  keyIcon?: string
  event?: string
  for?: string
  forIcon?: string
  secondary?: boolean
}>()

import optionIcon from '@/assets/icons/option.png'
</script>
