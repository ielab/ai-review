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
          <p class="tw-text-2xl tw-font-bold">{{ postReview?.dataset_name }}</p>
          <div class="tw-absolute tw-right-0 tw-m-6 tw-gap-2 tw-flex">
            <Button
              rounded
              outlined
              icon="pi pi-stop"
              severity="danger"
              v-tooltip.bottom="'Finish'"
              @click="updateReviewProgress()"
            />
          </div>
        </div>
        <div class="tw-flex tw-flex-col tw-gap-4 tw-px-4">
          <div class="tw-flex tw-flex-col tw-mt-4 tw-gap-4">
            <div class="tw-flex tw-justify-between tw-items-center">
              <p class="tw-text-2xl tw-font-medium">A list of studies</p>
              <Button
                v-tooltip.top="{
                  value: 'Apply to selected studies only',
                  pt: {
                    root: 'tw-max-w-none',
                    text: 'tw-text-sm',
                  },
                }"
                label="Apply Post-Reviewer"
                @click="applyPostReviewer()"
              />
            </div>
            <DataTable
              v-model:selection="selectedStudies"
              :value="postReview?.data"
              :rowClass="getRowClass"
              show-gridlines
              class="custom-datatable"
            >
              <Column
                selectionMode="multiple"
                headerStyle="width: 3rem"
              ></Column>
              <Column
                :pt="{
                  root: 'tw-max-w-[10rem] tw-whitespace-normal',
                  header: 'tw-max-w-[10rem] tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">Order</p>
                </template>
                <template #body="slotProps">
                  <p class="tw-m-auto tw-text-center">
                    {{ slotProps.data.order }}
                  </p>
                </template>
              </Column>

              <Column
                :pt="{
                  root: 'tw-max-w-[10rem] tw-whitespace-normal',
                  header: 'tw-max-w-[10rem] tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">PMID</p>
                </template>
                <template #body="slotProps">
                  <p class="tw-m-auto tw-text-center">
                    {{ slotProps.data.pmid }}
                  </p>
                </template>
              </Column>

              <Column
                :pt="{
                  root: 'tw-max-w-[10rem] tw-whitespace-normal',
                  header: 'tw-max-w-[10rem] tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">Title</p>
                </template>
                <template #body="slotProps">
                  <p class="tw-m-auto tw-text-center">
                    {{ slotProps.data.title }}
                  </p>
                </template>
              </Column>

              <Column
                :pt="{
                  root: 'tw-max-w-md tw-whitespace-normal',
                  header: 'tw-max-w-md tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">Abstract</p>
                </template>
                <template #body="slotProps">
                  <div
                    class="tw-flex tw-flex-col tw-justify-center tw-items-center tw-gap-2 tw-my-2"
                  >
                    <p
                      class="tw-leading-relaxed"
                      :class="{
                        'tw-line-clamp-5':
                          !expandedAbstracts[slotProps.data.pmid],
                      }"
                    >
                      {{ slotProps.data.abstract }}
                    </p>

                    <Button
                      :label="
                        expandedAbstracts[slotProps.data.pmid]
                          ? 'Show Less'
                          : 'Show More'
                      "
                      text
                      :pt="{
                        root: 'tw-w-fit tw-text-sm tw-font-normal tw-py-1 tw-px-2 tw-shadow-none',
                      }"
                      @click="toggleAbstract(slotProps.data.pmid)"
                    />
                  </div>
                </template>
              </Column>

              <Column
                :pt="{
                  root: 'tw-max-w-[10rem] tw-whitespace-normal',
                  header: 'tw-max-w-[10rem] tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">Assessment</p>
                </template>
                <template #body="slotProps">
                  <p
                    class="tw-m-auto tw-text-center tw-font-bold tw-bg-white tw-outline tw-outline-[0.1vw] tw-rounded tw-p-2"
                    :class="{
                      'tw-text-red-500':
                        slotProps.data.assessment === 'exclude',
                      'tw-text-green-500':
                        slotProps.data.assessment === 'include',
                    }"
                  >
                    {{ toTitleCase(slotProps.data.assessment) }}
                  </p>
                </template>
              </Column>

              <Column
                :pt="{
                  root: 'tw-max-w-md tw-whitespace-normal',
                  header: 'tw-max-w-md tw-whitespace-normal',
                }"
              >
                <template #header>
                  <p class="tw-m-auto tw-text-center">Post-Reviewer</p>
                </template>
                <template #body="slotProps">
                  <div
                    v-if="
                      slotProps.data.post_reviewer_response &&
                      postReviewResult.includes(slotProps.data.pmid)
                    "
                    class="tw-flex tw-flex-col tw-justify-center tw-items-center tw-gap-2 tw-my-2"
                  >
                    <p
                      v-if="
                        expandedAbstracts[
                          `${slotProps.data.pmid}_post_reviewer`
                        ]
                      "
                      class="tw-leading-relaxed"
                      :class="{
                        'tw-line-clamp-5':
                          !expandedAbstracts[
                            `${slotProps.data.pmid}_post_reviewer`
                          ],
                      }"
                      v-html="
                        slotProps.data.post_reviewer_response.replace(
                          /\n/g,
                          '<br>'
                        )
                      "
                    />
                    <div
                      v-else
                      class="tw-flex tw-items-center tw-gap-2"
                      :class="{
                        'tw-text-green-500':
                          slotProps.data.post_reviewer_response.slice(
                            14,
                            19
                          ) === 'Agree',
                        'tw-text-red-500':
                          slotProps.data.post_reviewer_response.slice(
                            14,
                            19
                          ) !== 'Agree',
                      }"
                    >
                      <i
                        class="pi"
                        :class="{
                          'pi-thumbs-up':
                            slotProps.data.post_reviewer_response.slice(
                              14,
                              19
                            ) === 'Agree',
                          'pi-thumbs-down':
                            slotProps.data.post_reviewer_response.slice(
                              14,
                              19
                            ) !== 'Agree',
                        }"
                      />
                      <p class="tw-m-auto tw-text-center tw-font-bold">
                        {{
                          slotProps.data.post_reviewer_response.slice(
                            14,
                            19
                          ) === "Agree"
                            ? "Agree"
                            : "Disagree"
                        }}
                      </p>
                    </div>

                    <Button
                      :label="
                        expandedAbstracts[
                          `${slotProps.data.pmid}_post_reviewer`
                        ]
                          ? 'Show Less'
                          : 'Show More'
                      "
                      text
                      :pt="{
                        root: 'tw-w-fit tw-text-sm tw-font-normal tw-py-1 tw-px-2 tw-shadow-none',
                      }"
                      @click="
                        toggleAbstract(`${slotProps.data.pmid}_post_reviewer`)
                      "
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </div>
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
</template>

<style scoped>
.p-button-outlined {
  background: white;
}

.custom-datatable ::v-deep(.p-datatable-tbody > tr > td),
.custom-datatable ::v-deep(.p-datatable-thead > tr > th) {
  @apply tw-border-slate-300;
}
</style>

<script lang="ts" setup>
import Loading from "@/components/Loading.vue";
import ScrollPanel from "primevue/scrollpanel";
import AssistantPanel from "@/components/AssistantPanel.vue";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
const route = useRoute();

import { State } from "@/types/reviewer";
import { DEFAULT_STATE } from "@/defaults/reviewer";
const state = ref<State>(DEFAULT_STATE);

const selectedStudies = ref();

import { toTitleCase } from "@/utils/string";

import { useReview } from "@/composables/review";
const { coProcess, updateVisibleChat, chatClient } = useReview(state);

import { useLLMConfig } from "@/composables/llmConfig";
const { init } = useLLMConfig(state, route);

const getRowClass = (data: any) => {
  if (
    data.post_reviewer_response.slice(14, 19) === "Agree" &&
    postReviewResult.value.includes(data.pmid)
  ) {
    return "tw-bg-green-50";
  } else if (
    data.post_reviewer_response.slice(14, 19) !== "Agree" &&
    postReviewResult.value.includes(data.pmid)
  ) {
    return "tw-bg-red-50";
  }
};
const expandedAbstracts = ref<{ [key: string]: boolean }>({});
function toggleAbstract(key: string): void {
  expandedAbstracts.value[key] = !expandedAbstracts.value[key];
}

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
import { IDoc } from "@/types/corpus";
const { showToast } = useToast();

const updateReviewProgress = async () => {
  try {
    setLoading(true);

    const body = {
      review_id: route.params.id,
      action: "finish",
    };

    await axios.post("/review/review_progress", body, getTokenHeader());

    router.push({ name: "summary", params: { id: route.params.id } });
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

const postReview = ref<{
  data: {
    order: number;
    pmid: number;
    title: string;
    abstract: string;
    assessment: string;
    post_reviewer_response: string;
  }[];
  dataset_name: string;
}>();

onMounted(async () => {
  try {
    setLoading(true);
    const body = {
      review_id: route.params.id,
      export: true,
      filter_type: "all",
    };
    const result = await axios.post(
      "review/post_review_table",
      body,
      getTokenHeader()
    );
    postReview.value = result.data;
  } catch (error: unknown) {
    console.error(error);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Fetch Studies", e.message);
    } else if (error instanceof Error) {
      showToast("error", "Cannot Fetch Studies", error.message);
    } else {
      showToast("error", "Cannot Fetch Studies", "An unknown error occurred");
    }
  } finally {
    setLoading(false);
  }
});

const postReviewResult = ref<number[]>([]);

const applyPostReviewer = async () => {
  if (!selectedStudies.value || selectedStudies.value.length === 0) {
    showToast(
      "warn",
      "No Studies Selected",
      "Please select at least one study to apply post-reviewer."
    );
    return;
  }

  // Extract PMIDs from selected studies
  const pmids = selectedStudies.value.map((study: IDoc) => study.pmid);

  // Add PMIDs to postReviewResult (if needed locally)
  postReviewResult.value = [...pmids];

  try {
    showToast(
      "success",
      "Post-Reviewer Applied",
      "Post-reviewer responses have been updated for selected studies."
    );
  } catch (error: unknown) {
    console.error(error);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Apply Post-Reviewer", e.message);
    } else if (error instanceof Error) {
      showToast("error", "Cannot Apply Post-Reviewer", error.message);
    } else {
      showToast(
        "error",
        "Cannot Apply Post-Reviewer",
        "An unknown error occurred"
      );
    }
  } finally {
    setLoading(false);
  }
};
</script>
