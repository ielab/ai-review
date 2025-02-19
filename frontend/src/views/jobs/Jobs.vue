<template>
  <div class="tw-w-11/12 tw-my-10">
    <span
      class="tw-flex tw-gap-10 tw-items-center tw-text-slate-800 tw-mt-5 tw-mb-10 tw-whitespace-nowrap"
    >
      <div class="tw-bg-slate-200 tw-rounded-full tw-p-2">
        <i class="pi pi-file tw-text-4xl"></i>
      </div>
      <div class="tw-pr-8 tw-text-5xl tw-font-bold">Job/Result List</div>
    </span>
    <Table :data="jobs" :colTable="jobColumn" tableType="job" actionColumnHeader="Model">
      <template #col(name)="slotProps">
        <div
          class="tw-flex tw-gap-2 tw-items-center tw-justify-center tw-text-center tw-cursor-pointer"
          :class="{
            'tw-text-red-500 tw-font-bold': slotProps.node.data['status'] == 'Error',
            'tw-text-neutral-500': slotProps.node.data['status'] == 'Queued',
            'tw-text-blue-600':
              slotProps.node.data['status'] != 'Queued' && slotProps.node.data['status'] != 'Error',
          }"
          @click="
            router.push({
              name: 'result',
              params: { id: slotProps.node.data['id'] },
            })
          "
        >
          <div class="tw-flex tw-flex-col">
            <div class="hover:tw-underline tw-underline-offset-2">
              {{ slotProps.node.data[slotProps.key] }}
            </div>
            <div class="tw-text-sm tw-text-neutral-600">
              {{ slotProps.node.data.auto_gen_code }}
            </div>
          </div>
          <i
            :class="{
              'pi pi-clock': slotProps.node.data['status'] == 'Queued',
              'pi pi-exclamation-circle tw-text-red-500': slotProps.node.data['status'] == 'Error',
              'pi pi-info-circle':
                slotProps.node.data['status'] != 'Error' &&
                slotProps.node.data['status'] != 'Queued',
            }"
          ></i>
        </div>
      </template>
      <template #col(best_model)="slotProps">
        <div class="tw-text-center">{{ slotProps.node.data.best_model?.name }}</div>
      </template>
      <template #action="slotProps">
        <div class="tw-flex tw-gap-2 tw-items-center tw-justify-center">
          <Button
            type="default"
            label="Download"
            icon="pi pi-download"
            :badge="formatFileSize(slotProps.node.data.best_model?.model_size_gb)"
            :isLoading="isLoading && slotProps.node.data.id === selectedJob?.id"
            :disabled="slotProps.node.data.status != 'Finished' || isLoading"
            :class="{
              'tw-cursor-not-allowed': slotProps.node.data.status != 'Finished',
            }"
            class="tw-min-w-[14rem] tw-text-sm"
            @click="onClickDownload(slotProps.node.data)"
          />
        </div>
      </template>
    </Table>
    <Modal
      v-model:is-active="confirmDownload"
      header="Confirm to download model"
      title="You are about to download the following model"
      rightBtn="Confirm"
      leftBtn="Cancel"
      icon="pi pi-exclamation-circle"
      iconColor="warning"
      @confirm="downloadModel"
    >
      <template #value>{{ selectedJob?.best_model.name }}</template>
      <template #body>Click confirm to start to download</template>
    </Modal>
  </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue'

import Table from '@/components/Table.vue'
import Button from '@/components/Button.vue'
import Modal from '@/components/Modal.vue'

import { IJobItem, jobColumn } from './configs/jobConfig.ts'

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

import { useRouter } from 'vue-router'
const router = useRouter()

/**
 * Select job to download model
 */

const confirmDownload = ref(false)

const selectedJob = ref<IJobItem['data'] | undefined>()

function onClickDownload(data: IJobItem['data']) {
  if (data.status != 'Finished') return
  selectedJob.value = data
  confirmDownload.value = true
}

// Download Model ------------------------------

import { getFileToDownload, downloadFileFromURL, formatFileSize } from '@/utils/download'

const downloadModel = async () => {
  try {
    setLoading(true)
    const keyword = selectedJob.value?.best_model?.hash_model_path
    if (!keyword) throw new Error('Model path is not found')
    showToast('info', 'Downloading', 'Please wait while downloading the model')
    const { url, filename } = await getFileToDownload(keyword, 'model')
    downloadFileFromURL(url, filename)
    confirmDownload.value = false
    showToast('success', 'Downloaded', 'Model has been downloaded successfully')
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Error on downloading', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Error on downloading', error.message)
    } else {
      showToast('error', 'Error on downloading', 'An unknown error occurred while downloading')
    }
  } finally {
    selectedJob.value = undefined
    setLoading(false)
  }
}

// Jobs Data -----------------------------------

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'
import { getTimeDifference } from '@/utils/time'
import { formatDateTime } from '@/utils/datetime.ts'

const jobs = ref<IJobItem[]>([])

const getJobs = async () => {
  try {
    const result = await axios.get('/encoder/jobs', getTokenHeader())
    const data = result.data
    jobs.value = data.map((item: IJobItem['data'], index: number) => {
      const timeSpent =
        item.job_started_at && item.job_ended_at
          ? getTimeDifference(item.job_started_at, item.job_ended_at)
          : 'N/A'
      item.job_queued_at = formatDateTime(item.job_queued_at)
      item.job_started_at = item.job_started_at ? formatDateTime(item.job_started_at) : null
      item.job_ended_at = item.job_ended_at ? formatDateTime(item.job_ended_at) : null
      return {
        key: item.id,
        data: {
          order: index + 1,
          ...item,
          timeSpent: timeSpent,
        },
      }
    })
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Fetch Jobs', e.message)
    } else {
      showToast('error', 'Cannot Fetch Jobs', 'Unknown Error')
    }
  }
}
getJobs()
</script>
