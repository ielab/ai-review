<template>
  <Container class="tw-mt-5 tw-grid tw-grid-rows tw-gap-6">
    <div class="tw-w-full tw-flex tw-items-center" v-if="data.status == 'Queued'">
      <i class="pi pi-spin pi-spinner tw-mr-5" style="font-size: 2rem"></i>
      <h1 class="tw-w-full tw-text-slate-800">Waiting in a Queue ...</h1>
      <Button label="Cancel" type="light" />
    </div>
    <div
      v-for="(section, no) in data.status == 'Error' ? configError : config"
      class="tw-grid tw-grid-cols-2 tw-gap-6"
    >
      <div v-if="no == 'section2'" v-for="column in section" class="tw-w-full tw-col-span-2">
        <Button
          v-if="!showMore"
          class="tw-w-full tw-my-6"
          icon="pi pi-chevron-down"
          label="More Detail"
          @click="showMore = !showMore"
        ></Button>
        <div v-if="showMore" class="tw-w-full tw-grid tw-col-span-2 tw-gap-6">
          <Divider class="tw-w-full tw-col-span-2 tw-mb-1" />
          <Inputbox
            v-for="(field, key) in column"
            :modelValue="formatValue(field.value, key as string)"
            :label="field.label"
            :id="key"
            :type="field.type"
            :colTable="predictedRankingColumn"
            :download="field.download"
            :downloadBtn="field.downloadBtn"
            :isExpand="field.isExpand"
            :row="field.row"
            :isLoading="isLoading"
            :class="field.span"
            disabled
            @download="download"
          />
          <Button
            class="tw-w-full tw-col-span-2 tw-my-6"
            icon="pi pi-chevron-up"
            type="light"
            label="Less Detail"
            @click="showMore = !showMore"
          ></Button>
        </div>
      </div>
      <div
        v-else
        v-for="column in section"
        class="tw-grid tw-gap-6 tw-w-full"
        :class="{ 'tw-col-span-2': no != 'section1' }"
      >
        <template v-for="(field, key) in column">
          <div v-if="field.type === 'table'" class="-tw-mr-6">
            <div class="tw-mb-2">{{ field.label }}</div>
            <div
              class="tw-border tw-border-solid tw-border-gray-300 tw-rounded-md tw-flex tw-items-center tw-gap-3 tw-pr-3"
            >
              <Table
                :class="{ 'tw-h-80 tw-overflow-hidden': !isTableExpand }"
                :data="formatValue(field.value, key as string)"
                :colTable="predictedRankingColumn"
                actionColumnHeader="Model"
              >
                <template #action="slotProps">
                  <div class="tw-flex tw-gap-2 tw-items-center tw-justify-center">
                    <Button
                      type="default"
                      label="Download"
                      :badge="formatFileSize(slotProps.node.data.model_size_gb)"
                      icon="pi pi-download"
                      :isLoading="
                        isLoading && downloadingHash == slotProps.node.data.hash_model_path
                      "
                      :disabled="isLoading"
                      class="tw-min-w-[12rem]"
                      :pt="{ badge: isLoading && 'tw-opacity-25' }"
                      @click="download(key as keyof IJob, slotProps.node)"
                    />
                  </div>
                </template>
              </Table>
              <i
                @click="isTableExpand = !isTableExpand"
                :class="isTableExpand ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                class="tw-cursor-pointer"
              />
            </div>
          </div>
          <Inputbox
            v-else
            :modelValue="formatValue(field.value, key as string)"
            :label="field.label"
            :id="key"
            :type="field.type"
            :download="field.download"
            :downloadBtn="field.downloadBtn"
            :isExpand="field.isExpand"
            :row="field.row"
            :isLoading="isLoading"
            :class="field.span"
            class="tw-w-full"
            disabled
            @download="download(key as keyof IJob, field.value)"
          />
        </template>
      </div>
    </div>
    <GeneratedQueries v-if="data.selection_method_is_pseudo_query_generated && data.status === 'Finished'" :data="data" />
  </Container>
  <Modal
    v-model:is-active="confirmDownloadModel"
    header="Confirm to download model"
    title="You are about to download the following model"
    rightBtn="Confirm"
    leftBtn="Cancel"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="confirmDownload('result', downloadingModel)"
  >
    <template #value>{{ downloadingModel.data.name }}</template>
    <template #body>Click confirm to start to download</template>
  </Modal>
</template>
<script lang="ts" setup>
import { PropType, ref } from 'vue'

import Divider from 'primevue/divider'
import Inputbox from '@/components/Inputbox.vue'
import Container from '@/components/Container.vue'
import Table from '@/components/Table.vue'
import Button from '@/components/Button.vue'
import Modal from '@/components/Modal.vue'
import GeneratedQueries from './generatedQueries.vue'

import { IJob, IModel } from '@/types/data'
import { config, configError } from '../configs/result'
import { predictedRankingColumn } from '../configs/predictedRanking'

const props = defineProps({
  data: { type: Object as PropType<IJob>, required: true },
})

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useLoading } from '@/composables/loading'
const { setLoading, isLoading } = useLoading(false)

/**
 * Field
 */

const showMore = ref(false)
const isTableExpand = ref(true)

const formatValue = (fieldData: any, key: string) => {
  const dataValue = props.data[key as keyof IJob]
  switch (key) {
    case 'instruction':
    case 'advice':
      return fieldData
    case 'result':
      if (dataValue === null) return []
      return (dataValue as IModel[]).map((item, index) => ({
        key: index,
        data: {
          ranking: index + 1,
          name: item.name,
          score: item.score.toFixed(10),
          hash_model_path: item.hash_model_path,
          model_size_gb: item.model_size_gb,
        },
      }))
    default:
      return dataValue
  }
}

/**
 * Download button
 */

import { AxiosError } from 'axios'
import { downloadFileFromURL, getFileToDownload, formatFileSize } from '@/utils/download'

const DOWNLOADING_CONFIG = {
  collection_corpus_first_entry: { key: 'collection_hash_corpus_path', fileType: 'corpus' },
  collection_queries_first_entry: { key: 'collection_hash_queries_path', fileType: 'queries' },
  result: { key: '', fileType: 'model' },
}

const downloadingHash = ref('')

const confirmDownloadModel = ref(false)
const downloadingModel = ref<any | null>(null)

const download = async (key: keyof IJob, data: any) => {
  if (key === 'result') {
    downloadingModel.value = data
    confirmDownloadModel.value = true
    return
  } else {
    confirmDownload(key, data)
  }
}

const confirmDownload = async (key: keyof IJob, data: any) => {
  try {
    confirmDownloadModel.value = false
    // Prevent download if the job is not finished
    if (isLoading.value) return
    // Get data to download
    const downloadingConfig = DOWNLOADING_CONFIG[key as keyof typeof DOWNLOADING_CONFIG]
    let keyword =
      key === 'result' ? data.data.hash_model_path : props.data[downloadingConfig.key as keyof IJob]
    if (!keyword) throw new Error('No file to download')
    downloadingHash.value = keyword
    setLoading(true)
    showToast(
      'info',
      'Downloading',
      `Please wait while downloading the ${downloadingConfig.fileType} file`
    )
    if (!keyword) throw new Error('No file to download')
    // Get file to download
    const { url, filename } = await getFileToDownload(keyword as string, downloadingConfig.fileType)
    // Download file from URL
    downloadFileFromURL(url, filename)
    showToast('success', 'Downloaded', 'File downloaded successfully')
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Error on downloading', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Error on downloading', error.message)
    } else {
      showToast('error', 'Error on downloading', 'An unknown error occurred while downloading.')
    }
  } finally {
    downloadingHash.value = ''
    setLoading(false)
  }
}
</script>
