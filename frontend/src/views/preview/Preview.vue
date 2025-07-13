<template>
  <Loading v-if="isLoading" />

  <BlockUI :blocked="blocked || isLoading" :pt="{ root: 'tw-z-0' }">
    <Container>
      <div class="tw-flex tw-flex-col tw-gap-6">
        <div class="tw-flex tw-w-full">
          <div class="tw-w-full tw-flex tw-items-center tw-gap-2">
            <p class="tw-font-bold">
              Dataset/Review Name <span class="tw-text-red-500">*</span>
            </p>
            <InputText v-model="reviewName" class="tw-w-1/2" />
          </div>
          <div
            class="tw-flex tw-flex-row tw-gap-2 tw-justify-end tw-items-end tw-w-full"
          >
            <Button
              label="Cancel"
              outlined
              @click="isCancelModalActive = true"
            />
            <Button label="Create Dataset/Review" @click="submit()" />
          </div>
        </div>
        <Divider />
        <Panel header="Your Studies">
          <div class="tw-flex tw-flex-col tw-gap-2">
            <small class="tw-text-center">
              Showing preview of first entry • Total
              <span class="tw-text-primary-500 tw-font-medium">
                {{ uploadCollectionFilesStore.totalDocuments }}
                <span v-if="uploadCollectionFilesStore.totalDocuments === 1">
                  study
                </span>
                <span v-else>studies</span>
              </span>
              in corpus
            </small>
            <Textarea
              v-model="uploadCollectionFilesStore.corpus.corpus_first_entry"
              :rows="10"
              disabled
            />
          </div>
        </Panel>
        <Panel header="Inclusion Criteria">
          <div
            v-for="(
              item, index
            ) in uploadCollectionFilesStore.inclusionCriteria"
            class="tw-flex tw-gap-4"
          >
            <p>{{ index + 1 }}.</p>
            <p>{{ item }}</p>
          </div>
        </Panel>
      </div>
    </Container>
  </BlockUI>

  <Modal
    v-model:isActive="isCreateModalActive"
    header="Confirm to create a dataset for your systematic review screening"
    title="Information"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="confirmSubmit"
  >
    <template #body>
      You cannot rename/change your dataset after this stage.
    </template>
  </Modal>

  <Modal
    v-model:isActive="isCancelModalActive"
    header="Cancel to create a collection from uploaded file(s)"
    title="Delete data"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="danger"
    @confirm="handleCancel()"
  >
    <template #body> Your data will be erased permanently. </template>
  </Modal>

  <Modal
    v-model:isActive="warningEmptyModal"
    header="Warning"
    title="Corpus File Not Found"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="router.push({ name: 'upload' })"
  >
    <template #body>
      Your uploaded corpus file was not found. Please upload the corpus file and
      inclusion criteria first.
    </template>
  </Modal>
</template>
<script lang="ts" setup>
import { ref, onMounted } from "vue";

import Divider from "primevue/divider";
import Modal from "@/components/Modal.vue";
import Container from "@/components/Container.vue";
import Button from "primevue/button";
import Textarea from "primevue/textarea";
import InputText from "primevue/inputtext";
import Panel from "primevue/panel";
import BlockUI from "primevue/blockui";
import Loading from "@/components/Loading.vue";

import { useRouter } from "vue-router";
const router = useRouter();

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

// import { useDirty } from "@/composables/dirty";
// const { setDirty, clearDirty } = useDirty();

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { ValidationError } from "joi";
import { validateCollection } from "./validations/validateCollection.ts";

const reviewName = ref("");
const docsPerPage = ref(10)
const isCreateModalActive = ref(false);
const isCancelModalActive = ref(false);
const errorMessage = ref("");

const blocked = ref(false);
const warningEmptyModal = ref(false);

// Collection Store -------------------------------------------
import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";
import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import { uploadCollectionFilesStore } from "@/stores/uploadCollection";

// Delete -----------------------------------------------------
const deleteCorpus = async () => {
  try {
    setLoading(true);
    console.log("deleting file...");

    const params = { corpus_id: uploadCollectionFilesStore.value.corpus.id };
    await axios.delete("/review/upload_corpus", getTokenHeader({ params }));
  } catch (error) {
    console.error(error);
    let errorMessage = "";
    if (error instanceof Error) errorMessage = error.message;
    if (error instanceof AxiosError)
      errorMessage = getResponseErrorMessage(error).message;
    console.log(errorMessage);
  } finally {
    setLoading(false);
  }
};

// Cancel and redirect to upload page
const handleCancel = async () => {
  await deleteCorpus();
  router.push({ name: "upload" });
};

// submit
const submit = async () => {
  try {
    // Validate collection name
    const validation = validateCollection(reviewName.value);
    if (validation.error) throw validation.error;
    isCreateModalActive.value = true;
  } catch (error) {
    console.error(error);
    if (error instanceof ValidationError) {
      errorMessage.value = error.details
        .map((detail) => detail.message)
        .join(" ");
      showToast("error", "Invalid Dataset/Review Name", errorMessage.value);
    } else if (error instanceof Error) {
      showToast("error", "Invalid Dataset/Review Name", error.message);
    } else {
      showToast("error", "Invalid Dataset/Review Name", "An error occurred.");
    }
  }
};

const confirmSubmit = async () => {
  try {
    setLoading(true);
    const body = {
      corpus_id: uploadCollectionFilesStore.value.corpus.id,
      dataset_name: reviewName.value,
      inclusion_criteria: JSON.stringify(uploadCollectionFilesStore.value.inclusionCriteria),
      show_docs_per_page: docsPerPage.value,
    };
    await axios.post("/review/dataset_creation", body, getTokenHeader());
    router.push({ name: "mydataset" });
  } catch (error) {
    console.error(error);

    if (error instanceof Error) {
      errorMessage.value = error.message;
    }

    if (error instanceof AxiosError) {
      errorMessage.value = getResponseErrorMessage(error).message;
    }

    showToast("error", "Failed to create datasets", errorMessage.value);
  } finally {
    setLoading(false);
  }
};

onMounted(() => {
  const emptyCorpus = uploadCollectionFilesStore.value.totalDocuments <= 0;
  const emptyInclusionCriteria = Object.values(
    uploadCollectionFilesStore.value.inclusionCriteria
  ).some((arr) => Array.isArray(arr) && arr.length === 0);

  if (emptyCorpus || emptyInclusionCriteria) {
    blocked.value = true;
    warningEmptyModal.value = true;
  }
});
</script>
