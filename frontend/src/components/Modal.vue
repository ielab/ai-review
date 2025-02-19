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
        <span class="tw-px-3">
          <h2>{{ title }}</h2>
          <div class="tw-font-bold tw-text-violet-600 tw-text-lg tw-break-all">
            <slot name="value"></slot>
          </div>
          <p></p>
          <slot name="body"></slot>
          <p></p>
          <div>
            <slot name="note"></slot>
          </div>
        </span>
      </div>
      <template #footer>
        <Button
          v-if="leftBtn"
          type="light"
          :label="leftBtn"
          severity="secondary"
          @click="handleClose"
        />
        <Button v-if="rightBtn" :label="rightBtn" :severity="severity" @click="handleConfirm" />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

import Dialog from 'primevue/dialog'
import Button from '@/components/Button.vue'

import { useRouter } from 'vue-router'
const router = useRouter()

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
})

const emit = defineEmits(['update:isActive', 'confirm', 'close'])
const visible = computed({
  get() {
    return props.isActive
  },
  set(value) {
    emit('update:isActive', value)
  },
})

function handleClose() {
  visible.value = false
}

function handleConfirm() {
  visible.value = false
  router.push({ name: props.route })
  emit('confirm', true)
}
</script>
