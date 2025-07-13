export const DEFAULT_STUDY = {
  id: null,
  name: "",
  screening_status: "",
  pipeline_type: "",
  current_screening_page: 1,
  show_docs_per_page: 10,
  created_at: "",
};

export const DEFAULT_DOC = {
  pmid: "",
  title: "",
  authors: "",
  abstract: "",
  user_feedback: null,
  pre_response: null,
  co_rating: null,
  post_response: null,
  feedbackLoading: false,
};

export const DEFAULT_LLM_PARAMETERS = {
  streaming: false,
  max_tokens: 0,
  model_name: "",
  temperature: 0,
  response_format: "",
};

export const DEFAULT_LLM_CONFIG = {
  pipeline_type: "",
  llm_interaction_level: false,
  llm_parameters: DEFAULT_LLM_PARAMETERS,
};

export const DEFAULT_STATE = {
  initLoading: true,
  configLoading: true,
  datasetName: "",
  docs: [DEFAULT_DOC],
  config: DEFAULT_LLM_CONFIG,
  askAIAllowed: false,
  visibleChat: false,
  studyIndex: 0,
  preResponse: [],
  coResponse: [],
  active: 0,
  pre: false,
  co: false,
  post: false,
  interactionLevel: false,
};
