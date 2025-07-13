<template>
  <Loading v-if="isLoading" />

  <BlockUI :blocked="isLoading" :pt="{ root: 'tw-z-0 tw-flex-1' }">
    <Container>
      <div class="tw-flex tw-flex-col tw-gap-4">
        <p
          class="tw-p-4 tw-text-2xl tw-font-bold tw-text-center tw-text-primary-800"
        >
          {{ datasetName }}
        </p>

        <div
          class="border tw-bg-primary-100/50 tw-rounded-md tw-p-6 tw-flex tw-flex-col tw-gap-6"
        >
          <div class="tw-text-2xl tw-font-medium tw-text-center">
            <p>You have paused screening!</p>
            <!-- <p>at page x/X</p> -->
          </div>

          <Panel header="Overall" :pt="{ header: 'tw-flex tw-justify-center' }">
            <div class="tw-grid tw-grid-cols-3 tw-gap-4 tw-items-center">
              <Panel
                :pt="{
                  header: 'tw-font-medium tw-p-3 tw-flex tw-justify-center',
                }"
              >
                <template #header>
                  Total&nbsp;<b>{{ reviewStats?.total_studies || 0 }}</b
                  >&nbsp;studies
                </template>
                <div class="tw-flex tw-flex-col tw-gap-4">
                  <Panel
                    :pt="{
                      header:
                        'tw-font-medium tw-p-2 tw-flex tw-justify-center tw-gap-2 tw-items-center tw-bg-green-50 tw-text-green-500',
                      content:
                        'tw-flex tw-flex-col tw-items-center tw-p-2 tw-gap-2',
                    }"
                  >
                    <template #header>
                      <p>
                        Included:
                        <b>
                          {{
                            (reviewStats?.human_include || 0) +
                            (reviewStats?.llm_include || 0)
                          }}
                        </b>
                      </p>
                    </template>
                    <div class="tw-flex tw-gap-2">
                      <div
                        class="tw-flex tw-items-center tw-gap-2 tw-w-[5.5rem]"
                      >
                        <div class="tw-w-[1.2rem] tw-text-center">
                          <i class="fa-solid fa-robot"></i>
                        </div>
                        <p>AI:</p>
                      </div>
                      <p
                        class="tw-font-bold tw-bg-green-500 tw-w-[2rem] tw-text-center tw-rounded tw-text-green-100"
                      >
                        {{ reviewStats?.llm_include || 0 }}
                      </p>
                    </div>
                    <div class="tw-flex tw-gap-2">
                      <div
                        class="tw-flex tw-items-center tw-gap-2 tw-w-[5.5rem]"
                      >
                        <div class="tw-w-[1.2rem] tw-text-center">
                          <i class="pi pi-user"></i>
                        </div>
                        <p>Human:</p>
                      </div>
                      <p
                        class="tw-font-bold tw-bg-green-100 tw-w-[2rem] tw-text-center tw-rounded tw-text-green-500"
                      >
                        {{ reviewStats?.human_include || 0 }}
                      </p>
                    </div>
                  </Panel>
                  <Panel
                    :pt="{
                      header:
                        'tw-font-medium tw-p-2 tw-flex tw-justify-center tw-gap-2 tw-items-center tw-bg-red-50 tw-text-red-500',
                      content:
                        'tw-flex tw-flex-col tw-items-center tw-p-2 tw-gap-2',
                    }"
                  >
                    <template #header>
                      <p>
                        Excluded:
                        <b>
                          {{
                            (reviewStats?.human_exclude || 0) +
                            (reviewStats?.llm_exclude || 0)
                          }}
                        </b>
                      </p>
                    </template>
                    <div class="tw-flex tw-gap-2">
                      <div
                        class="tw-flex tw-items-center tw-gap-2 tw-w-[5.5rem]"
                      >
                        <div class="tw-w-[1.2rem] tw-text-center">
                          <i class="fa-solid fa-robot"></i>
                        </div>
                        <p>AI:</p>
                      </div>
                      <p
                        class="tw-font-bold tw-bg-red-500 tw-w-[2rem] tw-text-center tw-rounded tw-text-red-100"
                      >
                        {{ reviewStats?.llm_exclude || 0 }}
                      </p>
                    </div>
                    <div class="tw-flex tw-gap-2">
                      <div
                        class="tw-flex tw-items-center tw-gap-2 tw-w-[5.5rem]"
                      >
                        <div class="tw-w-[1.2rem] tw-text-center">
                          <i class="pi pi-user"></i>
                        </div>
                        <p>Human:</p>
                      </div>
                      <p
                        class="tw-font-bold tw-bg-red-100 tw-w-[2rem] tw-text-center tw-rounded tw-text-red-500"
                      >
                        {{ reviewStats?.human_exclude || 0 }}
                      </p>
                    </div>
                  </Panel>
                </div>
              </Panel>
              <div>
                <Chart type="pie" :data="chartData" :options="chartOptions" />
              </div>
              <div class="tw-flex tw-flex-col tw-items-center">
                <div class="tw-flex tw-flex-col tw-gap-2">
                  <Button
                    label="Resume"
                    class="tw-w-full"
                    @click="updateReviewProgress()"
                  />
                  <small>continue screen with current AI assistant</small>
                </div>
              </div>
            </div>
          </Panel>
        </div>

        <div class="tw-flex tw-flex-col tw-mt-4">
          <p class="tw-text-2xl tw-font-medium">A list of studies</p>
          <div
            class="tw-flex tw-flex-col tw-gap-2 tw-sticky tw-top-0 tw-z-[100] tw-py-4 tw-mb-2 tw-backdrop-blur-sm"
          >
            <div class="tw-justify-between tw-flex">
              <div class="tw-items-center tw-flex tw-gap-1">
                <Button
                  outlined
                  icon="pi pi-file-export"
                  label="Export selected"
                  :pt="{
                    root: 'tw-bg-white hover:tw-opacity-75 tw-transition-all',
                  }"
                  @click="exportSelected()"
                />
                <span>as .nbib</span>
              </div>
              <div class="tw-items-center tw-flex tw-gap-2">
                <Button
                  :outlined="filters.all ? false : true"
                  :class="{ 'tw-bg-white': !filters.all }"
                  :label="`All (${filterCounts?.all})`"
                  :pt="{
                    root: 'hover:tw-opacity-75 tw-transition-all tw-shadow-none',
                  }"
                  @click="toggleFilter('all')"
                />
                <Button
                  :outlined="filters.include ? false : true"
                  :class="{ 'tw-bg-white': !filters.include }"
                  :label="`Include (${filterCounts?.include})`"
                  severity="success"
                  :pt="{
                    root: 'hover:tw-opacity-75 tw-transition-all tw-shadow-none',
                  }"
                  @click="toggleFilter('include')"
                />
                <Button
                  :outlined="filters.exclude ? false : true"
                  :class="{ 'tw-bg-white': !filters.exclude }"
                  :label="`Exclude (${filterCounts?.exclude})`"
                  severity="danger"
                  :pt="{
                    root: 'hover:tw-opacity-75 tw-transition-all tw-shadow-none',
                  }"
                  @click="toggleFilter('exclude')"
                />
              </div>
            </div>
          </div>

          <DataTable
            :value="filteredStudies"
            :rowClass="getRowClass"
            show-gridlines
            class="custom-datatable"
          >
            <Column field="order">
              <template #header>
                <p class="tw-m-auto tw-text-center">Order</p>
              </template>
              <template #body="slotProps">
                <p class="tw-m-auto tw-text-center">
                  {{ slotProps.data.order }}
                </p>
              </template>
            </Column>
            <Column field="pmid">
              <template #header>
                <p class="tw-m-auto tw-text-center">PMID</p>
              </template>
              <template #body="slotProps">
                <p class="tw-m-auto tw-text-center">
                  {{ slotProps.data.pmid }}
                </p>
              </template>
            </Column>
            <Column field="title">
              <template #header>
                <p class="tw-m-auto tw-text-center">Title</p>
              </template>
            </Column>
            <Column field="abstract">
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
                      root: 'tw-w-fit tw-text-sm tw-font-normal tw-py-1 tw-px-2',
                    }"
                    @click="toggleAbstract(slotProps.data.pmid)"
                  />
                </div>
              </template>
            </Column>
            <Column field="assessment">
              <template #header>
                <p class="tw-m-auto tw-text-center">Assessment</p>
              </template>
              <template #body="slotProps">
                <p
                  class="tw-m-auto tw-text-center tw-font-bold tw-bg-white tw-outline tw-outline-[0.1vw] tw-rounded tw-p-2"
                  :class="{
                    'tw-text-red-500': slotProps.data.assessment === 'exclude',
                    'tw-text-green-500':
                      slotProps.data.assessment === 'include',
                  }"
                >
                  {{ toTitleCase(slotProps.data.assessment) }}
                </p>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </Container>
  </BlockUI>
</template>

<script lang="ts" setup>
import Loading from "@/components/Loading.vue";
import BlockUI from "primevue/blockui";
import Container from "@/components/Container.vue";
import Panel from "primevue/panel";
import Chart from "primevue/chart";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";

import { ref, onMounted } from "vue";
import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";
import { useRoute, useRouter } from "vue-router";
import { useError } from "@/composables/error";
import { useToast } from "@/composables/toast";
import { useLoading } from "@/composables/loading";

const route = useRoute();
const router = useRouter();
const { getResponseErrorMessage } = useError();
const { showToast } = useToast();
const { setLoading, isLoading } = useLoading(false);
import { toTitleCase } from "@/utils/string";

const filters = ref({
  all: true,
  include: false,
  exclude: false,
});

const expandedAbstracts = ref<{ [key: number]: boolean }>({});

function toggleFilter(filter: string): void {
  if (filter === "all")
    filters.value = { all: true, include: false, exclude: false };
  else if (filter === "include")
    filters.value = { all: false, include: true, exclude: false };
  else filters.value = { all: false, include: false, exclude: true };
  applyFilters();
}

function toggleAbstract(pmid: number): void {
  expandedAbstracts.value[pmid] = !expandedAbstracts.value[pmid];
}

const filteredStudies = ref<typeof studies.value>([]);

function applyFilters(): void {
  if (filters.value.all) {
    filteredStudies.value = studies.value || [];
    return;
  }

  filteredStudies.value = (studies.value || []).filter((study) => {
    if (filters.value.include && study.assessment === "include") return true;
    if (filters.value.exclude && study.assessment === "exclude") return true;
    return false;
  });
}

const chartData = ref();
const chartOptions = ref();

const setChartData = () => {
  const documentStyle = getComputedStyle(document.body);
  return {
    labels: [
      "Included (AI Decision)",
      "Excluded (AI Decision)",
      "Included (Human Decision)",
      "Excluded (Human Decision)",
    ],
    datasets: [
      {
        data: [
          reviewStats.value?.llm_include || 0,
          reviewStats.value?.llm_exclude || 0,
          reviewStats.value?.human_include || 0,
          reviewStats.value?.human_exclude || 0,
        ],
        backgroundColor: [
          documentStyle.getPropertyValue("--green-500"),
          documentStyle.getPropertyValue("--red-500"),
          documentStyle.getPropertyValue("--green-100"),
          documentStyle.getPropertyValue("--red-100"),
        ],
        hoverBackgroundColor: [
          documentStyle.getPropertyValue("--green-500"),
          documentStyle.getPropertyValue("--red-500"),
          documentStyle.getPropertyValue("--green-100"),
          documentStyle.getPropertyValue("--red-100"),
        ],
      },
    ],
  };
};

const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue("--text-color");
  return {
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          color: textColor,
        },
      },
    },
  };
};

const datasetName = ref<String>("");
const reviewStats = ref<{
  total_studies: number;
  human_reviewed: number;
  human_include: number;
  human_exclude: number;
  llm_reviewed: number;
  llm_include: number;
  llm_exclude: number;
}>();
const exportUrl = ref<String>();
const filterCounts = ref<{
  all: number;
  exclude: number;
  include: number;
  unjudge: number;
}>();
const studies = ref<
  {
    order: Number;
    pmid: Number;
    abstract: String;
    assessment: String;
    title: String;
  }[]
>();

const init = async () => {
  try {
    setLoading(true);
    const body = {
      review_id: route.params.id,
      export: true,
      filter_type: "all",
    };
    const result = await axios.post(
      "review/results_checking_pause",
      body,
      getTokenHeader()
    );
    datasetName.value = result.data.data.dataset_name;
    reviewStats.value = result.data.data.review_stats;
    exportUrl.value = result.data.data.export_url;
    filterCounts.value = result.data.data.filter_counts;
    studies.value = result.data.data.studies;
    if (studies.value) {
      studies.value.forEach((study) => {
        expandedAbstracts.value[study.pmid as number] = false;
      });
      applyFilters();
    }
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Pause Review", e.message);
    } else if (error instanceof Error) {
      showToast("error", "Cannot Pause Review", error.message);
    } else {
      showToast("error", "Cannot Pause Review", "An error occurred");
    }
  } finally {
    setLoading(false);
  }
};

const getRowClass = (data: any) => {
  return data.assessment === "exclude" ? "tw-bg-red-50" : "tw-bg-green-50";
};

const updateReviewProgress = async () => {
  try {
    setLoading(true);

    const body = {
      review_id: route.params.id,
      action: "resume",
    };

    await axios.post("/review/review_progress", body, getTokenHeader());

    router.push({ name: "review", params: { id: route.params.id } });
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

const exportSelected = () => {
  // Ensure exportUrl.value is defined and convert to primitive string
  if (!exportUrl.value) {
    console.error("Export URL is undefined");
    return;
  }

  const encodedUrl = encodeURI(String(exportUrl.value)); // Convert to primitive string

  const link = document.createElement("a");
  link.href = encodedUrl;
  link.download = ""; // let the browser use the filename from the URL or server
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

onMounted(async () => {
  await init();
  chartData.value = setChartData();
  chartOptions.value = setChartOptions();
});
</script>

<style scoped>
.custom-datatable ::v-deep(.p-datatable-tbody > tr > td),
.custom-datatable ::v-deep(.p-datatable-thead > tr > th) {
  @apply tw-border-slate-300;
}
</style>
