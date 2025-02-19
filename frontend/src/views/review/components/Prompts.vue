<template>
  <div>
    <div class="tw-p-4 tw-flex tw-flex-col tw-gap-5 tw-relative">
      <!-- <p class="tw-font-bold tw-text-gray-600">Prompts Configurations</p> -->

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label class="tw-font-medium">System Prompt</label>
        <Textarea
          rows="4"
          v-model="systemPrompt"
          :pt="{ root: 'tw-text-sm tw-p-1' }"
        />
      </div>

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label class="tw-font-medium">Task Template</label>
        <Textarea
          rows="4"
          v-model="taskTemplate"
          :pt="{ root: 'tw-text-sm tw-p-1' }"
        />
      </div>

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label class="tw-font-medium">Response Format</label>
        <Textarea
          rows="8"
          v-model="responseFormat"
          :pt="{ root: 'tw-text-sm tw-p-1' }"
        />
      </div>

      <div class="tw-flex tw-flex-col tw-gap-2">
        <label class="tw-font-medium">Inclusion Criteria</label>
        <Textarea
          rows="8"
          v-model="inclusionCriteria"
          :pt="{ root: 'tw-text-sm tw-p-1' }"
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
        <Button
          icon="pi pi-save"
          label="Save Prompts"
          :pt="{ root: '!tw-py-[0.2rem]' }"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";

import Textarea from "primevue/textarea";
import Button from "@/components/Button.vue";

const systemPrompt = ref(
  "You evaluate the relevance of scientific publications based on named criteria and based on title and abstract of a publication. Your answer consists only of a single digit ({digit_string}). Do not include further explanation."
);

const taskTemplate = ref(
  "On a scale from 1 (very low probability) to {levels} (very high probability), how would you rate the relevance of the scientific publication for inclusion into a systematic literature review based on the relevant criteria and based on title and abstract?"
);

const responseFormat =
  ref(`Based on the selected study and the configured inclusion/exclusion criteria, here’s my feedback: "{Title}" by {Authors}  
Conclusion: [Provide a single paragraph stating whether the study meets the criteria, specifying which criteria are met. Use clear, objective language.]  
Relevance: Rated [X]/4 (high/moderate/low probability of inclusion) for the systematic review.`);

const inclusionCriteria = ref(
  "(a) longitudinal studies with at least three measurement waves measuring posttraumatic stress disorder (PTSD),                                                   (b) studies that measured PTSD on a continuous scale via an interview or questionnaire,                     (c) and studies that used a clustering method (Latent growth mixture modelling, hierarchical cluster analysis),                                                             (d) traumatic stress symptoms following events that appeared to fulfill DSM-IV criterion A1 for PTSD or acute stress disorder."
);
</script>
