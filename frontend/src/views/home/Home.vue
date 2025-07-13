<template>
  <div class="tw-w-full">
    <div class="iframe-background">
      <div class="iframe">
        <iframe
          src="https://giphy.com/embed/pOEbLRT4SwD35IELiQ"
          width="100%"
          height="100%"
          style="position: absolute"
          frameBorder="0"
          class="giphy-embed"
          allowFullScreen
        ></iframe>
        <div class="dark-overlay"></div>
      </div>
      <div class="text-overlay tw-flex tw-flex-col tw-gap-7">
        <p class="tw-font-bold tw-text-4xl">AiReview</p>
        <p class="tw-text-nowrap tw-text-2xl">
          An Interactive Platform for LLM-Enhanced Systematic Review Screening
        </p>
        <div class="tw-flex tw-flex-col tw-gap-4">
          <p>
            AiReview is designed to (i) enable end users (e.g., medical
            researchers, librarians) with access to LLMs for SR tasks,
            especially T&A screening; and (ii) investigate the impact of LLMs on
            SR tasks through systematic evaluation and analysis.
          </p>
          <!-- <Message
            :closable="false"
            :pt="{ wrapper: 'tw-p-3', icon: 'tw-hidden' }"
          >
            <p class="tw-font-normal tw-text-sm">
              <span class="tw-font-bold">Note:</span> This is a demo
              website showcasing partial functionalities listed in our demo
              paper. The complete implementation will be available by the
              conference time. Currently, we use fixed example studies (as shown
              in the paper) to demonstrate the interface, avoiding API costs.
            </p>
          </Message> -->
        </div>
      </div>
    </div>
    <div class="tw-px-64 tw-py-16 tw-flex tw-flex-col tw-gap-16">
      <Fieldset
        legend="How to Use AiReview"
        :pt="{
          legend: 'tw-py-0 tw-px-3 tw-border-none tw-bg-transparent tw-text-xl',
        }"
      >
        <div class="tw-grid tw-grid-rows-3 tw-p-4 tw-gap-x-16 tw-gap-y-8">
          <div
            v-for="(item, index) in howToUse"
            class="tw-flex tw-flex-col tw-gap-4"
          >
            <div class="tw-flex tw-items-center tw-gap-2">
              <div class="icon-container">
                <i :class="item.icon" class="fa-lg tw-text-primary-500" />
              </div>
              <p class="tw-font-bold">{{ index + 1 }}. {{ item.header }}</p>
            </div>
            <p class="tw-text-[#4b5563]">{{ item.label }}</p>
          </div>
        </div>
      </Fieldset>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";

import Fieldset from "primevue/fieldset";
// import Message from "primevue/message";

const howToUse = ref([
  {
    icon: "pi pi-book",
    header: "Access Co-reviewer Mode",
    label: `Click the "Co-reviewer Screening" button to start. In this mode, you'll work alongside an LLM to screen titles and abstracts.`,
  },
  {
    icon: "pi pi-upload",
    header: "Review Example Studies",
    label: `Interact with our pre-loaded example studies to experience the screening interface and LLM assistance features.`,
  },
  {
    icon: "pi pi-info-circle",
    header: "Provide Feedback",
    label: `As you work through the examples, you can experience how the system provides LLM-assisted screening suggestions and supports your decision-making process.`,
  },
]);
</script>
