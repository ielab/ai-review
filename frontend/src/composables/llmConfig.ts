import { watch, Ref } from "vue";
import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";
import { useToast } from "@/composables/toast";
import { useError } from "@/composables/error";
import { canAskAI } from "@/utils/reviewer";
import { ILLMConfig, IDoc } from "@/types/reviewer";
import { ICoResponse, IPreResponse } from "@/types/response";
import { RouteLocationNormalizedLoaded } from "vue-router";

export function useLLMConfig(
  state: Ref<{
    config: ILLMConfig;
    configLoading: boolean;
    pre: boolean;
    co: boolean;
    post: boolean;
    interactionLevel: boolean;
    askAIAllowed: boolean;
    visibleChat: boolean;
    preResponse: IPreResponse[];
    studyIndex: number;
    datasetName: string; // Added
    docs: IDoc[]; // Added
    coResponse: ICoResponse[]; // Added
  }>,
  route: RouteLocationNormalizedLoaded
) {
  const { showToast } = useToast();
  const { getResponseErrorMessage } = useError();

  let debounceTimeout: ReturnType<typeof setTimeout> | null = null;

  const getLLMConfig = async () => {
    try {
      const headers = {
        "Content-Type": "multipart/form-data",
        ...getTokenHeader(),
      };
      const formData = new FormData();
      formData.append("review_id", String(route.params.id));

      const result = await axios.post(
        "review/get_llm_config",
        formData,
        headers
      );
      state.value.config = result.data.data as ILLMConfig;
    } catch (error) {
      handleError(error, "Cannot Fetch LLM Config Data");
    }
  };

  const updateConfig = async () => {
    const pipelineType = getPipelineType();
    const body = {
      review_id: route.params.id,
      llm_parameters: JSON.stringify(state.value.config.llm_parameters),
      pipeline_type: pipelineType,
      llm_interaction_level: state.value.interactionLevel,
    };

    try {
      state.value.configLoading = true;
      await axios.post("review/llm_config", body, getTokenHeader());
      await init();
    } catch (error) {
      console.error("Failed to update config:", error);
    } finally {
      state.value.configLoading = false;
    }
  };

  const updatePrompt = async (prompt: String) => {
    const body = {
      review_id: route.params.id,
      prompt_type: "co_ask_ai_prompt",
      prompt_content: prompt,
    };

    try {
      state.value.configLoading = true;
      await axios.post("review/update_prompt", body, getTokenHeader());
      await init();
    } catch (error) {
      console.error("Failed to update prompt:", error);
    } finally {
      state.value.configLoading = false;
    }
  };

  const getPipelineType = () => {
    const { pre, co, post } = state.value;
    if (pre && co && post) return "full";
    if (pre && co && !post) return "pre-co";
    if (pre && !co && post) return "pre-post";
    if (pre && !co && !post) return "pre-only";
    if (!pre && co && post) return "co-post";
    if (!pre && co && !post) return "co-only";
    if (!pre && !co && post) return "post-only";
    return "none";
  };

  const init = async () => {
    await getLLMConfig();
    state.value.pre =
      state.value.config.pipeline_type.includes("pre") ||
      state.value.config.pipeline_type === "full";
    state.value.co =
      state.value.config.pipeline_type.includes("co") ||
      state.value.config.pipeline_type === "full";
    state.value.post =
      state.value.config.pipeline_type.includes("post") ||
      state.value.config.pipeline_type === "full";
    state.value.interactionLevel = state.value.config.llm_interaction_level;
    state.value.askAIAllowed = canAskAI(
      state.value.config.pipeline_type,
      state.value.interactionLevel
    );

    if (!state.value.visibleChat && state.value.askAIAllowed) {
      state.value.visibleChat = true;
    }

    if (state.value.pre) {
      state.value.preResponse = (await llmProcess("pre")) || [];
    }
  };

  const llmProcess = async (
    task: "pre" | "ask_ai" | "pico_extract" | "detail_reason"
  ) => {
    try {
      const headers = {
        "Content-Type": "multipart/form-data",
        ...getTokenHeader(),
      };
      const formData = new FormData();
      formData.append("review_id", String(route.params.id));
      formData.append("page_index", "0");
      formData.append("study_index", String(state.value.studyIndex));
      formData.append("task", task);

      const result = await axios.post("review/llm_process", formData, headers);
      return task === "pre"
        ? result.data.data.responses
        : result.data.data.llm_response;
    } catch (error) {
      handleError(error, "Cannot Process LLM");
      return null;
    }
  };

  const handleError = (error: unknown, title: string) => {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", title, e.message);
    } else if (error instanceof Error) {
      showToast("error", title, error.message);
    } else {
      showToast("error", title, "An error occurred");
    }
  };

  watch(
    [
      () => state.value.pre,
      () => state.value.co,
      () => state.value.post,
      () => state.value.interactionLevel,
    ],
    () => {
      if (debounceTimeout) clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(updateConfig, 400);
    }
  );

  return { init, updateConfig, updatePrompt };
}
