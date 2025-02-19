<template>
  <Button
    :rounded="rounded"
    :severity="severity"
    :text="text"
    :disabled="disabled"
    :pt="{
      root: [size === 'small' ? 'tw-w-3 tw-h-3 !tw-p-3' : '!tw-w-10 !tw-h-10'],
    }"
    class="tw-transform active:tw-scale-[0.8] tw-transition tw-duration-150"
  >
    <template #icon>
      <i :class="[icon, size === 'small' ? 'fa-xs' : '']" />
    </template>
  </Button>
</template>

<script lang="ts" setup>
import { PropType, computed } from "vue";

import Button from "primevue/button";

const props = defineProps({
  icon: { type: String, default: "" },
  badge: { type: String, default: "" },
  type: { type: String as PropType<"default" | "light">, default: "default" },
  size: { type: String as PropType<"default" | "small">, default: "default" },
  text: { type: Boolean },
  severity: { type: String, default: "primary" },
  rounded: { type: Boolean },
  disabled: { type: Boolean },
  isLoading: { type: Boolean },
});
const emit = defineEmits(["update:state"]);

// const isLoading = computed({
//  get() {
//    return props.isLoading
//  },
//  set(value) {
//    emit('update:state', value)
//  },
// })

computed({
  get() {
    return props.isLoading;
  },
  set(value) {
    emit("update:state", value);
  },
});
</script>
