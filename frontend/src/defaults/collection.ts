import { ICollection, IJobForm } from '@/types/data'

export const CREATE_JOB: IJobForm = {
  name: '',
  selection_method_id: undefined,
}

export const DEFAULT_COLLECTION: ICollection = {
  id: undefined,
  name: '',
  real_corpus_path: '',
  hash_corpus_path: '',
  real_queries_path: '',
  hash_queries_path: '',
  real_embedding_path: '',
  real_search_results_path: '',
  created_at: undefined,
  archived_at: undefined,
  status: '',
  corpus_first_entry: '',
  queries_first_entry: '',
  selection_methods: [],
}
