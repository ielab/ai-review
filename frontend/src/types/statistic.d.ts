export interface IProgessReview {
  current_page_review: IPageReview
  total_page_review: IPageReview
  relevance_discovery_curve: IRelevanceDiscoveryCurve
  reviewed?: number
  include?: number
  maybe?: number
  exclude?: number
}

export interface IRelevanceDiscoveryCurve {
  'x-axis': IAxis
  'y-axis': IAxis
}

export interface IAxis {
  value: number[]
  label: string
}

export interface IPageReview {
  total_number_to_review: number
  reviewed: number
  include: number
  maybe: number
  exclude: number
}
