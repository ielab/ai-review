import { IUploadedCorpus, IReview, IDoc, ICorpus } from '@/types/corpus'
import { DEFAULT_PROGRESS_REVIEW } from './statistic'

export const DEFAULT_UPLOADED_CORPUS: IUploadedCorpus = {
  id: null,
  status: '',
  created_at: '',
  updated_at: '',
  hash_corpus_path: '',
  real_corpus_path: '',
  corpus_first_entry: '',
}

export const DEFAULT_CORPUS: ICorpus = {
  title: '',
  authors: [],
  abstract: '',
}

export const DEFAULT_DOC: IDoc = {
  pmid: '',
  rank: 0,
  score: 0,
  feedback: 'unjudge',
  feedback_created_at: '',
  feedback_updated_at: '',
  corpus: DEFAULT_CORPUS,
}

export const DEFAULT_REVIEW: IReview = {
  dataset_name: '',
  screening_progress_pannel: '',
  screening_pannel: [DEFAULT_DOC],
  dashboard_data: DEFAULT_PROGRESS_REVIEW,
  total_number_of_pages: 0,
  current_page_index: 0,
}
