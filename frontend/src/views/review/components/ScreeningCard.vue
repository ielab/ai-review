<template>
  <Card
    :pt="{
      root: 'tw-text-black tw-p-2 tw-rounded-xl tw-bg-white',
      body: 'tw-p-0',
      content: 'tw-px-3',
      footer: 'tw-py-0 tw-px-3',
    }"
    :class="[
      isCompleteReview ? 'tw-bg-primary-500/5' : 'tw-bg-white',
      props.selected
        ? 'active-step'
        : 'tw-border-solid tw-border-slate-100 tw-shadow',
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
              {{ props.doc.title }}
            </p>
            <p class="tw-text-indigo-500 tw-font-medium">
              {{ props.doc.authors }}
            </p>
          </div>
        </div>
        <Divider />
      </div>
    </template>
    <template #content>
      <div>
        <div v-if="!showFullAbstract" class="tw-leading-relaxed tw-inline">
          {{ truncatedAbstract }}
        </div>

        <div v-else class="tw-leading-relaxed tw-inline">
          {{ props.doc.abstract }}
        </div>

        <p
          @click="toggleAbstract"
          class="tw-inline tw-text-primary-500 tw-font-medium tw-cursor-pointer tw-ml-2"
        >
          {{ showFullAbstract ? "Show Less" : "Show More" }}
        </p>
      </div>
    </template>
    <template #footer>
      <div class="tw-flex">
        <div class="tw-flex tw-gap-4">
          <Button
            :pt="{ root: 'tw-py-[0.5rem]' }"
            icon="fa-solid fa-xmark"
            label="Exclude"
            severity="danger"
            @click.stop="giveFeedback('exclude')"
            class="tw-w-[11rem]"
            :style="getActiveStyle('exclude')"
          />
          <Button
            :pt="{ root: 'tw-py-[0.5rem]' }"
            icon="fa-solid fa-check"
            label="Include"
            severity="success"
            @click.stop="giveFeedback('include')"
            class="tw-w-[11rem]"
            :style="getActiveStyle('include')"
          />
        </div>
        <div class="tw-flex-1 tw-flex tw-justify-end tw-gap-4">
          <Button
            v-if="preResponse && !suggestionVisible"
            outlined
            :pt="{ root: 'tw-py-[0.5rem]' }"
            label="Request AI Suggestion"
            @click="suggestionVisible = !suggestionVisible"
          />
          <div
            v-if="preResponse && suggestionVisible"
            class="tw-flex tw-relative tw-w-fit tw-justify-end"
          >
            <Button
              label="Click to Copy AI Suggestion"
              outlined
              icon="pi pi-clone"
              :pt="{
                root: 'tw-py-[0.5rem] tw-opacity-0 tw-z-[1000] tw-transition-all hover:tw-opacity-100 tw-bg-white',
              }"
              :severity="
                parseDecisionReason(preResponse.content)?.decision === 'Exclude'
                  ? 'danger'
                  : 'success'
              "
              v-tooltip.top="{
                value: `${parseDecisionReason(preResponse.content)?.reason}`,
                pt: {
                  root: 'tw-max-w-[50vw]',
                  text: 'tw-text-sm',
                },
              }"
              @click="copyReasoning"
            />
            <Button
              outlined
              :pt="{ root: 'tw-py-[0.5rem] tw-bg-white' }"
              class="tw-absolute tw-opacity-100 hover:tw-opacity-0 tw-transition-all"
              :severity="
                parseDecisionReason(preResponse.content)?.decision === 'Exclude'
                  ? 'danger'
                  : 'success'
              "
              :icon="
                parseDecisionReason(preResponse.content)?.decision === 'Exclude'
                  ? 'pi pi-times-circle'
                  : 'pi pi-check-circle'
              "
              :label="`AI suggests: ${
                parseDecisionReason(preResponse.content)?.decision
              }`"
            />
          </div>

          <Button
            v-if="state.askAIAllowed"
            :pt="{ root: 'tw-py-[0.5rem]' }"
            icon="pi pi-sparkles"
            label="Ask AI"
            class="tw-w-[11rem]"
            @click.stop="askAI"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
@keyframes blink {
  from {
    @apply tw-border-indigo-100;
  }
  50% {
    @apply tw-border-indigo-300;
  }
  to {
    @apply tw-border-indigo-100;
  }
}

.active-step {
  @apply tw-bg-primary-200 tw-border-4 tw-border-solid tw-border-primary-100;
  animation: blink 2s infinite;
}
</style>

<script lang="ts" setup>
import Card from "primevue/card";
import Button from "primevue/button";
import Divider from "primevue/divider";

import { ref, computed, onMounted, watch } from "vue";
import { IDoc, State } from "@/types/reviewer";
import { IPreResponse } from "@/types/response";
import { parseDecisionReason } from "@/utils/string";

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

const props = defineProps<{
  doc: IDoc;
  selected: boolean;
  index: number;
  state: State;
  preResponse: IPreResponse;
}>();

const suggestionVisible = ref(false);

const showFullAbstract = ref(false);
const maxLength = 500; // Adjust this value as needed

const truncatedAbstract = computed(() => {
  if (!props.doc.abstract || props.doc.abstract.length <= maxLength) {
    return props.doc.abstract;
  }
  return props.doc.abstract.substring(0, maxLength) + "...";
});

const toggleAbstract = () => {
  showFullAbstract.value = !showFullAbstract.value;
};

// -------------------------------------

const isCompleteReview = ref(false);
const feedback = ref();

const emit = defineEmits([
  "update:visible-chat",
  "update:study-index",
  "ask-a-i",
  "give-feedback",
]);

// const selectedCardStyle = "box-shadow: #8B5CF6 0px 0px 0px 2px";
const includeStyle =
  "box-shadow: #dcfce7 0px 0px 0px 2px, #4ade80 0px 0px 0px 4px";
const excludeStyle =
  "box-shadow: #fecaca 0px 0px 0px 2px, #f87171 0px 0px 0px 4px";

function getActiveStyle(value: "include" | "exclude") {
  const styleMap = {
    include: includeStyle,
    exclude: excludeStyle,
  };

  if (isCompleteReview.value) {
    if (feedback.value === value) {
      return styleMap[value];
    }
    return "opacity: 40%";
  }
}

function askAI() {
  emit("update:visible-chat", true);
  emit("update:study-index", props.index);
  emit("ask-a-i", props.index);
}

const copyReasoning = async () => {
  const decision = parseDecisionReason(props.preResponse.content)?.reason;

  if (decision) {
    try {
      await navigator.clipboard.writeText(decision);
    } catch (error) {
      console.error("Failed to copy decision:", error); // Optional: to log failure
    }
  }

  showToast("success", "AI suggestion copied successfully.");
};

const giveFeedback = async (
  userFeedback: "include" | "exclude" | "unjudged"
) => {
  if (feedback.value === userFeedback) return;

  emit('update:study-index', props.index)
  emit("give-feedback", userFeedback);

  feedback.value = userFeedback;
  isCompleteReview.value = true;
};

onMounted(() => {
  feedback.value = props.doc.user_feedback;
  isCompleteReview.value = !!feedback.value;
});

watch(
  () => props.state.config.llm_interaction_level,
  (level: boolean) => {
    suggestionVisible.value = level;
  },
  { immediate: true }
);
</script>
