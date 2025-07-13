import { ref } from 'vue'

import { IUploadedCorpus } from '@/types/corpus'
import { DEFAULT_UPLOADED_CORPUS } from '@/defaults/corpus'

interface IUploadCollectionFilesStore {
  file: File | null
  corpus: IUploadedCorpus
  inclusionCriteria: string[]
  totalDocuments: number
}

const DEFAULT_UPLOAD_COLLECTION_FILES_STORE: IUploadCollectionFilesStore = {
  file: null,
  corpus: { ...DEFAULT_UPLOADED_CORPUS },
  inclusionCriteria: [],
  totalDocuments: 0,
}

export const uploadCollectionFilesStore = ref<IUploadCollectionFilesStore>({
  ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE,
})

export function clearUploadCollectionFilesStore() {
  uploadCollectionFilesStore.value = {
    ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE,
  }
}
