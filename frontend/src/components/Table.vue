<template>
  <div class="card">
    <TreeTable :value="data" paginator :rows="10">
      <Column
        v-for="(item, key) in colTable"
        :key="key"
        :field="item"
        :class="{
          'tw-w-16': item == 'order',
          'tw-w-44': ['name', 'job_queued_at', 'job_started_at', 'timeSpent'].includes(key),
        }"
      >
        <template #header="slotProps">
          <div class="tw-capitalize tw-text-center tw-justify-center tw-flex tw-items-center">
            <div class="tw-flex tw-flex-col">
              {{ slotProps.column.props.field }}
            </div>
          </div>
        </template>
        <template #body="slotProps">
          <slot :name="`col(${key})`" :node="slotProps.node" :key="key">
            <div
              v-if="key == 'status'"
              :class="{
                'tw-text-red-500': slotProps.node.data[key] == 'Error',
                'tw-text-teal-500': slotProps.node.data[key] == 'Finished',
                'tw-text-amber-500':
                  slotProps.node.data[key] == 'Selection' || slotProps.node.data[key] == 'Encoding',
                'tw-text-neutral-400': slotProps.node.data[key] == 'Queued',
                'tw-text-violet-600': slotProps.node.data[key] == 'Created',
              }"
              class="tw-flex tw-items-center tw-justify-center tw-text-center tw-font-semibold"
            >
              {{ slotProps.node.data[key] }}
            </div>
            <div v-else class="tw-flex tw-items-center tw-justify-center tw-text-center">
              {{ slotProps.node.data[key] }}
            </div>
          </slot>
        </template>
      </Column>
      <Column :header="actionColumnHeader" class="tw-text-center">
        <template #body="slotProps">
          <slot name="action" :node="slotProps.node"></slot>
        </template>
      </Column>
    </TreeTable>
  </div>
</template>
<script lang="ts" setup>
import { PropType } from 'vue'

import TreeTable from 'primevue/treetable'
import Column from 'primevue/column'

defineProps({
  data: { type: null },
  colTable: { type: Object },
  tableType: { type: String as PropType<'collection' | 'job'> },
  actionColumnHeader: { type: String, default: 'Action' },
})
</script>
