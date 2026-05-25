<template>
  <div class="space-y-6">
    <!-- Charts Container -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Line Chart -->
      <div class="card">
        <h3 class="text-lg font-semibold text-white mb-4">Tốc độ Gói & Lưu lượng (5 phút gần đây)</h3>
        <div class="h-80">
          <canvas ref="lineChartRef"></canvas>
        </div>
      </div>

      <!-- Pie Chart -->
      <div class="card">
        <h3 class="text-lg font-semibold text-white mb-4">Tỷ lệ Normal vs Attack</h3>
        <div class="h-80">
          <canvas ref="pieChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Top IPs Tables -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Attacking IPs -->
      <div class="card">
        <h3 class="text-lg font-semibold text-white mb-4">Top 5 IPs Tấn công</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-700">
                <th class="text-left py-2 text-slate-300">IP Address</th>
                <th class="text-right py-2 text-slate-300">Flows</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ip, idx) in topAttackingIPs" :key="idx" class="border-b border-slate-700 hover:bg-slate-700/50">
                <td class="py-3">
                  <span class="font-mono text-red-400">{{ ip.ip }}</span>
                </td>
                <td class="text-right">
                  <span class="badge badge-danger">{{ ip.count }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Targeted IPs -->
      <div class="card">
        <h3 class="text-lg font-semibold text-white mb-4">Top 5 IPs Bị Nhắm Tới</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-700">
                <th class="text-left py-2 text-slate-300">IP Address</th>
                <th class="text-right py-2 text-slate-300">Flows</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ip, idx) in topTargetedIPs" :key="idx" class="border-b border-slate-700 hover:bg-slate-700/50">
                <td class="py-3">
                  <span class="font-mono text-yellow-400">{{ ip.ip }}</span>
                </td>
                <td class="text-right">
                  <span class="badge badge-warning">{{ ip.count }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import Chart from 'chart.js/auto'
import { useFlowStore } from '../stores'
import { getpkrate, getnormal_attack } from '../composables/dashboad'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

const lineChartRef = ref(null)
const pieChartRef = ref(null)
const lineChart = ref(null)
const pieChart = ref(null)

const flowStore = useFlowStore()
const topAttackingIPs = computed(() => flowStore.topAttackingIPs)
const topTargetedIPs = computed(() => flowStore.topTargetedIPs)

let refreshInterval = null
let isUpdating = false

// Debounce helper
const debounce = (fn, delay = 100) => {
  let timeout
  return (...args) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}

const safeUpdateLineChart = debounce(async () => {
  if (!lineChart.value || isUpdating) return
  isUpdating = true

  try {
    const data = await getpkrate()
    if (!data?.labels || !data?.datasets?.length) return

    const chart = lineChart.value

    // Cập nhật labels
    chart.data.labels = [...data.labels]

    // Cập nhật datasets một cách an toàn
    const newDatasets = data.datasets.map((dataset, index) => ({
      ...dataset,
      yAxisID: index === 0 ? 'y' : 'y1',
      tension: 0.3,
      fill: true
    }))

    // Thay thế datasets cũ
    chart.data.datasets = newDatasets

    chart.update('none')
  } catch (error) {
    console.error('Error updating line chart:', error)
  } finally {
    isUpdating = false
  }
}, 300)

const safeUpdatePieChart = debounce(async () => {
  if (!pieChart.value || isUpdating) return
  isUpdating = true

  try {
    const data = await getnormal_attack()
    if (!data?.datasets?.[0]?.data) return

    const chart = pieChart.value
    const dataset = chart.data.datasets[0]

    dataset.data = [...data.datasets[0].data]

    if (data.labels?.length) {
      chart.data.labels = [...data.labels]
    }

    if (data.datasets[0].backgroundColor) {
      dataset.backgroundColor = [...data.datasets[0].backgroundColor]
    }
    if (data.datasets[0].borderColor) {
      dataset.borderColor = [...data.datasets[0].borderColor]
    }

    chart.update('none')
  } catch (error) {
    console.error('Error updating pie chart:', error)
  } finally {
    isUpdating = false
  }
}, 300)

onMounted(async () => {
  try {
    const [lineData, pieData] = await Promise.all([
      getpkrate(),
      getnormal_attack()
    ])

    // Line Chart
    const lineCtx = lineChartRef.value.getContext('2d')
    lineChart.value = new ChartJS(lineCtx, {
      type: 'line',
      data: {
        labels: lineData.labels || [],
        datasets: (lineData.datasets || []).map((dataset, index) => ({
          ...dataset,
          yAxisID: index === 0 ? 'y' : 'y1',
          tension: 0.3,
          fill: true
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { labels: { color: '#cbd5e1' } } },
        scales: {
          y: { type: 'linear', position: 'left', title: { display: true, text: 'Packet Rate (pps)', color: '#cbd5e1' }, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
          y1: { type: 'linear', position: 'right', title: { display: true, text: 'Kbps', color: '#cbd5e1' }, ticks: { color: '#94a3b8' }, grid: { drawOnChartArea: false } },
          x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
        }
      }
    })

    // Pie Chart
    const pieCtx = pieChartRef.value.getContext('2d')
    pieChart.value = new ChartJS(pieCtx, {
      type: 'doughnut',
      data: {
        labels: pieData?.labels || ['Normal', 'Attack'],
        datasets: [{
          data: pieData?.datasets?.[0]?.data || [65, 35],
          backgroundColor: pieData?.datasets?.[0]?.backgroundColor || ['#10b981', '#ef4444'],
          borderColor: pieData?.datasets?.[0]?.borderColor || ['#064e3b', '#7f1d1d'],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#cbd5e1', padding: 20, font: { size: 12 } }
          }
        }
      }
    })

    // Auto refresh với debounce
    refreshInterval = setInterval(() => {
      safeUpdateLineChart()
      safeUpdatePieChart()
    }, 5000)

  } catch (error) {
    console.error('Lỗi khởi tạo chart:', error)
  }
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  lineChart.value?.destroy()
  pieChart.value?.destroy()
})
</script>