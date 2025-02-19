<template>
  <Button
    v-if="loading"
    :badge="badge"
    :severity="severity"
    class="tw-justify-center tw-flex tw-gap-4 tw-transform active:tw-scale-[0.9] tw-transition tw-duration-150"
    :class="{
      'tw-cursor-not-allowed': disabled,
      'tw-py-[0.5rem]': size === 'small',
    }"
    :disabled="true"
  >
    <i class="pi pi-spin pi-spinner" />
    <b>{{ label }}</b>
  </Button>
  <Button
    v-else
    :badge="badge"
    :severity="severity"
    class="tw-justify-center tw-flex tw-gap-4 tw-transform active:tw-scale-[0.9] tw-transition tw-duration-150"
    :class="{
      'tw-cursor-not-allowed': disabled,
      'tw-py-[0.5rem]': size === 'small',
    }"
    :disabled="disabled"
  >
    <i v-if="icon" :class="icon" />
    <b>{{ label }}</b>
  </Button>
</template>

<script lang="ts" setup>
import { PropType } from "vue";

import Button from "primevue/button";

defineProps({
  icon: { type: String, default: "" },
  label: { type: String, default: "" },
  badge: { type: String, default: "" },
  type: { type: String as PropType<"default" | "light">, default: "default" },
  size: { type: String as PropType<"default" | "small">, default: "default" },
  severity: { type: String, default: "primary" },
  disabled: { type: Boolean },
  loading: { type: Boolean, default: false },
});
</script>
