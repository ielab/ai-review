export interface IChat {
  message: string;
  response: string;
}

export type IPipelineType =
  | string
  | "pre-only"
  | "co-only"
  | "post-only"
  | "pre-co"
  | "pre-post"
  | "co-post"
  | "full";

export type IScreeningStatus =
  | string
  | "not_start"
  | "screening"
  | "paused"
  | "finished";

export interface IStudy {
  id: null | number;
  name: string;
  screening_status: IScreeningStatus;
  pipeline_type: IPipelineType;
  current_screening_page: number;
  show_docs_per_page: number;
  created_at: string;
}

export interface IDoc {
  pmid: string;
  title: string;
  authors: string;
  abstract: string;
  user_feedback: 'include' | 'exclude' | null;
  pre_response: null;
  co_rating: null;
  post_response: null;
  feedbackLoading: boolean;
}

export interface ILLMConfig {
  pipeline_type: string;
  llm_interaction_level: boolean;
  llm_parameters: ILLMParameters;
}

export interface ILLMParameters {
  streaming: boolean;
  max_tokens: number;
  model_name: string;
  temperature: number;
  response_format: string;
}

export interface State {
  initLoading: boolean;
  configLoading: boolean;
  datasetName: string;
  docs: IDoc[];
  config: ILLMConfig;
  askAIAllowed: boolean;
  visibleChat: boolean;
  studyIndex: number;
  preResponse: IPreResponse[];
  coResponse: ICoResponse[];
  active: number;
  pre: boolean;
  co: boolean;
  post: boolean;
  interactionLevel: boolean;
}
