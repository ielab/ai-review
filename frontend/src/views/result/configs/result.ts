export interface FieldItem {
  [selection: string]: {
    [column: string]: {
      [field: string]: {
        label: string
        type?: string
        value?: string
        download?: boolean
        downloadBtn?: boolean
        isExpand?: boolean
        row?: number
        span?: string
      }
    }
  }
}

export const config: FieldItem = {
  section1: {
    column1: {
      id: {
        label: 'Job ID',
        type: 'text',
        value: '00002',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      name: {
        label: 'Job Name',
        type: 'text',
        value: 'UserName 102',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      auto_gen_code: {
        label: 'Auto-Generated Code',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 5,
        isExpand: false,
      },
    },
    column2: {
      selection_method_name: {
        label: 'Model Selection Method',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      selection_method_description: {
        label: 'Description of Model Selection Method',
        type: 'textArea',
        download: false,
        downloadBtn: false,
        row: 6,
        isExpand: false,
      },
    },
  },
  section2: {
    column: {
      collection_id: {
        label: 'Collection ID',
        type: 'text',
      },
      collection_name: {
        label: 'Collection Name',
        type: 'text',
      },
      collection_corpus_first_entry: {
        label: '1 courpus.jsonl (Preview - the first 10 rows)',
        type: 'codeblock',
        download: true,
        downloadBtn: false,
        row: 5,
        isExpand: false,
        span: 'tw-col-span-2',
      },
      collection_queries_first_entry: {
        label: '2 queries.jsonl (Preview - the first 10 rows)',
        type: 'codeblock',
        download: true,
        downloadBtn: false,
        row: 5,
        isExpand: false,
        span: 'tw-col-span-2',
      },
      job_queued_at: {
        label: 'Queue Timestamp',
        type: 'date',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      waitingTime: {
        label: 'Waiting Time',
        type: 'time',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      job_started_at: {
        label: 'Start Timestamp',
        type: 'date',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      timeSpent: {
        label: 'Time Spent',
        type: 'time',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
    },
  },
  section3: {
    column: {
      result: {
        label: 'Predicted Ranking',
        type: 'table',
        download: false,
        downloadBtn: false,
        row: 7,
        span: 'tw-col-span-2',
      },
      instruction: {
        label: 'Instruction',
        type: 'collapse_textArea',
        value:
          'General Guidelines for Usage  \n\n' +
          'For each model, you can download a zip file with the model checkpoint from HuggingFace MTEB leaderboard, and with the script file with the sample code for inference and search. The following variables are specified for each dense retriever: encoder model, tokenizer and a scoring function (only cosine similarity [cos_sim] or dot product [dot] are supported). Each model also supports two main functions: encode_queries and encode_corpus.',
        download: false,
        downloadBtn: false,
        row: 6,
        isExpand: true,
        span: 'tw-col-span-2',
      },
    },
  },
}

export const configError: FieldItem = {
  section1: {
    column1: {
      id: {
        label: 'Job ID',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      name: {
        label: 'Job Name',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      auto_gen_code: {
        label: 'Auto-Generated Code',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 5,
        isExpand: false,
      },
    },
    column2: {
      selection_method_name: {
        label: 'Model Selection Method',
        type: 'text',
        download: false,
        downloadBtn: false,
        row: 1,
        isExpand: false,
      },
      selection_method_description: {
        label: 'Description of Model Selection Method',
        type: 'textArea',
        download: false,
        downloadBtn: false,
        row: 5,
        isExpand: false,
      },
    },
  },
  section2: {
    column: {
      collection_corpus_first_entry: {
        label: '1 courpus.jsonl (Preview - the first 10 rows)',
        type: 'codeblock',
        download: true,
        downloadBtn: false,
        row: 8,
        isExpand: false,
      },
      collection_queries_first_entry: {
        label: '2 queries.jsonl (Preview - the first 10 rows)',
        type: 'codeblock',
        download: true,
        downloadBtn: false,
        row: 8,
        isExpand: false,
      },
    },
  },
  section3: {
    column: {
      error_msg: {
        label: 'Error',
        type: 'collapse_textArea',
        download: false,
        downloadBtn: false,
        row: 3,
        isExpand: true,
      },
      advice: {
        label: 'Advice',
        type: 'collapse_textArea',
        value:
          'Please check your dataset if it conforms to the requirements of the GenericDataLoader. You then please re-upload your corrected dataset and create as a new job. \n\nIf the error persists, please contact e.khramtsova at uq.edu.au for further information.',
        download: false,
        downloadBtn: false,
        row: 5,
        isExpand: true,
      },
    },
  },
}
