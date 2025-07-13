<template>
  <div class="tw-flex-1 tw-overflow-y-hidden">
    <ScrollPanel
      style="width: 100%; height: 100%"
      :pt="{
        bary: 'tw-bg-primary-500 tw-opacity-100',
      }"
    >
      <div
        class="tw-flex tw-flex-col tw-gap-8 tw-overflow-auto tw-py-4 tw-px-8"
      >
        <div class="tw-flex tw-flex-col tw-gap-2">
          <label class="tw-font-medium">Large Language Model</label>
          <Dropdown
            v-model="selectedModel"
            :options="models"
            optionLabel="label"
          />
        </div>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <label class="tw-font-medium"
            >Temperature
            <span class="tw-text-gray-500 tw-text-xs"
              >(Lower for more consistent results)</span
            ></label
          >
          <div class="tw-flex tw-items-center tw-gap-4">
            <Tag :value="formattedTemperature" />
            <Slider
              v-model="temperature"
              :step="0.1"
              :min="0"
              :max="1"
              :pt="{ handle: 'tw-translate-y-[-50%]' }"
              class="tw-w-[95%] tw-mx-auto"
            />
          </div>
          <div class="tw-flex tw-justify-between">
            <p class="tw-text-gray-500 tw-text-sm">Deterministic (0)</p>
            <p class="tw-text-gray-500 tw-text-sm">Creative (1)</p>
          </div>
        </div>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <label class="tw-font-medium"
            >Maximum Output Range
            <span class="tw-text-gray-500 tw-text-xs">(in tokens)</span></label
          >
          <Dropdown
            v-model="selectedLength"
            :options="lengths"
            optionLabel="label"
          />
        </div>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <label class="tw-font-medium">Response Format</label>
          <Dropdown
            v-model="selectedFormat"
            :options="formats"
            optionLabel="label"
          />
        </div>
      </div>
    </ScrollPanel>
    <div
      class="tw-flex tw-justify-between tw-flex-1 tw-px-8 tw-py-4 tw-sticky tw-bottom-0 tw-z-[100]"
    >
      <Button
        outlined
        severity="secondary"
        icon="pi pi-refresh"
        label="Reset to Default"
        @click="resetToDefault"
      />
      <Button icon="pi pi-check" label="Apply Changes" @click="applyChanges" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import Dropdown from "primevue/dropdown";
import Slider from "primevue/slider";
import Button from "primevue/button";
import Tag from "primevue/tag";
import ScrollPanel from "primevue/scrollpanel";

import { useToast } from "@/composables/toast";
import { State } from "@/types/reviewer";
import { useLLMConfig } from "@/composables/llmConfig";
import { useRoute } from "vue-router";

const { showToast } = useToast();
const route = useRoute();

const props = defineProps<{
  state: State;
}>();

const { updateConfig } = useLLMConfig(ref(props.state), route);

// Large Language Model
const models = ref([{ label: "GPT-4o", value: "gpt-4o" }]);
const selectedModel = computed({
  get: () => {
    const matchingModel = models.value.find(
      (model) => model.value === props.state.config.llm_parameters.model_name
    );
    return matchingModel;
  },
  set: (value) => {
    props.state.config.llm_parameters.model_name = value?.value || "gpt-4o";
  },
});

// Temperature
const temperature = ref(props.state.config.llm_parameters.temperature);
const formattedTemperature = computed(() => {
  return temperature.value.toFixed(1); // Format to one decimal place
});

// Maximum Output Range
const lengths = ref([
  { label: "1024 tokens (~750 words)", value: 1024 },
  { label: "2048 tokens (~1500 words)", value: 2048 },
]);
const selectedLength = computed({
  get: () => {
    const matchingLength = lengths.value.find(
      (length) => length.value === props.state.config.llm_parameters.max_tokens
    );
    return matchingLength;
  },
  set: (value) => {
    props.state.config.llm_parameters.max_tokens = value?.value || 2048;
  },
});

// Response Format
const formats = ref([{ label: "Text", value: "text" }]);
const selectedFormat = computed({
  get: () => {
    const matchingFormat = formats.value.find(
      (format) =>
        format.value === props.state.config.llm_parameters.response_format
    );
    return matchingFormat;
  },
  set: (value) => {
    props.state.config.llm_parameters.response_format = value?.value || "text";
  },
});

const applyChanges = async () => {
  try {
    props.state.configLoading = true;
    props.state.config.llm_parameters.temperature = temperature.value;
    props.state.config.llm_parameters.max_tokens =
      selectedLength.value?.value || 2048;
    await updateConfig();
    showToast(
      "success",
      "Configuration Updated",
      "Settings have been successfully applied."
    );
  } catch (error) {
    showToast(
      "error",
      "Update Failed",
      "Failed to apply configuration changes."
    );
    console.error("Failed to apply changes:", error);
  } finally {
    props.state.configLoading = false;
  }
};

const resetToDefault = async () => {
  try {
    temperature.value = 0; // Default temperature
    props.state.config.llm_parameters.temperature = 0;
    props.state.config.llm_parameters.max_tokens = 2048; // Default max_tokens
    selectedLength.value = lengths.value.find(
      (length) => length.value === 2048
    );
    await updateConfig();
    showToast(
      "success",
      "Reset to Default",
      "Configuration has been reset to default values."
    );
  } catch (error) {
    showToast(
      "error",
      "Update Failed",
      "Failed to reset to default values."
    );
    console.error("Failed to apply changes:", error);
  }
};
</script>
