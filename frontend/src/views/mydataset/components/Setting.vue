<template>
  <Dialog v-model:visible="visible" modal :draggable="false" class="tw-w-[55%]">
    <template #header>
      <div class="tw-flex tw-items-center tw-gap-2">
        <i class="pi pi-cog" style="font-size: 1.5rem" />
        <h2>Check settings before screening</h2>
      </div>
    </template>

    <div class="tw-flex tw-flex-col tw-gap-4">
      <Panel :pt="{ header: 'tw-p-3' }">
        <template #header>
          <div class="tw-flex tw-items-center tw-gap-2">
            <p class="tw-font-bold">AI Pipeline Builder</p>
            <i
              v-tooltip.top="{
                value:
                  'Choose when you want AI help: before, during or after your screening work',
                pt: {
                  root: 'tw-max-w-none',
                  text: 'tw-text-sm',
                },
              }"
              class="pi pi-info-circle"
            />
          </div>
        </template>
        <div class="tw-flex tw-flex-col tw-gap-3">
          <div
            class="tw-rounded border tw-p-3 tw-flex tw-items-center tw-gap-2"
          >
            <small class="tw-font-medium">Current Selection:</small>
            <Tag :value="pipeline.label" />
          </div>
          <div
            class="tw-flex tw-font-medium tw-gap-6 tw-items-center tw-justify-center"
          >
            <div
              v-tooltip.top="{
                value: 'Let AI screen for you first.',
                pt: {
                  root: 'tw-max-w-none',
                  text: 'tw-text-sm',
                },
              }"
              @click="updatePipelineBuilder('pre')"
              class="tw-cursor-pointer tw-py-8 tw-rounded-md border tw-items-center tw-w-full tw-flex tw-flex-col"
              :class="{
                'tw-bg-blue-50 tw-border-blue-300 !tw-opacity-100 tw-shadow':
                  pipelineBuilder.pre,
              }"
            >
              <div
                class="tw-flex tw-items-center tw-gap-2 tw-select-none"
                :class="{
                  'tw-text-blue-500': pipelineBuilder.pre,
                }"
              >
                <i
                  :class="pipelineBuilder.pre ? 'pi pi-check' : 'pi pi-times'"
                />
                Pre-reviewer
              </div>
            </div>

            <i class="pi pi-arrow-right tw-text-slate-400 tw-text-xs" />

            <div
              v-tooltip.top="{
                value: 'Ask AI to help when you screen.',
                pt: {
                  root: 'tw-max-w-none',
                  text: 'tw-text-sm',
                },
              }"
              @click="updatePipelineBuilder('co')"
              class="tw-cursor-pointer tw-py-8 tw-rounded-md border tw-items-center tw-w-full tw-flex tw-flex-col"
              :class="{
                'tw-bg-green-50 tw-border-green-300 !tw-opacity-100 tw-shadow':
                  pipelineBuilder.co,
              }"
            >
              <div
                class="tw-flex tw-items-center tw-gap-2 tw-select-none"
                :class="{
                  'tw-text-green-500': pipelineBuilder.co,
                }"
              >
                <i
                  :class="pipelineBuilder.co ? 'pi pi-check' : 'pi pi-times'"
                />
                Co-reviewer
              </div>
            </div>

            <i class="pi pi-arrow-right tw-text-slate-400 tw-text-xs" />

            <div
              v-tooltip.top="{
                value: 'Let AI check your screened studies',
                pt: {
                  root: 'tw-max-w-none',
                  text: 'tw-text-sm',
                },
              }"
              @click="updatePipelineBuilder('post')"
              class="tw-cursor-pointer tw-py-8 tw-rounded-md border tw-items-center tw-w-full tw-flex tw-flex-col"
              :class="{
                'tw-bg-purple-50 tw-border-purple-300 !tw-opacity-100 tw-shadow':
                  pipelineBuilder.post,
              }"
            >
              <div
                class="tw-flex tw-items-center tw-gap-2 tw-select-none"
                :class="{
                  'tw-text-purple-500': pipelineBuilder.post,
                }"
              >
                <i
                  :class="pipelineBuilder.post ? 'pi pi-check' : 'pi pi-times'"
                />
                Post-reviewer
              </div>
            </div>
          </div>

          <Panel :pt="{ header: 'tw-p-3' }">
            <template #header>
              <div class="tw-flex tw-items-center tw-gap-2">
                <small class="tw-font-medium">AI Interaction Level</small>
                <i
                  v-tooltip.top="{
                    value:
                      'Toggle how much AI helps: wait for your request (Low) or get instant suggestions (High)',
                    pt: {
                      root: 'tw-max-w-none',
                      text: 'tw-text-sm',
                    },
                  }"
                  class="pi pi-info-circle tw-text-sm"
                />
              </div>
            </template>
            <div class="tw-flex tw-flex-col tw-gap-3">
              <div>
                <div
                  class="tw-w-1/4 tw-flex tw-justify-center tw-mx-auto tw-justify-between tw-px-4 tw-pb-2"
                  style="border-bottom: 1.5px solid black"
                >
                  <i
                    class="pi pi-user"
                    :class="{ 'tw-text-primary-500': !high }"
                  />
                  <i
                    class="pi pi-microchip-ai"
                    :class="{ 'tw-text-primary-500': high }"
                  />
                </div>

                <div
                  class="tw-w-1/4 tw-justify-center tw-mx-auto tw-flex tw-transition-all tw-duration-300"
                  :class="
                    high ? 'tw-translate-x-[15%]' : 'tw-translate-x-[-15%]'
                  "
                >
                  <i class="fa-solid fa-caret-up tw-text-xl" />
                </div>

                <div class="tw-flex tw-justify-center tw-items-center tw-gap-2">
                  <small
                    :class="!high ? 'tw-text-primary-500' : 'tw-text-slate-400'"
                  >
                    Low Support
                  </small>
                  <InputSwitch v-model="high" class="tw-scale-[0.75]" />
                  <small
                    :class="high ? 'tw-text-primary-500' : 'tw-text-slate-400'"
                  >
                    High Support
                  </small>
                </div>
              </div>

              <div
                class="tw-bg-[#FAFAFA] tw-p-2 border tw-rounded tw-flex tw-flex-col tw-justify-center tw-gap-2"
              >
                <small class="tw-font-medium tw-text-center"
                  >AI Roles in Pipeline</small
                >
                <small>
                  <ul>
                    <li>
                      <div class="tw-flex tw-items-center tw-gap-6">
                        <p class="tw-font-medium tw-w-[5%]">Pre:</p>
                        <p class="tw-w-[35%]">Let AI screen for you first.</p>
                        <div
                          v-if="!high"
                          class="tw-flex tw-items-center tw-gap-2"
                        >
                          <i class="fa-regular fa-hand" />
                          <p>Show result upon requested</p>
                        </div>
                        <div v-else class="tw-flex tw-items-center tw-gap-2">
                          <i class="pi pi-eye" />
                          <p>Reveal results along with studies</p>
                        </div>
                      </div>
                    </li>
                  </ul>
                </small>

                <small>
                  <ul>
                    <li>
                      <div class="tw-flex tw-items-center tw-gap-6">
                        <p class="tw-font-medium tw-w-[5%]">Co:</p>
                        <p class="tw-w-[35%]">
                          Ask AI to help when you screen.
                        </p>
                        <div
                          v-if="!high"
                          class="tw-flex tw-items-center tw-gap-2"
                        >
                          <i class="fa-regular fa-hand" />
                          <p>Help options for predefined tasks</p>
                        </div>
                        <div v-else class="tw-flex tw-items-center tw-gap-2">
                          <i class="pi pi-comments" />
                          <p>In addition to help options, enable chat</p>
                        </div>
                      </div>
                    </li>
                  </ul>
                </small>

                <small>
                  <ul>
                    <li>
                      <div class="tw-flex tw-items-center tw-gap-6">
                        <p class="tw-font-medium tw-w-[5%]">Post:</p>
                        <p class="tw-w-[35%]">
                          Let AI check your screened studies.
                        </p>
                        <div
                          v-if="!high"
                          class="tw-flex tw-items-center tw-gap-2"
                        >
                          <i class="fa-regular fa-hand" />
                          <p>Show result upon requested</p>
                        </div>
                        <div v-else class="tw-flex tw-items-center tw-gap-2">
                          <i class="pi pi-list-check" />
                          <p>
                            Check potential incorrect decisions, enable chat
                          </p>
                        </div>
                      </div>
                    </li>
                  </ul>
                </small>
              </div>
            </div>
          </Panel>
        </div>
      </Panel>
      <Panel header="AI Model" :pt="{ header: 'tw-p-3' }">
        <Dropdown
          v-model="selectedModel"
          :options="groupedModels"
          optionLabel="label"
          optionGroupLabel="label"
          optionGroupChildren="items"
          placeholder="Select a model"
          class="tw-w-full"
        >
          <template #optiongroup="slotProps">
            <div class="tw-flex tw-items-center tw-gap-2">
              <img
                :alt="slotProps.option.label"
                :src="openai"
                style="width: 18px"
              />
              <div>{{ slotProps.option.label }}</div>
            </div>
          </template>
        </Dropdown>
      </Panel>
      <Panel header="AI Prompts" :pt="{ header: 'tw-p-3' }">
        <div
          class="tw-rounded border tw-p-3 tw-mb-3 tw-flex tw-items-center tw-gap-2"
        >
          <small class="tw-font-medium">Editing prompts for:</small>
          <Tag value="Pre-Reviewer Prompts" />
        </div>
        <div class="tw-grid tw-grid-cols-3 tw-gap-3">
          <div class="border tw-rounded tw-p-3 tw-flex tw-flex-col tw-gap-2">
            <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
              <i class="pi pi-comment tw-text-blue-500" />
              <p>System Prompt</p>
            </div>
            <Textarea
              v-model="prompts.systemPrompts"
              class="tw-w-full"
              disabled
              :rows="4"
              :pt="{ root: 'tw-p-2 tw-text-sm' }"
            />
          </div>

          <div class="border tw-rounded tw-p-3 tw-flex tw-flex-col tw-gap-2">
            <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
              <i class="pi pi-file tw-text-green-500" />
              <p>Task Specification</p>
            </div>
            <Textarea
              v-model="prompts.taskSpecification"
              class="tw-w-full"
              disabled
              :rows="4"
              :pt="{ root: 'tw-p-2 tw-text-sm' }"
            />
          </div>

          <div class="border tw-rounded tw-p-3 tw-flex tw-flex-col tw-gap-2">
            <div class="tw-flex tw-items-center tw-gap-2 tw-font-medium">
              <i class="pi pi-book tw-text-purple-500" />
              <p>Output Format</p>
            </div>
            <Textarea
              v-model="prompts.outputFormat"
              class="tw-w-full"
              disabled
              :rows="4"
              :pt="{ root: 'tw-p-2 tw-text-sm' }"
            />
          </div>
        </div>
      </Panel>
    </div>

    <template #footer>
      <div class="tw-flex tw-justify-end">
        <Button
          severity="secondary"
          label="Back"
          @click="visible = false"
        />
        <Button
          label="Start screening"
          :loading="isLoading"
          @click="submit"
        />
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";

import Dialog from "primevue/dialog";
import Panel from "primevue/panel";
import Tag from "primevue/tag";
import Dropdown from "primevue/dropdown";
import Textarea from "primevue/textarea";
import InputSwitch from "primevue/inputswitch";
import Button from "primevue/button";

import openai from "@/assets/icons/openai.png";

import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useRouter } from "vue-router";
const router = useRouter();

const props = defineProps<{
  isActive?: boolean;
  id?: number;
}>();

const emit = defineEmits(["update:isActive"]);
const visible = computed({
  get() {
    return props.isActive;
  },
  set(value) {
    emit("update:isActive", value);
  },
});

const prompts = ref({
  systemPrompts: "Generally how AI work like, e.g. role",
  taskSpecification: "Specify what task AI will do, e.g. judge relevance",
  outputFormat: "Formatting the way AI responses",
});

const high = ref(false);

const pipelineBuilder = ref({ pre: true, co: true, post: true });

const selectedModel = ref({ label: "GPT-4o", value: "gpt-4o" });
const groupedModels = ref([
  {
    img: "@/assets/icons/openai.png",
    label: "OpenAI",
    items: [{ label: "GPT-4o", value: "gpt-4o" }],
  },
]);

const updatePipelineBuilder = (pipeline: "pre" | "co" | "post") => {
  // Toggle the respective pipeline value
  if (pipeline === "pre")
    pipelineBuilder.value.pre = !pipelineBuilder.value.pre;
  if (pipeline === "co") pipelineBuilder.value.co = !pipelineBuilder.value.co;
  if (pipeline === "post")
    pipelineBuilder.value.post = !pipelineBuilder.value.post;

  // Check if at least one is true, else revert the last toggle
  if (
    !pipelineBuilder.value.pre &&
    !pipelineBuilder.value.co &&
    !pipelineBuilder.value.post
  ) {
    // Revert the toggle if all are false
    if (pipeline === "pre")
      pipelineBuilder.value.pre = !pipelineBuilder.value.pre;
    if (pipeline === "co") pipelineBuilder.value.co = !pipelineBuilder.value.co;
    if (pipeline === "post")
      pipelineBuilder.value.post = !pipelineBuilder.value.post;
  }
};

const pipeline = computed(() => {
  // Ensure we cover all combinations of pre, co, and post
  const { pre, co, post } = pipelineBuilder.value;

  if (pre && co && post) return { label: "Full Pipeline", value: "full" };
  if (pre && co && !post) return { label: "Pre-Co Pipeline", value: "pre-co" };
  if (pre && !co && post)
    return { label: "Pre-Post Pipeline", value: "pre-post" };
  if (pre && !co && !post) return { label: "Pre-Only", value: "pre-only" };
  if (!pre && co && post)
    return { label: "Co-Post Pipeline", value: "co-post" };
  if (!pre && co && !post) return { label: "Co-Only", value: "co-only" };
  if (!pre && !co && post) return { label: "Post-Only", value: "post-only" };

  // If none of the conditions are true, return a default
  return { label: "Full Pipeline", value: "full" };
});

async function submit() {
  try {
    setLoading(true);

    const body = {
      review_id: props.id,
      llm_parameters: JSON.stringify({
        model_name: "gpt-4o",
        temperature: 0,
        max_tokens: 2048,
        response_format: "text",
        streaming: true,
      }),
      pipeline_type: pipeline.value.value,
      llm_interaction_level: high.value,
    };

    const result = await axios.post(
      "review/llm_config",
      body,
      getTokenHeader()
    );

    showToast("success", result.data.message);
    router.push({ name: "review", params: { id: Number(props.id) } });
  } catch (error) {
    setLoading(false);
    console.error(error);
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", "Cannot Set LLM parameters for a dataset", e.message);
    } else if (error instanceof Error) {
      showToast(
        "error",
        "Cannot Set LLM parameters for a dataset",
        error.message
      );
    } else {
      showToast(
        "error",
        "Cannot Set LLM parameters for a dataset",
        "An error occurred"
      );
    }
  }
}
</script>
