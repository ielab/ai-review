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
          <label class="tw-font-medium">Ask AI Prompt</label>
          <Textarea
            v-model="prompt"
            rows="7"
            :pt="{ root: 'tw-text-sm tw-p-1' }"
          />
        </div>

        <Accordion>
          <AccordionTab
            header="Sample Prompt"
            :pt="{ headeraction: 'tw-p-3 tw-font-medium', content: 'tw-p-2' }"
          >
            <Textarea
              :value="defaultPrompt"
              rows="7"
              :pt="{ root: 'tw-text-sm tw-p-1 tw-w-full' }"
            />
          </AccordionTab>
        </Accordion>
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
        @click="applyChanges(defaultPrompt)"
      />
      <Button
        icon="pi pi-check"
        label="Apply Changes"
        @click="applyChanges(prompt)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import Button from "primevue/button";
import ScrollPanel from "primevue/scrollpanel";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";

import { useToast } from "@/composables/toast";
import { State } from "@/types/reviewer";
import { useLLMConfig } from "@/composables/llmConfig";
import { useRoute } from "vue-router";
import Textarea from "primevue/textarea";

const { showToast } = useToast();
const route = useRoute();

const props = defineProps<{
  state: State;
}>();

const { updatePrompt } = useLLMConfig(ref(props.state), route);

const defaultPrompt = ref<string>(
  `{"system": "You are a research assistant helping with systematic review screening. Your task is to provide clear, concise feedback about whether a study meets the inclusion criteria, following a specific structured format. Base your assessment on the provided inclusion/exclusion criteria and study details.", "assistant": "On a scale from 1 (very low probability) to 4 (very high probability), how would you rate the relevance of the scientific publication for inclusion into a systematic literature review based on the relevant criteria and based on title and abstract?\n\nInclusion criteria: \n{inclusion_criteria}\n\nResponse format:\nBased on the selected study and the configured inclusion/exclusion criteria, here's my feedback:\n\"{title}\" by {authors}\nConclusion: [Provide a single paragraph stating whether the study meets the criteria, listing specifically which criteria are met. Use clear, objective language.]\nRelevance: Rated [X]/4 (high/moderate/low probability of inclusion) for the systematic review."}`
);

const prompt = ref<string>("");

const applyChanges = async (prompt: String) => {
  try {
    props.state.configLoading = true;
    await updatePrompt(prompt);
    showToast(
      "success",
      "Prompt Saved",
      "The prompt has been updated successfully."
    );
  } catch (error) {
    showToast(
      "error",
      "Failed to Save Prompt",
      "An error occurred while updating the prompt."
    );
    console.error("Failed to apply changes:", error);
  } finally {
    props.state.configLoading = false;
  }
};
</script>
