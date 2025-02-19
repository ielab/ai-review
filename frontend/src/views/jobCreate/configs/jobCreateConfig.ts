export interface FieldItem {
  [field: string]: {
    label: string
    type?: string
    value?: string
    download?: boolean
    downloadBtn?: boolean
    isExpand?: boolean
    row?: number
    span?: string
    dataKey?: string
    mandatory?: boolean
    disabled?: boolean
    expand?: boolean
  }
}

export const config_section1: FieldItem = {
  id: {
    label: 'Collection ID',
    type: 'text',
    row: 1,
    mandatory: true,
    span: 'tw-w-2/12',
  },
  name: {
    label: 'Collection Name',
    type: 'text',
    row: 1,
    mandatory: true,
    span: 'tw-w-7/12',
  },
}

export const config_section2: FieldItem = {
  name: {
    dataKey: 'name',
    label: 'Job Name',
    type: 'text',
    mandatory: true,
  },
  selection_method_id: {
    dataKey: 'selection_method_id',
    label: 'Model Selection Method',
    type: 'dropdown',
    mandatory: true,
  },
}

export const config_section3: FieldItem = {
  corpus_first_entry: {
    label: 'corpus.jsonl (Preview - the first 10 rows)',
    type: 'codeblock',
    row: 6,
    expand: true,
  },
  queries_first_entry: {
    label: 'queries.jsonl (Preview - the first 10 rows)',
    type: 'codeblock',
    row: 5,
    expand: true,
  },
}
