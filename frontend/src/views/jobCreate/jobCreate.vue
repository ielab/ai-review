<template>
  <Container class="tw-flex tw-flex-col tw-gap-3">
    <div class="tw-flex tw-w-full tw-mb-2">
      <div class="tw-w-full tw-flex tw-gap-5">
        <Inputbox
          v-for="(item, key) in config_section1"
          :modelValue="collection[key as keyof typeof collection]"
          :type="item.type"
          :label="item.label"
          :isExpand="true"
          disabled
          :class="item.span"
        ></Inputbox>
      </div>
      <div
        v-if="!isSelectionStarted"
        class="tw-flex tw-flex-row tw-gap-2 tw-justify-end tw-items-end tw-w-6/12"
      >
        <Button
          label="Back"
          type="light"
          :isLoading="isLoading"
          @click="router.push({ name: 'collections' })"
        ></Button>
        <Button label="Start model selection" :isLoading="isLoading" @click="startModel"></Button>
      </div>
    </div>
    <Divider />
    <div class="tw-grid tw-grid-cols-2 tw-gap-6">
      <div v-for="item in config_section2" class="tw-grid tw-grid-rows">
        <Inputbox
          v-model="formData[item.dataKey as keyof typeof formData]"
          :type="item.type"
          :label="item.label"
          :isExpand="true"
          :dropdownOptions="dropdownOptions"
          :mandatory="item.mandatory"
          :disabled="item.disabled"
          :row="item.row"
        ></Inputbox>
      </div>
      <div class="tw-grid tw-grid-rows tw-col-start-2">
        <Inputbox
          :modelValue="currentModelSelectionDescription"
          type="textArea"
          label="Description of Model Selection Method"
          :row="6"
          disabled
        ></Inputbox>
      </div>
    </div>
    <div class="tw-flex tw-flex-col tw-gap-2">
      <h3>Your Dataset</h3>
      <Inputbox
        v-for="(item, key) in config_section3"
        :modelValue="collection[key as keyof typeof collection]"
        :type="item.type"
        :label="item.label"
        :mandatory="item.mandatory"
        :isExpand="item.expand"
        class="tw-mb-5"
        :row="item.row"
        disabled
      ></Inputbox>
    </div>
  </Container>
  <Modal
    v-model:isActive="createdSuccess_isActive"
    header="Your job was successfully created"
    title="Information"
    rightBtn="Okay"
    icon="pi pi-check-circle"
    iconColor="success"
    route="jobs"
  >
    <template #body>
      Your dataset is now associated with the job ID and name. We will regularly remove uploaded
      datasets. We also strictly protect privacy and information you provide to our system.
    </template>
  </Modal>
  <Modal
    v-model:isActive="confirm_isActive"
    header="Confirm your job"
    title="Estimated time"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="confirmStartModel"
  >
    <template #body>
      Your confirmation will be created as a job in queue. There are {{ queue }} jobs in a queue
      before yours.
    </template>
    <template #note
      ><span class="pi pi-exclamation-circle tw-pr-2 tw-text-violet-600"></span>Note that you cannot
      further edit this job after you make this confirmation.</template
    >
  </Modal>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'

import Modal from '@/components/Modal.vue'
import Divider from 'primevue/divider'
import Container from '@/components/Container.vue'
import Inputbox from '@/components/Inputbox.vue'
import Button from '@/components/Button.vue'

import { config_section1, config_section2, config_section3 } from './configs/jobCreateConfig.ts'

import { CREATE_JOB, DEFAULT_COLLECTION } from '@/defaults/collection'
import { IJobForm, ISelectionMethod } from '@/types/data'

import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

const formData = ref<IJobForm>({ ...CREATE_JOB })

/**
 * Starting Model Selection
 */

const createdSuccess_isActive = ref(false)
const confirm_isActive = ref()

const isSelectionStarted = ref(false)

const startModel = async () => {
  const validation = validateJob(formData.value)
  if (validation.error) {
    const e = validation.error as ValidationError
    showToast(
      'error',
      'Cannot Start Model Selection',
      `\n- ${e.message.split('. ').join('\n\n- ')}\n\n`
    )
  } else {
    const isSuccessGettingQueue = await getQueue()
    if (!isSuccessGettingQueue) return
    confirm_isActive.value = true
  }
}

const confirmStartModel = async () => {
  try {
    // Send request
    const body = {
      collection_id: collection.value.id,
      method: formData.value.selection_method_id,
      job_name: formData.value.name,
    }
    setLoading(true)
    await axios.post('/collection/processing', body, getTokenHeader())
    isSelectionStarted.value = true
    createdSuccess_isActive.value = true
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Start Model Selection', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Start Model Selection', error.message)
    } else {
      showToast('error', 'Cannot Start Model Selection', 'An unknown error occurred')
    }
  } finally {
    setLoading(false)
  }
}

/**
 * Get Collection Detail
 */

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'
import { validateJob } from './validations/job'
import { ValidationError } from 'joi'

const collection = ref({ ...DEFAULT_COLLECTION })

const getCollectionDetail = async () => {
  try {
    const collectionId = route.params.id
    const result = await axios.get(`/encoder/collection/${collectionId}`, getTokenHeader())
    collection.value = result.data
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Fetch Collection Detail', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Fetch Collection Detail', error.message)
    } else {
      showToast('error', 'Cannot Fetch Collection Detail', 'An error occurred')
    }
  }
}
getCollectionDetail()

/**
 * Form Config
 */

import { DENSE_RETRIEVERS } from '@/defaults/job'

const currentModelSelectionDescription = computed(() => {
  const id = formData.value.selection_method_id
  return collection.value.selection_methods.find((item: ISelectionMethod) => item.id === id)
    ?.description
})

const dropdownOptions = computed(() => {
  return collection.value.selection_methods
    .map((item: ISelectionMethod) => ({
      label: item.name,
      value: item.id,
    }))
    .sort((a, b) => {
      const aIndex = DENSE_RETRIEVERS.indexOf(a.label)
      const bIndex = DENSE_RETRIEVERS.indexOf(b.label)
      return aIndex - bIndex
    })
})

/**
 * Get queue
 */

const queue = ref(0)

const getQueue = async () => {
  try {
    const result = await axios.get('/collection/processing', getTokenHeader())
    queue.value = result.data.result
    return true
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Fetch Queue', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Fetch Queue', error.message)
    } else {
      showToast('error', 'Cannot Fetch Queue', 'An error occurred')
    }
    return false
  }
}
</script>
