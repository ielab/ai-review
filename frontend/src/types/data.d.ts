export interface IPreSignedURL {
  url: string
  fields: {
    key: string
    AWSAccessKeyId: string
    policy: string
    signature: string
  }
}

// TODO: Add 'user' interface

export interface ISelectionMethod {
  id: number
  name: string
  description: string
  is_pseudo_query_generated: boolean
}

export interface ICollection {
  id: number | undefined
  name: string
  real_corpus_path: string
  hash_corpus_path: string
  real_queries_path: string
  hash_queries_path: string
  real_embedding_path: string
  real_search_results_path: string
  created_at: Date | undefined
  archived_at: Date | undefined
  status: string
  corpus_first_entry: string
  queries_first_entry: string
  selection_methods: ISelectionMethod[]
  // TODO: Add 'user' field
}

export interface IModel {
  name: string
  score: number
  hash_model_path: string
  model_size_gb: number
}

export interface IJob {
  id: number | undefined
  name: string
  auto_gen_code: string
  selection_method_name: string
  selection_method_description: string
  selection_method_is_pseudo_query_generated: boolean
  collection_id: number | undefined
  collection_name: string
  collection_hash_corpus_path: string
  collection_hash_queries_path: string
  collection_corpus_first_entry: string
  collection_queries_first_entry: string
  job_queued_at: string
  job_started_at: string | null
  job_ended_at: string | null
  waitingTime: string
  timeSpent: string
  status: string
  result: IModel[]
  hash_pseudo_queries_path: string
  hash_pseudo_search_results_path: string
  error_msg: string
}

export interface IJobForm {
  name: name
  selection_method_id: number | undefined
}
