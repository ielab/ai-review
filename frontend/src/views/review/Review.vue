<template>
  <div class="tw-flex tw-flex-col tw-px-4 tw-bg-slate-50 tw-min-h-[94vh]">
    <div class="tw-flex tw-gap-2 tw-bg-slate-50 tw-pb-5">
      <div
        class="tw-h-full tw-flex tw-flex-col tw-gap-4"
        :class="visibleChat ? 'tw-w-[70%]' : 'tw-w-full'"
      >
        <div
          v-if="!visibleChat"
          class="tw-fixed tw-z-[100] tw-top-[3.8rem] tw-right-3"
        >
          <Button
            v-tooltip.left="`Expand SR Assistant Panel`"
            @click="updateVisibleChat(true)"
            icon="pi pi-sparkles"
            rounded
            class="tw-border-[0.2rem] tw-border-white tw-shadow"
          />
        </div>
        <ScrollPanel
          :pt="{
            bary: 'tw-bg-purple-500',
          }"
          class="tw-w-full"
        >
          <div class="tw-flex tw-flex-col tw-gap-4 tw-pl-1 tw-pr-4 tw-py-4">
            <p
              class="tw-text-xl tw-text-center tw-font-bold tw-items-center tw-flex tw-justify-center"
            >
              Bayesian PTSD-Trajectory Analysis with Informed Priors<br />Based
              on a Systematic Literature Search and Expert Elicitation
            </p>
            <div
              v-for="(article, index) in articles.slice(0, 25)"
              @click="selectCard(index)"
              class="screening-card"
            >
              <ScreeningCard
                v-if="!isLoading"
                :key="index"
                :index="index"
                class="tw-border-[0.05rem] tw-border-neutral-200 tw-bg-slate-50 tw-w-full"
                style="border: solid"
                :article="article"
                :selected="selectedCard === index"
                :showKeysGuide="showKeysGuide"
              />
            </div>
          </div>
        </ScrollPanel>
      </div>
      <div
        v-if="visibleChat"
        class="tw-w-[30%] tw-flex tw-flex-col tw-shadow tw-bg-white tw-h-[94vh] tw-fixed tw-z-[100] tw-right-0"
      >
        <div class="tw-px-4 tw-py-2 tw-flex tw-justify-between tw-items-center">
          <CustomIconButton
            v-tooltip.left="`Collapse SR Assistant Panel`"
            icon="pi pi-angle-double-right"
            class="tw-absolute tw-left-[-1.6rem] tw-top-0 tw-rounded-none"
            size="small"
            @click="updateVisibleChat(false)"
          />
          <h3 class="tw-text-slate-600">SR Assistant</h3>

          <div class="tw-flex tw-flex tw-flex-col tw-text-xs tw-items-center">
            <div class="tw-flex tw-items-center tw-gap-1">
              <p class="tw-font-medium">AI Role</p>
              <i class="pi pi-info-circle tw-scale-[0.9] tw-text-indigo-500" />
            </div>
            <div class="tw-flex tw-items-center tw-gap-1">
              <div class="tw-flex tw-h-[2rem] tw-items-center tw-gap-1">
                <ToggleButton
                  v-model="pre"
                  onLabel="Pre"
                  offLabel="Pre"
                  :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  @update:modelValue="updateRole('pre')"
                />
                <p>/</p>
                <ToggleButton
                  v-model="co"
                  onLabel="Co"
                  offLabel="Co"
                  :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  @update:modelValue="updateRole('co')"
                />
                <p>/</p>
                <ToggleButton
                  v-model="post"
                  onLabel="Post"
                  offLabel="Post"
                  :pt="{ root: 'tw-p-1 tw-text-xs' }"
                  @update:modelValue="updateRole('post')"
                />
              </div>
            </div>
          </div>

          <div class="tw-flex tw-flex tw-flex-col tw-text-xs tw-items-center">
            <div class="tw-flex tw-items-center tw-gap-1">
              <p class="tw-font-medium">AI Interaction</p>
              <i class="pi pi-info-circle tw-scale-[0.9] tw-text-indigo-500" />
            </div>
            <div class="tw-flex tw-items-center tw-gap-1">
              <p
                :class="
                  !high
                    ? 'tw-text-indigo-500 tw-font-medium'
                    : 'tw-text-gray-400'
                "
              >
                Low
              </p>
              <div class="tw-h-[2rem]">
                <InputSwitch
                  v-model="high"
                  class="tw-scale-[0.8]"
                  @update:modelValue="updateLevel()"
                />
              </div>
              <p
                :class="
                  high
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
          :pt="{
            nav: '!tw-bg-white',
            panelContainer: 'tw-p-0 tw-bg-transparent',
          }"
        >
          <TabPanel
            :pt="{ headerAction: '!tw-w-full !tw-py-2 !tw-px-4 !tw-bg-white' }"
          >
            <template #header>
              <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
                <i class="pi pi-comment" />
                Chat
              </div>
            </template>
            <Chat />
          </TabPanel>
          <TabPanel
            :pt="{ headerAction: '!tw-w-full !tw-py-2 !tw-px-4 !tw-bg-white' }"
          >
            <template #header>
              <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
                <i class="pi pi-sliders-v" />
                Model Config
              </div>
            </template>
            <ModelConfig />
          </TabPanel>
          <TabPanel
            :pt="{ headerAction: '!tw-w-full !tw-py-2 !tw-px-4 !tw-bg-white' }"
          >
            <template #header>
              <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
                <i class="pi pi-bookmark" />
                Prompts
              </div>
            </template>
            <Prompts />
          </TabPanel>
        </TabView>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Button from "primevue/button";
import ToggleButton from "primevue/togglebutton";

import Chat from "./components/Chat.vue";
import ModelConfig from "./components/ModelConfig.vue";
import Prompts from "./components/Prompts.vue";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import ScrollPanel from "primevue/scrollpanel";
import InputSwitch from "primevue/inputswitch";
import ScreeningCard from "./components/ScreeningCard.vue";

import { ref, nextTick, onMounted } from "vue";

import { useLoading } from "@/composables/loading";
const { isLoading } = useLoading(false);

// import { useDirty } from "@/composables/dirty";

import { reviewerStore } from "@/stores/reviewer";
import { storeReviewer } from "@/utils/reviewer";

// dummy
import articles from "./configs/data.json";
import CustomIconButton from "@/components/CustomIconButton.vue";

const showKeysGuide = ref(true);
const visibleChat = ref(reviewerStore.visibleChat);

// selecting article
const selectedCard = ref<number | null>(0);
const selectCard = (index: number) => {
  selectedCard.value = selectedCard.value === index ? null : index;
  scrollToSelectedCard(index);
};

const scrollToSelectedCard = (index: number | null) => {
  if (index !== null) {
    nextTick(() => {
      const cardElement = document.querySelectorAll(".screening-card")[
        index
      ] as HTMLElement;
      if (cardElement) {
        const navbarHeight = 26;
        const cardRect = cardElement.getBoundingClientRect();
        const scrollPosition =
          window.scrollY +
          cardRect.top -
          (window.innerHeight / 2 - cardRect.height / 2) -
          navbarHeight;

        window.scrollTo({
          top: scrollPosition,
          behavior: "smooth",
        });
      }
    });
  }
};

const pre = ref(reviewerStore.pre);
const co = ref(reviewerStore.co);
const post = ref(reviewerStore.post);
const high = ref(reviewerStore.level === "high");

function updateRole(role: "pre" | "co" | "post") {
  const reviewer = reviewerStore;

  if (role === "pre") {
    reviewer.pre = pre.value;
  } else if (role === "co") {
    reviewer.co = co.value;
  } else {
    reviewer.post = post.value;
  }

  storeReviewer(reviewer);
}

function updateLevel() {
  const reviewer = reviewerStore;

  if (high.value) {
    reviewer.level = "high";
  } else {
    reviewer.level = "low";
  }

  storeReviewer(reviewer);
}

function updateVisibleChat(visible: boolean) {
  const reviewer = reviewerStore;

  visibleChat.value = visible;
  reviewer.visibleChat = visible;

  storeReviewer(reviewer);
}

onMounted(() => {
  // console.log(reviewerStore);
});
</script>
