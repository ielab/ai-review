import {
  IPageReview,
  IProgessReview,
  IRelevanceDiscoveryCurve,
} from '@/types/statistic'

export const DEFAULT_PAGE_REVIEW: IPageReview = {
  total_number_to_review: 0,
  reviewed: 0,
  include: 0,
  maybe: 0,
  exclude: 0,
}

export const DEFAULT_RELEVANCE_DISCOVERY_CURVE: IRelevanceDiscoveryCurve = {
  'x-axis': {
    value: [0],
    label: '',
  },
  'y-axis': {
    value: [0],
    label: '',
  },
}

export const DEFAULT_PROGRESS_REVIEW: IProgessReview = {
  current_page_review: DEFAULT_PAGE_REVIEW,
  total_page_review: DEFAULT_PAGE_REVIEW,
  relevance_discovery_curve: DEFAULT_RELEVANCE_DISCOVERY_CURVE,
}
