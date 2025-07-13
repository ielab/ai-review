<template>
  <div
    class="tw-flex tw-overflow-x-hidden"
    :class="state.visibleChat ? 'tw-w-[30%]' : 'tw-w-[0%]'"
  >
    <div
      class="tw-w-full tw-h-full tw-shadow border tw-overflow-y-auto tw-bg-white tw-relative tw-transition-all"
      :class="state.visibleChat ? '' : 'tw-translate-x-[100%]'"
    >
      <div
        v-if="state.configLoading"
        class="tw-z-[1000] tw-absolute tw-left-1/2 tw-top-1/2 tw-translate-x-[-50%] tw-translate-y-[-50%]"
      >
        <i
          class="pi pi-spin pi-spinner tw-mx-auto tw-text-[5rem] tw-text-white"
        />
      </div>
      <BlockUI
        :blocked="state.configLoading"
        :pt="{ root: 'tw-z-0 tw-h-full' }"
      >
        <div class="tw-flex tw-flex-col tw-h-full">
          <div
            class="tw-flex tw-justify-between tw-py-2 tw-px-4 tw-items-center"
          >
            <p class="tw-font-medium tw-text-xl">SR Assistant</p>
            <div class="tw-flex tw-flex-col tw-items-center">
              <div class="tw-flex tw-items-center tw-gap-1 tw-font-medium">
                <p class="tw-text-xs">AI Role</p>
                <i class="pi pi-info-circle tw-text-xs" />
              </div>
              <div class="tw-flex tw-items-center tw-gap-1">
                <div class="tw-flex tw-h-[2rem] tw-items-center tw-gap-1">
                  <ToggleButton
                    v-model="state.pre"
                    onLabel="Pre"
                    offLabel="Pre"
                    :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  />
                  <p>/</p>
                  <ToggleButton
                    v-model="state.co"
                    onLabel="Co"
                    offLabel="Co"
                    :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  />
                  <p>/</p>
                  <ToggleButton
                    v-model="state.post"
                    onLabel="Post"
                    offLabel="Post"
                    :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  />
                </div>
              </div>
            </div>
            <div class="tw-flex tw-flex-col tw-items-center">
              <div class="tw-flex tw-items-center tw-gap-1 tw-font-medium">
                <p class="tw-text-xs">AI Interaction</p>
                <i class="pi pi-info-circle tw-text-xs" />
              </div>
              <div class="tw-flex tw-items-center tw-gap-1 tw-text-xs">
                <p
                  :class="
                    !state.interactionLevel
                      ? 'tw-text-indigo-500 tw-font-medium'
                      : 'tw-text-gray-400'
                  "
                >
                  Low
                </p>
                <div class="tw-h-[2rem]">
                  <InputSwitch
                    v-model="state.interactionLevel"
                    class="tw-scale-[0.8]"
                  />
                </div>
                <p
                  :class="
                    state.interactionLevel
                      ? 'tw-text-indigo-500 tw-font-medium'
                      : 'tw-text-gray-400'
                  "
                >
                  High
                </p>
              </div>
            </div>
          </div>
          <TabView
            v-model:activeIndex="activeTab"
            :pt="{ panelcontainer: 'tw-p-0 tw-rounded-none' }"
          >
            <TabPanel :pt="{ headerAction: 'tw-px-4 tw-py-2', content: '' }">
              <template #header>
                <i class="pi pi-comment tw-mr-2" />
                Chat
              </template>
            </TabPanel>
            <TabPanel :pt="{ headerAction: 'tw-px-4 tw-py-2', content: '' }">
              <template #header>
                <i class="pi pi-sliders-h tw-mr-2" />
                Model Config
              </template>
            </TabPanel>
            <TabPanel :pt="{ headerAction: 'tw-px-4 tw-py-2' }">
              <template #header>
                <i class="pi pi-bookmark tw-mr-2" />
                Prompts
              </template>
            </TabPanel>
          </TabView>
          <Chat
            v-if="activeTab === 0"
            :title="state.docs[state.studyIndex].title"
            :selectedCard="state.studyIndex"
            :config="state.config"
            :co-response="state.coResponse"
            :loading="state.configLoading"
            :co="state.co"
            :ask-a-i-allowed="state.askAIAllowed"
            @p-i-c-o-extraction="$emit('p-i-c-o-extraction', $event)"
            @detailed-reasoning="$emit('detailed-reasoning', $event)"
            @chat="$emit('chat', $event)"
          />
          <ModelConfig v-if="activeTab === 1" :state="state" />
          <Prompts v-if="activeTab === 2" :state="state" />
        </div>
      </BlockUI>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";

import ToggleButton from "primevue/togglebutton";
import InputSwitch from "primevue/inputswitch";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import Chat from "@/views/review/components/Chat.vue";
import ModelConfig from "@/views/review/components/ModelConfig.vue";
import Prompts from "@/views/review/components/Prompts.vue";
import BlockUI from "primevue/blockui";
import { defineProps, defineEmits } from "vue";
import { State } from "@/types/reviewer";

defineProps<{
  state: State;
}>();

const emit = defineEmits<{
  (e: "update:pre", value: boolean): void;
  (e: "update:co", value: boolean): void;
  (e: "update:post", value: boolean): void;
  (e: "update:interaction-level", value: boolean): void;
  (e: "p-i-c-o-extraction", value: string): void;
  (e: "detailed-reasoning", value: string): void;
  (e: "chat", value: string): void;
}>();

const activeTab = ref(0);
</script>
