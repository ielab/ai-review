import { ref, nextTick, Ref } from "vue";
import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";
import { useToast } from "@/composables/toast";
import { useError } from "@/composables/error";
import { IDoc } from "@/types/reviewer";
import { IPreResponse, ICoResponse } from "@/types/response";
import { useRoute } from "vue-router";
import { accountAuthStore } from "@/stores/auth";

export function useReview(
  state: Ref<{
    datasetName: string;
    docs: IDoc[];
    studyIndex: number;
    preResponse: IPreResponse[];
    coResponse: ICoResponse[];
    askAIAllowed: boolean;
    visibleChat: boolean;
  }>
) {
  const { showToast } = useToast();
  const { getResponseErrorMessage } = useError();
  const route = useRoute();
  const previousStudyIndex = ref<number>(-1);

  const getStudies = async () => {
    try {
      const headers = {
        "Content-Type": "multipart/form-data",
        ...getTokenHeader(),
      };
      const formData = new FormData();
      formData.append("review_id", String(route.params.id));
      formData.append("page_index", "0");

      const result = await axios.post("review/study_cards", formData, headers);
      state.value.datasetName = result.data.data.dataset_name;
      state.value.docs = result.data.data.studies;
    } catch (error) {
      handleError(error, "Cannot Fetch Review Data");
    }
  };

  const coProcess = async (
    task: "ask_ai" | "pico_extract" | "detail_reason"
  ) => {
    const responseKey = Date.now();

    if (
      state.value.coResponse.length > 0 &&
      state.value.studyIndex !== previousStudyIndex.value
    ) {
      state.value.coResponse = [];
    }
    previousStudyIndex.value = state.value.studyIndex;

    state.value.coResponse.push({
      key: responseKey,
      studyIndex: state.value.studyIndex,
      task,
      isLoading: true,
      llmResponse: "",
    });

    const result = await llmProcess(task);
    const responseIndex = state.value.coResponse.findIndex(
      (item) => item.key === responseKey
    );

    if (responseIndex !== -1) {
      state.value.coResponse[responseIndex] = {
        key: responseKey,
        studyIndex: state.value.studyIndex,
        task,
        isLoading: false,
        llmResponse: result,
      };
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
    }
  };

  const giveFeedback = async (
    studyIndex: number,
    userFeedback: "include" | "exclude" | null
  ) => {
    try {
      const body = {
        review_id: String(route.params.id),
        page_index: 0,
        study_index: studyIndex,
        feedback: userFeedback,
      };

      state.value.docs[studyIndex].feedbackLoading = true;

      await axios.post("/review/user_feedback", body, getTokenHeader());

      // Update the local state to reflect the feedback
      state.value.docs[studyIndex].user_feedback = userFeedback;

      showToast(
        "success",
        `Successfully stored user feedback for study ${studyIndex + 1}`
      );
    } catch (error) {
      handleError(error, "Cannot Give Feedback");
    } finally {
      state.value.docs[studyIndex].feedbackLoading = false;
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

  const updateVisibleChat = (visible: boolean) => {
    state.value.visibleChat = visible;
  };

  const updateStudyIndex = (index: number) => {
    state.value.studyIndex = index;
    scrollToStudyIndex(index);
  };

  const scrollToStudyIndex = (index: number) => {
    nextTick(() => {
      const cardElement = document.querySelectorAll(".screening-card")[
        index
      ] as HTMLElement;
      if (cardElement) {
        const navbarHeight = 26;
        const cardRect = cardElement.getBoundingClientRect();
        const scrollPosition =
          window.scrollY +
          cardRect.top -
          (window.innerHeight / 2 - cardRect.height / 2) -
          navbarHeight;

        window.scrollTo({
          top: scrollPosition,
          behavior: "smooth",
        });
      }
    });
  };

  const isAllFeedbackTrue = (): boolean => {
    return (
      state.value.docs.every((doc) => !!doc.user_feedback) &&
      state.value.docs.every((doc) => !doc.feedbackLoading)
    );
  };

  const chatClient = (inputMsg: string, studyIndex: number) => {
    try {
      const userId = Number(accountAuthStore.id);
      const reviewId = Number(route.params.id);
      const uri = `wss://aireview.ielab.io/api/ws/chat/${userId}/${reviewId}/?page_index=0&study_index=${studyIndex}`;
      const websocket = new WebSocket(uri);
      const responseKey = Date.now();
      let accumulatedResponse = "";

      // Clear coResponse if studyIndex has changed
      if (
        state.value.coResponse.length > 0 &&
        state.value.studyIndex !== previousStudyIndex.value
      ) {
        state.value.coResponse = [];
      }
      previousStudyIndex.value = state.value.studyIndex;

      // Initialize response in coResponse
      state.value.coResponse.push({
        key: responseKey,
        studyIndex: state.value.studyIndex,
        task: "user_ask_ai",
        isLoading: true,
        llmResponse: "",
        message: inputMsg,
      });

      websocket.onopen = () => {
        const message = JSON.stringify({ message: inputMsg });
        websocket.send(message);
        // console.log(`[You]: ${inputMsg}`);
        // console.log("[LLM]:");
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const response = data?.data?.chunk || "";
          const eventType = data?.event || "";

          if (
            eventType === "on_parser_start" ||
            eventType === "on_parser_stream"
          ) {
            accumulatedResponse += response;

            // Update coResponse with partial response
            const responseIndex = state.value.coResponse.findIndex(
              (item) => item.key === responseKey
            );
            if (responseIndex !== -1) {
              state.value.coResponse[responseIndex] = {
                key: responseKey,
                studyIndex: state.value.studyIndex,
                task: "user_ask_ai",
                isLoading: false,
                llmResponse: accumulatedResponse,
                message: inputMsg,
              };
            }
          } else {
            // Finalize response
            const responseIndex = state.value.coResponse.findIndex(
              (item) => item.key === responseKey
            );
            if (responseIndex !== -1) {
              state.value.coResponse[responseIndex] = {
                key: responseKey,
                studyIndex: state.value.studyIndex,
                task: "user_ask_ai",
                isLoading: false,
                llmResponse: accumulatedResponse,
                message: inputMsg,
              };
            }
            console.log("\n[LLM Done]");
            websocket.close();
          }
        } catch (error) {
          console.error("Error parsing JSON:", error);
          handleError(error, "Chat Client Error");
        }
      };

      websocket.onclose = () => {
        console.log("Connection closed.");
      };

      websocket.onerror = (error) => {
        console.error("An error occurred:", error);
        handleError(error, "Chat Client Error");
        const responseIndex = state.value.coResponse.findIndex(
          (item) => item.key === responseKey
        );
        if (responseIndex !== -1) {
          state.value.coResponse[responseIndex] = {
            key: responseKey,
            studyIndex: state.value.studyIndex,
            task: "ask_ai",
            isLoading: false,
            llmResponse: accumulatedResponse || "Error occurred during chat",
            message: inputMsg,
          };
        }
        websocket.close();
      };
    } catch (error) {
      console.error("An error occurred:", error);
      handleError(error, "Chat Client Error");
    }
  };

  return {
    getStudies,
    coProcess,
    updateVisibleChat,
    updateStudyIndex,
    isAllFeedbackTrue,
    giveFeedback,
    chatClient,
  };
}
