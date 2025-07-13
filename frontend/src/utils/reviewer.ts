import { ref } from "vue";

import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

const isError = ref(false);

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import { IPipelineType } from "@/types/reviewer";

const llmProcessResponse = ref();
const llmProcessMessage = ref("");

const llmProcess = async (
  task: "pre" | "ask_ai" | "pico_extract" | "detail_reason",
  reviewId: string,
  studyIndex: number
): Promise<void> => {
  try {
    setLoading(true);

    const headers = {
      "Content-Type": "multipart/form-data",
      ...getTokenHeader(),
    };

    const formData = new FormData();
    formData.append("review_id", reviewId);
    formData.append("page_index", "0");
    formData.append("study_index", String(studyIndex));
    formData.append("task", task);

    const result = await axios.post("review/llm_process", formData, headers);

    console.log(result.data);

    llmProcessResponse.value = result.data.data;
    llmProcessMessage.value = result.data.message;
  } catch (error) {
    isError.value = true;
    console.error(error);

    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      llmProcessMessage.value = e.message;
    } else if (error instanceof Error) {
      llmProcessMessage.value = error.message;
    } else {
      llmProcessMessage.value = "An error occurred";
    }
  } finally {
    setLoading(false);
  }
};

const canAskAI = (pipeline: IPipelineType, interactionLevel: boolean) => {
  const allowedTasks: Record<string, string[]> = {
    "pre-only": ["pre"],
    "co-only": ["ask_ai", "pico_extract", "detail_reason"],
    "post-only": ["post"],
    "pre-co": ["pre", "ask_ai", "pico_extract", "detail_reason"],
    "pre-post": ["pre", "post"],
    "co-post": ["ask_ai", "pico_extract", "detail_reason", "post"],
    full: ["pre", "ask_ai", "pico_extract", "detail_reason", "post"],
  };

  return allowedTasks[pipeline]?.includes("ask_ai") && interactionLevel
    ? true
    : false;
};

export {
  llmProcess,
  canAskAI,
  llmProcessResponse,
  llmProcessMessage,
  isLoading as llmProcessIsLoading,
  isError as llmProcessIsError,
};
