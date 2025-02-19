<template>
  <Card
    :pt="{
      root: 'tw-text-black tw-p-2 tw-rounded-xl',
      body: 'tw-p-0',
      content: 'tw-py-5 tw-px-3',
      footer: 'tw-py-0 tw-px-3',
    }"
    :style="props.selected ? selectedCardStyle : ''"
    class="tw-cursor-pointer"
    :class="[
      isCompleteReview ? 'tw-bg-indigo-50/80' : 'tw-bg-white',
      props.selected ? '' : 'tw-shadow',
    ]"
  >
    <template #header>
      <div class="tw-flex tw-flex-col tw-gap-y-2">
        <div class="tw-flex tw-justify-between">
          <div class="tw-flex tw-flex-col tw-gap-y-1 tw-pl-3">
            <p class="tw-font-medium tw-text-xl tw-pr-4">
              <span class="tw-text-sm tw-text-gray-400"
                >#{{ props.index + 1 }}</span
              >
              {{ props.article.title }}
            </p>
            <div>
              <span
                class="tw-text-indigo-500 tw-font-medium"
                v-for="(au, index) in article.authors"
                :key="index"
              >
                {{ au.split(", ")[1] }} {{ au.split(", ")[0]
                }}<span v-if="index != article.authors.length - 1">; </span>
              </span>
            </div>
          </div>
          <!-- <i
            @click.stop="updateFullView(true)"
            class="pi pi-window-maximize tw-text-slate-500 tw-cursor-pointer"
          ></i> -->
        </div>
        <Divider />
      </div>
    </template>
    <template #content>
      <p v-if="!selected" class="tw-line-clamp-3 tw-leading-relaxed">
        {{ props.article.abstract }}
      </p>
      <div v-else>
        <div
          v-if="extractSections(article.abstract)"
          class="tw-flex tw-flex-col tw-gap-y-3"
        >
          <p v-for="section in extractSections(article.abstract)">
            <span class="tw-font-medium">{{ section.header }}:</span>
            {{ section.content }}
          </p>
        </div>
        <p v-else class="tw-leading-relaxed">{{ article.abstract }}</p>
      </div>
    </template>
    <template #footer>
      <div
        class="tw-flex tw-justify-center tw-gap-x-6 tw-relative tw-items-end"
      >
        <!-- <div class="tw-absolute tw-right-0 tw-text-[0.7rem] tw-text-gray-400">
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-up"></i>
            <p>
              Press <b>Arrow Up</b>: Move Previous
            </p>
          </div>
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-down"></i>
            <p>
              Press <b>Arrow Down</b>: Move Next
            </p>
          </div>
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-turn-down tw-rotate-90"></i>
            <p>
              Press <b>Enter</b>: Full View Mode
            </p>
          </div>
        </div> -->
        <div class="tw-flex tw-justify-between tw-w-full tw-pb-2">
          <div class="tw-flex tw-gap-4">
            <Button
              :pt="{ root: 'tw-py-[0.2rem]' }"
              icon="fa-solid fa-xmark"
              label="Exclude"
              severity="danger"
              @click.stop="review('exclude')"
              class="tw-w-[11rem]"
              :style="getActiveStyle('exclude')"
            />
            <Button
              :pt="{ root: 'tw-py-[0.2rem]' }"
              icon="fa-solid fa-check"
              label="Include"
              severity="success"
              @click.stop="review('include')"
              class="tw-w-[11rem]"
              :style="getActiveStyle('include')"
            />
          </div>
          <div class="tw-flex tw-items-center tw-gap-4">
            <div
              class="tw-flex tw-items-center tw-gap-1 tw-text-primary-500 tw-font-medium"
            >
              <i class="pi pi-info-circle" />
              <p>
                AI suggests:
                <span v-if="index === 0" class="tw-text-green-500 tw-font-bold">
                  Include
                </span>
                <span v-else class="tw-text-red-500 tw-font-bold"> Exclude </span>
              </p>
            </div>
            <Button
              :pt="{ root: 'tw-py-[0.2rem]' }"
              icon="pi pi-sparkles"
              label="Ask AI"
              @click.stop="review('maybe')"
              class="tw-w-[11rem] tw-bg-indigo-500"
              :style="getActiveStyle('maybe')"
            />
          </div>
        </div>
      </div>
    </template>
  </Card>
  <ScreeningFullView
    :fullView="fullView"
    :index="index"
    @update:fullView="updateFullView"
  />
</template>

<script lang="ts" setup>
import Card from "primevue/card";
import Button from "primevue/button";
import ScreeningFullView from "./ScreeningFullView.vue";
import Divider from "primevue/divider";
import { ref } from "vue";

// import { useRoute } from "vue-router";
// const route = useRoute();

interface Article {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  feedback?: string;
}

const props = defineProps<{
  article: Article;
  selected: boolean;
  showKeysGuide: boolean;
  index: number;
}>();

// -------------------------------------

const isCompleteReview = ref(false);
const feedback = ref();

feedback.value = props.article.feedback;
isCompleteReview.value = feedback.value != null ? true : false;

function review(value: string) {
  if (isCompleteReview.value && feedback.value == value) {
    feedback.value = "";
    isCompleteReview.value = false;
  } else {
    feedback.value = value;
    if (feedback.value !== "maybe") {
      isCompleteReview.value = true;
    }
  }
}

const emit = defineEmits(["update:fullView"]);
const fullView = ref(false);
const updateFullView = (value: boolean) => {
  fullView.value = value;
  emit("update:fullView", fullView.value);
};

const selectedCardStyle = "box-shadow: #8B5CF6 0px 0px 0px 2px";
const includeStyle =
  "box-shadow: #dcfce7 0px 0px 0px 2px, #4ade80 0px 0px 0px 4px";
const maybeStyle =
  "box-shadow: #f1f5f9 0px 0px 0px 2px, #94a3b8 0px 0px 0px 4px";
const excludeStyle =
  "box-shadow: #fecaca 0px 0px 0px 2px, #f87171 0px 0px 0px 4px";

function getActiveStyle(value: "include" | "maybe" | "exclude") {
  const styleMap = {
    include: includeStyle,
    maybe: maybeStyle,
    exclude: excludeStyle,
  };

  if (isCompleteReview.value) {
    if (feedback.value === value) {
      return styleMap[value];
    }
    return "opacity: 40%";
  }
}

// window.addEventListener("keydown", (e) => {
//   if (e.key === "Enter" && props.selected) {
//     e.preventDefault(); // Prevent default action (like form submission)
//     updateFullView(true);
//   }
// });

function extractSections(abstract: string) {
  // Regular expression to match dynamic section headers followed by a colon and content
  const sectionRegex = /([A-Z][A-Z\s]*):\s*([\s\S]*?)(?=\s*[A-Z][A-Z\s]*:|$)/g;
  const sections = [];
  let match;

  // Iterate through all matches
  while ((match = sectionRegex.exec(abstract)) !== null) {
    const sectionHeader = match[1].trim();
    const sectionContent = match[2].trim();
    sections.push({
      header: sectionHeader,
      content: sectionContent,
    });
  }

  if (sections.length > 0) return sections;
  return null;
}
</script>
