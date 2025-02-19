<template>
  <div class="card tw-w-10/12">
    <Steps v-model:activeStep="activeIndex" :model="data.status === 'Error' ? items_error : items">
      <template #item="{ item, index }">
        <div class="tw-flex tw-flex-col tw-items-center tw-text-center tw-justify-center">
          <span
            class="tw-rounded-full tw-z-0 tw-w-16 tw-h-16 tw-flex tw-items-center tw-justify-center"
            :class="{
              'tw-bg-purple-100': index < activeIndex,
              'active-step': index === activeIndex,
              'surface-overlay tw-bg-slate-200': index > activeIndex,
              'tw-bg-red-200': data.status === 'Error',
            }"
          >
            <img :src="item.icon" alt="Icon" width="40" height="40" />
          </span>
          <div class="tw-mt-4">{{ item.label }}</div>
        </div>
      </template>
    </Steps>
  </div>
</template>
<style scoped>
@keyframes blink {
  from {
    @apply tw-border-purple-100;
  }
  50% {
    @apply tw-border-purple-300;
  }
  to {
    @apply tw-border-purple-100;
  }
}

.active-step {
  @apply tw-bg-purple-200 tw-border-4 tw-border-solid tw-border-purple-100;
  animation: blink 2s infinite;
}
</style>
<script lang="ts" setup>
import { PropType, computed, ref } from 'vue'

import Steps from 'primevue/steps'

import startIcon from '@/assets/icons/start.png'
import decodeIcon from '@/assets/icons/decode.png'
import workflowIcon from '@/assets/icons/workflow.png'
import flagIcon from '@/assets/icons/flag.png'
import error from '@/assets/icons/no-results.png'
import process from '@/assets/icons/more.png'

import { IJob } from '@/types/data'

const props = defineProps({
  data: { type: Object as PropType<IJob>, required: true },
})

/**
 * Stepper Configurations
 */

const items = ref([
  {
    label: 'Started',
    icon: startIcon,
  },
  {
    label: 'Dataset Encoding',
    icon: decodeIcon,
  },
  {
    label: 'Model Selection',
    icon: workflowIcon,
  },
  {
    label: 'Finished',
    icon: flagIcon,
  },
])

const items_error = ref([
  {
    label: 'Started',
    icon: startIcon,
  },
  {
    label: 'Processing',
    icon: process,
  },
  {
    label: 'Error',
    icon: error,
  },
])

/**
 * Active Step Checker
 */

const NORMAL_ACTIVE_ORDER = ['Queued', 'Encoding', 'Selection', 'Finished']
const ERROR_ACTIVE_ORDER = ['Queued', '', 'Error']

const activeIndex = computed(() => {
  if (props.data.status === 'Error') return ERROR_ACTIVE_ORDER.indexOf(props.data.status)
  return NORMAL_ACTIVE_ORDER.indexOf(props.data.status)
})
</script>
