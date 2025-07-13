import { IProgessReview } from './statistic'

export interface IUploadedCorpus {
  id: number | null
  status: string
  created_at: string
  updated_at: string
  hash_corpus_path: string
  real_corpus_path: string
  corpus_first_entry: string
}

export interface Author {
  author: string
  last_name: string
  first_name: string
  affiliations?: string[]
  author_abbreviated: string
}

export interface ICorpus {
  title: string
  authors: Author[]
  abstract: string
}

export interface IFeedback {
  feedback: 'unjudge' | 'include' | 'exclude' | 'maybe'
  feedback_created_at: string
  feedback_updated_at: string
}

export interface IDoc {
  pmid: string
  rank: number
  score: number
  feedback: 'unjudge' | 'include' | 'exclude' | 'maybe'
  feedback_created_at: string
  feedback_updated_at: string
  corpus: ICorpus
}

export interface IReview {
  dataset_name: string
  screening_progress_pannel: string
  screening_pannel: IDoc[]
  dashboard_data: IProgessReview
  total_number_of_pages: number
  current_page_index: nunmber
}

export interface IPicoQuery {
  P: string[]
  I: string[]
  C: string[]
  O: string[]
}
