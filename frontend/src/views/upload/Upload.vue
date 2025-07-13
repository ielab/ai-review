<template>
  <Loading v-if="isLoading" />

  <BlockUI :blocked="isLoading" :pt="{ root: 'tw-z-0' }">
    <Container>
      <div class="tw-flex tw-flex-col tw-gap-4">
        <FileUpload
          :multiple="true"
          :fileLimit="fileLimit"
          :maxFileSize="maxSize"
          customUpload
          :pt="{
            badge: { root: 'tw-hidden' },
            buttonbar: 'tw-p-0 tw-border-none tw-bg-white',
            content: 'tw-p-0 tw-border-none',
          }"
        >
          <template #header="{ chooseCallback, files }">
            <div class="tw-flex tw-flex-col tw-w-full">
              <h2>Instruction</h2>
              <div class="tw-flex tw-gap-4 tw-items-center tw-my-4 tw-w-full">
                <div class="tw-w-4/5">
                  <p class="tw-w-full">
                    Upload corpus.nbib or corpus.ris file
                    <span class="tw-text-red-500 tw-font-medium">
                      (required)
                    </span>
                    .
                  </p>
                  <div class="tw-flex tw-items-center tw-gap-2">
                    <p>
                      If you do not have one, you can try our system with an
                      example corpus & inclusion criteria by clicking
                    </p>
                    <div class="tw-flex tw-items-center tw-gap-2">
                      <i class="pi pi-file" /> Sample Dataset
                    </div>
                    <p>button</p>
                  </div>
                </div>

                <div class="tw-w-1/5">
                  <Button
                    @click="useDemoFile(files)"
                    label="Sample Dataset"
                    outlined
                    icon="pi pi-file"
                    class="tw-w-full"
                  />
                </div>
              </div>
            </div>

            <div
              class="tw-bg-[#fafafa] tw-w-full border tw-p-4 tw-rounded-t-lg"
            >
              <div
                v-tooltip="{
                  value: 'You can only upload one file.',
                  pt: {
                    root: 'tw-max-w-none',
                    text: 'tw-text-sm',
                  },
                }"
                class="tw-w-fit"
              >
                <Button
                  @click="chooseCallback"
                  label="Choose File"
                  outlined
                  icon="pi pi-plus"
                  :disabled="files.length > 0"
                />
              </div>
            </div>
          </template>
          <template #content="{ files, removeFileCallback }">
            <div class="tw-flex tw-flex-col tw-gap-6">
              <ul
                v-if="files.length > 0"
                class="tw-p-0 tw-m-0 tw-list-none tw-flex tw-flex-wrap tw-gap-2"
              >
                <li
                  v-for="(file, index) in files"
                  :key="file.name + index"
                  class="tw-flex tw-items-center tw-justify-between tw-w-full tw-p-6 border tw-rounded-b-lg"
                  style="border-top: none !important"
                >
                  <div class="tw-flex tw-items-center tw-gap-6">
                    <img
                      :src="getIcon(file.name)"
                      width="36"
                      :style="{
                        filter: `invert(0.5) sepia(1) saturate(300%) ${getHue(
                          file.name
                        )}`,
                      }"
                    />
                    <div>
                      <div class="tw-text-gray-600 tw-font-medium tw-mb-1">
                        {{ file.name }}
                      </div>
                      <div class="tw-text-gray-500 tw-text-xs">
                        {{ prettyBytes(file.size) }}
                      </div>
                    </div>
                  </div>
                  <i
                    @click="removeFileCallback(index)"
                    class="pi pi-times tw-cursor-pointer tw-text-red-500 tw-text-xl hover:tw-bg-red-100 tw-w-8 tw-h-8 tw-flex tw-items-center tw-justify-center tw-rounded-full tw-duration-150 active:tw-scale-95"
                  />
                </li>
              </ul>

              <div
                v-else
                class="tw-flex tw-items-center tw-justify-center tw-flex-col tw-p-10 border tw-rounded-lg"
              >
                <i
                  class="tw-m-2 pi pi-cloud-upload tw-rounded-full tw-border-2 tw-border-solid tw-text-gray-400 tw-border-gray-400 tw-p-8 tw-text-8xl"
                />
                <p class="tw-mt-4 tw-mb-0">
                  Drag and drop files here to upload.
                </p>
              </div>

              <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
                <Panel class="tw-w-full">
                  <template #header>
                    <p>
                      <span class="tw-font-bold">Inclusion Criteria </span>
                      <span class="tw-text-red-500 tw-font-medium">
                        (You need to input at least one inclusion criterion to
                        preceed.)
                      </span>
                    </p>
                  </template>
                  <div class="tw-flex tw-flex-col tw-gap-4">
                    <p>
                      List the criteria for including studies for the screening.
                    </p>
                    <div class="tw-flex tw-gap-4">
                      <InputText
                        class="tw-w-11/12"
                        type="text"
                        placeholder="Describe the criteria"
                        v-model="inclusionCriteria"
                      />
                      <Button
                        class="tw-w-1/12"
                        icon="pi pi-plus"
                        label="Add"
                        @click="push()"
                      />
                    </div>
                    <div
                      v-for="(x, index) in inclusionCriteriaArray"
                      class="tw-flex tw-gap-4 tw-items-center"
                    >
                      <div class="tw-flex tw-items-center tw-w-11/12 tw-gap-4">
                        <p>{{ index + 1 }}.</p>
                        <InputText
                          :pt="{
                            root: 'tw-bg-primary-50 tw-text-primary-500 tw-font-medium',
                          }"
                          class="tw-w-full"
                          type="text"
                          :value="x"
                          @input="(event:any) => update(index, event)"
                        />
                      </div>
                      <Button
                        class="tw-w-1/12"
                        icon="pi pi-trash"
                        severity="danger"
                        @click="remove(index)"
                      />
                    </div>
                  </div>
                </Panel>
              </div>
              <div class="tw-flex tw-justify-end">
                <Button
                  @click="submit(files)"
                  label="Next to Preview"
                  :disabled="!files.length || !inclusionCriteriaArray.length"
                />
              </div>
            </div>
          </template>
        </FileUpload>
      </div>
    </Container>
  </BlockUI>
</template>

<script lang="ts" setup>
import { ref, PropType } from "vue";
import prettyBytes from "pretty-bytes";
import FileUpload from "primevue/fileupload";
import Button from "primevue/button";
import Panel from "primevue/panel";
import InputText from "primevue/inputtext";
import BlockUI from "primevue/blockui";
import Container from "@/components/Container.vue";
import Loading from "@/components/Loading.vue";

defineProps({
  fileLimit: { type: Number, default: 3 },
  maxSize: { type: Number, default: 1024 ** 3 }, // 1GB
  submitLabel: { type: String, default: "Next to Preview" },
  inclusionCriteriaArray: { type: Array as PropType<string[]>, default: [] },
});

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

import { useRouter } from "vue-router";
const router = useRouter();

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();
import { ValidationError } from "joi";

// Collection Store -----------------------------------

import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";

import {
  uploadCollectionFilesStore,
  clearUploadCollectionFilesStore,
} from "@/stores/uploadCollection";

// Validate files to upload
const validateFiles = (files: File[]) => {
  // 1: INVALID -> No file selected
  if (files.length === 0)
    return showToast(
      "error",
      "No file selected",
      "Please select a file to upload."
    );
  // 2: INVALID -> Too many files
  if (files.length > 2)
    return showToast(
      "error",
      "Too many files",
      "Please select only corpus.jsonl and queries.jsonl."
    );
  return true;
};

// Inclusion Criteria -----------------------------------

const inclusionCriteriaArray = ref<string[]>([]);
const inclusionCriteria = ref<string>("");

function push() {
  inclusionCriteriaArray.value.push(inclusionCriteria.value);
  inclusionCriteria.value = "";
}

function update(index: number, event: Event) {
  const target = event.target as HTMLInputElement | null;
  if (target) {
    inclusionCriteriaArray.value[index] = target.value;
  }
}

function remove(index: number) {
  inclusionCriteriaArray.value.splice(index, 1);
}

const getIcon = (filename: string) => {
  if (["nbib", "ris"].includes(filename.split(".")[1])) {
    return "/file.png";
  }
  return "/warning.png";
};

const getHue = (filename: string) => {
  if (["nbib", "ris"].includes(filename.split(".")[1])) {
    return "hue-rotate(60deg)";
  }
  return "hue-rotate(315deg)";
};

const submit = async (files: File[]) => {
  // Reset stored files
  clearUploadCollectionFilesStore();

  // Validate files
  if (!validateFiles(files)) return;

  // Store files in your upload collection store (if needed for tracking)
  files.forEach((file) => {
    uploadCollectionFilesStore.value.file = file;
  });

  // Create FormData for the request
  const formData = new FormData();
  const corpusFile = files.find(
    (file) => file.name.endsWith(".nbib") || file.name.endsWith(".ris")
  ); // Adjust file name logic if needed

  if (!corpusFile) {
    return showToast("error", "File Not Found", "No .nbib or .ris file found!");
  }

  formData.append("nbib_file", corpusFile);

  try {
    setLoading(true);

    // Make the request
    const headers = {
      "Content-Type": "multipart/form-data",
      ...getTokenHeader(),
    };

    const result = await axios.post("/review/upload_corpus", formData, headers);

    uploadCollectionFilesStore.value.corpus =
      result.data.data.preview_uploaded_corpus;
    uploadCollectionFilesStore.value.inclusionCriteria =
      inclusionCriteriaArray.value;
    uploadCollectionFilesStore.value.totalDocuments =
      result.data.data.total_documents;

    // Redirect to the preview page
    router.push({ name: "preview" });
  } catch (error) {
    setLoading(false);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Error uploading corpus", e.message);
    } else if (error instanceof ValidationError) {
      const e = error as ValidationError;
      showToast(
        "error",
        "Error uploading corpus",
        `\n-${e.message.split(". ").join("\n\n- ")}\n\n`
      );
    } else {
      showToast("error", "Unknown error", error as string);
    }
  }
};

// Modify function to just add demo file to the file list
const useDemoFile = (files: File[]) => {
  // Clear all existing files
  files.splice(0, files.length);

  fetch("/aireview_demo.ris")
    .then((response) => response.blob())
    .then((blob) => {
      const demoFile = new File([blob], "aireview_demo.ris", {
        type: blob.type,
      });
      files.push(demoFile);
    })
    .catch((error) => {
      console.error("Error fetching demo file:", error);
    });

  inclusionCriteriaArray.value = [
    "Longitudinal studies with at least three measurement waves measuring posttraumatic stress disorder (PTSD)",
    "Studies that measured PTSD on a continuous scale via an interviewor questionnaire",
    "Studies that used a clustering method (Latent growth mixture modelling, hierarchical cluster analysis)",
    "Traumatic stress symptoms following events that appeared to fulfill DSM-IV criterion A1 for PTSD or acute stress disorder",
  ];
};
</script>
