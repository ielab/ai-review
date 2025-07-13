<template>
  <Loading v-if="isLoading" />
  <BlockUI :blocked="isLoading" :pt="{ root: 'tw-z-0 tw-flex-1' }">
    <Container
      icon="pi pi-inbox"
      title="My Dataset / Review List"
      class="tw-flex-col"
    >
      <div class="tw-flex tw-justify-end">
        <Button
          class="tw-w-[13.5%]"
          icon="pi pi-plus-circle"
          label="New Dataset"
          @click="navigateToUpload"
        />
      </div>

      <div class="tw-flex tw-gap-4 tw-items-center tw-my-8">
        <i class="pi pi-search" />
        <InputText
          fluid
          class="tw-w-full"
          placeholder="Search by Name"
          v-model="searchQuery"
        />
      </div>

      <DataTable
        :value="filteredStudies"
        showGridlines
        stripedRows
        paginator
        :rows="10"
        :rowsPerPageOptions="[10, 20, 50]"
        @page="updatePageIndex"
      >
        <template #empty>
          <div class="tw-flex tw-justify-center tw-items-center">
            <p>No data available.</p>
          </div>
        </template>

        <Column
          field="order"
          class="tw-w-[5%]"
          :pt="{ bodyCell: 'tw-text-center' }"
        >
          <template #header>
            <p class="tw-m-auto tw-text-center">Order</p>
          </template>
          <template #body="slotProps">
            {{ pageIndex * 10 + slotProps.index + 1 }}
          </template>
        </Column>

        <Column
          field="name"
          class="tw-w-[27%]"
          :pt="{ bodyCell: 'tw-text-center' }"
        >
          <template #header>
            <p class="tw-m-auto tw-text-center">Name</p>
          </template>
          <template #body="slotProps">
            {{ slotProps.data.name }}
          </template>
        </Column>

        <Column
          field="submission_timestamp"
          class="tw-w-[10%]"
          :pt="{ bodyCell: 'tw-text-center' }"
        >
          <template #header>
            <p class="tw-m-auto tw-text-center">Submission<br />Timestamp</p>
          </template>
          <template #body="slotProps">
            <div class="tw-flex tw-flex-col tw-items-center tw-gap-2">
              <div class="tw-flex tw-items-center tw-gap-2">
                <i class="pi pi-calendar" />
                <p>{{ formatDate(slotProps.data.created_at) || "—" }}</p>
              </div>
              <div class="tw-flex tw-items-center tw-gap-2">
                <i class="pi pi-clock" />
                <p>{{ formatTime(slotProps.data.created_at) || "—" }}</p>
              </div>
            </div>
          </template>
        </Column>

        <Column
          field="pipeline_type"
          class="tw-w-[10%]"
          :pt="{ bodyCell: 'tw-text-center' }"
        >
          <template #header>
            <p class="tw-m-auto tw-text-center">AI Assistance Type</p>
          </template>
          <template #body="slotProps">
            <p>{{ slotProps.data.pipeline_type || "Not selected" }}</p>
          </template>
        </Column>

        <Column
          field="screening_status"
          class="tw-w-[10%]"
          :pt="{ bodyCell: 'tw-text-center' }"
        >
          <template #header>
            <p class="tw-m-auto tw-text-center">Screening<br />Status</p>
          </template>
          <template #body="slotProps">
            <p
              class="tw-rounded-md tw-p-1"
              :class="getScreeningStatusClass(slotProps.data.screening_status)"
            >
              {{
                toTitleCase(slotProps.data.screening_status.replace("_", " "))
              }}
            </p>
          </template>
        </Column>

        <Column field="action" class="tw-w-[13.5%]">
          <template #header>
            <p class="tw-m-auto tw-text-center">Action</p>
          </template>
          <template #body="slotProps">
            <Button
              class="tw-w-full"
              :class="{
                'tw-bg-primary-100 tw-border-primary-100 tw-text-primary-500 hover:tw-bg-primary-200':
                  getActionButtonLabel(slotProps.data) === 'Resume',
                'tw-bg-red-500 tw-border-red-500 tw-text-white hover:tw-bg-red-600':
                  getActionButtonLabel(slotProps.data) === 'Config',
              }"
              :severity="getActionButtonSeverity(slotProps.data)"
              :label="getActionButtonLabel(slotProps.data)"
              :outlined="
                ['not_start'].includes(slotProps.data.screening_status)
              "
              @click="handleAction(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </Container>
  </BlockUI>

  <Setting
    :id="settingConfigStudyID"
    :isActive="settingConfigVisible"
    @update:isActive="settingConfigVisible = $event"
  />
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import axios, { AxiosError } from "axios";
import Container from "@/components/Container.vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import Setting from "./components/Setting.vue";
import Loading from "@/components/Loading.vue";
import BlockUI from "primevue/blockui";
import InputText from "primevue/inputtext";
import { formatDateTime } from "@/utils/datetime";
import { getTokenHeader } from "@/utils/auth";
import { toTitleCase } from "@/utils/string";
import { useLoading } from "@/composables/loading";
import { useError } from "@/composables/error";
import { useToast } from "@/composables/toast";
import type { IStudy, IScreeningStatus } from "@/types/reviewer";
import { DEFAULT_STUDY } from "@/defaults/reviewer";

// State
const searchQuery = ref<string>("");
const studies = ref<IStudy[]>([DEFAULT_STUDY]);
const settingConfigStudyID = ref<number | undefined>();
const settingConfigVisible = ref<boolean>(false);
const pageIndex = ref<number>(0);
const { setLoading, isLoading } = useLoading(false);
const { getResponseErrorMessage } = useError();
const { showToast } = useToast();
const router = useRouter();

// Computed
const filteredStudies = computed(() =>
  searchQuery.value
    ? studies.value.filter((study) =>
        study.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    : studies.value
);

// Methods
const fetchStudies = async () => {
  setLoading(true);
  try {
    const response = await axios.post("review/studies", {}, getTokenHeader());
    studies.value = response.data.data.sort(
      (a: IStudy, b: IStudy) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch (error) {
    handleError(error, "Cannot Fetch Dataset/Review List");
  } finally {
    setLoading(false);
  }
};

const updateReviewProgress = async (
  reviewId: string | string[],
  action: "start" | "pause" | "resume" | "finish" | "post_review"
) => {
  setLoading(true);
  try {
    await axios.post(
      "/review/review_progress",
      { review_id: reviewId, action },
      getTokenHeader()
    );
  } catch (error) {
    handleError(error, "Cannot Update Progress");
  } finally {
    setLoading(false);
  }
};

const handleError = (error: unknown, title: string) => {
  if (error instanceof AxiosError) {
    const errorResponse = getResponseErrorMessage(error);
    showToast("error", title, errorResponse.message);
  } else if (error instanceof Error) {
    showToast("error", title, error.message);
  } else {
    showToast("error", title, "An unknown error occurred");
  }
  console.error(error);
};

const navigateToUpload = () => router.push({ name: "upload" });

const updatePageIndex = (event: any) => {
  pageIndex.value = event.originalEvent.page;
};

const formatDate = (date: string) => formatDateTime(date).split(",")[0];
const formatTime = (date: string) => formatDateTime(date).split(",")[1];

const getScreeningStatusClass = (status: IScreeningStatus): string =>
  ({
    not_start: "tw-bg-gray-200 tw-text-gray-500",
    screening: "tw-bg-primary-100 tw-text-primary-500",
    paused: "tw-bg-orange-100 tw-text-orange-500",
    finished: "tw-bg-green-100 tw-text-green-500",
    "post-review": "tw-text-white tw-bg-primary-500",
  }[status] || "");

const getActionButtonSeverity = (study: IStudy): string => {
  if (study.screening_status === "not_start") return "secondary";
  if (study.screening_status === "paused") return "warning";
  if (study.screening_status === "finished") return "success";
  if (!study.pipeline_type) return "danger";
  return "";
};

const getActionButtonLabel = (study: IStudy) => {
  if (study.screening_status === "not_start" && study.pipeline_type)
    return "Start";
  if (study.screening_status === "screening") return "Resume";
  if (
    study.screening_status === "paused" ||
    study.screening_status === "finished"
  )
    return "Summary";
  if (study.screening_status === "post-review") return "Post Reviewer";
  if (!study.pipeline_type) return "Config";
};

const handleAction = async (study: IStudy) => {
  const { id, pipeline_type, screening_status } = study;

  if (!id) {
    console.error("Study ID is null, cannot proceed");
    showToast("error", "Invalid Study", "Study ID is missing");
    return;
  }

  if (!pipeline_type) {
    settingConfigStudyID.value = id;
    settingConfigVisible.value = true;
    return;
  }

  const routeMap: Record<string, string> = {
    not_start: "review",
    screening: "review",
    paused: "paused",
    finished: "summary",
    "post-review": "post-review",
  };

  const routeName = routeMap[screening_status];

  if (screening_status === "not_start") {
    await updateReviewProgress(id.toString(), "start");
  }

  if (routeName) {
    router.push({ name: routeName, params: { id } });
  } else {
    console.warn("Unknown screening status:", screening_status);
    showToast("error", "Unknown Status", "Cannot determine navigation target.");
  }
};

// Lifecycle
onMounted(fetchStudies);
</script>

<style scoped>
.p-button-outlined {
  @apply hover:tw-opacity-75 tw-transition-all tw-bg-primary-100;
}
.p-button-secondary {
  @apply tw-bg-white;
}
.p-button-danger {
  @apply tw-bg-red-500 tw-text-white tw-border-red-500 hover:tw-bg-red-600;
}
</style>
