<template>
  <LoadingScreen v-if="isLoading" />
  <Container
    v-else
    icon="pi pi-inbox"
    title="My Dataset / Review List"
    class="tw-flex-col"
  >
    <!-- <template #subtitle>
      <p>
        The estimated indexing time is approximately 30 seconds for the demo RIS
        file. Please refresh the page to view the updated status and start
        screening.
      </p>
      <p>
        (Auto-refreshing in {{ countdown }} second<span v-if="countdown !== 1"
          >s</span
        >.)
      </p>
    </template> -->

    <div class="tw-flex tw-justify-end tw-mb-8">
      <CustomButton
        class="tw-w-[13.5%]"
        icon="pi pi-plus-circle"
        label="New Dataset"
        @click="router.push({ name: 'upload' })"
      />
    </div>

    <DataTable showGridlines stripedRows>
      <Column
        field="order"
        class="tw-w-[5%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Order</p>
        </template>
        <template #body="slotProps">
          {{ slotProps.index + 1 }}
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
          {{ formatDateTime(slotProps.data.submission_timestamp) }}
        </template>
      </Column>
      <Column
        field="start_indexing_timestamp"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Start Indexing<br />Timestamp</p>
        </template>
        <template #body="slotProps">
          {{ formatDateTime(slotProps.data.start_indexing_timestamp) }}
        </template>
      </Column>
      <Column
        field="indexing_time_spent"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Indexing<br />Time Spent</p>
        </template>
        <template #body="slotProps">
          <p v-if="slotProps.data.indexing_time_spent">
            {{ slotProps.data.indexing_time_spent }}
          </p>
          <p v-else>—</p>
        </template>
      </Column>
      <Column
        field="indexing_status"
        class="tw-w-[13%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Indexing<br />Status</p>
        </template>
        <!-- <template #body="slotProps">
          <p
            class="tw-rounded"
            :class="getIndexingStatusClass(slotProps.data.indexing_status)"
          >
            {{ toTitleCase(slotProps.data.indexing_status.replace('_', ' ')) }}
          </p>
        </template> -->
      </Column>
      <Column
        field="screening_status"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Screening<br />Status</p>
        </template>
        <!-- <template #body="slotProps">
          <p
            class="tw-rounded"
            :class="getScreeningStatusClass(slotProps.data.screening_status)"
          >
            {{ toTitleCase(slotProps.data.screening_status.replace('_', ' ')) }}
          </p>
        </template> -->
      </Column>
      <Column field="action" class="tw-w-[13.5%]">
        <template #header>
          <p class="tw-m-auto tw-text-center">Action</p>
        </template>
        <!-- <template #body="slotProps">
          <CustomButton
            @click="
              navigation(
                slotProps.data.id,
                slotProps.data.screening_status,
                slotProps.data.current_page_index,
              )
            "
            class="tw-w-full"
            size="small"
            :label="getActionButtonLabel(slotProps.data.screening_status)"
            :disabled="
              slotProps.data.indexing_status !== 'index_ready' &&
              slotProps.data.indexing_status !== 're-rank_ready'
            "
          />
        </template> -->
      </Column>
    </DataTable>
  </Container>

  <Dialog v-model:visible="visible" modal :draggable="false" class="tw-w-[55%]">
    <template #header>
      <div class="tw-flex tw-items-center tw-gap-2">
        <i class="pi pi-cog" style="font-size: 1.5rem" />
        <h2>Check settings before screening</h2>
      </div>
    </template>

    <div class="tw-flex tw-flex-col tw-gap-4">
      <Panel header="AI Assistance setting">
        <div class="tw-flex tw-flex-col tw-gap-4">
          <div class="tw-grid tw-grid-cols-8 tw-gap-4">
            <p class="tw-col-span-2">AI-Assist Role</p>
            <div class="border tw-p-2 tw-rounded tw-col-span-2">
              <h4>Pre-reviewer</h4>
              <p>Let AI screen for you first</p>
            </div>
            <div
              class="border tw-border-primary-500 tw-p-2 tw-rounded tw-col-span-2 tw-bg-primary-50 tw-text-primary-500"
            >
              <h4>Co-reviewer</h4>
              <p>Ask AI to help when you screen</p>
            </div>
            <div class="border tw-p-2 tw-rounded tw-col-span-2">
              <h4>Post-reviewer</h4>
              <p>Let AI check your screened studies</p>
            </div>
          </div>

          <div class="tw-grid tw-grid-cols-8 tw-gap-4">
            <p class="tw-col-span-2">Interaction Level</p>
            <div class="tw-flex tw-items-center tw-gap-4 tw-col-span-2">
              <p
                :class="
                  !high ? 'tw-text-primary-500 tw-font-medium' : undefined
                "
              >
                low
              </p>
              <InputSwitch v-model="high" />
              <p
                :class="high ? 'tw-text-primary-500 tw-font-medium' : undefined"
              >
                high
              </p>
            </div>
          </div>
        </div>
      </Panel>

      <Panel header="AI Model setting">
        <div class="tw-flex tw-flex-col tw-gap-4">
          <div class="tw-flex tw-items-center tw-gap-2">
            <RadioButton v-model="modelSetting" name="gpt-4o" value="gpt-4o" />
            <p>GPT-4o (our API) or use your own API key</p>
          </div>
          <div class="tw-flex tw-items-center tw-gap-2">
            <RadioButton v-model="modelSetting" name="llama" value="llama" />
            <p>LLaMA</p>
          </div>
        </div>
      </Panel>

      <Panel header="AI Prompts setting">
        <div class="tw-flex tw-gap-4 tw-grid tw-grid-cols-3">
          <div
            class="border tw-p-8 tw-gap-2 tw-rounded tw-flex tw-flex-col tw-items-center tw-text-center tw-justify-center"
          >
            <div class="tw-flex tw-items-center tw-gap-1">
              <i class="pi pi-microchip-ai" />
              <h4>System</h4>
            </div>
            <p>(generally how AI work like, e.g. role)</p>
          </div>

          <div
            class="border tw-p-8 tw-gap-2 tw-rounded tw-flex tw-flex-col tw-items-center tw-text-center tw-justify-center"
          >
            <div class="tw-flex tw-items-center tw-gap-1">
              <i class="pi pi-clipboard" />
              <h4>Task</h4>
            </div>
            <p>(Specify what task AI will do e.g. judge relevance)</p>
          </div>

          <div
            class="border tw-p-8 tw-gap-2 tw-rounded tw-flex tw-flex-col tw-items-center tw-text-center tw-justify-center"
          >
            <div class="tw-flex tw-items-center tw-gap-1">
              <i class="pi pi-pencil" />
              <h4>Output</h4>
            </div>
            <p>(Formatting the way AI responses)</p>
          </div>
        </div>
      </Panel>
    </div>

    <template #footer>
      <div class="tw-flex tw-justify-end">
        <CustomButton
          severity="secondary"
          label="Back"
          @click="visible = false"
        />
        <CustomButton label="Start screening" />
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import Container from "@/components/Container.vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import CustomButton from "@/components/CustomButton.vue";
import Dialog from "primevue/dialog";
import Panel from "primevue/panel";
import InputSwitch from "primevue/inputswitch";
import RadioButton from "primevue/radiobutton";

import { ref } from "vue";
import { formatDateTime } from "@/utils/datetime";

// import axios, { AxiosError } from "axios";
// import { getTokenHeader } from "@/utils/auth";

// import { useRoute } from "vue-router";
// const route = useRoute();

// import { useError } from "@/composables/error";
// const { getResponseErrorMessage } = useError();

// import { useToast } from "@/composables/toast";
// const { showToast } = useToast();

import { useLoading } from "@/composables/loading";
// import { IDataset, IIndexingStatus, IScreeningStatus } from '@/types/dataset'
import router from "@/router";
const { isLoading } = useLoading(false);

const visible = ref(true);
const high = ref(true);

const modelSetting = ref("gpt-4o");
</script>
