export const config_section1 = {
  collectionName: {
    label: 'Dataset/Review Name',
    type: 'text',
    value: '',
    download: false,
    downloadBtn: false,
    row: 1,
    mandatory: true,
  },
}

export const config_section2 = {
  corpus: {
    dataKey: 'corpus',
    label: 'Only the first entry of the corpus',
    type: 'codeblock',
    download: false,
    downloadBtn: false,
    row: 10,
    mandatory: false,
  },
}
