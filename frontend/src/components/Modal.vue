<template>
  <div class="card flex justify-content-center">
    <Dialog
      v-model:visible="visible"
      modal
      :style="{ width: '36rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >
      <template #header>
        <div class="tw-flex tw-gap-3 tw-items-center">
          <i
            :class="[
              icon,
              {
                'tw-text-red-500': iconColor == 'danger',
                'tw-text-amber-500': iconColor == 'warning',
                'tw-text-teal-500': iconColor == 'success',
              },
            ]"
            class="tw-text-2xl"
          ></i>
          <span class="tw-font-bold">{{ header }}</span>
        </div>
      </template>
      <div class="tw-flex">
        <span class="tw-px-3 tw-flex tw-flex-col tw-gap-2">
          <h2 v-if="!title"><slot name="title"></slot></h2>

          <h2 v-else>{{ title }}</h2>

          <slot name="body"></slot>

          <div>
            <slot name="note"></slot>
          </div>
        </span>
      </div>
      <template #footer>
        <Button
          v-if="leftBtn"
          outlined
          :label="leftBtn"
          severity="secondary"
          @click="handleClose"
        />
        <Button
          v-if="rightBtn"
          :label="rightBtn"
          :severity="severity"
          @click="handleConfirm"
        />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";

import Dialog from "primevue/dialog";
import Button from "primevue/button";

import { useRouter } from "vue-router";
const router = useRouter();

const props = defineProps({
  isActive: { type: Boolean, default: false },
  header: { type: String },
  title: { type: String },
  leftBtn: { type: String },
  rightBtn: { type: String },
  icon: { type: String },
  iconColor: { type: String },
  route: { type: String },
  severity: { type: String },
});

const emit = defineEmits(["update:isActive", "confirm", "close"]);
const visible = computed({
  get() {
    return props.isActive;
  },
  set(value) {
    emit("update:isActive", value);
  },
});

function handleClose() {
  visible.value = false;
}

function handleConfirm() {
  visible.value = false;
  router.push({ name: props.route });
  emit("confirm", true);
}
</script>
