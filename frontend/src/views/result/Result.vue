<template>
  <div class="tw-grid tw-gap-9 tw-mt-8 tw-w-full">
    <div class="tw-flex tw-justify-center tw-items-center">
      <Stepper :data="data"></Stepper>
    </div>
    <div class="tw-flex tw-justify-center tw-items-center tw-w-full">
      <ResultForm :data="data" class="tw-w-full"></ResultForm>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue'

import Stepper from '@/components/Stepper.vue'
import ResultForm from './components/resultForm.vue'

import { IJob } from '@/types/data'
import { DEFAULT_JOB } from '@/defaults/job'

import { useRoute } from 'vue-router'
const route = useRoute()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

/**
 * Job Data
 */

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'
import { getTimeDifference } from '@/utils/time'
import { formatDateTime } from '@/utils/datetime'

const data = ref<IJob>({ ...DEFAULT_JOB })

const getJob = async () => {
  try {
    const result = await axios.get(`/encoder/job/${route.params.id}`, getTokenHeader())
    data.value = result.data
    data.value.waitingTime = data.value.job_started_at
      ? getTimeDifference(data.value.job_queued_at, data.value.job_started_at)
      : 'N/A'
    data.value.timeSpent =
      data.value.job_started_at && data.value.job_ended_at
        ? getTimeDifference(data.value.job_started_at, data.value.job_ended_at)
        : 'N/A'
    data.value.job_queued_at = data.value.job_queued_at
      ? formatDateTime(data.value.job_queued_at)
      : 'N/A'
    data.value.job_started_at = data.value.job_started_at
      ? formatDateTime(data.value.job_started_at)
      : 'N/A'
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Error fetching job', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Error fetching job', error.message)
    } else {
      showToast('error', 'Error fetching job', 'Unknown error')
    }
  }
}
getJob()
</script>
