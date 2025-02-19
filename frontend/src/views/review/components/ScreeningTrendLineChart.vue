<template>
  <Panel
    :pt="panelStyles"
    header="Relevance Discovery Curve"
  >
    <Chart
      type="line"
      :data="chartData"
      :options="chartOptions"
      class="tw-h-[13rem]"
    />
  </Panel>
</template>

<script setup>
import Panel from 'primevue/panel'
import Chart from 'primevue/chart'
import { ref, onMounted } from 'vue'

onMounted(() => {
  chartData.value = setChartData()
  chartOptions.value = setChartOptions()
})

const chartData = ref()
const chartOptions = ref()

const setChartData = () => {
  const documentStyle = getComputedStyle(document.documentElement)

  return {
    labels: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52],
    datasets: [
      {
        data: [0, 4, 7, 12, 17, 20, 21, 25, 29, 32, 33, 34, 40],
        fill: false,
        borderColor: '#8B5CF6',
        tension: 0.4,
      },
    ],
  }
}
const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement)
  const textColor = documentStyle.getPropertyValue('--text-color')
  const textColorSecondary = documentStyle.getPropertyValue(
    '--text-color-secondary',
  )
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border')

  return {
    maintainAspectRatio: false,
    aspectRatio: 0.6,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: textColorSecondary,
        },
        grid: {
          color: surfaceBorder,
        },
        title: {
          display: true,
          text: 'No. of Reviewed Clinical Studies',
        },
      },
      y: {
        ticks: {
          color: textColorSecondary,
        },
        grid: {
          color: surfaceBorder,
        },
        title: {
          display: true,
          text: 'No. of Relevant Clinical Studies',
        },
      },
    },
  }
}

const panelStyles = {
  header: 'tw-py-2',
  content: 'tw-pb-0 tw-p-2',
}
</script>
