<template>
  <div class="tw-flex-1 tw-overflow-y-hidden">
    <ScrollPanel
      style="width: 100%; height: 100%"
      :pt="{
        bary: 'tw-bg-primary-500 tw-opacity-100',
      }"
    >
      <div
        :class="{
          'tw-h-full':
            (coResponse &&
              coResponse.length === 1 &&
              coResponse.some((item) => item.isLoading === true)) ||
            (coResponse && coResponse.length <= 0),
        }"
        class="tw-flex tw-flex-col"
      >
        <div
          v-if="route.name !== 'post-review'"
          class="tw-drop-shadow-xl tw-bg-primary-50/25 tw-backdrop-blur-sm tw-sticky tw-top-0 tw-flex tw-justify-between tw-items-center tw-gap-2 tw-w-full tw-px-4 tw-py-2"
        >
          <i class="pi pi-book tw-text-sm" />
          <small class="tw-line-clamp-1 tw-flex-1 tw-truncate">{{
            title
          }}</small>
          <small class="tw-whitespace-nowrap"># {{ selectedCard + 1 }}</small>
        </div>

        <div
          v-if="coResponse && coResponse.length <= 0"
          class="tw-flex-1 tw-items-center tw-flex tw-justify-center"
        >
          <i class="pi pi-comments tw-text-primary-100 tw-text-6xl" />
        </div>

        <div
          v-else
          class="tw-flex tw-flex-col tw-gap-4 tw-p-6 tw-bg-white tw-h-full tw-min-h-[100vh]"
        >
          <div
            v-for="response in coResponse"
            class="tw-flex tw-flex-col tw-gap-4"
          >
            <div class="tw-flex tw-justify-end tw-h-full">
              <div
                class="tw-p-3 tw-leading-relaxed tw-rounded-xl tw-shadow tw-w-fit tw-bg-slate-50"
              >
                <p v-if="response.task === 'ask_ai'" class="tw-inline">
                  Ask AI
                </p>
                <p v-else-if="response.task === 'pico_extract'">
                  PICO Extraction
                </p>
                <p v-else-if="response.task === 'detail_reason'">
                  Detailed Reasoning
                </p>
                <p v-else>
                  {{ response.message }}
                </p>
              </div>
            </div>

            <div v-if="response.isLoading">
              <i class="pi pi-spin pi-spinner tw-text-primary-500" />
            </div>

            <div
              v-else
              class="tw-p-3 tw-leading-relaxed tw-rounded-xl tw-shadow tw-w-fit tw-bg-primary-50"
            >
              <p v-html="response.llmResponse.replace(/\n/g, '<br>')" />
            </div>
          </div>
        </div>

        <div
          :class="coResponse && coResponse.length > 0 ? 'tw-sticky' : ''"
          class="tw-w-full tw-drop-shadow-xl tw-bg-primary-50/25 tw-backdrop-blur-sm tw-bottom-0 tw-z-[1001] tw-p-4 tw-flex tw-flex-col tw-gap-2 tw-items-center tw-justify-center"
        >
          <div
            v-if="route.name !== 'post-review'"
            v-tooltip.top="{
              value: `${co ? '' : 'Please enable the Co AI Role.'}`,
              pt: {
                root: 'tw-max-w-none',
                text: 'tw-text-sm',
              },
            }"
            class="tw-bg-white tw-w-full tw-p-3 tw-flex tw-flex-col tw-gap-2 tw-rounded-md border tw-shadow"
          >
            <p>What other tasks can I assist with?</p>
            <div class="tw-flex tw-gap-2">
              <Button
                icon="pi pi-bookmark"
                label="PICO Extraction"
                text
                raised
                :disabled="!co"
                :pt="{ root: 'tw-w-full tw-p-2' }"
                @click="emit('p-i-c-o-extraction', selectedCard)"
              />
              <Button
                icon="pi pi-lightbulb"
                label="Detailed Reasoning"
                text
                raised
                :disabled="!co"
                :pt="{ root: 'tw-w-full tw-p-2' }"
                @click="emit('detailed-reasoning', selectedCard)"
              />
            </div>
          </div>
          <InputGroup
            v-tooltip.top="{
              value: `${
                askAIAllowed
                  ? ''
                  : 'Please enable the Co AI Role and set the interaction level to high.'
              }`,
              pt: {
                root: 'tw-max-w-none',
                text: 'tw-text-sm',
              },
            }"
          >
            <InputText
              :disabled="!askAIAllowed"
              v-model="inputMessage"
              placeholder="Type your message..."
              @keyup.enter="
                $emit('chat', inputMessage);
                inputMessage = '';
              "
            />
            <Button
              icon="pi pi-send"
              :disabled="!askAIAllowed"
              @click="$emit('chat', inputMessage)"
            />
          </InputGroup>
        </div>
      </div>
    </ScrollPanel>
  </div>
</template>

<script lang="ts" setup>
import { PropType, ref } from "vue";

import ScrollPanel from "primevue/scrollpanel";
import InputGroup from "primevue/inputgroup";
import InputText from "primevue/inputtext";
import Button from "primevue/button";

import { ILLMConfig } from "@/types/reviewer";
import { ICoResponse } from "@/types/response";

import { useRoute } from "vue-router";
const route = useRoute();

defineProps({
  title: { type: String, default: "" },
  selectedCard: { type: Number, default: 0 },
  config: { type: Object as PropType<ILLMConfig> }, // Define the correct type for config
  coResponse: { type: Array as PropType<ICoResponse[]> }, // Define the correct type for coResponse
  loading: { type: Boolean },
  askAIAllowed: { type: Boolean },
  co: { type: Boolean },
});

const emit = defineEmits(["p-i-c-o-extraction", "detailed-reasoning", "chat"]);
const inputMessage = ref("");
</script>
