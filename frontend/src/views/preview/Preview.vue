<template>
  <Container class="tw-flex tw-flex-col tw-gap-3 tw-mx-auto">
    <div class="tw-flex tw-w-full tw-mb-2">
      <div class="tw-w-full">
        <Inputbox
          v-for="item in config_section1"
          v-model="collectionName"
          :type="item.type"
          :label="item.label"
          :mandatory="item.mandatory"
          :isExpand="true"
          :disabled="isLoading"
          class="tw-w-11/12"
        ></Inputbox>
      </div>
      <div
        class="tw-flex tw-flex-row tw-gap-2 tw-justify-end tw-items-end tw-w-full"
      >
        <Button
          label="Cancel"
          type="light"
          @click="isCancelModalActive = true"
          :loading="isLoading"
        ></Button>
        <Button
          label="Create Dataset/Review"
          @click="submit"
          :loading="isLoading"
        ></Button>
      </div>
    </div>
    <ProgressBar
      v-if="uploadProgress.total"
      :value="uploadProgressPercentage"
    />
    <Divider />
    <div class="tw-grid tw-grid-cols-2 tw-gap-12">
      <div>
        <h3 class="tw-pb-5">Corpus Format Requirements</h3>
        <p>
          Make sure that your dataset conform to the system requirements and
          follow the format below:
        </p>
        <br />
        <div class="tw-pb-5">
          <b>- corpus.jsonl</b>: A text file in nbib format from the PubMed
          website, which includes at least 4 fields:
          <div class="tw-ml-2">
            <p>
              pmid (PMID): the 8-digit PubMed unique identifier or unique record
              identifier of literature in a custom database
            </p>
            <p>title (TI): the title of study</p>
            <p>
              abstract (AB): the abstract of study with paragraphs or passages
            </p>
            <p>author (AU): the full name of each author</p>
          </div>
        </div>
        <p>
          If your dataset does not follow the described format, please update
          your files and re-upload.
        </p>
      </div>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <h3>corpus.nbib</h3>
        <Inputbox
          v-for="item in config_section2"
          v-model="previewData[item.dataKey as keyof typeof previewData]"
          :type="item.type"
          :label="item.label"
          :mandatory="item.mandatory"
          :isExpand="true"
          class="tw-mb-5"
          :row="item.row"
          disabled
        ></Inputbox>
      </div>
    </div>
    <div>
      <p class="tw-pb-5">
        <b>- Evidence-based query in PICO</b>: Clinical questions organised according
        to the patient, intervention, comparison, and outcome (PICO) model. PICO
        is a search strategy tool for researchers to aid in finding clinically
        Include evidence on literature search quality.
      </p>
      <QueryPanel />
    </div>
  </Container>
  <Modal
    v-model:isActive="isCancelModalActive"
    header="Cancel to create a collection from uploaded file(s)"
    title="Delete data"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="danger"
    @confirm="handleCancel"
  >
    <template #body> Your data will be erased permanently. </template>
  </Modal>
  <Modal
    v-model:isActive="isCreateModalActive"
    header="Confirm to create a collection"
    title="Information"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="confirmSubmit"
  >
    <template #body>
      <p>
        After you create a collection, you will not be able to rename your
        collection and your original dataset (uploaded files) will be stored
        until it will be used to perform a model selection at the first time.
      </p>
      <p>
        For demonstration purpose, we will also delete your uploaded dataset if
        your collection is not being used for over 3 days. Only dataset
        embedding is kept for further model selections. We will regularly remove
        uploaded datasets and their embeddings. We also strictly protect privacy
        and information you provide to our system.
      </p>
    </template>
  </Modal>
</template>
<script lang="ts" setup>
import { computed, ref } from 'vue'

import Divider from 'primevue/divider'
import Modal from '@/components/Modal.vue'
import Container from '@/components/Container.vue'
import Inputbox from '@/components/Inputbox.vue'
import Button from '@/components/Button.vue'
import ProgressBar from 'primevue/progressbar'

import QueryPanel from '../review/components/QueryPanel.vue'

import { config_section1, config_section2 } from './configs/previewConfig.ts'

import { useRouter } from 'vue-router'
const router = useRouter()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

import { useDirty } from '@/composables/dirty'
const { setDirty, clearDirty } = useDirty()

const isCancelModalActive = ref(false)
const isCreateModalActive = ref(false)

// Collection Store -----------------------------------------------------

import axios, { AxiosError } from 'axios'
import {
  uploadCollectionFilesStore,
  clearUploadCollectionFilesStore,
} from '@/stores/uploadCollection'
import { IPreSignedURL } from '@/types/data'
import { readJSONL } from '@/utils/jsonl'
import { getTokenHeader } from '@/utils/auth'
import { delay } from '@/utils/async'
import { validateCollection } from './validations/validateCollection.ts'

const collectionName = ref('')
const uploadProgress = ref({ uploaded: 0, total: 0 })

const uploadProgressPercentage = computed(() =>
  Math.round(
    (uploadProgress.value.uploaded / uploadProgress.value.total) * 100,
  ),
)

// Get pre-signed URLs for uploading files
const getPreSignedURLs = async () => {
  // Get file names
  const files = uploadCollectionFilesStore.value
  const fileNames = Object.values(files)
    .map((file) => file?.name)
    .filter((name) => name)
  // Send request for pre-signed URLs
  const body = {
    collection_name: collectionName.value,
    file_names: fileNames,
    corpus_first_entry: previewData.value.corpus,
    queries_first_entry: previewData.value.queries,
  }
  const result = await axios.post('/encoder/s3', body, getTokenHeader())
  return {
    collection_id: result.data.collection_id as number,
    urls: result.data.urls as IPreSignedURL[],
  }
}

const handleUploadProgress = async (event: any) =>
  (uploadProgress.value.uploaded += event.bytes)

// Upload file to S3 using pre-signed URL
const uploadFile = async (
  file: File,
  preSignedURL: IPreSignedURL,
  collectionId: number,
) => {
  try {
    // Create form data
    const formData = new FormData()
    formData.append('AWSAccessKeyId', preSignedURL.fields.AWSAccessKeyId)
    formData.append('key', preSignedURL.fields.key)
    formData.append('policy', preSignedURL.fields.policy)
    formData.append('signature', preSignedURL.fields.signature)
    formData.append('file', file)

    // Update total file size
    uploadProgress.value.total += file.size

    // Send request
    const config = {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: handleUploadProgress,
    }
    await axios.post(preSignedURL.url, formData, config)
  } catch (error) {
    // Delete collection on error
    const params = { collection_id: collectionId }
    await axios.delete('/encoder/s3', getTokenHeader({ params }))
    // Re-throw error
    throw error
  }
}

// Submit -----------------------------------------------------

import { ValidationError } from 'joi'

const submit = async () => {
  try {
    // Validate collection name
    const validation = validateCollection(collectionName.value)
    if (validation.error) throw validation.error
    isCreateModalActive.value = true
  } catch (error) {
    console.error(error)
    if (error instanceof ValidationError) {
      const errorMessage = error.details
        .map((detail) => detail.message)
        .join(' ')
      showToast('error', 'Invalid collection name', errorMessage)
    } else if (error instanceof Error) {
      showToast('error', 'Invalid collection name', error.message)
    } else {
      showToast('error', 'Invalid collection name', 'An error occurred.')
    }
  }
}

const confirmSubmit = async () => {
  try {
    setLoading(true)
    // Get pre-signed URLs
    const { collection_id, urls } = await getPreSignedURLs()
    // Validate pre-signed URLs equal to files
    const numberOfURLs = urls.length
    const numberOfFiles = Object.values(
      uploadCollectionFilesStore.value,
    ).filter((file) => file).length
    if (numberOfURLs !== numberOfFiles)
      throw new Error(
        'Number of Pre-signed URLs do not match a number of files.',
      )
    // Upload files
    for (const url of urls) {
      const fileName = url.fields.key
        .split('/')
        .pop()
        ?.split('.')
        .shift() as keyof typeof uploadCollectionFilesStore.value
      const file = uploadCollectionFilesStore.value[fileName]
      if (file) await uploadFile(file, url, collection_id)
    }
    // Redirect to collection page
    clearDirty()
    clearUploadCollectionFilesStore()
    await delay(3000)
    router.push({ name: 'collections' })
  } catch (error) {
    console.error(error)
    let errorMessage = ''
    if (error instanceof Error) errorMessage = error.message
    if (error instanceof AxiosError)
      errorMessage = getResponseErrorMessage(error).message
    showToast('error', 'Failed to upload files', errorMessage)
  } finally {
    setLoading(false)
  }
}

// Preview File -----------------------------------------------------

const previewData = ref({ corpus: '', queries: '' })

// Read content of file
const readFile = async (file: File | null): Promise<string> => {
  if (!file) return ''
  // Create URL for file
  const url = URL.createObjectURL(file)
  // Read content of jsonl file
  const text = await readJSONL(url)
  return text
}

// Get preview data
const getPreviewData = async () => {
  // Read content
  const corpusText = await readFile(uploadCollectionFilesStore.value.corpus)
  const queriesText = await readFile(uploadCollectionFilesStore.value.queries)
  // Get only first entry of each file
  const corpus = corpusText
    .split('\n')
    .filter((_, index) => index < 10)
    .join('\n')
  const queries = queriesText
    .split('\n')
    .filter((_, index) => index < 10)
    .join('\n')
  // Set preview data
  previewData.value = { corpus, queries }
}

getPreviewData()

// Redirect to upload page on no corpus file otherwise set dirty state
if (!uploadCollectionFilesStore.value.corpus) router.push({ name: 'upload' })
else setDirty()

// Cancel and redirect to upload page
const handleCancel = () => {
  clearDirty()
  router.push({ name: 'upload' })
}
</script>
