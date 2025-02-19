import { ref } from 'vue'

interface IUploadCollectionFilesStore {
  corpus: File | null
  queries: File | null
}

const DEFAULT_UPLOAD_COLLECTION_FILES_STORE: IUploadCollectionFilesStore = {
  corpus: null,
  queries: null,
}

export const uploadCollectionFilesStore = ref<IUploadCollectionFilesStore>({
  ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE,
})

export function clearUploadCollectionFilesStore() {
  uploadCollectionFilesStore.value = { ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE }
}
