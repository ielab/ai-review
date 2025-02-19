<template>
  <div :class="{ 'p-read-only': disabled }" class="tw-flex tw-justify-center">
    <div class="tw-flex tw-flex-col tw-gap-2 tw-w-full">
      <div>
        <label>{{ label }}</label>
        <i v-if="mandatory" class="tw-text-rose-400"> *</i>
      </div>
      <div class="tw-flex tw-justify-center tw-items-center tw-w-full">
        <InputText v-if="type == 'text'" v-model="value" :disabled="disabled" class="tw-w-full" />
        <Password
          v-else-if="type == 'password'"
          v-model="value"
          :disabled="disabled"
          :feedback="feedback"
          class="tw-w-full"
        />
        <Dropdown
          v-else-if="type == 'dropdown'"
          v-model="value"
          :options="dropdownOptions"
          optionLabel="label"
          optionValue="value"
          class="tw-w-full"
        />
        <Textarea
          v-else-if="type == 'textArea'"
          :value="value"
          v-model="value"
          :rows="row"
          class="tw-w-full"
          :disabled="disabled"
        />
        <template v-else-if="type == 'collapse_textArea'">
          <span v-if="!expand" class="p-input-icon-right tw-w-full">
            <i class="pi pi-chevron-down tw-cursor-pointer" @click="expand = !expand" />
            <InputText :value="shortValue" class="tw-w-full" :disabled="disabled" />
          </span>
          <span v-if="expand" class="p-input-icon-right tw-w-full">
            <i class="pi pi-chevron-up tw-cursor-pointer" @click="expand = !expand" />
            <Textarea
              :value="value"
              v-model="model"
              :rows="row"
              :disabled="disabled"
              class="tw-w-full"
            />
          </span>
        </template>
        <InputGroup v-else-if="type == 'date'">
          <InputText v-model="value" :disabled="disabled" />
          <Button icon="pi pi-calendar" />
        </InputGroup>
        <template v-else-if="type == 'time'">
          <span class="p-input-icon-right tw-w-full">
            <i class="pi pi-clock" />
            <InputText v-model="value" :disabled="disabled" class="tw-w-full" />
          </span>
        </template>
        <template v-if="type === 'codeblock'">
          <div class="tw-w-full">
            <span v-if="!expand" class="p-input-icon-right tw-w-full">
              <i class="pi pi-chevron-down tw-cursor-pointer" @click="expand = !expand" />
              <InputText :value="shortValue" class="tw-w-full" :disabled="disabled" />
            </span>
            <div
              v-else
              class="tw-flex tw-items-center tw-gap-3 tw-p-3 tw-w-full tw-border tw-border-solid tw-border-gray-300 tw-rounded-md"
            >
              <div class="tw-flex-grow tw-w-0">
                <pre
                  class="tw-overflow-x-scroll"
                ><code v-html="beautify(value).value" class="tw-my-0 tw-text-base tw-h-80 tw-cursor-default tw-white"></code></pre>
              </div>
              <i
                class="pi pi-chevron-up tw-cursor-pointer tw-text-gray-500"
                @click="expand = !expand"
              />
            </div>
          </div>
        </template>
        <template v-if="download">
          <i
            class="pi pi-download tw-pl-5 tw-cursor-pointer"
            :class="{ 'tw-opacity-25': isLoading }"
            style="font-size: 1rem"
            @click="!isLoading && handleDownload(id)"
          ></i>
        </template>
        <Button v-if="downloadBtn" label="Download" icon="pi pi-download" class="tw-ml-5" />
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref, computed, PropType } from 'vue'

import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import InputGroup from 'primevue/inputgroup'
import Button from '@/components/Button.vue'

const model = ref()
const props = defineProps({
  id: { type: [String, Number] },
  type: { type: String, default: 'text' },
  label: { type: String, default: undefined },
  mandatory: { type: Boolean, default: false },
  feedback: { type: Boolean, default: false },
  download: { type: Boolean, default: false },
  downloadBtn: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  modelValue: { required: true },
  row: { type: Number },
  isExpand: { type: Boolean, default: false },
  colTable: { type: Object },
  dropdownOptions: { type: Array as PropType<{ label: string; value: any }[]> },
  isLoading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'download'])

const value: any = computed({
  get() {
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  },
})

const expand = ref(props.isExpand)

const handleDownload = (id: string | number | undefined, node: any = undefined) => {
  emit('download', id, node)
}

const shortValue = computed(() => {
  return value.value.length >= 80 ? (value.value as string).substring(0, 80) + '...' : value.value
})

/**
 * Beautify and highlight the code block
 */

import hljs from 'highlight.js'
import hlJSON from 'highlight.js/lib/languages/json'

hljs.registerLanguage('json', hlJSON)

const beautify = (value: string) => {
  return hljs.highlight(value, { language: 'json' })
}
</script>
