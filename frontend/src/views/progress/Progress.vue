<template>
  <Container>
    <div class="tw-flex tw-flex-col tw-gap-6">
      <p class="tw-text-2xl tw-font-bold tw-text-center">review.dataset_name</p>
      <div
        class="tw-flex tw-justify-between tw-items-center tw-gap-4 tw-relative"
      >
        <ScreeningProgressPanel :items="items" :active-step="2" />
        <div
          class="tw-absolute tw-right-0 tw-gap-4 tw-flex tw-bg-white tw-p-3 tw-top-1"
        >
          <CustomIconButton
            v-tooltip.top="'Resume'"
            icon="fa-solid fa-eject tw-rotate-90"
            rounded
          />
          <CustomIconButton
            v-tooltip.top="'Stop'"
            icon="fa-solid fa-stop"
            severity="danger"
            rounded
          />
        </div>
      </div>

      <QueryPanel />

      <div
        class="tw-flex tw-flex-col tw-gap-6 tw-bg-primary-50 tw-p-8 tw-rounded border"
      >
        <p class="tw-text-2xl tw-font-medium tw-text-center">
          You have paused your screening at page Number(route.query.index) + 1
        </p>

        <Panel :pt="{ header: 'tw-py-3' }">
          <template #header>
            <div class="tw-mx-auto">
              <h3>Overall</h3>
            </div>
          </template>

          <div class="tw-flex tw-items-center">
            <div class="tw-flex tw-flex-col tw-gap-2 tw-w-1/3 tw-items-center">
              <p>Total 100 studies</p>

              <div class="tw-flex tw-bg-green-200/40 tw-text-green-500 tw-rounded tw-px-1 tw-py-1">
                <p class="tw-w-[10rem]">Included:</p>
                <p>X</p>
              </div>

              <div class="tw-flex tw-ml-[2rem] tw-bg-purple-200/40 tw-text-purple-500 tw-rounded tw-px-1 tw-py-1">
                <div class="tw-w-[8rem] tw-flex tw-items-center tw-gap-2">
                  <div class="tw-w-[1.5rem] tw-flex tw-justify-center"><i class="fa-solid fa-robot" /></div>
                  <p>AI:</p>
                </div>
                <p>X</p>
              </div>

              <div class="tw-flex tw-ml-[2rem] tw-bg-primary-200/40 tw-text-primary-500 tw-rounded tw-px-1 tw-py-1">
                <div class="tw-w-[8rem] tw-flex tw-items-center tw-gap-2">
                  <div class="tw-w-[1.5rem] tw-flex tw-justify-center"><i class="fa-solid fa-user" /></div>
                  <p>HUMAN:</p>
                </div>
                <p>X</p>
              </div>
            </div>

            <div class="tw-w-1/3 tw-flex tw-flex-col tw-items-center">
              <Chart type="pie" class="w-full md:w-30rem" />
            </div>

            <div class="tw-w-1/3 tw-flex tw-flex-col tw-items-center tw-gap-2">
              <p>Revisit your past screening</p>
              <!-- <p class="tw-text-xs tw-text-gray-400">
                Note that you cannot modify your review decision.
              </p> -->
              <CustomButton label="Resume your screening" outlined />
            </div>
          </div>
        </Panel>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <p class="tw-text-2xl tw-font-bold">A list of studies</p>
          <div class="tw-justify-between tw-flex">
            <div class="tw-items-center tw-flex tw-gap-1">
              <CustomButton
                icon="pi pi-file-export"
                label="Export selected"
                outlined
              />
              <span>.nbib</span>
            </div>
            <div class="tw-items-center tw-flex tw-gap-2">
              <CustomButton label="All" />
              <CustomButton label="Include" severity="success" />
              <CustomButton label="Maybe" severity="secondary" />
              <CustomButton label="Exclude" severity="danger" />
            </div>
          </div>
        </div>

        <DataTable showGridlines stripedRows>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Order</p>
            </template>
            <template>
              <p class="tw-text-center">slotProps.index + 1</p>
            </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">PMID</p>
            </template>
            <template>
              <p class="tw-text-center">slotProps.data.pmid</p>
            </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Title</p>
            </template>
            <template> slotProps.data.corpus.title </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Assessment</p>
            </template>
            <template #body="slotProps">
              <p
                class="tw-text-center tw-rounded tw-font-medium"
                :class="{
                  'tw-bg-green-200': slotProps.data.feedback === 'include',
                  'tw-bg-red-200': slotProps.data.feedback === 'exclude',
                  'tw-bg-gray-200': slotProps.data.feedback === 'maybe',
                }"
              >
                toTitleCase(slotProps.data.feedback)
              </p>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </Container>
</template>

<script lang="ts" setup>
import CustomButton from "@/components/CustomButton.vue";
import Container from "@/components/Container.vue";
import QueryPanel from "../review/components/QueryPanel.vue";
import ScreeningProgressPanel from "../review/components/ScreeningProgressPanel.vue";

import { ref } from "vue";
import startIcon from "@/assets/icons/start.png";
import reviewIcon from "@/assets/icons/review.png";
import pauseIcon from "@/assets/icons/pause.png";

const items = ref([
  {
    label: "Started",
    icon: startIcon,
  },
  {
    label: "Reviewing",
    icon: reviewIcon,
  },
  {
    label: "Paused",
    icon: pauseIcon,
  },
]);
</script>
