import { IModel } from '@/types/data'

export interface IJobItem {
  key: number
  data: {
    id: number
    auto_gen_code: string
    name: string
    job_queued_at: string
    job_started_at: string | null
    job_ended_at: string | null
    timeSpent: string
    best_model: IModel
    status: string
  }
}

export const jobColumn = {
  order: 'order',
  name: 'job name (code)',
  job_queued_at: 'submit timestamp',
  job_started_at: 'start timestamp',
  timeSpent: 'time spent',
  best_model: 'best model',
  status: 'Status',
}
