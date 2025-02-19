<template>
  <Panel
    :pt="panelStyles"
    header="Current Page Review"
  >
  <div class="tw-absolute tw-w-full tw-px-5">
    <div class="tw-flex tw-justify-between tw-w-full">
      <div><p class="tw-font-bold">Page 3</p></div>
      <div class="tw-flex tw-flex-col tw-text-right tw-gap-y-1">
        <div class="tw-flex">
          <div class="tw-w-[11rem] tw-mr-2">
            <p>Total number to review:</p>
          </div>
          <p class="tw-font-bold tw-text-white tw-bg-[#8B5CF6] tw-w-[2rem] tw-text-center tw-rounded">
            25
          </p>
        </div>
        <div class="tw-flex">
          <div class="tw-w-[11rem] tw-mr-2">
            <p>Reviewed:</p>
          </div>
          <p class="tw-font-bold tw-bg-purple-200 tw-w-[2rem] tw-text-center tw-rounded">
            2
          </p>
        </div>
      </div>
    </div>
  </div>
    <Knob
      v-model="currentPageProgress"
      valueTemplate="{value}%"
      :min="0"
      :max="100"
      class="tw-mt-7"
      :size="70"
    />

    <div class="tw-flex tw-justify-between tw-w-full tw-gap-x-2">
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Include:</label>
        <p class="tw-font-bold tw-bg-green-200 tw-w-[2rem] tw-text-center tw-rounded">1</p>
      </div>
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Maybe:</label>
        <p class="tw-font-bold tw-bg-slate-200 tw-w-[2rem] tw-text-center tw-rounded">1</p>
      </div>
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Exclude:</label>
        <p class="tw-font-bold tw-bg-red-200 tw-w-[2rem] tw-text-center tw-rounded">0</p>
      </div>
    </div>
  </Panel>
</template>

<script lang="ts" setup>
import Panel from 'primevue/panel'
import Knob from 'primevue/knob'
import { ref } from 'vue'

const currentPageProgress = ref(8)

const panelStyles = {
  header: 'tw-py-2',
  content: 'tw-py-2 tw-flex tw-flex-col tw-items-center tw-relative tw-text-sm',
}
</script>
