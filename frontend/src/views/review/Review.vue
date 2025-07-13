<template>
  <div
    v-if="state.initLoading || isLoading"
    class="tw-flex tw-h-[94vh] tw-bg-primary-100"
  >
    <Loading severity="primary" />
  </div>

  <div v-else class="tw-flex tw-h-[94vh] tw-bg-primary-100">
    <div class="tw-flex-1">
      <ScrollPanel style="width: 100%; height: 100%" :pt="{}">
        <div
          class="tw-sticky tw-top-0 tw-z-[1001] tw-p-4 tw-flex tw-items-center tw-justify-center tw-bg-primary-50/25 tw-backdrop-blur-sm"
        >
          <p class="tw-text-2xl tw-font-bold">{{ state.datasetName }}</p>
          <div class="tw-absolute tw-right-0 tw-m-6 tw-gap-2 tw-flex">
            <Button
              rounded
              outlined
              icon="pi pi-pause"
              severity="warning"
              v-tooltip.bottom="'Pause'"
              @click="updateReviewProgress('pause')"
            />
            <Button
              rounded
              outlined
              icon="pi pi-stop"
              severity="danger"
              v-tooltip.bottom="state.post ? 'Post-Reviewer' : 'Finished'"
              @click="handleDialogVisibleForFinishScreening()"
            />
          </div>
        </div>
        <div class="tw-flex tw-flex-col tw-gap-4 tw-px-4">
          <div v-for="(doc, index) in state.docs" class="screening-card">
            <ScreeningCard
              class="tw-bg-slate-50 tw-w-full"
              :index="index"
              :doc="doc"
              :selected="state.studyIndex === index"
              :pre-response="state.pre ? state.preResponse[index] : undefined"
              :state="state"
              :ask-a-i-allowed="
                canAskAI(state.config.pipeline_type, state.interactionLevel)
              "
              @ask-a-i="coProcess('ask_ai')"
              @update:visible-chat="updateVisibleChat"
              @update:study-index="updateStudyIndex"
              @give-feedback="giveFeedback(state.studyIndex, $event)"
            />
          </div>
        </div>
        <div class="tw-flex tw-items-center tw-justify-center tw-p-2">
          <Paginator
            v-model:first="pageIndex"
            :rows="1"
            :totalRecords="1"
            template="PrevPageLink CurrentPageReport NextPageLink"
            :pt="{
              root: 'tw-bg-transparent tw-p-0',
              previousPageButton: 'tw-border-none',
              nextPageButton: 'tw-border-none',
            }"
          />
        </div>
      </ScrollPanel>
    </div>

    <Button
      v-if="!state.configLoading"
      :icon="
        state.visibleChat
          ? 'pi pi-angle-double-right'
          : 'pi pi-angle-double-left'
      "
      :pt="{
        root: 'tw-shadow-none tw-h-24 tw-p-0 tw-w-5 tw-absolute tw-top-1/2 tw-translate-y-[-50%] tw-z-[100] tw-transition-all',
      }"
      :class="
        state.visibleChat
          ? 'tw-left-[70%]'
          : 'tw-left-[100%] tw-translate-x-[-100%]'
      "
      @click="updateVisibleChat(!state.visibleChat)"
    />

    <AssistantPanel
      :state="state"
      @update:pre="state.pre = $event"
      @update:co="state.co = $event"
      @update:post="state.post = $event"
      @update:interaction-level="state.interactionLevel = $event"
      @p-i-c-o-extraction="coProcess('pico_extract')"
      @detailed-reasoning="coProcess('detail_reason')"
      @chat="chatClient($event, state.studyIndex)"
    />
  </div>

  <Modal
    v-model:is-active="readyToStartPostReview"
    header="Ready to start post-review ?"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="updateReviewProgress('post_review')"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <p>Please confirm that all studies have been screened.</p>
        <p>Once confirmed, you’ll move on to the post-review stage.</p>
      </div>
    </template>
  </Modal>

  <Modal
    v-model:is-active="completeScreeningBeforePostReview"
    header="Complete screening before post-review"
    leftBtn="Back"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <p>You haven’t screened all studies yet.</p>
        <p>Please assess every study before starting the post-review.</p>
      </div>
    </template>
  </Modal>

  <Modal
    v-model:is-active="confirmToFinishYourScreening"
    header="Confirm to finish your screening"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="updateReviewProgress('finish')"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <p>Please confirm that all studies have been assessed.</p>
        <p>
          Once confirmed, you will no longer be able to edit assessments or use
          the SR Assistant.
        </p>
      </div>
    </template>
  </Modal>

  <Modal
    v-model:is-active="unableToFinishScreening"
    header="Unable to finish screening"
    leftBtn="Back"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <p>You haven’t assessed all studies.</p>
        <p>Please complete the screening before finish.</p>
      </div>
    </template>
  </Modal>
</template>

<style scoped>
.p-button.p-button-warning,
.p-button.p-button-danger {
  background: white;
}
</style>

<script lang="ts" setup>
import Loading from "@/components/Loading.vue";
import ScrollPanel from "primevue/scrollpanel";
import ScreeningCard from "./components/ScreeningCard.vue";
import Paginator from "primevue/paginator";
import AssistantPanel from "@/components/AssistantPanel.vue";
import Modal from "@/components/Modal.vue";
import Button from "primevue/button";

import { ref, onMounted } from "vue";

import { useRoute } from "vue-router";
const route = useRoute();

import { State } from "@/types/reviewer";
import { DEFAULT_STATE } from "@/defaults/reviewer";
const state = ref<State>(DEFAULT_STATE);

import { canAskAI } from "@/utils/reviewer";

import { useReview } from "@/composables/review";
const {
  getStudies,
  coProcess,
  updateVisibleChat,
  updateStudyIndex,
  isAllFeedbackTrue,
  giveFeedback,
  chatClient,
} = useReview(state);

import { useLLMConfig } from "@/composables/llmConfig";
const { init } = useLLMConfig(state, route);

const pageIndex = ref(0);

onMounted(async () => {
  state.value.initLoading = true;
  await init();
  state.value.initLoading = false;
});

// --------------------------------

import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

import { useToast } from "@/composables/toast";
import router from "@/router";
const { showToast } = useToast();

const readyToStartPostReview = ref(false);
const completeScreeningBeforePostReview = ref(false);
const confirmToFinishYourScreening = ref(false);
const unableToFinishScreening = ref(false);

const handleDialogVisibleForFinishScreening = () => {
  if (state.value.post) {
    if (isAllFeedbackTrue()) {
      readyToStartPostReview.value = true;
    } else {
      completeScreeningBeforePostReview.value = true;
    }
  } else {
    if (isAllFeedbackTrue()) {
      confirmToFinishYourScreening.value = true;
    } else {
      unableToFinishScreening.value = true;
    }
  }
};

const updateReviewProgress = async (
  action: "pause" | "finish" | "post_review"
) => {
  try {
    setLoading(true);

    const body = {
      review_id: route.params.id,
      action,
    };

    await axios.post("/review/review_progress", body, getTokenHeader());

    if (action === "pause") {
      router.push({ name: "paused", params: { id: route.params.id } });
    } else if (action === "post_review") {
      router.push({ name: "post-review", params: { id: route.params.id } });
    } else {
      router.push({ name: "summary", params: { id: route.params.id } });
    }
  } catch (error: unknown) {
    setLoading(false);
    console.error(error);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Update Progress", e.message);
    } else if (error instanceof Error) {
      showToast("error", "Cannot Update Progress", error.message);
    } else {
      showToast("error", "Cannot Update Progress", "An unknown error occurred");
    }
  }
};

onMounted(async () => {
  try {
    setLoading(true);
    await getStudies();
  } catch (error: unknown) {
    console.error(error);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Fetch Stufies", e.message);
    } else if (error instanceof Error) {
      showToast("error", "Cannot Fetch Stufies", error.message);
    } else {
      showToast("error", "Cannot Fetch Stufies", "An unknown error occurred");
    }
  } finally {
    setLoading(false);
  }
});
</script>
