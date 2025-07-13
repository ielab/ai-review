export interface IPreResponse {
  study_index: number;
  content: string;
  performance: IPerformance;
}

export interface ICoResponse {
  key: number;
  studyIndex: number;
  task: "ask_ai" | "pico_extract" | "detail_reason" | "user_ask_ai";
  isLoading: boolean;
  llmResponse: string;
  message?: string;
}

export interface IPerformance {
  processing_time: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  model: string;
}
