<template>
  <div>
    <div class="tw-p-4 tw-flex tw-flex-col tw-gap-5 tw-relative">
      <div class="tw-flex tw-flex-col tw-gap-2">
        <label>Large Language Model</label>
        <Dropdown
          v-model="selectedModel"
          :options="models"
          optionLabel="name"
        />
      </div>

      <div class="tw-flex tw-flex-col tw-gap-3">
        <label
          >Temperature
          <span class="tw-text-gray-500 tw-text-xs"
            >(Lower for more consistent results)</span
          ></label
        >
        <Slider
          v-model="temperature"
          :pt="{ handle: 'tw-translate-y-[-50%]' }"
          class="tw-w-[95%] tw-mx-auto"
        />
        <div class="tw-flex tw-justify-between">
          <p class="tw-text-gray-500 tw-text-sm">Deterministic (0)</p>
          <p class="tw-text-gray-500 tw-text-sm">Creative (1)</p>
        </div>
      </div>

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label
          >Maximum Output Range
          <span class="tw-text-gray-500 tw-text-xs">(in tokens)</span></label
        >
        <Dropdown
          v-model="selectedLength"
          :options="lengths"
          optionLabel="name"
        />
      </div>

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label>Response Format</label>
        <Dropdown
          v-model="selectedFormat"
          :options="formats"
          optionLabel="name"
        />
      </div>

      <div class="tw-flex tw-justify-between">
        <Button
          text
          severity="secondary"
          icon="pi pi-refresh"
          label="Reset to Default"
          :pt="{ root: '!tw-px-1 !tw-py-[0.2rem]' }"
        />
        <Button label="Apply Changes" :pt="{ root: '!tw-py-[0.2rem]' }" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Dropdown from "primevue/dropdown";
import Slider from "primevue/slider";
import Button from "@/components/Button.vue";

import { ref } from "vue";

const models = ref([{ name: "gpt-4o" }]);
const selectedModel = ref(models.value[0]);

const temperature = ref(0);

const lengths = ref([
  { name: "1024 tokens (~750 words)" },
  { name: "2048 tokens (~1500 words)" },
]);
const selectedLength = ref(lengths.value[1]);

const formats = ref([{ name: "text" }]);
const selectedFormat = ref(formats.value[0]);
</script>
