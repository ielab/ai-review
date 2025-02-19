export interface ICollectionItem {
  key: number
  data: {
    id: number
    name: string
    created_at: string
    archived_at: string
    has_queries: boolean
    generated_embedding: boolean
  }
}

export const collectionColumn = {
  order: 'order',
  name: 'collection name',
  created_at: 'create timestamp',
  has_queries: 'has queries?',
  generated_embedding: 'has embedding been generated?',
}
