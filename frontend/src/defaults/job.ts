import { IJob } from '@/types/data'
import { DEFAULT_COLLECTION } from './collection'

export const DENSE_RETRIEVERS = [
  'LARMOR Short',
  'LARMOR Full',
  'Binary Entropy',
  'Query Alteration',
  'Fusion-based QPP',
  'QPP NQC',
  'QPP Sigma Max',
  'QPP SMV',
  'MSMARCO Rank',
  'MTEB Rank',
]

export const DEFAULT_JOB: IJob = {
  id: undefined,
  name: '',
  auto_gen_code: '',
  selection_method_name: '',
  selection_method_description: '',
  selection_method_is_pseudo_query_generated: false,
  collection_id: undefined,
  collection_name: DEFAULT_COLLECTION.name,
  collection_hash_corpus_path: DEFAULT_COLLECTION.hash_corpus_path,
  collection_hash_queries_path: DEFAULT_COLLECTION.hash_queries_path,
  collection_corpus_first_entry: '',
  collection_queries_first_entry: '',
  job_queued_at: '',
  job_started_at: null,
  job_ended_at: null,
  waitingTime: '',
  timeSpent: '',
  status: '',
  result: [],
  hash_pseudo_queries_path: '',
  hash_pseudo_search_results_path: '',
  error_msg: '',
}
