<template>
  <div class="tw-flex tw-justify-center tw-items-center tw-gap-x-3 tw-h-9">
    <Button
      :pt="{ root:'tw-bg-white tw-h-2 tw-w-6',icon: 'tw-text-xl' }"
      icon="pi pi-angle-left"
      text
      rounded
    />
    <p>Page</p>
    <InputText
    :pt="{root:'tw-h-2'}"
      type="number"
      class="tw-w-[4rem]"
      :value="3"
      min="1"
    />
    <p>of 8</p>
    <Button
      :pt="{ root:'tw-h-2 tw-w-6',icon: 'tw-text-xl' }"
      icon="pi pi-angle-right"
      text
      rounded
      @click="emit('update:nextPage', true)"
    />
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Button from '@/components/Button.vue'

const emit = defineEmits(['update:nextPage'])
</script>

<style scoped>
input {
    text-align: center
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>