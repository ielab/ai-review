<template>
  <Container class="tw-flex tw-flex-col tw-gap-5 tw-m-auto">
    <div class="tw-w-full tw-flex tw-flex-col tw-gap-y-2">
      <h2>Instruction</h2>
      <p>
        Upload corpus.nbib file (required). If you do not have one, you can try
        DenseReview with our sample corpus by downloading corpus.nbib (<a
          href="https://katya-transformer-storage.s3.ap-southeast-2.amazonaws.com/sample_corpus/corpus.jsonl"
          target="_blank"
          >link</a
        >) here.
      </p>
      <Uploader @submit="storeFiles" submitLabel="Preview" />
    </div>

    <div class="tw-my-4">
      <Panel>
        <template #header>
          <p class="tw-font-medium">
            Inclusion Criteria <span class="tw-text-red-500">*</span>
          </p>
        </template>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <p>List the criteria for including studies for the screening.</p>

          <Textarea :rows="4" />
        </div>
      </Panel>
    </div>
  </Container>
</template>
<script lang="ts" setup>
import Container from "@/components/Container.vue";
import Uploader from "@/components/Uploader.vue";
import Panel from "primevue/panel";
import Textarea from "primevue/textarea";

// import { ref } from "vue";

import { useRouter } from "vue-router";
const router = useRouter();

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

// Collection Store -----------------------------------

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
  // if (files.length > 2)
  //   return showToast(
  //     'error',
  //     'Too many files',
  //     'Please select only corpus.jsonl and queries.jsonl.',
  //   )
  // // 3: INVALID -> Invalid file on 1 file upload
  // if (files.length === 1 && files[0].name !== 'corpus.jsonl')
  //   return showToast('error', 'Invalid file', 'Please select corpus.jsonl.')
  // // 4: INVALID -> Invalid file on 2 files upload
  // const fileNames = files.map((file) => file.name)
  // if (
  //   files.length === 2 &&
  //   (!fileNames.includes('corpus.jsonl') ||
  //     !fileNames.includes('queries.jsonl'))
  // )
  //   return showToast(
  //     'error',
  //     'Invalid file',
  //     'There is some invalid file. Please select corpus.jsonl and queries.jsonl.',
  //   )
  // Otherwise, VALID
  return true;
};

const storeFiles = async (files: File[]) => {
  // Reset stored files
  clearUploadCollectionFilesStore();
  // Validate files
  if (!validateFiles(files)) return;
  // Store files
  files.forEach((file) => {
    if (file.name === "corpus.jsonl")
      uploadCollectionFilesStore.value.corpus = file;
    else if (file.name === "queries.jsonl")
      uploadCollectionFilesStore.value.queries = file;
  });
  // Redirect to preview page
  router.push({ name: "preview" });
};
</script>
