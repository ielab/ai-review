<template>
  <div class="tw-flex tw-gap-x-2 tw-w-full">
    <Accordion
      v-for="(item, index) in queryItems"
      :key="index"
      :activeIndex="0"
      class="tw-w-full"
      expandIcon="pi pi-chevron-up"
      collapseIcon="pi pi-chevron-down"
    >
      <AccordionTab
        :header="item.header"
        :pt="{
          headerAction: 'tw-py-2 tw-text-black',
          content: 'tw-py-0 tw-text-black',
        }"
      >
        <li
          class="tw-text-sm"
          v-for="x in item.content"
        >
          {{ x }}
        </li>
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script lang="ts" setup>
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'

const queryItems = [
  {
    header: 'Population',
    content: ['Aged 19 and over', 'Extraction Of Cataract'],
  },
  { header: 'Intervention', content: ['Insertion Of Intraocular Lens'] },
  { header: 'Comparison', content: ['Insertion Of Intraocular Lens'] },
  {
    header: 'Outcome',
    content: ['Finding Of Color Vision', 'Visual Acuity Testing'],
  },
]
</script>
