<template>
  <div class="card tw-w-full">
    <FileUpload
      :multiple="true"
      :fileLimit="fileLimit"
      :maxFileSize="maxSize"
      customUpload
      :pt="{
        badge: { root: 'tw-hidden' },
      }"
    >
      <template #header="{ chooseCallback, files }">
        <div class="tw-flex tw-flex-wrap tw-justify-between tw-items-center tw-flex-1 tw-gap-2">
          <div class="tw-flex tw-gap-2">
            <Button
              @click="chooseCallback"
              label="Choose File"
              type="light"
              icon="pi pi-plus"
            ></Button>
          </div>
          <div class="tw-flex tw-gap-2">
            <Button @click="submit(files)" :label="submitLabel" :disabled="!files.length"></Button>
          </div>
        </div>
      </template>
      <template #content="{ files, removeFileCallback }">
        <ul class="tw-p-0 tw-m-0 tw-list-none tw-flex tw-flex-wrap tw-gap-2">
          <li
            v-for="(file, index) in files"
            :key="file.name"
            class="tw-flex tw-items-center tw-justify-between tw-w-full tw-p-6 tw-border tw-border-solid tw-border-gray-300 tw-rounded-md"
          >
            <div class="tw-flex tw-items-center tw-gap-6">
              <img
                :src="getIcon(file.name)"
                width="36"
                :style="{
                  filter: `invert(0.5) sepia(1) saturate(300%) ${getHue(file.name)}`,
                }"
              />
              <div>
                <div class="tw-text-gray-600 tw-font-medium tw-mb-1">{{ file.name }}</div>
                <div class="tw-text-gray-500 tw-text-xs">{{ prettyBytes(file.size) }}</div>
              </div>
            </div>
            <i
              @click="removeFileCallback(index)"
              class="pi pi-times tw-cursor-pointer tw-text-red-500 tw-text-xl hover:tw-bg-red-100 tw-w-8 tw-h-8 tw-flex tw-items-center tw-justify-center tw-rounded-full tw-duration-150 active:tw-scale-95"
            />
          </li>
        </ul>
      </template>
      <template #empty>
        <div class="tw-flex tw-items-center tw-justify-center tw-flex-col tw-m-10">
          <i
            class="tw-m-2 pi pi-cloud-upload tw-rounded-full tw-border-2 tw-border-solid tw-text-gray-400 tw-border-gray-400 tw-p-8 tw-text-8xl"
          />
          <p class="tw-mt-4 tw-mb-0">Drag and drop files here to upload.</p>
        </div>
      </template>
    </FileUpload>
  </div>
</template>
<script lang="ts" setup>
import prettyBytes from 'pretty-bytes'

import FileUpload from 'primevue/fileupload'
import Button from '@/components/Button.vue'

defineProps({
  fileLimit: { type: Number, default: 3 },
  maxSize: { type: Number, default: 1024 ** 3 }, // 1GB
  submitLabel: { type: String, default: 'Submit' },
})
const emit = defineEmits(['submit'])

// Get icon for file
const getIcon = (filename: string) => {
  if (filename === 'corpus.jsonl') return '/file.png'
  if (filename === 'queries.jsonl') return '/q.png'
  return '/warning.png'
}

// Get hue for file
const getHue = (filename: string) => {
  if (['corpus.jsonl', 'queries.jsonl'].includes(filename)) return 'hue-rotate(60deg)'
  return 'hue-rotate(315deg)'
}

const submit = (files: File[]) => emit('submit', files)
</script>
